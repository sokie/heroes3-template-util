"""Visual representation of a zone on the canvas.

Layout matching the HOTA template editor: colored box with treasure value,
castle icons, resource mine icons with counts, and crossed swords.
Zone colors: player start = player color, treasure = gray/gold, junction = gold.
"""

import math

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from h3tc.editor.canvas.icons import (
    draw_castle,
    draw_computer_icon,
    draw_mine,
    draw_swords,
    draw_town,
    draw_treasure_chest,
    draw_value_label,
)
from h3tc.editor.constants import (
    SELECTION_COLOR,
    ZONE_BORDER_WIDTH,
    ZONE_CORNER_RADIUS,
    ZONE_SELECTED_BORDER_WIDTH,
    ZONE_SIZE_SCALE,
)
from h3tc.enums import RESOURCES
from h3tc.models import Zone

# Icon layout constants
_ICO = 24           # Icon size in pixels
_GAP = 4            # Gap between icon cells
_CELL_W = _ICO + 30 # Cell width: icon + label space
_MARGIN = 10        # Margin inside zone rect
_HEADER_H = _ICO + 10 # Height for header row (chest+treasure, swords)
_ROW_H = _ICO + 10  # Height per content row
_COLS = 3           # Icons per row

# Player colors (matching H3)
_PLAYER_COLORS = {
    "1": QColor(210, 65, 65),     # Red
    "2": QColor(55, 110, 220),    # Blue
    "3": QColor(200, 170, 110),   # Tan
    "4": QColor(90, 170, 80),     # Green
    "5": QColor(220, 150, 40),    # Orange
    "6": QColor(160, 90, 200),    # Purple
    "7": QColor(50, 180, 180),    # Teal
    "8": QColor(200, 130, 170),   # Pink
}


def _zone_color(zone: Zone) -> QColor:
    """Zone color based on type and treasure value.

    Player start = player color.
    Non-player zones colored by treasure value:
      0-99   = gray
      100-199 = silver
      200+   = gold
    """
    if zone.human_start == "x" or zone.computer_start == "x":
        owner = zone.ownership.strip()
        return _PLAYER_COLORS.get(owner, QColor(100, 149, 237))

    # All non-player zones: color by treasure value
    tval = _treasure_value(zone)
    if tval >= 200:
        return QColor(200, 170, 100)   # Gold
    if tval >= 100:
        return QColor(185, 190, 200)   # Silver
    return QColor(225, 225, 225)       # Light gray


def _int_val(s: str) -> int:
    s = s.strip()
    if not s:
        return 0
    try:
        return int(s)
    except ValueError:
        return 0


def _has_towns(zone: Zone) -> bool:
    pt = zone.player_towns
    nt = zone.neutral_towns
    return any(
        _int_val(v) > 0
        for v in [pt.min_towns, pt.min_castles, nt.min_towns, nt.min_castles]
    )


def _active_mines(zone: Zone) -> list[tuple[str, int, int]]:
    result = []
    for res in RESOURCES:
        mc = _int_val(zone.min_mines.get(res, ""))
        md = _int_val(zone.mine_density.get(res, ""))
        if mc > 0:
            result.append((res, mc, md))
    return result


_STRENGTH_MAP = {
    "weak": 1,
    "normal": 2,
    "strong": 3,
}


def _monster_strength(zone: Zone) -> int:
    val = zone.monster_strength.strip().lower()
    if val in _STRENGTH_MAP:
        return _STRENGTH_MAP[val]
    return _int_val(zone.monster_strength)


def _has_treasure(zone: Zone) -> bool:
    for tier in zone.treasure_tiers:
        if _int_val(tier.low) > 0 or _int_val(tier.high) > 0:
            return True
    return False


def _treasure_value(zone: Zone) -> int:
    """Calculate treasure value: sum of (low+high)/2 * density / 1000."""
    total = 0
    for tier in zone.treasure_tiers:
        low = _int_val(tier.low)
        high = _int_val(tier.high)
        density = _int_val(tier.density)
        if (low > 0 or high > 0) and density > 0:
            total += (low + high) / 2 * density
    return int(total / 1000) if total > 0 else 0


