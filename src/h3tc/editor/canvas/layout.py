"""Layout algorithms for zone positioning."""

import math
import random

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
) -> dict[str, tuple[float, float]]:
    """Snap positions to a grid and resolve overlaps.

    Args:
        positions: Dict mapping zone ID -> (x, y) position.
        grid_size: Size of grid cells.

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
            # Find nearest empty adjacent cell (spiral search)
            placed = False
            for radius in range(1, 20):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if abs(dx) != radius and abs(dy) != radius:
                            continue
                        candidate = (pos[0] + dx * grid_size, pos[1] + dy * grid_size)
                        if candidate not in occupied:
                            snapped[zid] = candidate
                            occupied[candidate] = zid
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break

    # Shift so all positions are positive with margin
    if snapped:
        min_x = min(p[0] for p in snapped.values())
        min_y = min(p[1] for p in snapped.values())
        if min_x < 50 or min_y < 50:
            off_x = -min_x + grid_size if min_x < 50 else 0
            off_y = -min_y + grid_size if min_y < 50 else 0
            snapped = {zid: (x + off_x, y + off_y) for zid, (x, y) in snapped.items()}

    return snapped


def force_directed_layout(
    template_map: TemplateMap,
    width: float = 800.0,
    height: float = 600.0,
    iterations: int = 120,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Compute zone positions using Fruchterman-Reingold force-directed layout.

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
    return snap_to_grid(result)
