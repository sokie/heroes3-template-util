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
                    colored: bool, angle: float = -20.0) -> None:
    """Draw a tilted fantasy sword at (cx, cy), H3-style."""
    painter.save()
    painter.translate(cx, cy)
    painter.rotate(angle)

    if colored:
        lw = max(s * 0.06, 0.6)
        outline_c = _BLACK
        blade_c = QColor(170, 185, 200)
        blade_hi = QColor(210, 220, 235)
        blade_dark = QColor(120, 130, 145)
        guard_c = QColor(150, 110, 40)
        guard_hi = QColor(185, 150, 60)
        handle_c = QColor(130, 85, 35)
        handle_hi = QColor(165, 120, 55)
        pommel_c = QColor(150, 110, 40)
        sparkle_c = QColor(200, 230, 255, 220)
    else:
        lw = max(s * 0.04, 0.4)
        outline_c = QColor(160, 160, 160, 100)
        blade_c = QColor(210, 210, 210, 100)
        blade_hi = QColor(225, 225, 225, 100)
        blade_dark = QColor(185, 185, 185, 100)
        guard_c = QColor(200, 195, 185, 100)
        guard_hi = QColor(210, 205, 195, 100)
        handle_c = QColor(195, 190, 180, 100)
        handle_hi = QColor(205, 200, 190, 100)
        pommel_c = QColor(200, 195, 185, 100)
        sparkle_c = QColor(255, 255, 255, 0)

    pen = QPen(outline_c, lw, Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)

    bw = s * 0.16  # blade half-width at base
    bl = s * 0.48  # blade length

    # Blade — chunky with flat sides tapering to point
    painter.setBrush(QBrush(blade_dark))
    painter.drawPolygon(QPolygonF([
        QPointF(-bw, 0),
        QPointF(-bw * 0.35, -bl * 0.85),
        QPointF(0, -bl),             # tip
        QPointF(bw * 0.35, -bl * 0.85),
        QPointF(bw, 0),
    ]))

    # Blade center highlight (bright edge running down the middle)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(blade_hi))
    painter.drawPolygon(QPolygonF([
        QPointF(-bw * 0.15, -bl * 0.05),
        QPointF(0, -bl),
        QPointF(bw * 0.15, -bl * 0.05),
    ]))

    # Crossguard — angled quillons with pointed ends
    painter.setPen(pen)
    gw = s * 0.18   # half-width of guard
    gh = s * 0.06   # guard thickness
    painter.setBrush(QBrush(guard_c))
    painter.drawPolygon(QPolygonF([
        QPointF(-gw - s * 0.06, gh * 0.3),     # left point
        QPointF(-gw, -gh * 0.5),
        QPointF(gw, -gh * 0.5),
        QPointF(gw + s * 0.06, gh * 0.3),      # right point
        QPointF(gw, gh),
        QPointF(-gw, gh),
    ]))
    # Guard highlight
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(guard_hi))
    painter.drawPolygon(QPolygonF([
        QPointF(-gw - s * 0.04, gh * 0.1),
        QPointF(-gw, -gh * 0.4),
        QPointF(gw * 0.3, -gh * 0.4),
        QPointF(gw * 0.2, gh * 0.2),
    ]))

    # Handle — leather-wrapped grip
    painter.setPen(pen)
    hw = s * 0.09   # handle half-width
    hh = s * 0.24   # handle height
    painter.setBrush(QBrush(handle_c))
    painter.drawRoundedRect(QRectF(-hw, gh, hw * 2, hh), hw * 0.3, hw * 0.3)

    # Wrap lines on handle
    wrap_pen = QPen(handle_hi, max(s * 0.025, 0.4))
    painter.setPen(wrap_pen)
    for wy in [0.25, 0.45, 0.65, 0.85]:
        y_pos = gh + hh * wy
        painter.drawLine(QPointF(-hw * 0.7, y_pos), QPointF(hw * 0.7, y_pos))

    # Pommel — small knob
    painter.setPen(pen)
    painter.setBrush(QBrush(pommel_c))
    pr = s * 0.06
    painter.drawEllipse(QPointF(0, gh + hh + pr * 0.4), pr, pr * 0.8)

    # Sparkle at crossguard (4-pointed star)
    if colored:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(sparkle_c))
        sp_x, sp_y = 0.0, -s * 0.02
        sp_r = s * 0.10
        painter.drawPolygon(QPolygonF([
            QPointF(sp_x, sp_y - sp_r),
            QPointF(sp_x + sp_r * 0.12, sp_y),
            QPointF(sp_x, sp_y + sp_r),
            QPointF(sp_x - sp_r * 0.12, sp_y),
        ]))
        painter.drawPolygon(QPolygonF([
            QPointF(sp_x - sp_r, sp_y),
            QPointF(sp_x, sp_y - sp_r * 0.12),
            QPointF(sp_x + sp_r, sp_y),
            QPointF(sp_x, sp_y + sp_r * 0.12),
        ]))

    painter.restore()


