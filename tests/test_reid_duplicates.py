"""Tests for Re-ID handling of duplicate/missing zone IDs and list reordering."""

import pytest
from PySide6.QtWidgets import QApplication

from h3tc.editor.canvas.scene import TemplateScene
from h3tc.models import Connection, TemplateMap, Zone, ZoneOptions

METHODS = ["dfs", "bfs"]

# Ensure a QApplication exists for QGraphicsScene
_app = QApplication.instance() or QApplication([])


def _make_map(
    zone_ids: list[str],
    connections: list[tuple[str, str]],
    positions: dict[str, tuple[float, float]],
) -> TemplateMap:
    """Build a TemplateMap with zones at given positions (via image_settings)."""
    zones = []
    for zid in zone_ids:
        pos = positions.get(zid, (100, 100))
        zone = Zone(
            id=zid,
            zone_options=ZoneOptions(
                image_settings=f"{int(pos[0])} {int(pos[1])}"
            ),
        )
        zones.append(zone)
    conns = [Connection(zone1=z1, zone2=z2, value="5000") for z1, z2 in connections]
    return TemplateMap(name="test", min_size="1", max_size="2",
                       zones=zones, connections=conns)


def _reid_via_scene(
    zone_ids: list[str],
    connections: list[tuple[str, str]],
    positions: dict[str, tuple[float, float]],
    method: str = "dfs",
) -> tuple[TemplateScene, TemplateMap, dict[str, str] | None]:
    """Create a scene, load a map, run re-ID, and return results."""
    tmap = _make_map(zone_ids, connections, positions)
    scene = TemplateScene()
    scene.load_map(tmap)
    mapping = scene.reid_zones(method=method)
    return scene, tmap, mapping


# ---------------------------------------------------------------------------
# Duplicate zone IDs
# ---------------------------------------------------------------------------


class TestDuplicateZoneIds:
    """Re-ID should handle duplicate zone IDs gracefully."""

    @pytest.mark.parametrize("method", METHODS)
    def test_two_zones_same_id(self, method):
        """Two zones with the same ID get unique sequential IDs after re-ID."""
        positions = {"1": (0, 0), "1_dup": (100, 0)}
        # Both zones have id="1"; we need positions for each zone object
        # We pass duplicate IDs in the list and unique keys in positions
        # for the image_settings
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="1", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="1", zone_options=ZoneOptions(image_settings="100 0")),
            ],
            connections=[Connection(zone1="1", zone2="1", value="5000")],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)

        ids = [z.id.strip() for z in tmap.zones]
        assert len(set(ids)) == 2, f"IDs should be unique, got {ids}"
        assert sorted(ids, key=int) == ["1", "2"]

    @pytest.mark.parametrize("method", METHODS)
    def test_three_zones_all_same_id(self, method):
        """Three zones all with id='5' get re-ID'd to 1, 2, 3."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="5", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="5", zone_options=ZoneOptions(image_settings="100 0")),
                Zone(id="5", zone_options=ZoneOptions(image_settings="200 0")),
            ],
            connections=[],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)

        ids = [z.id.strip() for z in tmap.zones]
        assert len(set(ids)) == 3, f"IDs should be unique, got {ids}"
        assert sorted(ids, key=int) == ["1", "2", "3"]

    @pytest.mark.parametrize("method", METHODS)
    def test_mixed_duplicates_and_unique(self, method):
        """Mix of duplicate and unique IDs all get clean sequential IDs."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="3", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="3", zone_options=ZoneOptions(image_settings="100 0")),
                Zone(id="7", zone_options=ZoneOptions(image_settings="200 0")),
                Zone(id="7", zone_options=ZoneOptions(image_settings="300 0")),
                Zone(id="1", zone_options=ZoneOptions(image_settings="400 0")),
            ],
            connections=[],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)

        ids = [z.id.strip() for z in tmap.zones]
        assert len(set(ids)) == 5, f"IDs should all be unique, got {ids}"
        assert sorted(ids, key=int) == ["1", "2", "3", "4", "5"]


# ---------------------------------------------------------------------------
# Zone list reordering after Re-ID
# ---------------------------------------------------------------------------


