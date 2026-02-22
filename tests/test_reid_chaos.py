"""Chaos/edge-case tests for Re-ID (DFS/BFS) and save validation."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from h3tc.editor.canvas.layout import _build_adjacency, compute_zone_reids
from h3tc.editor.canvas.scene import TemplateScene
from h3tc.enums import MONSTER_FACTIONS_SOD, TERRAINS_SOD
from h3tc.models import Connection, TemplatePack, TemplateMap, Zone, ZoneOptions

METHODS = ["dfs", "bfs"]

# Ensure a QApplication exists for QGraphicsScene
_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_map(
    zone_ids: list[str],
    connections: list[tuple[str, str]],
    positions: dict[str, tuple[float, float]] | None = None,
) -> TemplateMap:
    """Build a TemplateMap with zones at given positions (via image_settings)."""
    if positions is None:
        # Auto-assign horizontal positions
        positions = {zid: (i * 100, 0) for i, zid in enumerate(zone_ids)}
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
    positions: dict[str, tuple[float, float]] | None = None,
    method: str = "dfs",
) -> tuple[TemplateScene, TemplateMap, dict[str, str] | None]:
    """Create a scene, load a map, run re-ID, and return results."""
    tmap = _make_map(zone_ids, connections, positions)
    scene = TemplateScene()
    scene.load_map(tmap)
    mapping = scene.reid_zones(method=method)
    return scene, tmap, mapping


def _validate_and_fix_map(tm: TemplateMap) -> list[str]:
    """Pure-logic replica of MainWindow._validate_and_fix for a single map.

    Validates zone IDs are sequential 1..N, terrains/monsters have at least
    one enabled, and auto-fixes any issues found.
    """
    fixes = []

    # Check zone IDs are sequential 1..N
    expected = [str(i + 1) for i in range(len(tm.zones))]
    actual = [z.id.strip() for z in tm.zones]
    if actual != expected:
        id_map: dict[str, str] = {}
        changes = []
        for zone, new_id in zip(tm.zones, expected):
            old_id = zone.id.strip()
            if old_id != new_id:
                id_map[old_id] = new_id
                changes.append(f"{old_id or '(empty)'} → {new_id}")
                zone.id = new_id
        if id_map:
            for conn in tm.connections:
                z1 = conn.zone1.strip()
                z2 = conn.zone2.strip()
                if z1 in id_map:
                    conn.zone1 = id_map[z1]
                if z2 in id_map:
                    conn.zone2 = id_map[z2]
        if changes:
            fixes.append(
                f"Map '{tm.name}': re-numbered zone IDs: "
                + ", ".join(changes)
            )

    for zone in tm.zones:
        zid = zone.id.strip()

        has_terrain = any(
            zone.terrains.get(t, "").strip().lower() == "x"
            for t in TERRAINS_SOD
        )
        if not has_terrain and zone.terrain_match.strip().lower() != "x":
            zone.terrains["Dirt"] = "x"
            fixes.append(f"Zone {zid}: no terrain enabled, added Dirt")

        has_monster = any(
            zone.monster_factions.get(f, "").strip().lower() == "x"
            for f in MONSTER_FACTIONS_SOD
        )
        if not has_monster and zone.monster_match.strip().lower() != "x":
            zone.monster_factions["Neutral"] = "x"
            fixes.append(f"Zone {zid}: no monster faction enabled, added Neutral")

    return fixes


def _assert_sequential(tmap: TemplateMap):
    """Assert zone IDs are sequential 1..N and list is sorted."""
    ids = [z.id.strip() for z in tmap.zones]
    expected = [str(i + 1) for i in range(len(ids))]
    assert ids == expected, f"Expected {expected}, got {ids}"


# ---------------------------------------------------------------------------
# 1. Self-Loops
# ---------------------------------------------------------------------------


class TestSelfLoops:
    """Self-loop edges (zone connected to itself) should not break anything."""

    def test_adjacency_self_loop_present(self):
        """_build_adjacency includes self-loop in neighbor set (valid edge)."""
        adj = _build_adjacency(["1", "2"], [("1", "1"), ("1", "2")])
        assert "1" in adj["1"], "Self-loop should appear in neighbors"
        assert "2" in adj["1"]

    def test_adjacency_only_self_loop(self):
        """Zone with only a self-loop appears in own neighbor set."""
        adj = _build_adjacency(["1"], [("1", "1")])
        assert adj["1"] == {"1"}

    @pytest.mark.parametrize("method", METHODS)
    def test_compute_reids_with_self_loop(self, method):
        """compute_zone_reids doesn't crash on self-loops."""
        positions = {"1": (0, 0), "2": (100, 0)}
        connections = [("1", "1"), ("1", "2")]
        result = compute_zone_reids(positions, connections, method=method)
        assert set(result.values()) == {"1", "2"}

    @pytest.mark.parametrize("method", METHODS)
    def test_scene_reid_with_self_loop(self, method):
        """Scene re-ID with a self-loop produces correct sequential IDs."""
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["1", "2"],
            connections=[("1", "1"), ("1", "2")],
            method=method,
        )
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 2. Broken Connections
# ---------------------------------------------------------------------------