def draw_swords(painter: QPainter, x: float, y: float, size: float,
                strength: int) -> None:
    """Draw 3 tilted swords: first `strength` colored, rest light gray."""
    if strength <= 0:
        return
    s = size
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    spacing = s * 0.34
    total_w = spacing * 2
    start_x = x + (s - total_w) / 2
    sword_cy = y + s * 0.78
    for i in range(3):
        sx = start_x + i * spacing
        _draw_one_sword(painter, sx, sword_cy, s, colored=(i < strength),
                        angle=-20.0)

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

    # Triangle arrangement: 2 on bottom, 1 on top nestled in the groove
    lw = s * 0.58
    lh = s * 0.26
    sep = lh * 0.55  # horizontal separation between bottom logs
    bot_y = s * 0.54
    top_y = bot_y - lh * 0.72

    logs = [
        # Draw order: bottom-right (furthest back), bottom-left, top
        (s * 0.08 + sep, bot_y, QColor(150, 90, 35), QColor(185, 145, 85)),
        (s * 0.08, bot_y, QColor(140, 85, 30), QColor(180, 140, 80)),
        (s * 0.08 + sep / 2, top_y, QColor(160, 100, 40), QColor(195, 155, 90)),
    ]

    def _draw_log_body(lx, ly, bark_c):
        painter.setPen(pen)
        painter.setBrush(QBrush(bark_c))
        painter.drawRoundedRect(QRectF(lx, ly, lw, lh), lh * 0.45, lh * 0.45)
        # Dark grain lines on bark
        painter.setPen(QPen(bark_c.darker(130), max(s * 0.02, 0.5)))
        for g in [0.3, 0.5, 0.7]:
            painter.drawLine(
                QPointF(lx + lw * 0.08, ly + lh * g),
                QPointF(lx + lw * 0.7, ly + lh * g),
            )
        painter.setPen(pen)

    def _draw_log_end(lx, ly, end_c):
        er = lh * 0.45
        ecx = lx + lw - s * 0.01
        ecy = ly + lh / 2
        painter.setPen(pen)
        painter.setBrush(QBrush(end_c))
        painter.drawEllipse(QPointF(ecx, ecy), er, er)
        painter.setPen(QPen(end_c.darker(120), max(s * 0.02, 0.5)))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(ecx, ecy), er * 0.55, er * 0.55)
        painter.setPen(pen)

    # Draw back-to-front: bottom-left (furthest) → bottom-right → top
    for lx, ly, bark_c, end_c in logs:
        _draw_log_body(lx, ly, bark_c)
        _draw_log_end(lx, ly, end_c)

    painter.restore()


def _draw_ore(painter: QPainter, x: float, y: float, s: float) -> None:
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    # Cluster of angular ore rocks, like H3's lumpy grey stones
    # Back row (larger, darker)
    painter.setBrush(QBrush(QColor(105, 105, 110)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.10, s * 0.70), QPointF(s * 0.08, s * 0.45),
        QPointF(s * 0.22, s * 0.30), QPointF(s * 0.38, s * 0.42),
        QPointF(s * 0.40, s * 0.70),
    ]))
    painter.setBrush(QBrush(QColor(115, 115, 120)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.35, s * 0.72), QPointF(s * 0.40, s * 0.38),
        QPointF(s * 0.55, s * 0.25), QPointF(s * 0.68, s * 0.35),
        QPointF(s * 0.70, s * 0.72),
    ]))
    painter.setBrush(QBrush(QColor(100, 100, 105)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.58, s * 0.73), QPointF(s * 0.65, s * 0.40),
        QPointF(s * 0.78, s * 0.32), QPointF(s * 0.90, s * 0.50),
        QPointF(s * 0.88, s * 0.73),
    ]))

    # Front rocks (smaller, lighter — highlights)
    painter.setBrush(QBrush(QColor(145, 145, 150)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.18, s * 0.82), QPointF(s * 0.15, s * 0.60),
        QPointF(s * 0.30, s * 0.55), QPointF(s * 0.42, s * 0.65),
        QPointF(s * 0.38, s * 0.82),
    ]))
    painter.setBrush(QBrush(QColor(155, 155, 160)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.50, s * 0.82), QPointF(s * 0.52, s * 0.58),
        QPointF(s * 0.65, s * 0.52), QPointF(s * 0.78, s * 0.62),
        QPointF(s * 0.75, s * 0.82),
    ]))

    # Specular highlights
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(190, 190, 195, 100)))
    painter.drawEllipse(QPointF(s * 0.25, s * 0.40), s * 0.05, s * 0.03)
    painter.drawEllipse(QPointF(s * 0.56, s * 0.35), s * 0.04, s * 0.03)
    painter.drawEllipse(QPointF(s * 0.75, s * 0.42), s * 0.04, s * 0.02)

    painter.restore()


