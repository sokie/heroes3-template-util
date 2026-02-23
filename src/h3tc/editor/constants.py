"""Visual constants for the template editor."""

from dataclasses import dataclass, field
from enum import Enum

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor


class DisplayMode(Enum):
    DETAILS = "details"
    ZONE_ID = "zone_id"


# ── Theme Dataclass ───────────────────────────────────────────────────


@dataclass
class Theme:
    """All visual styling for the editor canvas."""

    name: str = "Default"

    # Canvas
    canvas_bg: tuple[int, int, int] = (238, 238, 240)

    # Grid
    grid_color: tuple[int, int, int] = (215, 215, 215)
    grid_minor_width: float = 0.7
    grid_major_color: tuple[int, int, int] = (185, 185, 185)
    grid_major_width: float = 1.0

    # Zone player colors  {ownership_id: (r,g,b)}
    zone_player_colors: dict[str, tuple[int, int, int]] = field(default_factory=lambda: {
        "0": (140, 170, 220),    # Default (unowned) - soft blue
        "1": (200, 115, 110),    # Player 1 - Red (pastel)
        "2": (110, 145, 215),    # Player 2 - Blue (pastel)
        "3": (210, 190, 145),    # Player 3 - Tan
        "4": (120, 185, 120),    # Player 4 - Green (pastel)
        "5": (220, 175, 100),    # Player 5 - Orange (pastel)
        "6": (170, 135, 205),    # Player 6 - Purple (pastel)
        "7": (110, 195, 195),    # Player 7 - Teal (pastel)
        "8": (210, 160, 185),    # Player 8 - Pink (pastel)
    })

    # Zone treasure colors
    zone_treasure_high: tuple[int, int, int] = (215, 195, 140)
    zone_treasure_mid: tuple[int, int, int] = (190, 195, 205)
    zone_treasure_low: tuple[int, int, int] = (218, 218, 218)

    # Zone rendering
    zone_border_width: int = 2
    zone_selected_border_width: int = 3
    zone_border_darken: int = 140
    zone_corner_radius: int = 8

    # Font sizes
    font_treasure: int = 34
    font_zone_id: int = 28
    font_label: int = 22
    font_count: int = 22
    font_connection_label: int = 28

    # Connection label colors
    connection_label_color: tuple[int, int, int] = (200, 40, 40)
    connection_label_pill_bg: tuple[int, int, int, int] = (255, 255, 255, 220)
    connection_label_border: tuple[int, int, int] | None = None
    connection_label_border_width: float = 1.0

    # Icon outline
    icon_outline_color: tuple[int, int, int] = (30, 30, 30)

    # Text shadow (1px dark offset for white text on dark zones)
    text_shadow: bool = False


# ── Pre-built Themes ──────────────────────────────────────────────────

THEME_LIGHT = Theme()

THEME_HIGH_CONTRAST = Theme(
    name="High Contrast",

    canvas_bg=(238, 238, 240),

    grid_color=(215, 215, 215),
    grid_minor_width=0.7,
    grid_major_color=(185, 185, 185),
    grid_major_width=1.0,

    # Vivid, saturated player colors matching H3 palette
    zone_player_colors={
        "0": (240, 240, 240),    # Unowned - white
        "1": (200, 75, 65),      # Player 1 - warm red
        "2": (55, 85, 195),      # Player 2 - deep blue
        "3": (185, 160, 115),    # Player 3 - tan/khaki
        "4": (45, 165, 45),      # Player 4 - vivid green
        "5": (230, 155, 35),     # Player 5 - bright orange
        "6": (130, 65, 170),     # Player 6 - deep purple
        "7": (55, 180, 185),     # Player 7 - vivid teal
        "8": (215, 145, 170),    # Player 8 - soft pink
    },

    # Treasure zones: light/near-white like the reference
    zone_treasure_high=(235, 230, 215),
    zone_treasure_mid=(225, 225, 230),
    zone_treasure_low=(235, 235, 235),

    zone_border_width=2,
    zone_selected_border_width=3,
    zone_border_darken=140,

    font_treasure=34,
    font_zone_id=28,
    font_label=22,
    font_count=22,
    font_connection_label=28,

    # Keep red connection labels like the reference
    connection_label_color=(200, 40, 40),
    connection_label_pill_bg=(255, 255, 255, 220),
    connection_label_border=None,
    connection_label_border_width=1.0,

    icon_outline_color=(30, 30, 30),

    text_shadow=False,
)


# ── Theme Manager (singleton) ────────────────────────────────────────


class ThemeManager(QObject):
    """Singleton that holds the active theme and emits on change."""

    theme_changed = Signal()

    _instance: "ThemeManager | None" = None

    def __new__(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True
        self._theme = THEME_LIGHT

    @property
    def theme(self) -> Theme:
        return self._theme

    def set_theme(self, theme: Theme) -> None:
        if self._theme is not theme:
            self._theme = theme
            self.theme_changed.emit()


# ── Convenience constants (match default theme for non-themed code) ───

GRID_SIZE = 20
GRID_MAJOR_EVERY = 5

CANVAS_BG_COLOR = QColor(238, 238, 240)
GRID_COLOR = QColor(215, 215, 215)
GRID_MAJOR_COLOR = QColor(185, 185, 185)

CANVAS_MARGIN = 200
DEFAULT_ZOOM = 1.0
MIN_ZOOM = 0.05
MAX_ZOOM = 5.0
ZOOM_FACTOR = 1.15

ZONE_MIN_WIDTH = 100
ZONE_MIN_HEIGHT = 60
ZONE_SIZE_SCALE = 11.0
ZONE_CORNER_RADIUS = 8
ZONE_BORDER_WIDTH = 2
ZONE_SELECTED_BORDER_WIDTH = 3
ZONE_FONT_SIZE = 16
ZONE_ID_FONT_SIZE = 18

ZONE_COLORS = {
    "human_start": {
        "0": QColor(140, 170, 220),
        "1": QColor(200, 115, 110),
        "2": QColor(110, 145, 215),
        "3": QColor(210, 190, 145),
        "4": QColor(120, 185, 120),
        "5": QColor(220, 175, 100),
        "6": QColor(170, 135, 205),
        "7": QColor(110, 195, 195),
        "8": QColor(210, 160, 185),
    },
    "computer_start": QColor(100, 149, 237),
    "treasure": QColor(210, 180, 140),
    "junction": QColor(218, 165, 32),
    "default": QColor(180, 180, 180),
}

CONNECTION_COLOR = QColor(80, 80, 80)
CONNECTION_SELECTED_COLOR = QColor(30, 120, 220)
CONNECTION_WIDTH = 3.0
CONNECTION_WIDE_WIDTH = 6.0
CONNECTION_LABEL_FONT_SIZE = 28
CONNECTION_ARROW_SIZE = 0

SELECTION_COLOR = QColor(30, 120, 220)