class TestBrokenConnections:
    """Connections referencing non-existent zones should be handled safely."""

    def test_adjacency_drops_nonexistent(self):
        """_build_adjacency ignores edges where one endpoint doesn't exist."""
        adj = _build_adjacency(["1", "2"], [("1", "99"), ("1", "2")])
        assert "99" not in adj["1"]
        assert "2" in adj["1"]

    def test_adjacency_both_endpoints_missing(self):
        """Both endpoints missing — no crash, no entries."""
        adj = _build_adjacency(["1"], [("88", "99")])
        assert len(adj) == 0

    @pytest.mark.parametrize("method", METHODS)
    def test_compute_reids_broken_conn(self, method):
        """compute_zone_reids handles connections to non-existent zones."""
        positions = {"1": (0, 0), "2": (100, 0)}
        connections = [("1", "99"), ("1", "2")]
        result = compute_zone_reids(positions, connections, method=method)
        assert set(result.values()) == {"1", "2"}

    @pytest.mark.parametrize("method", METHODS)
    def test_scene_reid_orphan_connection(self, method):
        """Scene re-ID with orphan connection doesn't crash."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="1", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="2", zone_options=ZoneOptions(image_settings="100 0")),
            ],
            connections=[
                Connection(zone1="1", zone2="2", value="5000"),
                Connection(zone1="1", zone2="99", value="5000"),
            ],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        mapping = scene.reid_zones(method=method)
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 3. Empty String Zone IDs
# ---------------------------------------------------------------------------


class TestEmptyStringZoneIds:
    """Zones with empty or whitespace-only IDs."""

    @pytest.mark.parametrize("method", METHODS)
    def test_empty_id_gets_assigned(self, method):
        """Zone with id='' gets a proper sequential ID after re-ID."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="2", zone_options=ZoneOptions(image_settings="100 0")),
            ],
            connections=[],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)
        _assert_sequential(tmap)

    @pytest.mark.parametrize("method", METHODS)
    def test_whitespace_ids_treated_as_duplicates(self, method):
        """Whitespace-only IDs are handled like empty/duplicate IDs."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id=" ", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="  ", zone_options=ZoneOptions(image_settings="100 0")),
                Zone(id="3", zone_options=ZoneOptions(image_settings="200 0")),
            ],
            connections=[],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 4. Partial Connectivity
# ---------------------------------------------------------------------------


class TestPartialConnectivity:
    """Maps with disconnected clusters and islands."""

    @pytest.mark.parametrize("method", METHODS)
    def test_connected_cluster_plus_islands(self, method):
        """Connected cluster gets lower IDs, islands appended."""
        # Use non-sequential IDs to ensure re-ID actually runs
        positions = {
            "10": (0, 0), "20": (100, 0), "30": (200, 0),  # connected
            "40": (300, 100), "50": (400, 100),  # islands
        }
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["10", "20", "30", "40", "50"],
            connections=[("10", "20"), ("20", "30")],
            positions=positions,
            method=method,
        )
        _assert_sequential(tmap)
        assert mapping is not None
        # Islands should have higher IDs than connected cluster
        connected_new = {mapping[z] for z in ["10", "20", "30"]}
        island_new = {mapping[z] for z in ["40", "50"]}
        assert max(int(x) for x in connected_new) < min(int(x) for x in island_new)

    @pytest.mark.parametrize("method", METHODS)
    def test_two_separate_clusters(self, method):
        """Two separate clusters — each explored fully before next."""
        positions = {
            "A": (0, 0), "B": (100, 0),    # cluster 1
            "C": (0, 200), "D": (100, 200),  # cluster 2
        }
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["A", "B", "C", "D"],
            connections=[("A", "B"), ("C", "D")],
            positions=positions,
            method=method,
        )
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 5. Cyclic Connections
# ---------------------------------------------------------------------------


class TestCyclicConnections:
    """Cycles in connections should not cause infinite loops."""

    @pytest.mark.parametrize("method", METHODS)
    def test_triangle_cycle(self, method):
        """Triangle A-B-C-A completes without infinite loop."""
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["1", "2", "3"],
            connections=[("1", "2"), ("2", "3"), ("3", "1")],
            method=method,
        )
        _assert_sequential(tmap)

    @pytest.mark.parametrize("method", METHODS)
    def test_five_zone_ring(self, method):
        """5-zone ring traversal completes correctly."""
        ids = ["1", "2", "3", "4", "5"]
        conns = [("1", "2"), ("2", "3"), ("3", "4"), ("4", "5"), ("5", "1")]
        positions = {
            "1": (100, 0), "2": (200, 50), "3": (175, 150),
            "4": (25, 150), "5": (0, 50),
        }
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=ids, connections=conns, positions=positions, method=method,
        )
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 6. Duplicate Connections
# ---------------------------------------------------------------------------


class TestDuplicateConnections:
    """Same pair connected multiple times should be idempotent."""

    @pytest.mark.parametrize("method", METHODS)
    def test_same_pair_twice(self, method):
        """Duplicate connection (1,2)+(1,2) doesn't break re-ID."""
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["1", "2", "3"],
            connections=[("1", "2"), ("1", "2"), ("2", "3")],
            method=method,
        )
        _assert_sequential(tmap)

    @pytest.mark.parametrize("method", METHODS)
    def test_reverse_duplicate(self, method):
        """Reverse duplicate (1,2)+(2,1) doesn't break re-ID."""
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["1", "2", "3"],
            connections=[("1", "2"), ("2", "1"), ("2", "3")],
            method=method,
        )
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 7. Validate and Fix
# ---------------------------------------------------------------------------