def _draw_mercury(painter: QPainter, x: float, y: float, s: float) -> None:
    """Cauldron/pot on a tripod stand, matching H3's mercury icon."""
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)
    cx = s / 2

    # Wood logs under the cauldron (crossed)
    wood_pen = QPen(_BLACK, max(s * 0.04, 0.6), Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap)
    painter.setPen(wood_pen)

    # Two crossed logs
    bark1 = QColor(150, 95, 35)
    bark2 = QColor(140, 85, 30)
    log_h = s * 0.10

    # Left-to-right log
    painter.setBrush(QBrush(bark1))
    painter.save()
    painter.translate(cx, s * 0.78)
    painter.rotate(-15)
    painter.drawRoundedRect(QRectF(-s * 0.35, -log_h / 2, s * 0.70, log_h),
                            log_h * 0.4, log_h * 0.4)
    painter.restore()

    # Right-to-left log (crossing)
    painter.setBrush(QBrush(bark2))
    painter.save()
    painter.translate(cx, s * 0.80)
    painter.rotate(15)
    painter.drawRoundedRect(QRectF(-s * 0.35, -log_h / 2, s * 0.70, log_h),
                            log_h * 0.4, log_h * 0.4)
    painter.restore()

    painter.setPen(pen)

    # Cauldron body (rounded pot shape)
    painter.setPen(pen)
    pot_c = QColor(95, 95, 100)
    painter.setBrush(QBrush(pot_c))
    pot = QPainterPath()
    pot.moveTo(cx - s * 0.28, s * 0.32)
    pot.quadTo(cx - s * 0.32, s * 0.55, cx - s * 0.18, s * 0.68)
    pot.quadTo(cx, s * 0.76, cx + s * 0.18, s * 0.68)
    pot.quadTo(cx + s * 0.32, s * 0.55, cx + s * 0.28, s * 0.32)
    pot.closeSubpath()
    painter.drawPath(pot)

    # Pot rim (thick ellipse at top)
    painter.setBrush(QBrush(QColor(120, 120, 125)))
    painter.drawEllipse(QPointF(cx, s * 0.32), s * 0.29, s * 0.08)
    # Inner rim darker
    painter.setBrush(QBrush(QColor(70, 70, 75)))
    painter.drawEllipse(QPointF(cx, s * 0.33), s * 0.22, s * 0.05)

    # Mercury liquid surface (silvery blue shimmer)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(170, 200, 215, 180)))
    painter.drawEllipse(QPointF(cx, s * 0.35), s * 0.18, s * 0.04)

    # Highlight on pot body
    painter.setBrush(QBrush(QColor(140, 140, 145, 80)))
    painter.drawEllipse(QPointF(cx - s * 0.10, s * 0.48), s * 0.08, s * 0.12)

    painter.restore()


def _draw_sulfur(painter: QPainter, x: float, y: float, s: float) -> None:
    """Sandy/golden pyramid mound, matching H3's sulfur icon."""
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)

    # Pyramid with just the very tip rounded
    mound = QPainterPath()
    mound.moveTo(s * 0.08, s * 0.82)
    mound.lineTo(s * 0.44, s * 0.26)
    mound.quadTo(s * 0.50, s * 0.20, s * 0.56, s * 0.26)
    mound.lineTo(s * 0.92, s * 0.82)
    mound.closeSubpath()

    left_face = QPainterPath()
    left_face.moveTo(s * 0.08, s * 0.82)
    left_face.lineTo(s * 0.44, s * 0.26)
    left_face.quadTo(s * 0.50, s * 0.20, s * 0.50, s * 0.23)
    left_face.lineTo(s * 0.50, s * 0.82)
    left_face.closeSubpath()

    # Fill the two faces without outline first
    painter.setPen(Qt.PenStyle.NoPen)

    # Right/darker face
    painter.setBrush(QBrush(QColor(215, 185, 95)))
    painter.drawPath(mound)

    # Left/lighter face (overdraws left half)
    painter.setBrush(QBrush(QColor(235, 210, 120)))
    painter.drawPath(left_face)

    # Highlight near peak
    painter.setBrush(QBrush(QColor(250, 235, 150, 160)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.38, s * 0.50),
        QPointF(s * 0.50, s * 0.24),
        QPointF(s * 0.50, s * 0.50),
    ]))

    # Subtle granular texture dots
    painter.setBrush(QBrush(QColor(195, 165, 70, 100)))
    for dx, dy in [(0.30, 0.65), (0.55, 0.70), (0.70, 0.75),
                   (0.40, 0.55), (0.62, 0.60)]:
        painter.drawEllipse(QPointF(s * dx, s * dy), s * 0.02, s * 0.02)

    # Outline on top — uniform thickness on all edges
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(mound)

    painter.restore()


