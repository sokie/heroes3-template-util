"""Tests for SOD -> HOTA conversion."""

import tempfile
from pathlib import Path

import pytest

from h3tc.parsers.sod import SodParser
from h3tc.parsers.hota import HotaParser
from h3tc.parsers.hota18 import Hota18Parser
from h3tc.writers.hota import HotaWriter
from h3tc.converters.sod_to_hota import sod_to_hota
from h3tc.converters.hota_to_hota18 import hota_to_hota18

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


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

    # Monster factions: Forge dropped, Cove/Factory enabled (any SOD on),
    # Conflux enabled (all SOD factions including Forge were on)
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


# --- Game comparison helpers ---

_ZONE_SKIP_FIELDS = {"zone_options", "positions"}
_ZONE_OPTION_SKIP_FIELDS = {"image_settings"}


def _compare_zones(our_zone, game_zone, skip_monster_strength=False):
    """Compare two zones field-by-field, skipping image_settings."""
    for field in our_zone.model_fields:
        if field in _ZONE_SKIP_FIELDS:
            continue
        if skip_monster_strength and field == "monster_strength":
            continue
        our_val = getattr(our_zone, field)
        game_val = getattr(game_zone, field)
        assert our_val == game_val, (
            f"Zone {our_zone.id} field '{field}' mismatch: "
            f"{our_val!r} != {game_val!r}"
        )
    # Compare zone_options excluding image_settings
    for field in our_zone.zone_options.model_fields:
        if field in _ZONE_OPTION_SKIP_FIELDS:
            continue
        our_val = getattr(our_zone.zone_options, field)
        game_val = getattr(game_zone.zone_options, field)
        assert our_val == game_val, (
            f"Zone {our_zone.id} zone_options.{field} mismatch: "
            f"{our_val!r} != {game_val!r}"
        )


# --- Game comparison tests ---


def test_sod_to_hota18_vs_game_jebus():
    """Compare our SOD→HOTA18 conversion against the game's for Jebus Cross."""
    sod_path = TEMPLATES_DIR / "sod_complete" / "Jebus Cross" / "rmg.txt"
    game_path = TEMPLATES_DIR / "jebus_converted.h3t"

    sod_pack = SodParser().parse(sod_path)
    hota_pack = sod_to_hota(sod_pack)
    hota18_pack = hota_to_hota18(hota_pack)

    game_pack = Hota18Parser().parse(game_path)

    assert len(hota18_pack.maps) == len(game_pack.maps)
    for our_map, game_map in zip(hota18_pack.maps, game_pack.maps):
        assert len(our_map.zones) == len(game_map.zones)
        for our_zone, game_zone in zip(our_map.zones, game_map.zones):
            _compare_zones(our_zone, game_zone)


def test_sod_to_hota18_vs_game_original():
    """Compare our SOD→HOTA18 conversion against the game's for {Original} (first map)."""
    sod_path = TEMPLATES_DIR / "sod_complete" / "{Original}" / "rmg.txt"
    game_path = TEMPLATES_DIR / "orig_converted.h3t"

    sod_pack = SodParser().parse(sod_path)
    hota_pack = sod_to_hota(sod_pack)
    hota18_pack = hota_to_hota18(hota_pack)

    game_pack = Hota18Parser().parse(game_path)

    # Compare first map's zones (skip monster_strength: our writer outputs
    # "normal" which is the normalized form, game may preserve SOD's "avg")
    our_map = hota18_pack.maps[0]
    game_map = game_pack.maps[0]
    assert len(our_map.zones) == len(game_map.zones)
    for our_zone, game_zone in zip(our_map.zones, game_map.zones):
        _compare_zones(our_zone, game_zone, skip_monster_strength=True)


def test_sod_monster_strength_normalization():
    """Verify the SOD parser normalizes 'avg' to 'normal' for monster_strength."""
    sod_path = TEMPLATES_DIR / "sod_original_template_pack.txt"
    sod_pack = SodParser().parse(sod_path)

    # The fixture has 'avg' in the raw file; parser should normalize to 'normal'
    zone = sod_pack.maps[0].zones[0]
    assert zone.monster_strength == "normal"
