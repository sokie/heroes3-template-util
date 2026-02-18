"""Tests for HOTA -> SOD conversion."""

import tempfile
from pathlib import Path

import pytest

from h3tc.parsers.hota import HotaParser
from h3tc.parsers.sod import SodParser
from h3tc.writers.sod import SodWriter
from h3tc.converters.hota_to_sod import hota_to_sod


def test_hota_to_sod_basic(hota_filepath):
    """Convert HOTA pack to SOD and verify structure."""
    parser = HotaParser()
    hota_pack = parser.parse(hota_filepath)

    sod_pack = hota_to_sod(hota_pack)

    # No pack metadata in SOD
    assert sod_pack.metadata is None
    assert sod_pack.field_counts is None

    # Same number of maps
    assert len(sod_pack.maps) == len(hota_pack.maps)

    for hota_map, sod_map in zip(hota_pack.maps, sod_pack.maps):
        assert sod_map.name == hota_map.name
        assert len(sod_map.zones) == len(hota_map.zones)
        assert len(sod_map.connections) == len(hota_map.connections)


def test_hota_to_sod_zone_conversion(hota_filepath):
    """Verify zone fields are correctly converted to SOD."""
    parser = HotaParser()
    hota_pack = parser.parse(hota_filepath)
    sod_pack = hota_to_sod(hota_pack)

    hota_zone = hota_pack.maps[0].zones[0]
    sod_zone = sod_pack.maps[0].zones[0]

    # Core fields preserved
    assert sod_zone.id == hota_zone.id
    assert sod_zone.human_start == hota_zone.human_start
    assert sod_zone.base_size == hota_zone.base_size
    assert sod_zone.positions == hota_zone.positions

    # Town types: only SOD factions (no Cove/Factory)
    assert "Cove" not in sod_zone.town_types
    assert "Factory" not in sod_zone.town_types

    # Terrains: no Highlands/Wasteland
    assert "Highlands" not in sod_zone.terrains
    assert "Wasteland" not in sod_zone.terrains

    # Monster factions: no Conflux/Cove/Factory, Forge added
    assert "Forge" in sod_zone.monster_factions
    assert sod_zone.monster_factions["Forge"] == "x"

    # Zone options stripped
    assert sod_zone.zone_options.placement is None


def test_hota_to_sod_connection_conversion(hota_filepath):
    """Verify connection HOTA-only fields are stripped."""
    parser = HotaParser()
    hota_pack = parser.parse(hota_filepath)
    sod_pack = hota_to_sod(hota_pack)

    sod_conn = sod_pack.maps[0].connections[0]

    assert sod_conn.road is None
    assert sod_conn.conn_type is None
    assert sod_conn.fictive is None
    assert sod_conn.portal_repulsion is None


def test_hota_to_sod_roundtrip_write(hota_filepath):
    """Convert HOTA->SOD, write, parse back, verify structure."""
    hota_parser = HotaParser()
    hota_pack = hota_parser.parse(hota_filepath)
    sod_pack = hota_to_sod(hota_pack)

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        outpath = Path(f.name)

    writer = SodWriter()
    writer.write(sod_pack, outpath)

    # Parse back
    sod_parser = SodParser()
    reparsed = sod_parser.parse(outpath)
    outpath.unlink()

    assert len(reparsed.maps) == len(hota_pack.maps)

    for hota_map, reparsed_map in zip(hota_pack.maps, reparsed.maps):
        assert reparsed_map.name == hota_map.name
        assert len(reparsed_map.zones) == len(hota_map.zones)
        assert len(reparsed_map.connections) == len(hota_map.connections)


def test_sod_hota_sod_roundtrip(sod_filepath):
    """SOD -> HOTA -> SOD roundtrip: shared fields should match."""
    from h3tc.converters.sod_to_hota import sod_to_hota

    sod_parser = SodParser()
    original = sod_parser.parse(sod_filepath)

    # SOD -> HOTA -> SOD
    hota_pack = sod_to_hota(original, pack_name="test")
    back_to_sod = hota_to_sod(hota_pack)

    assert len(back_to_sod.maps) == len(original.maps)

    for orig_map, rt_map in zip(original.maps, back_to_sod.maps):
        assert rt_map.name == orig_map.name
        assert len(rt_map.zones) == len(orig_map.zones)

        for orig_z, rt_z in zip(orig_map.zones, rt_map.zones):
            assert rt_z.id == orig_z.id
            assert rt_z.base_size == orig_z.base_size
            assert rt_z.positions == orig_z.positions
            assert rt_z.monster_strength == orig_z.monster_strength
            assert rt_z.min_mines == orig_z.min_mines
            assert rt_z.mine_density == orig_z.mine_density
            # Town types: Conflux should match (was Elemental->Conflux in SOD parse)
            for faction in ["Castle", "Rampart", "Tower", "Inferno",
                            "Necropolis", "Dungeon", "Stronghold",
                            "Fortress", "Conflux"]:
                assert rt_z.town_types.get(faction) == orig_z.town_types.get(faction), (
                    f"Town type {faction} mismatch in zone {orig_z.id}"
                )
