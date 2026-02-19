"""Tests for HOTA 1.8.x parsing, writing, roundtrip, and conversions."""

import tempfile
from pathlib import Path

import pytest

from h3tc.parsers.hota18 import Hota18Parser
from h3tc.parsers.hota import HotaParser
from h3tc.writers.hota18 import Hota18Writer
from h3tc.writers.hota import HotaWriter
from h3tc.converters.hota_to_hota18 import hota_to_hota18
from h3tc.converters.hota18_to_hota import hota18_to_hota
from h3tc.converters.hota_to_sod import hota_to_sod
from h3tc.converters.sod_to_hota import sod_to_hota
from h3tc.formats import detect_format

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
HOTA18_FILEPATH = TEMPLATES_DIR / "jebus_converted.h3t"


@pytest.fixture
def hota18_filepath():
    return HOTA18_FILEPATH


# ── Parsing ──────────────────────────────────────────────────────────────


def test_hota18_parse_basic(hota18_filepath):
    """Parse HOTA 1.8.x file and verify structure."""
    parser = Hota18Parser()
    pack = parser.parse(hota18_filepath)

    assert pack.metadata is not None
    assert pack.field_counts is not None
    assert pack.field_counts.town == "12"
    assert len(pack.maps) >= 1


def test_hota18_parse_zone_factions(hota18_filepath):
    """Verify zones have 12 town factions and 13 monster factions."""
    parser = Hota18Parser()
    pack = parser.parse(hota18_filepath)

    zone = pack.maps[0].zones[0]
    assert len(zone.town_types) == 12
    assert "Bulwark" in zone.town_types
    assert "Factory" in zone.town_types

    assert len(zone.monster_factions) == 13
    assert "Bulwark" in zone.monster_factions
    assert "Neutral" in zone.monster_factions


# ── Format detection ─────────────────────────────────────────────────────


def test_hota18_format_detection(hota18_filepath):
    """Verify auto-detection picks Hota18Parser for 140-col files."""
    parser = detect_format(hota18_filepath)
    assert parser.format_id == "hota18"


def test_format_detection_all_formats(hota18_filepath, hota_filepath, sod_filepath):
    """Verify auto-detection works for all three formats."""
    assert detect_format(sod_filepath).format_id == "sod"
    assert detect_format(hota_filepath).format_id == "hota17"
    assert detect_format(hota18_filepath).format_id == "hota18"


# ── Roundtrip ────────────────────────────────────────────────────────────


def test_hota18_roundtrip(hota18_filepath):
    """Parse HOTA 1.8.x -> write -> parse again -> compare."""
    parser = Hota18Parser()
    original = parser.parse(hota18_filepath)

    with tempfile.NamedTemporaryFile(suffix=".h3t", delete=False) as f:
        outpath = Path(f.name)

    writer = Hota18Writer()
    writer.write(original, outpath)

    roundtripped = parser.parse(outpath)
    outpath.unlink()

    assert len(original.maps) == len(roundtripped.maps)
    assert original.metadata == roundtripped.metadata
    assert original.field_counts == roundtripped.field_counts

    for om, rm in zip(original.maps, roundtripped.maps):
        assert om.name == rm.name
        assert len(om.zones) == len(rm.zones)
        assert len(om.connections) == len(rm.connections)

        for oz, rz in zip(om.zones, rm.zones):
            assert oz == rz

        for oc, rc in zip(om.connections, rm.connections):
            oc_dict = oc.model_dump(exclude={"extra_zone_cols"})
            rc_dict = rc.model_dump(exclude={"extra_zone_cols"})
            assert oc_dict == rc_dict


# ── Conversions ──────────────────────────────────────────────────────────


def test_hota_to_hota18(hota_filepath):
    """Convert HOTA 1.7.x -> 1.8.x and verify Bulwark added."""
    parser = HotaParser()
    hota_pack = parser.parse(hota_filepath)

    hota18_pack = hota_to_hota18(hota_pack)

    assert hota18_pack.field_counts.town == "12"
    assert len(hota18_pack.maps) == len(hota_pack.maps)

    for hm, h18m in zip(hota_pack.maps, hota18_pack.maps):
        assert h18m.name == hm.name
        assert len(h18m.zones) == len(hm.zones)

        for hz, h18z in zip(hm.zones, h18m.zones):
            assert "Bulwark" in h18z.town_types
            assert "Bulwark" in h18z.monster_factions
            assert len(h18z.town_types) == 12
            assert len(h18z.monster_factions) == 13


def test_hota18_to_hota(hota18_filepath):
    """Convert HOTA 1.8.x -> 1.7.x and verify Bulwark removed."""
    parser = Hota18Parser()
    hota18_pack = parser.parse(hota18_filepath)

    hota_pack = hota18_to_hota(hota18_pack)

    assert hota_pack.field_counts.town == "11"
    assert len(hota_pack.maps) == len(hota18_pack.maps)

    for h18m, hm in zip(hota18_pack.maps, hota_pack.maps):
        for h18z, hz in zip(h18m.zones, hm.zones):
            assert "Bulwark" not in hz.town_types
            assert "Bulwark" not in hz.monster_factions
            assert len(hz.town_types) == 11
            assert len(hz.monster_factions) == 12


def test_hota18_to_sod(hota18_filepath):
    """Convert HOTA 1.8.x -> SOD (via hota_to_sod)."""
    parser = Hota18Parser()
    hota18_pack = parser.parse(hota18_filepath)

    sod_pack = hota_to_sod(hota18_pack)

    assert sod_pack.metadata is None
    assert sod_pack.field_counts is None
    assert len(sod_pack.maps) == len(hota18_pack.maps)

    for sod_map in sod_pack.maps:
        for zone in sod_map.zones:
            assert "Bulwark" not in zone.town_types
            assert "Bulwark" not in zone.monster_factions


def test_sod_to_hota18(sod_filepath):
    """Convert SOD -> HOTA 1.8.x (via sod_to_hota then hota_to_hota18)."""
    from h3tc.parsers.sod import SodParser

    sod_pack = SodParser().parse(sod_filepath)
    hota_pack = sod_to_hota(sod_pack, pack_name="Test 1.8")
    hota18_pack = hota_to_hota18(hota_pack)

    assert hota18_pack.field_counts.town == "12"
    assert hota18_pack.metadata.name == "Test 1.8"

    for tmap in hota18_pack.maps:
        for zone in tmap.zones:
            assert "Bulwark" in zone.town_types
            assert "Bulwark" in zone.monster_factions


def test_hota_to_hota18_roundtrip_write(hota_filepath):
    """Convert HOTA 1.7.x -> 1.8.x, write, parse back."""
    hota_pack = HotaParser().parse(hota_filepath)
    hota18_pack = hota_to_hota18(hota_pack)

    with tempfile.NamedTemporaryFile(suffix=".h3t", delete=False) as f:
        outpath = Path(f.name)

    Hota18Writer().write(hota18_pack, outpath)
    reparsed = Hota18Parser().parse(outpath)
    outpath.unlink()

    assert len(reparsed.maps) == len(hota_pack.maps)
    for om, rm in zip(hota18_pack.maps, reparsed.maps):
        assert om.name == rm.name
        assert len(om.zones) == len(rm.zones)
        for oz, rz in zip(om.zones, rm.zones):
            assert oz == rz


# Use conftest fixtures
@pytest.fixture
def hota_filepath():
    return TEMPLATES_DIR / "hota_original_template_pack.h3t"


@pytest.fixture
def sod_filepath():
    return TEMPLATES_DIR / "sod_original_template_pack.txt"
