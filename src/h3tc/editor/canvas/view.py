"""Zoomable, pannable graphics view with grid background."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QWheelEvent, QMouseEvent
from PySide6.QtWidgets import QGraphicsView

from h3tc.editor.constants import (
    GRID_COLOR,
    GRID_MAJOR_COLOR,
    GRID_MAJOR_EVERY,
    GRID_SIZE,
    MAX_ZOOM,
    MIN_ZOOM,
    ZOOM_FACTOR,
)


class TemplateView(QGraphicsView):
    """Graphics view with zoom (Ctrl+scroll), pan (middle-drag), and grid."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._zoom = 1.0
        self._panning = False
        self._pan_start = None

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setBackgroundBrush(QColor(245, 245, 245))
        self.setMinimumSize(400, 300)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)

        left = int(rect.left()) - (int(rect.left()) % GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % GRID_SIZE)

        # Minor grid lines
        painter.setPen(QPen(GRID_COLOR, 0.5))
        x = left
        while x <= rect.right():
            if (x // GRID_SIZE) % GRID_MAJOR_EVERY != 0:
                painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += GRID_SIZE

        y = top
        while y <= rect.bottom():
            if (y // GRID_SIZE) % GRID_MAJOR_EVERY != 0:
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += GRID_SIZE

        # Major grid lines
        painter.setPen(QPen(GRID_MAJOR_COLOR, 0.8))
        x = left
        while x <= rect.right():
            if (x // GRID_SIZE) % GRID_MAJOR_EVERY == 0:
                painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += GRID_SIZE

        y = top
        while y <= rect.bottom():
            if (y // GRID_SIZE) % GRID_MAJOR_EVERY == 0:
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += GRID_SIZE

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                factor = ZOOM_FACTOR
            else:
                factor = 1.0 / ZOOM_FACTOR

            new_zoom = self._zoom * factor
            if MIN_ZOOM <= new_zoom <= MAX_ZOOM:
                self._zoom = new_zoom
                self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._panning and self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - delta.x())
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - delta.y())
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def zoom_to_fit(self) -> None:
        """Zoom to fit all items in the view."""
        scene = self.scene()
        if scene and scene.items():
            self.fitInView(scene.itemsBoundingRect().adjusted(-50, -50, 50, 50),
                           Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = self.transform().m11()

    @property
    def zoom_level(self) -> float:
        return self._zoom