class TestValidateAndFix:
    """Test the save validation logic (replicated from MainWindow._validate_and_fix)."""

    def test_sequential_no_fix(self):
        """Already sequential IDs with terrain/monsters → no fixes."""
        tmap = _make_map(["1", "2", "3"], [("1", "2"), ("2", "3")])
        for z in tmap.zones:
            z.terrains["Dirt"] = "x"
            z.monster_factions["Neutral"] = "x"
        fixes = _validate_and_fix_map(tmap)
        assert fixes == []

    def test_non_sequential_renumbered(self):
        """Non-sequential IDs get renumbered."""
        tmap = _make_map(["5", "3", "1"], [("5", "3"), ("3", "1")])
        fixes = _validate_and_fix_map(tmap)
        assert any("re-numbered" in f for f in fixes)
        _assert_sequential(tmap)

    def test_gap_in_ids_renumbered(self):
        """Gap in IDs (1, 3, 5) gets renumbered to (1, 2, 3)."""
        tmap = _make_map(["1", "3", "5"], [("1", "3"), ("3", "5")])
        fixes = _validate_and_fix_map(tmap)
        assert any("re-numbered" in f for f in fixes)
        _assert_sequential(tmap)

    def test_empty_id_renumbered(self):
        """Empty ID gets renumbered and fix message says '(empty)'."""
        tmap = _make_map(["", "2"], [])
        fixes = _validate_and_fix_map(tmap)
        assert any("(empty)" in f for f in fixes)
        _assert_sequential(tmap)

    def test_connections_updated_after_renumber(self):
        """Connection references updated after renumbering."""
        tmap = _make_map(["10", "20"], [("10", "20")])
        _validate_and_fix_map(tmap)
        assert tmap.connections[0].zone1 == "1"
        assert tmap.connections[0].zone2 == "2"

    def test_missing_terrain_adds_dirt(self):
        """Zone with no terrain enabled gets Dirt."""
        tmap = _make_map(["1"], [])
        # Ensure no terrains set
        tmap.zones[0].terrains = {}
        tmap.zones[0].terrain_match = ""
        fixes = _validate_and_fix_map(tmap)
        assert any("Dirt" in f for f in fixes)
        assert tmap.zones[0].terrains.get("Dirt") == "x"

    def test_terrain_match_x_no_fix(self):
        """terrain_match='x' counts as having terrain — no fix needed."""
        tmap = _make_map(["1"], [])
        tmap.zones[0].terrains = {}
        tmap.zones[0].terrain_match = "x"
        fixes = _validate_and_fix_map(tmap)
        assert not any("terrain" in f.lower() for f in fixes)

    def test_terrain_already_set_no_fix(self):
        """Zone with terrain already set → no terrain fix."""
        tmap = _make_map(["1"], [])
        tmap.zones[0].terrains = {"Grass": "x"}
        fixes = _validate_and_fix_map(tmap)
        assert not any("terrain" in f.lower() for f in fixes)

    def test_missing_monster_adds_neutral(self):
        """Zone with no monster faction gets Neutral."""
        tmap = _make_map(["1"], [])
        tmap.zones[0].monster_factions = {}
        tmap.zones[0].monster_match = ""
        fixes = _validate_and_fix_map(tmap)
        assert any("Neutral" in f for f in fixes)
        assert tmap.zones[0].monster_factions.get("Neutral") == "x"

    def test_monster_match_x_no_fix(self):
        """monster_match='x' counts as having monsters — no fix."""
        tmap = _make_map(["1"], [])
        tmap.zones[0].monster_factions = {}
        tmap.zones[0].monster_match = "x"
        fixes = _validate_and_fix_map(tmap)
        assert not any("monster" in f.lower() for f in fixes)

    def test_multiple_fixes_combined(self):
        """Non-sequential IDs + missing terrain + missing monsters → all fixed."""
        tmap = _make_map(["5", "3"], [("5", "3")])
        tmap.zones[0].terrains = {}
        tmap.zones[0].terrain_match = ""
        tmap.zones[0].monster_factions = {}
        tmap.zones[0].monster_match = ""
        tmap.zones[1].terrains = {}
        tmap.zones[1].terrain_match = ""
        tmap.zones[1].monster_factions = {}
        tmap.zones[1].monster_match = ""
        fixes = _validate_and_fix_map(tmap)
        assert any("re-numbered" in f for f in fixes)
        assert any("Dirt" in f for f in fixes)
        assert any("Neutral" in f for f in fixes)
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 8. Large Scale
# ---------------------------------------------------------------------------


