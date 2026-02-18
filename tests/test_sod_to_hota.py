"""Tests for SOD -> HOTA conversion."""

import tempfile
from pathlib import Path

import pytest

from h3tc.parsers.sod import SodParser
from h3tc.parsers.hota import HotaParser
from h3tc.writers.hota import HotaWriter
from h3tc.converters.sod_to_hota import sod_to_hota


def test_sod_to_hota_basic(sod_filepath):
    """Convert SOD pack to HOTA and verify structure."""
    parser = SodParser()
    sod_pack = parser.parse(sod_filepath)

    hota_pack = sod_to_hota(sod_pack, pack_name="Test Pack")

    # Pack metadata
    assert hota_pack.metadata is not None
    assert hota_pack.metadata.name == "Test Pack"
    assert hota_pack.field_counts is not None

    # Same number of maps
    assert len(hota_pack.maps) == len(sod_pack.maps)

    # Each map has same zones and connections count
    for sod_map, hota_map in zip(sod_pack.maps, hota_pack.maps):
        assert hota_map.name == sod_map.name
        assert hota_map.min_size == sod_map.min_size
        assert hota_map.max_size == sod_map.max_size
        assert len(hota_map.zones) == len(sod_map.zones)
        assert len(hota_map.connections) == len(sod_map.connections)

        # Map options should be set (not None)
        assert hota_map.options.artifacts is not None


def test_sod_to_hota_zone_conversion(sod_filepath):
    """Verify zone fields are correctly converted."""
    parser = SodParser()
    sod_pack = parser.parse(sod_filepath)
    hota_pack = sod_to_hota(sod_pack)

    sod_zone = sod_pack.maps[0].zones[0]
    hota_zone = hota_pack.maps[0].zones[0]

    # Core fields preserved
    assert hota_zone.id == sod_zone.id
    assert hota_zone.human_start == sod_zone.human_start
    assert hota_zone.base_size == sod_zone.base_size
    assert hota_zone.positions == sod_zone.positions
    assert hota_zone.monster_strength == sod_zone.monster_strength

    # Town types: Conflux mapped; Cove/Factory enabled when all SOD factions are
    assert "Conflux" in hota_zone.town_types
    assert hota_zone.town_types["Cove"] == "x"  # all SOD factions enabled
    assert hota_zone.town_types["Factory"] == "x"
    assert "Elemental" not in hota_zone.town_types

    # Terrains: Highlands/Wasteland empty (SOD terrains not all enabled)
    assert hota_zone.terrains["Highlands"] == ""
    assert hota_zone.terrains["Wasteland"] == ""

    # Monster factions: Forge dropped, Conflux/Cove/Factory enabled (all SOD on)
    assert "Forge" not in hota_zone.monster_factions
    assert hota_zone.monster_factions["Conflux"] == "x"
    assert hota_zone.monster_factions["Cove"] == "x"
    assert hota_zone.monster_factions["Factory"] == "x"

    # Zone options defaults
    assert hota_zone.zone_options.placement == ""
    assert hota_zone.zone_options.monsters_disposition_standard == "3"
    assert hota_zone.zone_options.monsters_joining_percentage == "1"
    assert hota_zone.zone_options.monsters_join_only_for_money == "x"


def test_sod_to_hota_connection_conversion(sod_filepath):
    """Verify connection fields are correctly converted."""
    parser = SodParser()
    sod_pack = parser.parse(sod_filepath)
    hota_pack = sod_to_hota(sod_pack)

    sod_conn = sod_pack.maps[0].connections[0]
    hota_conn = hota_pack.maps[0].connections[0]

    # Core fields preserved
    assert hota_conn.zone1 == sod_conn.zone1
    assert hota_conn.zone2 == sod_conn.zone2
    assert hota_conn.value == sod_conn.value
    assert hota_conn.positions == sod_conn.positions

    # HOTA-only fields set to empty (matching game behavior)
    assert hota_conn.road == ""
    assert hota_conn.conn_type == ""
    assert hota_conn.fictive == ""
    assert hota_conn.portal_repulsion == ""


def test_sod_to_hota_roundtrip_write(sod_filepath):
    """Convert SOD->HOTA, write, parse back, verify structure intact."""
    sod_parser = SodParser()
    sod_pack = sod_parser.parse(sod_filepath)
    hota_pack = sod_to_hota(sod_pack, pack_name="Roundtrip Test")

    with tempfile.NamedTemporaryFile(suffix=".h3t", delete=False) as f:
        outpath = Path(f.name)

    writer = HotaWriter()
    writer.write(hota_pack, outpath)

    # Parse back
    hota_parser = HotaParser()
    reparsed = hota_parser.parse(outpath)
    outpath.unlink()

    assert reparsed.metadata.name == "Roundtrip Test"
    assert len(reparsed.maps) == len(sod_pack.maps)

    for sod_map, reparsed_map in zip(sod_pack.maps, reparsed.maps):
        assert reparsed_map.name == sod_map.name
        assert len(reparsed_map.zones) == len(sod_map.zones)
        assert len(reparsed_map.connections) == len(sod_map.connections)