def _draw_crystal(painter: QPainter, x: float, y: float, s: float) -> None:
    """Red crystal cluster with branching shards, matching H3's crystal icon."""
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    # Central tall shard
    painter.setBrush(QBrush(QColor(210, 55, 65)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.40, s * 0.82),
        QPointF(s * 0.42, s * 0.15),
        QPointF(s * 0.52, s * 0.12),
        QPointF(s * 0.58, s * 0.82),
    ]))

    # Left shard (angled out)
    painter.setBrush(QBrush(QColor(185, 40, 50)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.28, s * 0.82),
        QPointF(s * 0.18, s * 0.35),
        QPointF(s * 0.28, s * 0.30),
        QPointF(s * 0.42, s * 0.82),
    ]))

    # Right shard (angled out)
    painter.setBrush(QBrush(QColor(195, 45, 55)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.55, s * 0.82),
        QPointF(s * 0.72, s * 0.28),
        QPointF(s * 0.80, s * 0.32),
        QPointF(s * 0.72, s * 0.82),
    ]))

    # Small shard far left
    painter.setBrush(QBrush(QColor(175, 35, 45)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.15, s * 0.82),
        QPointF(s * 0.10, s * 0.52),
        QPointF(s * 0.18, s * 0.48),
        QPointF(s * 0.28, s * 0.82),
    ]))

    # Highlights (light streaks on shards)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(240, 140, 150, 140)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.44, s * 0.55),
        QPointF(s * 0.46, s * 0.18),
        QPointF(s * 0.49, s * 0.55),
    ]))
    painter.setBrush(QBrush(QColor(235, 120, 130, 120)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.73, s * 0.55),
        QPointF(s * 0.74, s * 0.32),
        QPointF(s * 0.76, s * 0.55),
    ]))

    # White specular highlight at top of main shard
    painter.setBrush(QBrush(QColor(255, 200, 200, 100)))
    painter.drawEllipse(QPointF(s * 0.48, s * 0.20), s * 0.03, s * 0.05)

    painter.restore()


def _draw_gems(painter: QPainter, x: float, y: float, s: float) -> None:
    """Scattered colorful gemstones, matching H3's gems icon."""
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)

    # Back row gems (partially occluded)
    # Purple gem (back left)
    painter.setPen(pen)
    painter.setBrush(QBrush(QColor(120, 40, 170)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.15, s * 0.42), QPointF(s * 0.22, s * 0.28),
        QPointF(s * 0.32, s * 0.30), QPointF(s * 0.35, s * 0.45),
        QPointF(s * 0.25, s * 0.55),
    ]))
    # Green gem (back center)
    painter.setBrush(QBrush(QColor(45, 165, 50)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.38, s * 0.38), QPointF(s * 0.48, s * 0.22),
        QPointF(s * 0.60, s * 0.25), QPointF(s * 0.62, s * 0.42),
        QPointF(s * 0.50, s * 0.50),
    ]))

    # Front row gems (on top)
    # Large red gem (front center)
    painter.setBrush(QBrush(QColor(210, 35, 40)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.32, s * 0.58), QPointF(s * 0.42, s * 0.40),
        QPointF(s * 0.55, s * 0.38), QPointF(s * 0.62, s * 0.55),
        QPointF(s * 0.52, s * 0.72), QPointF(s * 0.38, s * 0.72),
    ]))
    # Blue gem (front right)
    painter.setBrush(QBrush(QColor(50, 85, 210)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.60, s * 0.55), QPointF(s * 0.70, s * 0.38),
        QPointF(s * 0.82, s * 0.42), QPointF(s * 0.85, s * 0.58),
        QPointF(s * 0.75, s * 0.70),
    ]))
    # Small yellow gem (front left)
    painter.setBrush(QBrush(QColor(220, 200, 40)))
    painter.drawPolygon(QPolygonF([
        QPointF(s * 0.12, s * 0.62), QPointF(s * 0.18, s * 0.50),
        QPointF(s * 0.28, s * 0.52), QPointF(s * 0.30, s * 0.65),
        QPointF(s * 0.20, s * 0.72),
    ]))

    # Specular highlights
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255, 90)))
    painter.drawEllipse(QPointF(s * 0.46, s * 0.46), s * 0.04, s * 0.03)
    painter.drawEllipse(QPointF(s * 0.73, s * 0.44), s * 0.03, s * 0.02)
    painter.drawEllipse(QPointF(s * 0.50, s * 0.28), s * 0.03, s * 0.02)

    painter.restore()