class TestLargeScale:
    """Stress tests with many zones."""

    @pytest.mark.parametrize("method", METHODS)
    def test_50_zones_linear_chain(self, method):
        """50 zones in a linear chain → all sequential."""
        n = 50
        ids = [str(i + 1) for i in range(n)]
        conns = [(str(i + 1), str(i + 2)) for i in range(n - 1)]
        positions = {str(i + 1): (i * 100, 0) for i in range(n)}
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=ids, connections=conns, positions=positions, method=method,
        )
        _assert_sequential(tmap)

    @pytest.mark.parametrize("method", METHODS)
    def test_50_zones_star_topology(self, method):
        """50 zones in a star (hub + 49 spokes) → all sequential."""
        import math
        n = 50
        ids = [str(i + 1) for i in range(n)]
        # Zone 1 is center, 2..50 connected to 1
        conns = [("1", str(i + 2)) for i in range(n - 1)]
        positions = {"1": (500, 500)}
        for i in range(1, n):
            angle = 2 * math.pi * i / (n - 1)
            positions[str(i + 1)] = (500 + 400 * math.cos(angle),
                                      500 + 400 * math.sin(angle))
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=ids, connections=conns, positions=positions, method=method,
        )
        _assert_sequential(tmap)


# ---------------------------------------------------------------------------
# 9. Non-Sequential Starting IDs
# ---------------------------------------------------------------------------


class TestNonSequentialStartingIds:
    """Zones with sparse or oddly formatted IDs."""

    @pytest.mark.parametrize("method", METHODS)
    def test_sparse_ids(self, method):
        """Sparse IDs [10, 20, 30] → renumbered to [1, 2, 3]."""
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["10", "20", "30"],
            connections=[("10", "20"), ("20", "30")],
            method=method,
        )
        _assert_sequential(tmap)

    @pytest.mark.parametrize("method", METHODS)
    def test_leading_zeros(self, method):
        """Leading zeros ['01', '02', '03'] → renumbered without zeros."""
        scene, tmap, mapping = _reid_via_scene(
            zone_ids=["01", "02", "03"],
            connections=[("01", "02"), ("02", "03")],
            method=method,
        )
        _assert_sequential(tmap)
        # Verify no leading zeros remain
        for z in tmap.zones:
            assert z.id.strip() == str(int(z.id.strip()))


