"""Visual constants for the template editor."""

from PySide6.QtGui import QColor

# Grid
GRID_SIZE = 20
GRID_COLOR = QColor(215, 215, 215)
GRID_MAJOR_COLOR = QColor(185, 185, 185)
GRID_MAJOR_EVERY = 5

# Canvas
CANVAS_BG_COLOR = QColor(238, 238, 240)
CANVAS_MARGIN = 200
DEFAULT_ZOOM = 1.0
MIN_ZOOM = 0.05
MAX_ZOOM = 5.0
ZOOM_FACTOR = 1.15

# Zone rendering
ZONE_MIN_WIDTH = 100
ZONE_MIN_HEIGHT = 60
ZONE_SIZE_SCALE = 11.0  # sqrt(base_size) * scale -> pixel width
ZONE_CORNER_RADIUS = 8
ZONE_BORDER_WIDTH = 2
ZONE_SELECTED_BORDER_WIDTH = 3
ZONE_FONT_SIZE = 16
ZONE_ID_FONT_SIZE = 18

# Zone colors by type
ZONE_COLORS = {
    "human_start": {
        "0": QColor(140, 170, 220),   # Default (unowned) - soft blue
        "1": QColor(200, 115, 110),   # Player 1 - Red (pastel)
        "2": QColor(110, 145, 215),   # Player 2 - Blue (pastel)
        "3": QColor(210, 190, 145),   # Player 3 - Tan
        "4": QColor(120, 185, 120),   # Player 4 - Green (pastel)
        "5": QColor(220, 175, 100),   # Player 5 - Orange (pastel)
        "6": QColor(170, 135, 205),   # Player 6 - Purple (pastel)
        "7": QColor(110, 195, 195),   # Player 7 - Teal (pastel)
        "8": QColor(210, 160, 185),   # Player 8 - Pink (pastel)
    },
    "computer_start": QColor(100, 149, 237),  # Uses player color like human_start
    "treasure": QColor(210, 180, 140),
    "junction": QColor(218, 165, 32),
    "default": QColor(180, 180, 180),
}

# Connection rendering
CONNECTION_COLOR = QColor(80, 80, 80)
CONNECTION_SELECTED_COLOR = QColor(30, 120, 220)
CONNECTION_WIDTH = 3.0
CONNECTION_WIDE_WIDTH = 6.0
CONNECTION_LABEL_FONT_SIZE = 28
CONNECTION_ARROW_SIZE = 0  # No arrows for undirected connections

# Selection
SELECTION_COLOR = QColor(30, 120, 220)
