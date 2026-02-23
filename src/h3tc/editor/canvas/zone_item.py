"""Visual representation of a zone on the canvas.

Layout matching the HOTA template editor: colored box with treasure value,
castle icons, resource mine icons with counts, and crossed swords.
Zone colors: player start = player color, treasure = gray/gold, junction = gold.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
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
    DisplayMode,
    ZONE_SIZE_SCALE,
    ThemeManager,
)
from h3tc.enums import RESOURCES
from h3tc.models import Zone

# Icon layout constants – sized to match HOTA editor
_ICO = 52           # Icon size in pixels
_CELL_W = _ICO + 14 # Cell width: icon + padding (count goes below, not beside)
_MARGIN = 16        # Margin inside zone rect
_COLS = 5           # Icons per row


def _header_h() -> int:
    """Header row height: adapts to treasure font size."""
    t = _theme()
    return max(_ICO + 20, t.font_treasure + _ICO // 2 + 10)


def _row_h() -> int:
    """Content row height: adapts to count font size."""
    t = _theme()
    count_h = max(t.font_count + 6, 26)
    return _ICO + count_h + 4


def _theme():
    return ThemeManager().theme


def _zone_color(zone: Zone) -> QColor:
    """Zone color based on type and treasure value.

    Player start = player color from theme.
    Non-player zones colored by treasure value.
    """
    t = _theme()
    if zone.human_start == "x" or zone.computer_start == "x":
        owner = zone.ownership.strip()
        colors = t.zone_player_colors
        rgb = colors.get(owner, colors["0"])
        return QColor(*rgb)

    tval = _treasure_value(zone)
    if tval >= 200:
        return QColor(*t.zone_treasure_high)
    if tval >= 100:
        return QColor(*t.zone_treasure_mid)
    return QColor(*t.zone_treasure_low)


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
    "avg": 2,
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


def _content_metrics(zone: Zone) -> tuple[int, int]:
    """Return (rows, max_icons_in_any_row) for zone content."""
    rows = 0
    max_cols = 0
    pt = zone.player_towns
    nt = zone.neutral_towns

    p_count = (_int_val(pt.min_castles) > 0) + (_int_val(pt.min_towns) > 0)
    if p_count > 0:
        rows += 1
        max_cols = max(max_cols, p_count)

    n_count = (_int_val(nt.min_castles) > 0) + (_int_val(nt.min_towns) > 0)
    if n_count > 0:
        rows += 1
        max_cols = max(max_cols, n_count)

    mines = _active_mines(zone)
    if mines:
        rows += math.ceil(len(mines) / _COLS)
        max_cols = max(max_cols, min(len(mines), _COLS))

    return rows, max_cols


def zone_size(zone: Zone) -> tuple[float, float]:
    """Calculate zone pixel size - proportional to base_size, fits content."""
    try:
        base = int(zone.base_size) if zone.base_size.strip() else 5
    except ValueError:
        base = 5

    rows, max_cols = _content_metrics(zone)
    scale = math.sqrt(max(base, 1)) * ZONE_SIZE_SCALE

    # Width: header needs chest + treasure text + gap + swords
    header_w = _ICO + 8 + 80 + 20 + _ICO  # chest + val + gap + swords
    # Content width adapts to actual number of icons per row
    actual_cols = max(max_cols, 1)
    content_w = 38 + actual_cols * _CELL_W + _MARGIN * 2
    w = max(header_w + _MARGIN * 2, content_w, scale * 3, 160)

    # Height: header + content rows + ID line + margins
    content_h = _header_h() + rows * _row_h() + _MARGIN * 2 + 40
    h = max(content_h, scale * 2, 110)

    # Keep zones square
    side = max(w, h)
    return side, side


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
    t = _theme()
    if dark_bg:
        # Text shadow for readability
        if t.text_shadow:
            painter.setPen(QPen(QColor(0, 0, 0, 120)))
            painter.drawText(rect.adjusted(1, 1, 1, 1), flags, text)
        fg = QColor(255, 255, 255)
    else:
        fg = QColor(30, 30, 30)
    painter.setPen(QPen(fg))
    painter.drawText(rect, flags, text)


def _draw_icon_with_count(
    painter: QPainter, draw_fn, ix: float, iy: float,
    icon_size: float, count: str, dark_bg: bool,
) -> None:
    """Draw an icon with its count centered below it."""
    draw_fn(painter, ix, iy, icon_size)
    t = _theme()
    # Count text centered below icon (extra bold for readability)
    count_h = max(t.font_count + 6, 26)
    count_rect = QRectF(ix - 4, iy + icon_size + 2, icon_size + 8, count_h)
    _draw_text(
        painter, _make_font(t.font_count, extra_bold=True), count_rect,
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        count, dark_bg,
    )


class ZoneItem(QGraphicsRectItem):
    """A draggable zone rectangle with content icons."""

    def __init__(self, zone: Zone) -> None:
        w, h = zone_size(zone)
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
        w, h = zone_size(self.zone)
        self.setRect(0, 0, w, h)
        self._update_appearance()
        self.update()

    def _update_appearance(self) -> None:
        t = _theme()
        self.setBrush(QBrush(self._color))
        self.setPen(QPen(self._color.darker(t.zone_border_darken), t.zone_border_width))

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_background(painter)

        scene = self.scene()
        mode = getattr(scene, 'display_mode', DisplayMode.DETAILS)
        if mode == DisplayMode.ZONE_ID:
            self._paint_zone_id(painter)
        else:
            self._paint_details(painter)

    def _paint_background(self, painter: QPainter) -> None:
        t = _theme()
        rect = self.rect()
        corner_r = t.zone_corner_radius
        is_junction = self.zone.junction.strip().lower() == "x"
        if is_junction:
            rim_w = min(rect.width(), rect.height()) * 0.16
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(120, 120, 120)))
            painter.drawRoundedRect(rect, corner_r, corner_r)
            inner = rect.adjusted(rim_w, rim_w, -rim_w, -rim_w)
            inner_r = max(corner_r - rim_w * 0.5, 1)
            painter.setBrush(QBrush(self._color))
            painter.drawRoundedRect(inner, inner_r, inner_r)
        if self.isSelected():
            painter.setPen(QPen(SELECTION_COLOR, t.zone_selected_border_width))
            painter.setBrush(Qt.BrushStyle.NoBrush if is_junction else QBrush(self._color))
            painter.drawRoundedRect(rect, corner_r, corner_r)
        elif not is_junction:
            painter.setPen(QPen(self._color.darker(t.zone_border_darken), t.zone_border_width))
            painter.setBrush(QBrush(self._color))
            painter.drawRoundedRect(rect, corner_r, corner_r)

    def _paint_zone_id(self, painter: QPainter) -> None:
        rect = self.rect()
        dark_bg = _is_dark_bg(self._color)
        font_size = int(min(rect.width(), rect.height()) * 0.45)
        font = _make_font(font_size, extra_bold=True)
        _draw_text(
            painter, font, rect,
            Qt.AlignmentFlag.AlignCenter,
            self.zone.id.strip(), dark_bg,
        )

    def _paint_details(self, painter: QPainter) -> None:
        t = _theme()
        rect = self.rect()
        zone = self.zone
        dark_bg = _is_dark_bg(self._color)

        ox = rect.x() + _MARGIN
        oy = rect.y() + _MARGIN

        # ── Header row: chest+treasure (left), swords (right) ──
        tval = _treasure_value(zone)
        strength = _monster_strength(zone)
        hx = ox

        # Calculate swords position first so we can constrain treasure label
        sx = rect.x() + rect.width() - _MARGIN - _ICO if strength > 0 else 0

        # Draw swords first so treasure text renders on top if they overlap
        if strength > 0:
            draw_swords(painter, sx, oy, _ICO, strength)

        if tval > 0:
            draw_treasure_chest(painter, hx, oy, _ICO)
            hx += _ICO + 8
            # Constrain label width to not overlap with swords
            max_label_w = 80
            if strength > 0:
                max_label_w = max(sx - hx - 8, 40)
            draw_value_label(painter, hx, oy, max_label_w, _ICO, str(tval),
                             t.font_treasure, dark_bg)
            hx += max_label_w + 4

        # ── Zone ID (bottom-right) ───────────────────────────
        id_h = 34
        id_y = rect.y() + rect.height() - _MARGIN - id_h
        is_junction = zone.junction.strip().lower() == "x"
        is_computer = zone.computer_start.strip().lower() == "x"

        # Measure ID text width to position PC icon correctly
        id_text = zone.id.strip()
        id_font = _make_font(t.font_zone_id)
        from PySide6.QtGui import QFontMetrics
        id_fm = QFontMetrics(id_font)
        id_text_w = id_fm.horizontalAdvance(id_text)

        if is_computer:
            pc_size = 24
            pc_x = rect.x() + rect.width() - _MARGIN - id_text_w - pc_size - 8
            pc_y = id_y + (id_h - pc_size) / 2
            draw_computer_icon(painter, pc_x, pc_y, pc_size)

        # Junction zones: ID sits over the dark rim, so force white text
        # with a dark shadow for readability regardless of inner fill color
        id_rect = QRectF(ox, id_y, rect.width() - _MARGIN * 2, id_h)
        id_flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if is_junction:
            painter.setFont(id_font)
            painter.setPen(QPen(QColor(0, 0, 0, 160)))
            shadow_rect = id_rect.translated(1, 1)
            painter.drawText(shadow_rect, id_flags, id_text)
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(id_rect, id_flags, id_text)
        else:
            _draw_text(painter, id_font, id_rect, id_flags, id_text, dark_bg)

        # ── Content rows: icons with counts below ────────────
        cy = oy + _header_h()
        cx = ox

        if _has_towns(zone):
            pt = zone.player_towns
            nt = zone.neutral_towns
            label_font = _make_font(t.font_label)
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
                cy += _row_h()

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
                cy += _row_h()

        # Resource mines: icon on top, count below
        mines = _active_mines(zone)
        if mines:
            for i, (res, mc, md) in enumerate(mines):
                col = i % _COLS
                if i > 0 and col == 0:
                    cy += _row_h()
                ix = cx + col * _CELL_W
                label = f"{mc}/{md}" if md > 0 else str(mc)
                _draw_icon_with_count(
                    painter,
                    lambda p, x, y, s, r=res: draw_mine(p, x, y, s, r),
                    ix, cy, _ICO, label, dark_bg)
            cy += _row_h()

    def center_point(self):
        rect = self.rect()
        return self.mapToScene(rect.center())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            scene = self.scene()
            if scene and getattr(scene, 'snap_to_grid', False):
                from h3tc.editor.constants import GRID_SIZE
                x = round(value.x() / GRID_SIZE) * GRID_SIZE
                y = round(value.y() / GRID_SIZE) * GRID_SIZE
                value = QPointF(x, y)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            scene = self.scene()
            if scene and hasattr(scene, "zone_moved"):
                scene.zone_moved(self)
        return super().itemChange(change, value)