class TestZoneListReordering:
    """After Re-ID, the zones list should be sorted by new ID."""

    @pytest.mark.parametrize("method", METHODS)
    def test_zones_sorted_by_id_after_reid(self, method):
        """Zones list order matches sequential IDs after re-ID."""
        # Zone IDs in reverse order — re-ID should fix ordering
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["3", "2", "1"],
            connections=[("1", "2"), ("2", "3")],
            positions={"1": (0, 0), "2": (100, 0), "3": (200, 0)},
            method=method,
        )

        ids = [z.id.strip() for z in tmap.zones]
        assert ids == [str(i + 1) for i in range(len(ids))], (
            f"Zones should be in sequential order, got {ids}"
        )

    @pytest.mark.parametrize("method", METHODS)
    def test_reordering_matches_expected_sequential(self, method):
        """Each zone at index i should have id=str(i+1)."""
        scene, tmap, _ = _reid_via_scene(
            zone_ids=["5", "3", "1", "4", "2"],
            connections=[("1", "2"), ("2", "3"), ("3", "4"), ("4", "5")],
            positions={
                "1": (0, 0), "2": (100, 0), "3": (200, 0),
                "4": (300, 0), "5": (400, 0),
            },
            method=method,
        )

        for i, zone in enumerate(tmap.zones):
            expected = str(i + 1)
            assert zone.id.strip() == expected, (
                f"Zone at index {i} should have id={expected}, got {zone.id}"
            )

    @pytest.mark.parametrize("method", METHODS)
    def test_save_validation_no_renumber_after_reid(self, method):
        """After Re-ID, save validation should find no issues to fix."""
        scene, tmap, _ = _reid_via_scene(
            zone_ids=["3", "1", "2"],
            connections=[("1", "2"), ("2", "3")],
            positions={"1": (0, 0), "2": (100, 0), "3": (200, 0)},
            method=method,
        )

        # Simulate the save validation check from main_window._validate_and_fix
        expected = [str(i + 1) for i in range(len(tmap.zones))]
        actual = [z.id.strip() for z in tmap.zones]
        assert actual == expected, (
            f"Save validation would re-number: actual={actual}, expected={expected}"
        )


# ---------------------------------------------------------------------------
# Connections updated correctly
# ---------------------------------------------------------------------------


class TestConnectionsAfterReid:
    """Connections should reference the new zone IDs after Re-ID."""

    @pytest.mark.parametrize("method", METHODS)
    def test_connections_use_new_ids(self, method):
        """Connection zone references are updated to new IDs."""
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["10", "20", "30"],
            connections=[("10", "20"), ("20", "30")],
            positions={"10": (0, 0), "20": (100, 0), "30": (200, 0)},
            method=method,
        )

        zone_ids = {z.id.strip() for z in tmap.zones}
        for conn in tmap.connections:
            assert conn.zone1.strip() in zone_ids, (
                f"Connection zone1={conn.zone1} not in zone IDs {zone_ids}"
            )
            assert conn.zone2.strip() in zone_ids, (
                f"Connection zone2={conn.zone2} not in zone IDs {zone_ids}"
            )

    @pytest.mark.parametrize("method", METHODS)
    def test_connections_updated_with_duplicates(self, method):
        """Connections are updated even when starting from duplicate IDs."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="1", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="1", zone_options=ZoneOptions(image_settings="100 0")),
                Zone(id="2", zone_options=ZoneOptions(image_settings="200 0")),
            ],
            connections=[Connection(zone1="1", zone2="2", value="5000")],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)

        zone_ids = {z.id.strip() for z in tmap.zones}
        assert len(zone_ids) == 3
        for conn in tmap.connections:
            assert conn.zone1.strip() in zone_ids
            assert conn.zone2.strip() in zone_ids


# ---------------------------------------------------------------------------
# Zone items dict consistency
# ---------------------------------------------------------------------------


class TestZoneItemsConsistency:
    """The scene's _zone_items dict should be consistent after Re-ID."""

    @pytest.mark.parametrize("method", METHODS)
    def test_zone_items_match_zone_ids(self, method):
        """Every zone ID has a corresponding entry in _zone_items."""
        scene, tmap, _ = _reid_via_scene(
            zone_ids=["3", "1", "2"],
            connections=[("1", "2"), ("2", "3")],
            positions={"1": (0, 0), "2": (100, 0), "3": (200, 0)},
            method=method,
        )

        zone_ids = {z.id.strip() for z in tmap.zones}
        item_ids = set(scene._zone_items.keys())
        assert zone_ids == item_ids, (
            f"Zone IDs {zone_ids} != item IDs {item_ids}"
        )

    @pytest.mark.parametrize("method", METHODS)
    def test_zone_items_after_dedup(self, method):
        """After de-duplication, _zone_items has correct count."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="1", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="1", zone_options=ZoneOptions(image_settings="100 0")),
            ],
            connections=[],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)

        assert len(scene._zone_items) == 2, (
            f"Expected 2 zone items, got {len(scene._zone_items)}"
        )
        assert set(scene._zone_items.keys()) == {"1", "2"}
