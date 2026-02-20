"""Visual representation of a connection between zones."""

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from h3tc.editor.constants import (
    CONNECTION_COLOR,
    CONNECTION_LABEL_FONT_SIZE,
    CONNECTION_SELECTED_COLOR,
    CONNECTION_WIDE_WIDTH,
    CONNECTION_WIDTH,
)
from h3tc.models import Connection


def _intersect_rect_line(rect: QRectF, p1: QPointF, p2: QPointF) -> QPointF:
    """Find intersection of line p1->p2 with rect edges. p1 should be inside rect."""
    center = rect.center()
    dx = p2.x() - center.x()
    dy = p2.y() - center.y()

    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return center

    # Check each edge
    candidates = []
    hw = rect.width() / 2
    hh = rect.height() / 2

    # Right edge
    if dx > 0:
        t = hw / dx
        y = dy * t
        if abs(y) <= hh:
            candidates.append(QPointF(center.x() + hw, center.y() + y))
    # Left edge
    if dx < 0:
        t = -hw / dx
        y = dy * t
        if abs(y) <= hh:
            candidates.append(QPointF(center.x() - hw, center.y() + y))
    # Bottom edge
    if dy > 0:
        t = hh / dy
        x = dx * t
        if abs(x) <= hw:
            candidates.append(QPointF(center.x() + x, center.y() + hh))
    # Top edge
    if dy < 0:
        t = -hh / dy
        x = dx * t
        if abs(x) <= hw:
            candidates.append(QPointF(center.x() + x, center.y() - hh))

    if candidates:
        # Return closest to p2
        return min(candidates, key=lambda c: QLineF(c, p2).length())
    return center


class ConnectionItem(QGraphicsPathItem):
    """A line connecting two zone items with a value label."""

    def __init__(self, connection: Connection, zone1_item, zone2_item) -> None:
        super().__init__()
        self.connection = connection
        self.zone1_item = zone1_item
        self.zone2_item = zone2_item

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(0)  # Below zones
        self._update_path()

    @property
    def _is_wide(self) -> bool:
        return self.connection.wide.strip().lower() == "x"

    @property
    def _line_width(self) -> float:
        return CONNECTION_WIDE_WIDTH if self._is_wide else CONNECTION_WIDTH

    @property
    def _label(self) -> str:
        val = self.connection.value.strip()
        if not val or val == "0":
            return ""
        # Show abbreviated guard value (e.g., 45000 -> "45k")
        try:
            n = int(val)
            if n >= 1000:
                return f"{n // 1000}k"
            return val
        except ValueError:
            return val

    def _update_path(self) -> None:
        """Recalculate line path based on zone positions."""
        from PySide6.QtGui import QPainterPath

        r1 = self.zone1_item.mapToScene(self.zone1_item.rect()).boundingRect()
        r2 = self.zone2_item.mapToScene(self.zone2_item.rect()).boundingRect()

        c1 = r1.center()
        c2 = r2.center()

        p1 = _intersect_rect_line(r1, c1, c2)
        p2 = _intersect_rect_line(r2, c2, c1)

        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        self.setPath(path)

        self._p1 = p1
        self._p2 = p2
        self._midpoint = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)

    def refresh_path(self) -> None:
        """Refresh the path when connected zones move."""
        self._update_path()
        self.update()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = CONNECTION_SELECTED_COLOR if self.isSelected() else CONNECTION_COLOR
        pen = QPen(color, self._line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        label = self._label
        if label:
            # Measure label to create gap in line
            font = QFont("Helvetica Neue", CONNECTION_LABEL_FONT_SIZE, QFont.Weight.Bold)
            font.setStyleHint(QFont.StyleHint.SansSerif)
            painter.setFont(font)
            fm = painter.fontMetrics()
            text_rect = fm.boundingRect(label)
            label_w = text_rect.width() + 20
            label_h = text_rect.height() + 10

            # Find the point along the line at half distance, then offset
            line = QLineF(self._p1, self._p2)
            total_len = line.length()
            if total_len > label_w + 20:
                # Gap in line: draw two segments
                half = total_len / 2
                gap_half = label_w / 2 + 4

                t1 = (half - gap_half) / total_len
                t2 = (half + gap_half) / total_len
                gap_p1 = QPointF(
                    self._p1.x() + (self._p2.x() - self._p1.x()) * t1,
                    self._p1.y() + (self._p2.y() - self._p1.y()) * t1,
                )
                gap_p2 = QPointF(
                    self._p1.x() + (self._p2.x() - self._p1.x()) * t2,
                    self._p1.y() + (self._p2.y() - self._p1.y()) * t2,
                )

                painter.setPen(pen)
                painter.drawLine(self._p1, gap_p1)
                painter.drawLine(gap_p2, self._p2)
            else:
                # Line too short for gap, just draw it
                painter.setPen(pen)
                painter.drawLine(self._p1, self._p2)

            # Draw label at midpoint with white pill background
            bg_rect = QRectF(
                self._midpoint.x() - label_w / 2,
                self._midpoint.y() - label_h / 2,
                label_w,
                label_h,
            )
            # White translucent rounded-rect pill
            painter.setPen(QPen(color, 1))
            painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
            painter.drawRoundedRect(bg_rect, label_h / 2, label_h / 2)
            # Red label text
            painter.setPen(QPen(QColor(200, 40, 40)))
            painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, label)
        else:
            # No label, draw full line
            painter.setPen(pen)
            painter.drawLine(self._p1, self._p2)

        # Wide indicator
        if self._is_wide:
            pen = QPen(color, 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            line = QLineF(self._p1, self._p2)
            normal = line.normalVector()
            normal.setLength(5)
            offset = QPointF(normal.dx(), normal.dy())
            painter.drawLine(
                QLineF(self._p1 + offset, self._p2 + offset)
            )
            painter.drawLine(
                QLineF(self._p1 - offset, self._p2 - offset)
            )

    def boundingRect(self) -> QRectF:
        extra = max(self._line_width, 20)  # Extra for label
        return self.path().boundingRect().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        """Make the clickable area wider than the visible line."""
        from PySide6.QtGui import QPainterPathStroker

        stroker = QPainterPathStroker()
        stroker.setWidth(max(self._line_width + 8, 12))
        return stroker.createStroke(self.path())
