"""Visual constants for the template editor."""

from PySide6.QtGui import QColor

# Grid
GRID_SIZE = 20
GRID_COLOR = QColor(230, 230, 230)
GRID_MAJOR_COLOR = QColor(200, 200, 200)
GRID_MAJOR_EVERY = 5

# Zone rendering
ZONE_MIN_WIDTH = 80
ZONE_MIN_HEIGHT = 50
ZONE_SIZE_SCALE = 11.0  # sqrt(base_size) * scale -> pixel width
ZONE_CORNER_RADIUS = 6
ZONE_BORDER_WIDTH = 2
ZONE_SELECTED_BORDER_WIDTH = 3
ZONE_FONT_SIZE = 10
ZONE_ID_FONT_SIZE = 9

# Zone colors by type
ZONE_COLORS = {
    "human_start": {
        "0": QColor(100, 149, 237),   # Default blue (unowned)
        "1": QColor(70, 130, 230),    # Player 1 - Blue
        "2": QColor(220, 80, 80),     # Player 2 - Red
        "3": QColor(100, 180, 100),   # Player 3 - Green (tan in H3)
        "4": QColor(160, 100, 200),   # Player 4 - Purple
        "5": QColor(220, 160, 60),    # Player 5 - Orange
        "6": QColor(80, 190, 190),    # Player 6 - Teal
        "7": QColor(200, 140, 180),   # Player 7 - Pink
        "8": QColor(160, 160, 160),   # Player 8 - Gray
    },
    "computer_start": QColor(100, 100, 100),
    "treasure": QColor(210, 180, 140),
    "junction": QColor(218, 165, 32),
    "default": QColor(180, 180, 180),
}

# Connection rendering
CONNECTION_COLOR = QColor(80, 80, 80)
CONNECTION_SELECTED_COLOR = QColor(30, 120, 220)
CONNECTION_WIDTH = 2.0
CONNECTION_WIDE_WIDTH = 4.0
CONNECTION_LABEL_FONT_SIZE = 9
CONNECTION_ARROW_SIZE = 0  # No arrows for undirected connections

# Canvas
CANVAS_MARGIN = 200
DEFAULT_ZOOM = 1.0
MIN_ZOOM = 0.05
MAX_ZOOM = 5.0
ZOOM_FACTOR = 1.15

# Selection
SELECTION_COLOR = QColor(30, 120, 220)
