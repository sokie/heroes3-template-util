"""Visual representation of a zone on the canvas.

Layout matching the HOTA template editor: colored box with treasure value,
castle icons, resource mine icons with counts, and crossed swords.
Zone colors: player start = player color, treasure = gray/gold, junction = gold.
"""

import math

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
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
    ZONE_COLORS,
    ZONE_CORNER_RADIUS,
    ZONE_SELECTED_BORDER_WIDTH,
    ZONE_SIZE_SCALE,
)
from h3tc.enums import RESOURCES
from h3tc.models import Zone

# Icon layout constants – sized to match HOTA editor
_ICO = 52           # Icon size in pixels
_CELL_W = _ICO + 14 # Cell width: icon + padding (count goes below, not beside)
_MARGIN = 16        # Margin inside zone rect
_HEADER_H = _ICO + 20 # Height for header row (chest+treasure, swords)
_ROW_H = _ICO + 28  # Height per content row (icon + count text below)
_COLS = 3           # Icons per row

# Font sizes (scene-coordinate points)
_FONT_TREASURE = 34  # Treasure value next to chest
_FONT_ZONE_ID = 28   # Zone ID in bottom-right corner
_FONT_LABEL = 22     # P: / N: row labels
_FONT_COUNT = 22     # Count values below icons


def _zone_color(zone: Zone) -> QColor:
    """Zone color based on type and treasure value.

    Player start = player color from constants.
    Non-player zones colored by treasure value.
    """
    if zone.human_start == "x" or zone.computer_start == "x":
        owner = zone.ownership.strip()
        colors = ZONE_COLORS["human_start"]
        return colors.get(owner, colors["0"])

    tval = _treasure_value(zone)
    if tval >= 200:
        return QColor(215, 195, 140)    # Pastel gold
    if tval >= 100:
        return QColor(190, 195, 205)    # Pastel silver
    return QColor(218, 218, 218)        # Light gray


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

    # Width: header needs chest + treasure text + gap + swords
    header_w = _ICO + 8 + 80 + 20 + _ICO * 2.1  # chest + val + gap + swords
    # Content needs COLS icon cells + label prefix
    content_w = 38 + _COLS * _CELL_W + _MARGIN * 2
    w = max(header_w + _MARGIN * 2, content_w, scale * 3, 160)

    # Height: header + content rows + ID line + margins
    content_h = _HEADER_H + rows * _ROW_H + _MARGIN * 2 + 40
    h = max(content_h, scale * 2, 110)

    return w, h


def _is_dark_bg(color: QColor) -> bool:
    brightness = color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114
    return brightness < 150


def _make_font(size: int, bold: bool = True, extra_bold: bool = False) -> QFont:
    if extra_bold:
        weight = QFont.Weight.ExtraBold
    elif bold:
        weight = QFont.Weight.Bold
    else:
        weight = QFont.Weight.Normal
    f = QFont("Helvetica Neue", size, weight)
    f.setStyleHint(QFont.StyleHint.SansSerif)
    return f


def _draw_text(
    painter: QPainter, font: QFont, rect: QRectF, flags: int, text: str,
    dark_bg: bool = True,
) -> None:
    painter.setFont(font)
    fg = QColor(255, 255, 255) if dark_bg else QColor(30, 30, 30)
    painter.setPen(QPen(fg))
    painter.drawText(rect, flags, text)


def _draw_icon_with_count(
    painter: QPainter, draw_fn, ix: float, iy: float,
    icon_size: float, count: str, dark_bg: bool,
) -> None:
    """Draw an icon with its count centered below it."""
    draw_fn(painter, ix, iy, icon_size)
    # Count text centered below icon (extra bold for readability)
    count_rect = QRectF(ix - 4, iy + icon_size + 2, icon_size + 8, 26)
    _draw_text(
        painter, _make_font(_FONT_COUNT, extra_bold=True), count_rect,
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        count, dark_bg,
    )


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

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setOffset(3, 4)
        shadow.setColor(QColor(0, 0, 0, 55))
        self.setGraphicsEffect(shadow)

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
            rim_w = min(rect.width(), rect.height()) * 0.16
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(120, 120, 120)))
            painter.drawRoundedRect(rect, ZONE_CORNER_RADIUS, ZONE_CORNER_RADIUS)
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

        if tval > 0:
            draw_treasure_chest(painter, hx, oy, _ICO)
            hx += _ICO + 8
            draw_value_label(painter, hx, oy, 80, _ICO, str(tval),
                             _FONT_TREASURE, dark_bg)
            hx += 84

        if strength > 0:
            sw = _ICO + 2 * _ICO * 0.55
            sx = rect.x() + rect.width() - _MARGIN - sw
            draw_swords(painter, sx, oy, _ICO, strength)

        # ── Zone ID (bottom-right) ───────────────────────────
        id_h = 34
        id_y = rect.y() + rect.height() - _MARGIN - id_h
        is_computer = zone.computer_start.strip().lower() == "x"
        if is_computer:
            pc_size = 24
            id_text = zone.id.strip()
            fm_width = max(len(id_text) * 16, 20)
            pc_x = rect.x() + rect.width() - _MARGIN - fm_width - pc_size - 6
            pc_y = id_y + (id_h - pc_size) / 2
            draw_computer_icon(painter, pc_x, pc_y, pc_size)
        _draw_text(
            painter, _make_font(_FONT_ZONE_ID),
            QRectF(ox, id_y, rect.width() - _MARGIN * 2, id_h),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            zone.id.strip(), dark_bg,
        )

        # ── Content rows: icons with counts below ────────────
        cy = oy + _HEADER_H
        cx = ox

        if _has_towns(zone):
            pt = zone.player_towns
            nt = zone.neutral_towns
            label_font = _make_font(_FONT_LABEL)
            fg = QColor(255, 255, 255) if dark_bg else QColor(30, 30, 30)
            label_w = 38

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
                    _draw_icon_with_count(
                        painter, draw_castle, ix, cy,
                        _ICO, str(p_c), dark_bg)
                    ix += _CELL_W

                p_t = _int_val(pt.min_towns)
                if p_t > 0:
                    _draw_icon_with_count(
                        painter, draw_town, ix, cy,
                        _ICO, str(p_t), dark_bg)
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
                    _draw_icon_with_count(
                        painter, draw_castle, ix, cy,
                        _ICO, str(n_c), dark_bg)
                    ix += _CELL_W

                n_t = _int_val(nt.min_towns)
                if n_t > 0:
                    _draw_icon_with_count(
                        painter, draw_town, ix, cy,
                        _ICO, str(n_t), dark_bg)
                cy += _ROW_H

        # Resource mines: icon on top, count below
        mines = _active_mines(zone)
        if mines:
            for i, (res, mc, md) in enumerate(mines):
                col = i % _COLS
                if i > 0 and col == 0:
                    cy += _ROW_H
                ix = cx + col * _CELL_W
                label = f"{mc}/{md}" if md > 0 else str(mc)
                _draw_icon_with_count(
                    painter,
                    lambda p, x, y, s, r=res: draw_mine(p, x, y, s, r),
                    ix, cy, _ICO, label, dark_bg)
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
