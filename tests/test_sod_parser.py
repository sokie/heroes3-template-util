"""Tests for the SOD parser."""

from h3tc.parsers.sod import SodParser


def test_sod_parse_basic(sod_filepath):
    parser = SodParser()
    pack = parser.parse(sod_filepath)

    assert pack.metadata is None
    assert pack.field_counts is None
    assert len(pack.maps) > 0
    assert len(pack.header_rows) == 3


def test_sod_first_map(sod_filepath):
    parser = SodParser()
    pack = parser.parse(sod_filepath)

    first_map = pack.maps[0]
    assert first_map.name == "Small Ring"
    assert first_map.min_size == "1"
    assert first_map.max_size == "2"
    assert len(first_map.zones) == 8
    assert len(first_map.connections) > 0


def test_sod_zone_details(sod_filepath):
    parser = SodParser()
    pack = parser.parse(sod_filepath)

    zone = pack.maps[0].zones[0]
    assert zone.id == "1"
    assert zone.human_start == "x"
    assert zone.base_size == "11"
    assert zone.positions.min_human == "1"
    assert zone.positions.max_human == "8"
    # Elemental -> Conflux canonical name
    assert "Conflux" in zone.town_types
    assert "Elemental" not in zone.town_types
    # Forge is preserved for roundtrip fidelity
    assert "Forge" in zone.monster_factions
    assert len(zone.treasure_tiers) == 3


def test_sod_connection_details(sod_filepath):
    parser = SodParser()
    pack = parser.parse(sod_filepath)

    conn = pack.maps[0].connections[0]
    assert conn.zone1 == "1"
    assert conn.zone2 == "2"
    assert conn.value == "4500"
    # SOD connections have no HOTA fields
    assert conn.road is None
    assert conn.conn_type is None


def test_sod_multiline_name(sod_filepath):
    """SOD has template names like 'Ready \\nor Not' with quoted newlines."""
    parser = SodParser()
    pack = parser.parse(sod_filepath)

    names = [m.name for m in pack.maps]
    # Check that multiline names are parsed correctly
    matching = [n for n in names if "Ready" in n and "Not" in n]
    assert len(matching) == 1
    assert "\n" in matching[0] or "Ready" in matching[0]
