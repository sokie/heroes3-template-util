"""JSON persistence for editor themes (all 3 presets + active selection)."""

import dataclasses
import json
from pathlib import Path

from h3tc.editor.constants import Theme

_THEME_DIR = Path.home() / ".h3tc"
_THEME_FILE = _THEME_DIR / "theme.json"
_VERSION = 2


def _serialize_theme(theme: Theme) -> dict:
    """Convert a Theme dataclass to a JSON-safe dict."""
    data: dict = {}
    for f in dataclasses.fields(theme):
        val = getattr(theme, f.name)
        if isinstance(val, tuple):
            val = list(val)
        elif isinstance(val, dict):
            val = {k: list(v) if isinstance(v, tuple) else v for k, v in val.items()}
        data[f.name] = val
    return data


def _deserialize_theme(theme_data: dict) -> Theme:
    """Convert a dict back into a Theme, fixing list→tuple conversions."""
    field_types = {f.name: f.type for f in dataclasses.fields(Theme)}
    cleaned: dict = {}
    for key, val in theme_data.items():
        if key not in field_types:
            continue
        if isinstance(val, list):
            val = tuple(val)
        elif isinstance(val, dict) and key == "zone_player_colors":
            val = {k: tuple(v) if isinstance(v, list) else v for k, v in val.items()}
        cleaned[key] = val
    return Theme(**cleaned)


def save_themes(themes: dict[str, Theme], active: str) -> None:
    """Serialize all 3 presets + active name to ~/.h3tc/theme.json."""
    data = {
        "version": _VERSION,
        "active": active,
        "themes": {name: _serialize_theme(t) for name, t in themes.items()},
    }
    _THEME_DIR.mkdir(parents=True, exist_ok=True)
    _THEME_FILE.write_text(json.dumps(data, indent=2) + "\n", "utf-8")


def load_themes() -> tuple[dict[str, Theme], str] | None:
    """Load all saved presets from ~/.h3tc/theme.json.

    Returns (themes_dict, active_name) or None on missing/corrupt/version-mismatch.
    """
    if not _THEME_FILE.exists():
        return None

    try:
        raw = json.loads(_THEME_FILE.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    if raw.get("version") != _VERSION:
        return None

    active = raw.get("active", "Default")
    themes_raw = raw.get("themes")
    if not isinstance(themes_raw, dict):
        return None

    try:
        themes = {name: _deserialize_theme(data) for name, data in themes_raw.items()}
    except (TypeError, ValueError):
        return None

    return themes, active