def _content_rows(zone: Zone) -> int:
    rows = 0
    pt = zone.player_towns
    nt = zone.neutral_towns
    if _int_val(pt.min_castles) > 0 or _int_val(pt.min_towns) > 0:
        rows += 1
    if _int_val(nt.min_castles) > 0 or _int_val(nt.min_towns) > 0:
        rows += 1
    mines = _active_mines(zone)
    if mines:
        rows += math.ceil(len(mines) / _COLS)
    return rows


def _zone_size(zone: Zone) -> tuple[float, float]:
    """Calculate zone pixel size - proportional to base_size, fits content."""
    try:
        base = int(zone.base_size) if zone.base_size.strip() else 5
    except ValueError:
        base = 5

    rows = _content_rows(zone)
    scale = math.sqrt(max(base, 1)) * ZONE_SIZE_SCALE

    # Width: fit COLS icon cells, with minimum from base_size scale
    content_w = _COLS * _CELL_W + _MARGIN * 2
    w = max(content_w, scale * 3, 100)

    # Height: header + content rows + ID line + margins
    content_h = _HEADER_H + rows * _ROW_H + _MARGIN * 2 + 20
    h = max(content_h, scale * 2, 70)

    return w, h


def _is_dark_bg(color: QColor) -> bool:
    """Return True if background is dark enough to need white text."""
    brightness = color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114
    return brightness < 150


def _draw_text(
    painter: QPainter, font: QFont, rect: QRectF, flags: int, text: str,
    dark_bg: bool = True,
) -> None:
    """Draw plain text. White on dark bg, black on light bg."""
    painter.setFont(font)
    fg = QColor(255, 255, 255) if dark_bg else QColor(30, 30, 30)
    painter.setPen(QPen(fg))
    painter.drawText(rect, flags, text)