def _draw_gold(painter: QPainter, x: float, y: float, s: float) -> None:
    """Mound of gold nuggets with sparkle, matching H3's gold icon."""
    painter.save()
    painter.translate(x, y)
    pen = _pen(s)
    painter.setPen(pen)

    # Back row nuggets (darker, partially hidden)
    nuggets_back = [
        (s * 0.18, s * 0.52, s * 0.14, s * 0.11, QColor(160, 130, 30)),
        (s * 0.40, s * 0.48, s * 0.15, s * 0.12, QColor(170, 135, 35)),
        (s * 0.62, s * 0.50, s * 0.14, s * 0.11, QColor(155, 125, 28)),
    ]
    for nx, ny, nw, nh, nc in nuggets_back:
        painter.setBrush(QBrush(nc))
        painter.drawEllipse(QRectF(nx, ny, nw, nh))

    # Front row nuggets (lighter, larger)
    nuggets_front = [
        (s * 0.10, s * 0.60, s * 0.18, s * 0.15, QColor(200, 165, 45)),
        (s * 0.28, s * 0.62, s * 0.20, s * 0.16, QColor(215, 180, 55)),
        (s * 0.50, s * 0.60, s * 0.19, s * 0.15, QColor(210, 175, 50)),
        (s * 0.68, s * 0.62, s * 0.16, s * 0.14, QColor(195, 160, 42)),
    ]
    for nx, ny, nw, nh, nc in nuggets_front:
        painter.setBrush(QBrush(nc))
        painter.drawEllipse(QRectF(nx, ny, nw, nh))

    # Top nuggets (brightest)
    nuggets_top = [
        (s * 0.25, s * 0.52, s * 0.16, s * 0.13, QColor(225, 195, 65)),
        (s * 0.45, s * 0.50, s * 0.17, s * 0.14, QColor(230, 200, 70)),
    ]
    for nx, ny, nw, nh, nc in nuggets_top:
        painter.setBrush(QBrush(nc))
        painter.drawEllipse(QRectF(nx, ny, nw, nh))

    # Sparkle / shine effect (4-pointed star)
    painter.setPen(Qt.PenStyle.NoPen)
    sparkle_c = QColor(255, 255, 240, 220)
    sx, sy = s * 0.38, s * 0.38
    sr = s * 0.14  # sparkle radius

    # Vertical spike
    painter.setBrush(QBrush(sparkle_c))
    painter.drawPolygon(QPolygonF([
        QPointF(sx, sy - sr),
        QPointF(sx + sr * 0.12, sy),
        QPointF(sx, sy + sr),
        QPointF(sx - sr * 0.12, sy),
    ]))
    # Horizontal spike
    painter.drawPolygon(QPolygonF([
        QPointF(sx - sr, sy),
        QPointF(sx, sy - sr * 0.12),
        QPointF(sx + sr, sy),
        QPointF(sx, sy + sr * 0.12),
    ]))

    # Small secondary sparkle
    sx2, sy2 = s * 0.65, s * 0.45
    sr2 = s * 0.08
    painter.drawPolygon(QPolygonF([
        QPointF(sx2, sy2 - sr2),
        QPointF(sx2 + sr2 * 0.15, sy2),
        QPointF(sx2, sy2 + sr2),
        QPointF(sx2 - sr2 * 0.15, sy2),
    ]))
    painter.drawPolygon(QPolygonF([
        QPointF(sx2 - sr2, sy2),
        QPointF(sx2, sy2 - sr2 * 0.15),
        QPointF(sx2 + sr2, sy2),
        QPointF(sx2, sy2 + sr2 * 0.15),
    ]))

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