# ---------------------------------------------------------------------------
# 10. Idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Re-ID should be idempotent — second call is a no-op."""

    @pytest.mark.parametrize("method", METHODS)
    def test_second_reid_returns_none(self, method):
        """Re-ID twice: second call returns None (no changes)."""
        scene, tmap, mapping1 = _reid_via_scene(
            zone_ids=["3", "1", "2"],
            connections=[("1", "2"), ("2", "3")],
            method=method,
        )
        assert mapping1 is not None
        mapping2 = scene.reid_zones(method=method)
        assert mapping2 is None, "Second re-ID should return None (no changes)"

    @pytest.mark.parametrize("method", METHODS)
    def test_reid_then_validate_no_fixes(self, method):
        """After re-ID, validate_and_fix finds no renumbering to do."""
        scene, tmap, _ = _reid_via_scene(
            zone_ids=["5", "3", "1"],
            connections=[("1", "3"), ("3", "5")],
            method=method,
        )
        # Add terrain/monster so validate doesn't flag those
        for zone in tmap.zones:
            zone.terrains["Dirt"] = "x"
            zone.monster_factions["Neutral"] = "x"
        fixes = _validate_and_fix_map(tmap)
        assert fixes == [], f"Expected no fixes after re-ID, got {fixes}"


# ---------------------------------------------------------------------------
# 11. Chaos Combo
# ---------------------------------------------------------------------------


class TestChaosCombo:
    """Combined chaos scenarios testing multiple edge cases at once."""

    @pytest.mark.parametrize("method", METHODS)
    def test_8_zones_full_chaos(self, method):
        """8 zones: duplicates + empty ID + self-loop + broken conn + non-sequential."""
        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=[
                Zone(id="5", zone_options=ZoneOptions(image_settings="0 0")),
                Zone(id="5", zone_options=ZoneOptions(image_settings="100 0")),
                Zone(id="", zone_options=ZoneOptions(image_settings="200 0")),
                Zone(id="10", zone_options=ZoneOptions(image_settings="300 0")),
                Zone(id="10", zone_options=ZoneOptions(image_settings="400 0")),
                Zone(id="3", zone_options=ZoneOptions(image_settings="500 0")),
                Zone(id="7", zone_options=ZoneOptions(image_settings="600 0")),
                Zone(id="99", zone_options=ZoneOptions(image_settings="700 0")),
            ],
            connections=[
                Connection(zone1="5", zone2="5", value="5000"),    # self-loop
                Connection(zone1="5", zone2="10", value="5000"),   # dup to dup
                Connection(zone1="10", zone2="3", value="5000"),
                Connection(zone1="3", zone2="7", value="5000"),
                Connection(zone1="7", zone2="999", value="5000"),  # broken
            ],
        )
        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)
        _assert_sequential(tmap)
        assert len(tmap.zones) == 8

    @pytest.mark.parametrize("method", METHODS)
    def test_20_zones_mega_chaos(self, method):
        """20 zones: duplicates + islands + self-loops + broken conn → all clean."""
        zones = []
        # 3 duplicate pairs (IDs: 1,1, 2,2, 3,3) = 6 zones
        for dup_id in ["1", "2", "3"]:
            for j in range(2):
                x = (int(dup_id) - 1) * 200 + j * 100
                zones.append(Zone(
                    id=dup_id,
                    zone_options=ZoneOptions(image_settings=f"{x} 0"),
                ))
        # 5 islands (IDs: 50-54) = 5 zones
        for i in range(5):
            zones.append(Zone(
                id=str(50 + i),
                zone_options=ZoneOptions(image_settings=f"{600 + i * 100} 200"),
            ))
        # 9 connected zones (IDs: 10-18) = 9 zones
        for i in range(9):
            zones.append(Zone(
                id=str(10 + i),
                zone_options=ZoneOptions(image_settings=f"{i * 100} 400"),
            ))
        assert len(zones) == 20

        connections = [
            # Self-loops
            Connection(zone1="10", zone2="10", value="5000"),
            Connection(zone1="11", zone2="11", value="5000"),
            # Connected chain 10-11-12-...-18
            *[Connection(zone1=str(10 + i), zone2=str(11 + i), value="5000")
              for i in range(8)],
            # Broken connection
            Connection(zone1="10", zone2="999", value="5000"),
        ]

        tmap = TemplateMap(
            name="test", min_size="1", max_size="2",
            zones=zones, connections=connections,
        )

        # Clear terrain/monsters to also test validate
        for z in tmap.zones:
            z.terrains = {}
            z.terrain_match = ""
            z.monster_factions = {}
            z.monster_match = ""

        scene = TemplateScene()
        scene.load_map(tmap)
        scene.reid_zones(method=method)
        _assert_sequential(tmap)
        assert len(tmap.zones) == 20

        # Now validate — should add Dirt and Neutral to all zones
        fixes = _validate_and_fix_map(tmap)
        assert any("Dirt" in f for f in fixes)
        assert any("Neutral" in f for f in fixes)
        # After validation, IDs should still be sequential
        _assert_sequential(tmap)
