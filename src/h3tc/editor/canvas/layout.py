"""Layout algorithms for zone positioning."""

import math
import random
from collections import defaultdict

from h3tc.models import TemplateMap


def _estimate_zone_width(zone) -> float:
    """Estimate zone box width from base_size (matches ZoneItem._zone_size logic)."""
    try:
        base = int(zone.base_size) if zone.base_size.strip() else 5
    except ValueError:
        base = 5
    scale = math.sqrt(max(base, 1)) * 11.0  # ZONE_SIZE_SCALE
    content_w = 3 * 54 + 20  # _COLS * _CELL_W + _MARGIN * 2
    return max(content_w, scale * 3, 100)


def _build_adjacency(
    zone_ids: list[str],
    edges: list[tuple[str, str]],
) -> dict[str, set[str]]:
    """Build adjacency map from edges."""
    adj: dict[str, set[str]] = defaultdict(set)
    id_set = set(zone_ids)
    for z1, z2 in edges:
        if z1 in id_set and z2 in id_set:
            adj[z1].add(z2)
            adj[z2].add(z1)
    return adj


def _push_leaves_to_edges(
    positions: dict[str, tuple[float, float]],
    zones: list,
    adj: dict[str, set[str]],
    grid_size: float,
) -> dict[str, tuple[float, float]]:
    """Push degree-1 player zones to outer edges of the layout.

    Leaf zones (degree=1) with human_start are placed one grid cell further
    outward from their single neighbor, using the leaf's force-directed
    position to determine direction (not the layout center, which fails
    for star topologies where all leaves share one hub).
    """
    if not positions:
        return positions

    result = dict(positions)
    zone_map = {z.id.strip(): z for z in zones}

    for zid, neighbors in adj.items():
        if len(neighbors) != 1:
            continue
        zone = zone_map.get(zid)
        if not zone:
            continue
        # Only push player start zones
        if not (hasattr(zone, "human_start") and zone.human_start.strip().lower() == "x"):
            continue

        neighbor_id = next(iter(neighbors))
        if neighbor_id not in positions:
            continue

        nx, ny = positions[neighbor_id]
        lx, ly = positions[zid]
        # Direction from hub to leaf's original force-directed position
        dx = lx - nx
        dy = ly - ny
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.01:
            dx, dy = 1.0, 0.0
        else:
            dx /= dist
            dy /= dist

        # Place leaf one grid cell beyond neighbor in that direction
        result[zid] = (nx + dx * grid_size, ny + dy * grid_size)

    return result


def _align_rows_cols(
    positions: dict[str, tuple[float, float]],
    grid_size: float,
    threshold_ratio: float = 0.4,
) -> dict[str, tuple[float, float]]:
    """Align zones that are almost on the same row or column.

    Groups zones whose y-coordinates are within threshold_ratio * grid_size
    and snaps them to the same y. Same for x-coordinates.
    """
    if not positions:
        return positions

    threshold = threshold_ratio * grid_size
    result = dict(positions)
    zone_ids = list(result.keys())

    # Align rows (y-coordinates)
    sorted_by_y = sorted(zone_ids, key=lambda z: result[z][1])
    i = 0
    while i < len(sorted_by_y):
        group = [sorted_by_y[i]]
        j = i + 1
        while j < len(sorted_by_y):
            if abs(result[sorted_by_y[j]][1] - result[group[0]][1]) <= threshold:
                group.append(sorted_by_y[j])
                j += 1
            else:
                break
        if len(group) > 1:
            avg_y = sum(result[z][1] for z in group) / len(group)
            # Snap to nearest grid line
            snapped_y = round(avg_y / grid_size) * grid_size
            for z in group:
                result[z] = (result[z][0], snapped_y)
        i = j

    # Align columns (x-coordinates)
    sorted_by_x = sorted(zone_ids, key=lambda z: result[z][0])
    i = 0
    while i < len(sorted_by_x):
        group = [sorted_by_x[i]]
        j = i + 1
        while j < len(sorted_by_x):
            if abs(result[sorted_by_x[j]][0] - result[group[0]][0]) <= threshold:
                group.append(sorted_by_x[j])
                j += 1
            else:
                break
        if len(group) > 1:
            avg_x = sum(result[z][0] for z in group) / len(group)
            snapped_x = round(avg_x / grid_size) * grid_size
            for z in group:
                result[z] = (snapped_x, result[z][1])
        i = j

    return result


