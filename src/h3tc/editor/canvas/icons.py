"""Vector icons drawn directly with QPainter for resolution independence.

All icons scale cleanly at any zoom level since they use QPainter paths
rather than cached pixmaps.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)

_BLACK = QColor(30, 30, 30)


def _pen(s: float) -> QPen:
    """Outline pen scaled to icon size."""
    return QPen(_BLACK, max(s * 0.08, 1.0), Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)


# ── Treasure Chest ──────────────────────────────────────────────────

def draw_treasure_chest(painter: QPainter, x: float, y: float, size: float) -> None:
    s = size
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    # Chest body
    bx, by, bw, bh = s * 0.12, s * 0.48, s * 0.76, s * 0.38
    painter.setBrush(QBrush(QColor(160, 100, 40)))
    painter.drawRoundedRect(QRectF(bx, by, bw, bh), s * 0.04, s * 0.04)

    # Lid
    lh = s * 0.28
    painter.setBrush(QBrush(QColor(140, 85, 30)))
    painter.drawRoundedRect(QRectF(bx, by - lh + s * 0.06, bw, lh), s * 0.06, s * 0.06)

    # Metal bands
    painter.setPen(QPen(QColor(180, 160, 60), s * 0.04))
    painter.drawLine(QPointF(bx, by + bh * 0.35), QPointF(bx + bw, by + bh * 0.35))
    painter.drawLine(QPointF(bx, by - lh * 0.2), QPointF(bx + bw, by - lh * 0.2))

    # Clasp
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(220, 190, 50)))
    painter.drawEllipse(QPointF(s * 0.5, by + s * 0.01), s * 0.06, s * 0.06)

    # Colorful gems on top
    gems = [
        (s * 0.28, by - lh * 0.4, QColor(220, 40, 40)),
        (s * 0.42, by - lh * 0.6, QColor(50, 180, 50)),
        (s * 0.56, by - lh * 0.5, QColor(60, 100, 220)),
        (s * 0.70, by - lh * 0.35, QColor(220, 200, 40)),
    ]
    for gx, gy, gc in gems:
        painter.setBrush(QBrush(gc))
        painter.setPen(QPen(_BLACK, s * 0.04))
        painter.drawEllipse(QPointF(gx, gy), s * 0.07, s * 0.07)

    painter.restore()


# ── Castle / Town ───────────────────────────────────────────────────

def draw_castle(painter: QPainter, x: float, y: float, size: float) -> None:
    s = size
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    wall_c = QColor(180, 165, 140)
    roof_c = QColor(150, 60, 50)

    # Main wall
    ww, wh = s * 0.55, s * 0.35
    wx = (s - ww) / 2
    wy = s * 0.55
    painter.setBrush(QBrush(wall_c))
    painter.drawRect(QRectF(wx, wy, ww, wh))

    # Left tower
    tw = s * 0.22
    painter.drawRect(QRectF(wx - tw * 0.3, wy - s * 0.18, tw, s * 0.18 + wh))
    painter.setBrush(QBrush(roof_c))
    lx = wx - tw * 0.3
    painter.drawPolygon(QPolygonF([
        QPointF(lx - s * 0.02, wy - s * 0.18),
        QPointF(lx + tw / 2, wy - s * 0.35),
        QPointF(lx + tw + s * 0.02, wy - s * 0.18),
    ]))

    # Right tower
    painter.setBrush(QBrush(wall_c))
    rx = wx + ww - tw * 0.7
    painter.drawRect(QRectF(rx, wy - s * 0.18, tw, s * 0.18 + wh))
    painter.setBrush(QBrush(roof_c))
    painter.drawPolygon(QPolygonF([
        QPointF(rx - s * 0.02, wy - s * 0.18),
        QPointF(rx + tw / 2, wy - s * 0.35),
        QPointF(rx + tw + s * 0.02, wy - s * 0.18),
    ]))

    # Center tower (taller)
    painter.setBrush(QBrush(wall_c))
    ctw = s * 0.18
    ctx = (s - ctw) / 2
    painter.drawRect(QRectF(ctx, wy - s * 0.25, ctw, s * 0.25))
    painter.setBrush(QBrush(roof_c))
    painter.drawPolygon(QPolygonF([
        QPointF(ctx - s * 0.02, wy - s * 0.25),
        QPointF(ctx + ctw / 2, wy - s * 0.42),
        QPointF(ctx + ctw + s * 0.02, wy - s * 0.25),
    ]))

    # Gate
    painter.setBrush(QBrush(QColor(70, 45, 25)))
    gw, gh = s * 0.12, s * 0.18
    painter.drawRoundedRect(QRectF((s - gw) / 2, wy + wh - gh, gw, gh),
                            s * 0.02, s * 0.02)

    painter.restore()


# ── Town (smaller building, distinct from castle) ──────────────────

def draw_town(painter: QPainter, x: float, y: float, size: float) -> None:
    s = size
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    wall_c = QColor(175, 155, 130)
    roof_c = QColor(130, 80, 50)

    # Main building
    bw, bh = s * 0.50, s * 0.35
    bx = (s - bw) / 2
    by = s * 0.55
    painter.setBrush(QBrush(wall_c))
    painter.drawRect(QRectF(bx, by, bw, bh))

    # Roof (simple triangle)
    painter.setBrush(QBrush(roof_c))
    painter.drawPolygon(QPolygonF([
        QPointF(bx - s * 0.04, by),
        QPointF(s * 0.5, by - s * 0.28),
        QPointF(bx + bw + s * 0.04, by),
    ]))

    # Door
    painter.setBrush(QBrush(QColor(70, 45, 25)))
    dw, dh = s * 0.12, s * 0.18
    painter.drawRoundedRect(QRectF((s - dw) / 2, by + bh - dh, dw, dh),
                            s * 0.02, s * 0.02)

    # Window
    painter.setBrush(QBrush(QColor(160, 200, 230)))
    ww = s * 0.10
    painter.drawRect(QRectF(s * 0.5 - ww / 2, by + s * 0.06, ww, ww))

    painter.restore()


# ── Single Sword ────────────────────────────────────────────────────

def _draw_one_sword(painter: QPainter, cx: float, cy: float, s: float,
                    colored: bool) -> None:
    """Draw a single upright sword at (cx, cy) with height ~s."""
    painter.save()
    painter.translate(cx, cy)

    if colored:
        lw = max(s * 0.06, 0.6)
        outline_c = _BLACK
    else:
        lw = max(s * 0.04, 0.4)
        outline_c = QColor(180, 180, 180, 120)

    if colored:
        blade_c = QColor(180, 195, 210)
        guard_c = QColor(160, 120, 40)
        handle_c = QColor(120, 80, 30)
        pommel_c = QColor(190, 170, 50)
    else:
        blade_c = QColor(220, 220, 220, 120)
        guard_c = QColor(210, 210, 205, 120)
        handle_c = QColor(205, 205, 200, 120)
        pommel_c = QColor(215, 215, 210, 120)

    bw = s * 0.14  # blade width
    bl = s * 0.50  # blade length
    # Blade
    painter.setPen(QPen(outline_c, lw, Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(QBrush(blade_c))
    painter.drawPolygon(QPolygonF([
        QPointF(-bw / 2, 0),
        QPointF(0, -bl),           # tip
        QPointF(bw / 2, 0),
    ]))
    # Crossguard
    gw = s * 0.32
    gh = s * 0.08
    painter.setBrush(QBrush(guard_c))
    painter.drawRoundedRect(QRectF(-gw / 2, 0, gw, gh), gh * 0.3, gh * 0.3)
    # Handle
    hw = s * 0.10
    hh = s * 0.22
    painter.setBrush(QBrush(handle_c))
    painter.drawRoundedRect(QRectF(-hw / 2, gh, hw, hh), hw * 0.3, hw * 0.3)
    # Pommel
    pr = s * 0.07
    painter.setBrush(QBrush(pommel_c))
    painter.drawEllipse(QPointF(0, gh + hh + pr * 0.5), pr, pr)

    painter.restore()


def draw_swords(painter: QPainter, x: float, y: float, size: float,
                strength: int) -> None:
    """Draw 3 single swords: first `strength` colored, rest light gray."""
    if strength <= 0:
        return
    s = size
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    spacing = s * 0.38
    total_w = spacing * 2
    start_x = x + (s - total_w) / 2
    sword_cy = y + s * 0.82  # bottom of sword handle
    for i in range(3):
        sx = start_x + i * spacing
        _draw_one_sword(painter, sx, sword_cy, s, colored=(i < strength))

    painter.restore()


# ── Computer Icon ──────────────────────────────────────────────────

def draw_computer_icon(painter: QPainter, x: float, y: float, size: float) -> None:
    """Draw a small monitor/PC icon (like HOTA editor) for computer start zones."""
    s = size
    painter.save()
    painter.translate(x, y)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = _pen(s)
    painter.setPen(pen)

    # Monitor body
    mw, mh = s * 0.80, s * 0.55
    mx = (s - mw) / 2
    my = s * 0.08
    painter.setBrush(QBrush(QColor(60, 60, 70)))
    painter.drawRoundedRect(QRectF(mx, my, mw, mh), s * 0.04, s * 0.04)

    # Screen
    sw, sh = mw * 0.80, mh * 0.75
    sx = mx + (mw - sw) / 2
    sy = my + (mh - sh) / 2
    painter.setBrush(QBrush(QColor(140, 180, 220)))
    painter.drawRect(QRectF(sx, sy, sw, sh))

    # Stand
    stand_w = s * 0.20
    stand_h = s * 0.15
    painter.setBrush(QBrush(QColor(80, 80, 90)))
    painter.drawRect(QRectF((s - stand_w) / 2, my + mh, stand_w, stand_h))

    # Base
    base_w = s * 0.45
    base_h = s * 0.06
    painter.drawRect(QRectF((s - base_w) / 2, my + mh + stand_h, base_w, base_h))

    painter.restore()


# ── Resource Icons ──────────────────────────────────────────────────

def _draw_wood(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    colors = [QColor(150, 95, 35), QColor(170, 110, 45), QColor(140, 85, 30)]
    lw = s * 0.65
    lh = s * 0.18
    lx = (s - lw) / 2

    for i, c in enumerate(colors):
        ly = s * 0.25 + i * (lh + s * 0.04)
        painter.setBrush(QBrush(c))
        painter.drawRoundedRect(QRectF(lx, ly, lw, lh), s * 0.06, s * 0.06)
        painter.setBrush(QBrush(c.lighter(115)))
        painter.drawEllipse(QPointF(lx + lw - s * 0.02, ly + lh / 2),
                            lh * 0.4, lh * 0.4)
    painter.restore()


def _draw_ore(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    rocks = [
        (s * 0.22, s * 0.50, s * 0.30, s * 0.30, QColor(140, 140, 140)),
        (s * 0.48, s * 0.45, s * 0.34, s * 0.36, QColor(120, 120, 120)),
        (s * 0.30, s * 0.28, s * 0.38, s * 0.32, QColor(160, 160, 160)),
    ]
    for rx, ry, rw, rh, c in rocks:
        painter.setBrush(QBrush(c))
        painter.drawEllipse(QRectF(rx, ry, rw, rh))
    painter.restore()


def _draw_mercury(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)
    cx = s / 2

    painter.setBrush(QBrush(QColor(110, 110, 115)))
    body = QPainterPath()
    body.moveTo(cx - s * 0.3, s * 0.35)
    body.lineTo(cx - s * 0.25, s * 0.78)
    body.quadTo(cx, s * 0.88, cx + s * 0.25, s * 0.78)
    body.lineTo(cx + s * 0.3, s * 0.35)
    body.closeSubpath()
    painter.drawPath(body)

    painter.setBrush(QBrush(QColor(130, 130, 135)))
    painter.drawEllipse(QPointF(cx, s * 0.35), s * 0.3, s * 0.08)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(160, 200, 220)))
    painter.drawEllipse(QPointF(cx, s * 0.37), s * 0.22, s * 0.05)
    painter.restore()


def _draw_sulfur(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    painter.setBrush(QBrush(QColor(220, 190, 50)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.15, s * 0.82),
        QPointF(s * 0.30, s * 0.42),
        QPointF(s * 0.50, s * 0.30),
        QPointF(s * 0.70, s * 0.45),
        QPointF(s * 0.85, s * 0.82),
    ]))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(245, 230, 80)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.35, s * 0.50),
        QPointF(s * 0.50, s * 0.30),
        QPointF(s * 0.55, s * 0.55),
    ]))
    painter.restore()


def _draw_crystal(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    shards = [
        ([s * 0.20, s * 0.82, s * 0.15, s * 0.35, s * 0.35, s * 0.82], QColor(200, 50, 60)),
        ([s * 0.32, s * 0.82, s * 0.40, s * 0.18, s * 0.55, s * 0.82], QColor(220, 60, 70)),
        ([s * 0.50, s * 0.82, s * 0.65, s * 0.30, s * 0.80, s * 0.82], QColor(190, 45, 55)),
    ]
    for pts, c in shards:
        painter.setBrush(QBrush(c))
        poly = QPolygonF([QPointF(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)])
        painter.drawPolygon(poly)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(240, 130, 140, 160)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.36, s * 0.65),
        QPointF(s * 0.40, s * 0.18),
        QPointF(s * 0.46, s * 0.55),
    ]))
    painter.restore()


def _draw_gems(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    gems = [
        (s * 0.20, s * 0.55, s * 0.20, QColor(220, 40, 40)),
        (s * 0.45, s * 0.50, s * 0.22, QColor(50, 170, 50)),
        (s * 0.72, s * 0.55, s * 0.18, QColor(60, 90, 220)),
        (s * 0.32, s * 0.32, s * 0.18, QColor(220, 200, 40)),
        (s * 0.58, s * 0.30, s * 0.16, QColor(180, 50, 200)),
    ]
    for gx, gy, gr, gc in gems:
        painter.setBrush(QBrush(gc))
        painter.drawPolygon(QPolygonF([
            QPointF(gx, gy - gr * 0.8),
            QPointF(gx + gr * 0.7, gy),
            QPointF(gx, gy + gr * 0.8),
            QPointF(gx - gr * 0.7, gy),
        ]))
    painter.restore()


def _draw_gold(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    cx = s / 2
    coin_c = QColor(210, 175, 55)
    coin_d = QColor(180, 145, 40)

    for i in range(4):
        cy = s * 0.72 - i * s * 0.1
        rx, ry = s * 0.28, s * 0.08
        painter.setBrush(QBrush(coin_d if i % 2 == 0 else coin_c))
        painter.drawEllipse(QPointF(cx, cy), rx, ry)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(240, 210, 80, 150)))
    painter.drawEllipse(QPointF(cx - s * 0.05, s * 0.38), s * 0.1, s * 0.04)
    painter.restore()


# ── Dispatch ────────────────────────────────────────────────────────

_RESOURCE_DRAW = {
    "Wood": _draw_wood,
    "Ore": _draw_ore,
    "Mercury": _draw_mercury,
    "Sulfur": _draw_sulfur,
    "Crystal": _draw_crystal,
    "Gems": _draw_gems,
    "Gold": _draw_gold,
}


def draw_mine(painter: QPainter, x: float, y: float, size: float,
              resource: str) -> None:
    fn = _RESOURCE_DRAW.get(resource)
    if fn:
        fn(painter, x, y, size)


# ── Value Label ─────────────────────────────────────────────────────

def draw_value_label(
    painter: QPainter,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    font_size: int = 9,
    dark_bg: bool = True,
) -> None:
    """Draw a plain value label. White on dark bg, black on light bg."""
    painter.save()
    font = QFont("Helvetica Neue", font_size, QFont.Weight.Bold)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    painter.setFont(font)
    r = QRectF(x, y, width, height)
    align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    if dark_bg:
        # 1px dark text shadow for readability on dark backgrounds
        painter.setPen(QPen(QColor(0, 0, 0, 100)))
        painter.drawText(r.adjusted(1, 1, 1, 1), align, text)
        painter.setPen(QPen(QColor(255, 255, 255)))
    else:
        painter.setPen(QPen(QColor(30, 30, 30)))
    painter.drawText(r, align, text)
    painter.restore()
