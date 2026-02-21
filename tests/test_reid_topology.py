"""Tests for connectivity-preserving zone re-ID (DFS and BFS methods)."""

import math
from pathlib import Path

import pytest

from h3tc.editor.canvas.layout import (
    _build_adjacency,
    compute_zone_reids,
    image_settings_layout,
)
from h3tc.formats import detect_format

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
HOTA_COMPLETE = TEMPLATES_DIR / "hota_complete"

METHODS = ["dfs", "bfs"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_map(filename: str, map_name: str | None = None):
    """Load a template file and return (positions, connections, template_map)."""
    filepath = HOTA_COMPLETE / filename
    parser = detect_format(filepath)
    pack = parser.parse(filepath)
    for tmap in pack.maps:
        if map_name is None or tmap.name.strip() == map_name:
            positions = image_settings_layout(tmap)
            connections = [
                (c.zone1.strip(), c.zone2.strip()) for c in tmap.connections
            ]
            return positions, connections, tmap
    raise ValueError(f"Map {map_name!r} not found in {filename}")


# ---------------------------------------------------------------------------
# DFS-specific behavior
# ---------------------------------------------------------------------------


class TestDfsBehavior:
    """Test DFS-specific properties."""

    def test_root_is_top_left(self):
        """ID 1 should go to the top-left connected zone."""
        positions = {
            "bottom_left": (0, 200),
            "top_right": (200, 0),
            "top_left": (0, 0),
        }
        connections = [("top_left", "top_right"), ("top_left", "bottom_left")]
        reid = compute_zone_reids(positions, connections, method="dfs")
        assert reid["top_left"] == "1"

    def test_dfs_keeps_branch_contiguous(self):
        """DFS should fully explore each branch before backtracking."""
        # Trunk with two branches:
        #   root -- b1a -- b1b    (top branch, y=0)
        #     |
        #   b2a -- b2b            (bottom branch, y=100+)
        positions = {
            "root": (0, 0),
            "b1a": (100, 0), "b1b": (200, 0),
            "b2a": (0, 100), "b2b": (0, 200),
        }
        connections = [
            ("root", "b1a"), ("b1a", "b1b"),
            ("root", "b2a"), ("b2a", "b2b"),
        ]
        reid = compute_zone_reids(positions, connections, method="dfs")
        assert reid["root"] == "1"
        b1_ids = {int(reid["b1a"]), int(reid["b1b"])}
        b2_ids = {int(reid["b2a"]), int(reid["b2b"])}
        # Each branch should have contiguous IDs
        assert max(b1_ids) - min(b1_ids) == 1
        assert max(b2_ids) - min(b2_ids) == 1
        # Top branch (y=0) before bottom branch (y=100+)
        assert max(b1_ids) < min(b2_ids)


# ---------------------------------------------------------------------------
# BFS-specific behavior
# ---------------------------------------------------------------------------


class TestBfsBehavior:
    """Test BFS-specific properties."""

    def test_root_is_top_left(self):
        """ID 1 should go to the top-left connected zone."""
        positions = {
            "bottom_left": (0, 200),
            "top_right": (200, 0),
            "top_left": (0, 0),
        }
        connections = [("top_left", "top_right"), ("top_left", "bottom_left")]
        reid = compute_zone_reids(positions, connections, method="bfs")
        assert reid["top_left"] == "1"

    def test_bfs_level_by_level(self):
        """BFS should process all neighbors at distance 1 before distance 2."""
        #   a (top-left, root)
        #   |
        #   b -- c
        #   |
        #   d -- e
        positions = {
            "a": (0, 0),
            "b": (0, 100), "c": (100, 100),
            "d": (0, 200), "e": (100, 200),
        }
        connections = [
            ("a", "b"), ("b", "c"), ("b", "d"), ("d", "e"),
        ]
        reid = compute_zone_reids(positions, connections, method="bfs")
        # BFS: a=1, then b=2 (level 1), then c,d=3,4 (level 2), then e=5
        assert reid["a"] == "1"
        assert reid["b"] == "2"
        # c and d are both level 2 — should come before e (level 3)
        assert int(reid["c"]) < int(reid["e"])
        assert int(reid["d"]) < int(reid["e"])
        assert reid["e"] == "5"

    def test_bfs_horizontal_sweep(self):
        """On a wide map, BFS should sweep left-to-right across rows."""
        # Two rows connected vertically:
        #   a1 -- a2 -- a3   (top row, y=0)
        #   |     |     |
        #   b1 -- b2 -- b3   (bottom row, y=100)
        positions = {
            "a1": (0, 0), "a2": (100, 0), "a3": (200, 0),
            "b1": (0, 100), "b2": (100, 100), "b3": (200, 100),
        }
        connections = [
            ("a1", "a2"), ("a2", "a3"),
            ("b1", "b2"), ("b2", "b3"),
            ("a1", "b1"), ("a2", "b2"), ("a3", "b3"),
        ]
        reid = compute_zone_reids(positions, connections, method="bfs")
        # BFS from a1: level 0=[a1], level 1=[a2,b1] (sorted by y,x),
        # level 2=[a3,b2], level 3=[b3]
        assert reid["a1"] == "1"
        # a2 (y=0,x=100) should come before b1 (y=100,x=0) — lower y wins
        assert int(reid["a2"]) < int(reid["b1"])


# ---------------------------------------------------------------------------
# Shared behavior (both methods)
# ---------------------------------------------------------------------------


class TestSharedBehavior:
    """Properties that must hold for both DFS and BFS."""

    @pytest.mark.parametrize("method", METHODS)
    def test_follows_connections(self, method):
        """Traversal should follow connections — not jump to unconnected zones."""
        positions = {"a": (0, 0), "b": (100, 0), "c": (200, 0), "d": (300, 0)}
        connections = [("a", "b"), ("b", "c"), ("c", "d")]
        reid = compute_zone_reids(positions, connections, method=method)
        order = sorted(reid.keys(), key=lambda z: int(reid[z]))
        conn_set = {frozenset(c) for c in connections}
        for i in range(len(order) - 1):
            assert frozenset([order[i], order[i + 1]]) in conn_set

    @pytest.mark.parametrize("method", METHODS)
    def test_y_then_x_sort(self, method):
        """Neighbor sort key should be (y, x)."""
        positions = {"c": (200, 0), "a": (0, 0), "b": (100, 0)}
        connections = [("a", "b"), ("b", "c")]
        reid = compute_zone_reids(positions, connections, method=method)
        assert reid["a"] == "1"
        assert reid["b"] == "2"
        assert reid["c"] == "3"

    @pytest.mark.parametrize("method", METHODS)
    def test_disconnected_appended_last(self, method):
        positions = {"a": (0, 0), "b": (100, 0), "c": (50, 50)}
        connections = [("a", "b")]
        result = compute_zone_reids(positions, connections, method=method)
        assert int(result["c"]) == 3

    @pytest.mark.parametrize("method", METHODS)
    def test_multiple_components(self, method):
        """Each component explored fully before moving to next."""
        positions = {
            "a1": (0, 0), "a2": (100, 0),
            "b1": (0, 200), "b2": (100, 200),
        }
        connections = [("a1", "a2"), ("b1", "b2")]
        result = compute_zone_reids(positions, connections, method=method)
        assert int(result["a1"]) <= 2
        assert int(result["a2"]) <= 2
        assert int(result["b1"]) >= 3
        assert int(result["b2"]) >= 3


# ---------------------------------------------------------------------------
# Real template map tests
# ---------------------------------------------------------------------------


class TestRealMaps:
    """Verify re-ID on actual template maps with both methods."""

    @pytest.mark.parametrize("method", METHODS)
    def test_all_zones_get_sequential_ids(self, method):
        for filename in [
            "Spider.h3t", "Boomerang.h3t",
            "Clash of Dragons.h3t", "8xm12a.h3t",
        ]:
            positions, connections, _ = _load_map(filename)
            if positions is None:
                continue
            reid = compute_zone_reids(positions, connections, method=method)
            assert len(reid) == len(positions), (
                f"{filename}/{method}: {len(reid)} IDs for {len(positions)} zones"
            )
            new_ids = sorted(int(v) for v in reid.values())
            assert new_ids == list(range(1, len(positions) + 1)), (
                f"{filename}/{method}: IDs are not 1..N"
            )

    def test_dfs_consecutive_ids_are_connected(self):
        """DFS: most consecutive ID pairs should be connected (parent-child)."""
        for filename in [
            "Spider.h3t", "Boomerang.h3t",
            "Clash of Dragons.h3t", "8xm12a.h3t",
        ]:
            positions, connections, _ = _load_map(filename)
            if positions is None:
                continue
            reid = compute_zone_reids(positions, connections, method="dfs")
            conn_set = {frozenset(c) for c in connections}
            order = sorted(reid.keys(), key=lambda z: int(reid[z]))
            connected_pairs = sum(
                1
                for i in range(len(order) - 1)
                if frozenset([order[i], order[i + 1]]) in conn_set
            )
            ratio = connected_pairs / max(len(order) - 1, 1)
            assert ratio >= 0.5, (
                f"{filename}/dfs: only {ratio:.0%} consecutive pairs connected"
            )

    @pytest.mark.parametrize("method", METHODS)
    def test_id1_is_top_left(self, method):
        """Zone with ID 1 should be near the top of the layout."""
        for filename in [
            "Spider.h3t", "Boomerang.h3t",
            "Clash of Dragons.h3t", "8xm12a.h3t",
        ]:
            positions, connections, _ = _load_map(filename)
            if positions is None:
                continue
            reid = compute_zone_reids(positions, connections, method=method)
            root = next(z for z, nid in reid.items() if nid == "1")
            root_y = positions[root][1]
            median_y = sorted(p[1] for p in positions.values())[len(positions) // 2]
            assert root_y <= median_y, (
                f"{filename}/{method}: ID 1 zone y={root_y:.0f} > median={median_y:.0f}"
            )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    @pytest.mark.parametrize("method", METHODS)
    def test_empty(self, method):
        assert compute_zone_reids({}, [], method=method) == {}

    @pytest.mark.parametrize("method", METHODS)
    def test_single_zone(self, method):
        result = compute_zone_reids({"1": (0, 0)}, [], method=method)
        assert result == {"1": "1"}

    @pytest.mark.parametrize("method", METHODS)
    def test_all_disconnected(self, method):
        """Disconnected zones sorted by (y, x)."""
        positions = {"3": (200, 0), "1": (0, 100), "2": (100, 0)}
        result = compute_zone_reids(positions, [], method=method)
        # (y,x): 2=(100,0)→y=0, 3=(200,0)→y=0, 1=(0,100)→y=100
        assert result["2"] == "1"
        assert result["3"] == "2"
        assert result["1"] == "3"

    def test_default_method_is_dfs(self):
        """Calling without method= should use DFS."""
        positions = {"a": (0, 0), "b": (100, 0)}
        connections = [("a", "b")]
        default = compute_zone_reids(positions, connections)
        explicit = compute_zone_reids(positions, connections, method="dfs")
        assert default == explicit