def image_settings_layout(
    template_map: TemplateMap,
    gap: float = 30.0,
) -> dict[str, tuple[float, float]] | None:
    """Extract zone positions from HOTA image_settings coordinates.

    Computes scale dynamically so zone boxes don't overlap.

    Args:
        template_map: The template map containing zones.
        gap: Minimum pixel gap between zone edges.

    Returns:
        Dict mapping zone ID -> (x, y) position, or None if too few zones
        have valid image_settings.
    """
    zones = template_map.zones
    if not zones:
        return None

    # Parse raw positions and estimate widths
    raw: dict[str, tuple[float, float]] = {}
    widths: dict[str, float] = {}
    zone_by_id: dict[str, object] = {}
    for zone in zones:
        zid = zone.id.strip()
        img = zone.zone_options.image_settings
        if not img or not img.strip():
            continue
        parts = img.strip().split()
        try:
            values = [float(v) for v in parts]
        except ValueError:
            continue
        if len(values) < 2:
            continue
        # First two values are the zone's own position.
        # 4-value entries add a mirror position (x2, y2) which we ignore.
        raw[zid] = (values[0], values[1])
        widths[zid] = _estimate_zone_width(zone)
        zone_by_id[zid] = zone

    # Require at least half the zones to have valid coordinates
    if len(raw) < len(zones) / 2:
        return None

    # Compute scale: ensure no pair of zones overlaps
    # For each pair: scale * dist >= (w1 + w2) / 2 + gap
    zone_ids = list(raw.keys())
    min_scale = 1.0
    for i, z1 in enumerate(zone_ids):
        x1, y1 = raw[z1]
        for j in range(i + 1, len(zone_ids)):
            z2 = zone_ids[j]
            x2, y2 = raw[z2]
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if dist < 0.1:
                continue
            needed = (widths[z1] + widths[z2]) / 2 + gap
            required_scale = needed / dist
            if required_scale > min_scale:
                min_scale = required_scale

    # Apply scale and shift to positive coordinates
    positions: dict[str, tuple[float, float]] = {}
    for zid, (x, y) in raw.items():
        positions[zid] = (x * min_scale, y * min_scale)

    if positions:
        min_x = min(p[0] for p in positions.values())
        min_y = min(p[1] for p in positions.values())
        margin = 100.0
        off_x = -min_x + margin
        off_y = -min_y + margin
        positions = {zid: (x + off_x, y + off_y) for zid, (x, y) in positions.items()}

    return positions


def snap_to_grid(
    positions: dict[str, tuple[float, float]],
    grid_size: float = 150.0,
    adj: dict[str, set[str]] | None = None,
) -> dict[str, tuple[float, float]]:
    """Snap positions to a grid and resolve overlaps.

    Args:
        positions: Dict mapping zone ID -> (x, y) position.
        grid_size: Size of grid cells.
        adj: Optional adjacency map for connection-aware collision resolution.

    Returns:
        Dict mapping zone ID -> snapped (x, y) position.
    """
    if not positions:
        return {}

    # Snap each position to nearest grid point
    snapped: dict[str, tuple[float, float]] = {}
    for zid, (x, y) in positions.items():
        gx = round(x / grid_size) * grid_size
        gy = round(y / grid_size) * grid_size
        snapped[zid] = (gx, gy)

    # Resolve overlaps: if multiple zones map to the same cell, nudge extras
    occupied: dict[tuple[float, float], str] = {}
    for zid, pos in snapped.items():
        if pos not in occupied:
            occupied[pos] = zid
        else:
            # Find best empty cell, preferring proximity to neighbors
            _resolve_collision(zid, pos, snapped, occupied, grid_size, adj)

    # Shift so all positions are positive with margin
    if snapped:
        min_x = min(p[0] for p in snapped.values())
        min_y = min(p[1] for p in snapped.values())
        if min_x < 50 or min_y < 50:
            off_x = -min_x + grid_size if min_x < 50 else 0
            off_y = -min_y + grid_size if min_y < 50 else 0
            snapped = {zid: (x + off_x, y + off_y) for zid, (x, y) in snapped.items()}

    return snapped


def _resolve_collision(
    zid: str,
    original_pos: tuple[float, float],
    snapped: dict[str, tuple[float, float]],
    occupied: dict[tuple[float, float], str],
    grid_size: float,
    adj: dict[str, set[str]] | None,
) -> None:
    """Resolve a grid collision by finding the best nearby empty cell.

    When adjacency info is available, prefers cells closer to the zone's
    neighbors' centroid. Otherwise falls back to spiral search.
    """
    # Compute neighbor centroid if adjacency is available
    neighbor_centroid = None
    if adj and zid in adj:
        neighbors_with_pos = [
            snapped[n] for n in adj[zid] if n in snapped and n != zid
        ]
        if neighbors_with_pos:
            neighbor_centroid = (
                sum(p[0] for p in neighbors_with_pos) / len(neighbors_with_pos),
                sum(p[1] for p in neighbors_with_pos) / len(neighbors_with_pos),
            )

    if neighbor_centroid:
        # Score candidates by distance to neighbor centroid
        best_pos = None
        best_score = float("inf")
        for radius in range(1, 20):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    candidate = (
                        original_pos[0] + dx * grid_size,
                        original_pos[1] + dy * grid_size,
                    )
                    if candidate in occupied:
                        continue
                    dist_to_centroid = math.sqrt(
                        (candidate[0] - neighbor_centroid[0]) ** 2
                        + (candidate[1] - neighbor_centroid[1]) ** 2
                    )
                    if dist_to_centroid < best_score:
                        best_score = dist_to_centroid
                        best_pos = candidate
            # If we found something at this radius, no need to go further
            if best_pos is not None:
                break
        if best_pos is not None:
            snapped[zid] = best_pos
            occupied[best_pos] = zid
    else:
        # Fallback: simple spiral search
        for radius in range(1, 20):
            placed = False
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    candidate = (
                        original_pos[0] + dx * grid_size,
                        original_pos[1] + dy * grid_size,
                    )
                    if candidate not in occupied:
                        snapped[zid] = candidate
                        occupied[candidate] = zid
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break