class ZoneItem(QGraphicsRectItem):
    """A draggable zone rectangle with content icons."""

    def __init__(self, zone: Zone) -> None:
        w, h = _zone_size(zone)
        super().__init__(0, 0, w, h)
        self.zone = zone
        self._color = _zone_color(zone)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setZValue(1)
        self._update_appearance()

    def refresh(self) -> None:
        self._color = _zone_color(self.zone)
        w, h = _zone_size(self.zone)
        self.setRect(0, 0, w, h)
        self._update_appearance()
        self.update()

    def _update_appearance(self) -> None:
        self.setBrush(QBrush(self._color))
        self.setPen(QPen(self._color.darker(140), ZONE_BORDER_WIDTH))

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        rect = self.rect()
        zone = self.zone
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ── Background ───────────────────────────────────────
        is_junction = zone.junction.strip().lower() == "x"
        if is_junction:
            # Thick gray rim (~25% of surface) for junction zones
            rim_w = min(rect.width(), rect.height()) * 0.14
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(140, 140, 140)))
            painter.drawRoundedRect(rect, ZONE_CORNER_RADIUS, ZONE_CORNER_RADIUS)
            # Inner fill
            inner = rect.adjusted(rim_w, rim_w, -rim_w, -rim_w)
            inner_r = max(ZONE_CORNER_RADIUS - rim_w * 0.5, 1)
            painter.setBrush(QBrush(self._color))
            painter.drawRoundedRect(inner, inner_r, inner_r)
        if self.isSelected():
            painter.setPen(QPen(SELECTION_COLOR, ZONE_SELECTED_BORDER_WIDTH))
            painter.setBrush(Qt.BrushStyle.NoBrush if is_junction else QBrush(self._color))
            painter.drawRoundedRect(rect, ZONE_CORNER_RADIUS, ZONE_CORNER_RADIUS)
        elif not is_junction:
            painter.setPen(QPen(self._color.darker(140), ZONE_BORDER_WIDTH))
            painter.setBrush(QBrush(self._color))
            painter.drawRoundedRect(rect, ZONE_CORNER_RADIUS, ZONE_CORNER_RADIUS)

        dark_bg = _is_dark_bg(self._color)

        ox = rect.x() + _MARGIN
        oy = rect.y() + _MARGIN

        # ── Header row: chest+treasure (left), swords (right) ──
        tval = _treasure_value(zone)
        strength = _monster_strength(zone)
        hx = ox

        # Chest icon + treasure value at top-left
        if tval > 0:
            draw_treasure_chest(painter, hx, oy, _ICO)
            hx += _ICO + 4
            draw_value_label(painter, hx, oy, 40, _ICO, str(tval), 14,
                             dark_bg)
            hx += 44

        # Swords at top-right (always 3: colored for active, gray for inactive)
        if strength > 0:
            sw = _ICO + 2 * _ICO * 0.55  # 3 swords with spacing
            sx = rect.x() + rect.width() - _MARGIN - sw
            draw_swords(painter, sx, oy, _ICO, strength)

        # Zone ID (bottom-right corner) with PC icon for computer start
        id_y = rect.y() + rect.height() - 20
        is_computer = zone.computer_start.strip().lower() == "x"
        if is_computer:
            # Draw PC icon to the left of the zone ID
            pc_size = 16
            id_text = zone.id.strip()
            # Approximate text width for positioning
            fm_width = max(len(id_text) * 8, 12)
            pc_x = rect.x() + rect.width() - _MARGIN - fm_width - pc_size - 4
            pc_y = id_y + 1
            draw_computer_icon(painter, pc_x, pc_y, pc_size)
        _draw_text(
            painter, QFont("Helvetica", 10, QFont.Weight.Bold),
            QRectF(ox, id_y,
                   rect.width() - _MARGIN * 2, 18),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
            zone.id.strip(), dark_bg,
        )

        # ── Content icons ────────────────────────────────────
        cy = oy + _HEADER_H
        cx = ox

        # Towns/Castles rows - player row labeled "P:", neutral labeled "N:"
        if _has_towns(zone):
            pt = zone.player_towns
            nt = zone.neutral_towns
            label_font = QFont("Helvetica", 9, QFont.Weight.Bold)
            fg = QColor(255, 255, 255) if dark_bg else QColor(30, 30, 30)
            label_w = 18

            has_player = (
                _int_val(pt.min_castles) > 0 or _int_val(pt.min_towns) > 0
            )
            has_neutral = (
                _int_val(nt.min_castles) > 0 or _int_val(nt.min_towns) > 0
            )

            # Player buildings row
            if has_player:
                painter.setFont(label_font)
                painter.setPen(QPen(fg))
                painter.drawText(
                    QRectF(cx, cy, label_w, _ICO),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    "P:",
                )
                ix = cx + label_w

                p_c = _int_val(pt.min_castles)
                if p_c > 0:
                    draw_castle(painter, ix, cy, _ICO)
                    draw_value_label(painter, ix + _ICO + 3, cy, 22, _ICO,
                                     str(p_c), 11, dark_bg)
                    ix += _CELL_W

                p_t = _int_val(pt.min_towns)
                if p_t > 0:
                    draw_town(painter, ix, cy, _ICO)
                    draw_value_label(painter, ix + _ICO + 3, cy, 22, _ICO,
                                     str(p_t), 11, dark_bg)
                cy += _ROW_H

            # Neutral buildings row
            if has_neutral:
                painter.setFont(label_font)
                painter.setPen(QPen(fg))
                painter.drawText(
                    QRectF(cx, cy, label_w, _ICO),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    "N:",
                )
                ix = cx + label_w

                n_c = _int_val(nt.min_castles)
                if n_c > 0:
                    draw_castle(painter, ix, cy, _ICO)
                    draw_value_label(painter, ix + _ICO + 3, cy, 22, _ICO,
                                     str(n_c), 11, dark_bg)
                    ix += _CELL_W

                n_t = _int_val(nt.min_towns)
                if n_t > 0:
                    draw_town(painter, ix, cy, _ICO)
                    draw_value_label(painter, ix + _ICO + 3, cy, 22, _ICO,
                                     str(n_t), 11, dark_bg)
                cy += _ROW_H

        # Resource mines in grid
        mines = _active_mines(zone)
        if mines:
            for i, (res, mc, md) in enumerate(mines):
                col = i % _COLS
                if i > 0 and col == 0:
                    cy += _ROW_H
                ix = cx + col * _CELL_W
                draw_mine(painter, ix, cy, _ICO, res)
                label = f"{mc} / {md}" if md > 0 else str(mc)
                draw_value_label(painter, ix + _ICO + 3, cy, 28, _ICO,
                                 label, 11, dark_bg)
            cy += _ROW_H

    def center_point(self):
        rect = self.rect()
        return self.mapToScene(rect.center())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            scene = self.scene()
            if scene and hasattr(scene, "zone_moved"):
                scene.zone_moved(self)
        return super().itemChange(change, value)
