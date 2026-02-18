"""JSON sidecar file for persisting zone visual positions."""

import json
from pathlib import Path

_SIDECAR_SUFFIX = ".h3tc-layout.json"
_VERSION = 1


def sidecar_path(template_path: Path) -> Path:
    """Get the sidecar file path for a template file."""
    return template_path.with_suffix(template_path.suffix + _SIDECAR_SUFFIX)


def load_layout(template_path: Path) -> dict[str, dict[str, tuple[float, float]]]:
    """Load zone positions from sidecar.

    Returns:
        Dict mapping map_name -> {zone_id: (x, y)}.
    """
    path = sidecar_path(template_path)
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    if data.get("version") != _VERSION:
        return {}

    result: dict[str, dict[str, tuple[float, float]]] = {}
    for map_name, map_data in data.get("maps", {}).items():
        zones = {}
        for zone_id, pos in map_data.get("zones", {}).items():
            if isinstance(pos, dict) and "x" in pos and "y" in pos:
                zones[zone_id] = (float(pos["x"]), float(pos["y"]))
        result[map_name] = zones
    return result


def save_layout(
    template_path: Path,
    layouts: dict[str, dict[str, tuple[float, float]]],
) -> None:
    """Save zone positions to sidecar.

    Args:
        template_path: Path to the .txt template file.
        layouts: Dict mapping map_name -> {zone_id: (x, y)}.
    """
    data = {"version": _VERSION, "maps": {}}
    for map_name, zones in layouts.items():
        data["maps"][map_name] = {
            "zones": {
                zid: {"x": round(x, 1), "y": round(y, 1)}
                for zid, (x, y) in zones.items()
            }
        }

    path = sidecar_path(template_path)
    path.write_text(json.dumps(data, indent=2) + "\n", "utf-8")