def force_directed_layout(
    template_map: TemplateMap,
    width: float = 800.0,
    height: float = 600.0,
    iterations: int = 120,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Compute zone positions using Fruchterman-Reingold force-directed layout.

    Post-processing pipeline:
    1. Force-directed placement (Fruchterman-Reingold)
    2. Push degree-1 player zones to edges
    3. Snap to dynamic grid with connection-aware collision resolution
    4. Align near-matching rows and columns

    Args:
        template_map: The template map containing zones and connections.
        width: Base canvas width for layout.
        height: Base canvas height for layout.
        iterations: Number of iterations for convergence.
        seed: Random seed for reproducible layout.

    Returns:
        Dict mapping zone ID -> (x, y) position.
    """
    zones = template_map.zones
    if not zones:
        return {}

    rng = random.Random(seed)

    # Build adjacency
    zone_ids = [z.id.strip() for z in zones]
    id_set = set(zone_ids)
    edges: list[tuple[str, str]] = []
    for conn in template_map.connections:
        z1 = conn.zone1.strip()
        z2 = conn.zone2.strip()
        if z1 in id_set and z2 in id_set:
            edges.append((z1, z2))

    adj = _build_adjacency(zone_ids, edges)

    n = len(zone_ids)
    if n == 1:
        return {zone_ids[0]: (width / 2, height / 2)}

    # Scale canvas area with zone count so large maps get more space
    scale_factor = max(1.0, math.sqrt(n / 5))
    w = width * scale_factor
    h = height * scale_factor

    # Zone sizes for repulsion scaling
    zone_sizes: dict[str, float] = {}
    for z in zones:
        try:
            bs = int(z.base_size) if z.base_size.strip() else 5
        except ValueError:
            bs = 5
        zone_sizes[z.id.strip()] = math.sqrt(max(bs, 1)) * 10

    # Initial random positions
    positions: dict[str, list[float]] = {}
    for zid in zone_ids:
        positions[zid] = [
            rng.uniform(w * 0.15, w * 0.85),
            rng.uniform(h * 0.15, h * 0.85),
        ]

    area = w * h
    k = math.sqrt(area / n) * 1.0  # Optimal distance

    for iteration in range(iterations):
        temp = max(0.01, (1.0 - iteration / iterations) * w * 0.1)

        # Repulsive forces between all pairs
        disp: dict[str, list[float]] = {zid: [0.0, 0.0] for zid in zone_ids}

        for i, z1 in enumerate(zone_ids):
            for j in range(i + 1, n):
                z2 = zone_ids[j]
                dx = positions[z1][0] - positions[z2][0]
                dy = positions[z1][1] - positions[z2][1]
                dist = max(math.sqrt(dx * dx + dy * dy), 0.01)

                # Scale repulsion by zone sizes
                size_factor = (zone_sizes.get(z1, 40) + zone_sizes.get(z2, 40)) / 60
                repulsion = (k * k * size_factor) / dist

                fx = (dx / dist) * repulsion
                fy = (dy / dist) * repulsion
                disp[z1][0] += fx
                disp[z1][1] += fy
                disp[z2][0] -= fx
                disp[z2][1] -= fy

        # Attractive forces along edges
        for z1, z2 in edges:
            dx = positions[z1][0] - positions[z2][0]
            dy = positions[z1][1] - positions[z2][1]
            dist = max(math.sqrt(dx * dx + dy * dy), 0.01)
            attraction = (dist * dist) / k

            fx = (dx / dist) * attraction
            fy = (dy / dist) * attraction
            disp[z1][0] -= fx
            disp[z1][1] -= fy
            disp[z2][0] += fx
            disp[z2][1] += fy

        # Apply displacements with temperature limiting
        for zid in zone_ids:
            dx, dy = disp[zid]
            dist = max(math.sqrt(dx * dx + dy * dy), 0.01)
            scale = min(dist, temp) / dist
            positions[zid][0] += dx * scale
            positions[zid][1] += dy * scale

            # Keep within bounds
            margin = 80
            positions[zid][0] = max(margin, min(w - margin, positions[zid][0]))
            positions[zid][1] = max(margin, min(h - margin, positions[zid][1]))

    result = {zid: (pos[0], pos[1]) for zid, pos in positions.items()}

    # Dynamic grid size based on largest zone width
    max_width = max((_estimate_zone_width(z) for z in zones), default=150)
    gap = 30.0
    grid_size = max_width + gap

    # Post-processing pipeline
    result = _push_leaves_to_edges(result, zones, adj, grid_size)
    result = snap_to_grid(result, grid_size=grid_size, adj=adj)
    result = _align_rows_cols(result, grid_size)

    return result
