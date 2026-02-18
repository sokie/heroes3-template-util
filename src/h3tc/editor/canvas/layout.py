"""Force-directed layout for zone positioning (Fruchterman-Reingold)."""

import math
import random

from h3tc.models import TemplateMap


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

    return {zid: (pos[0], pos[1]) for zid, pos in positions.items()}
