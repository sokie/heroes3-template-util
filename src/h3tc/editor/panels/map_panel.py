"""Map settings panel for name and size."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from h3tc.editor.panels.binding import bind_spinbox, disconnect_all
from h3tc.models import TemplateMap


def _make_spinbox(minimum: int = 0, maximum: int = 999) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setFixedWidth(80)
    return spin


class MapPanel(QWidget):
    """Map-level settings: name, min/max size."""

    map_changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._template_map: TemplateMap | None = None
        self._widgets: list = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Map Settings")
        title.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        layout.addWidget(title)

        grp = QGroupBox("Map")
        g = QGridLayout(grp)

        g.addWidget(QLabel("Name"), 0, 0)
        self._name = QLineEdit()
        g.addWidget(self._name, 0, 1, 1, 3)

        g.addWidget(QLabel("Size"), 1, 0)
        self._min_size = _make_spinbox(36, 252)
        g.addWidget(self._min_size, 1, 1)
        g.addWidget(QLabel("to"), 1, 2)
        self._max_size = _make_spinbox(36, 252)
        g.addWidget(self._max_size, 1, 3)

        layout.addWidget(grp)

        # Info labels
        info = QGroupBox("Info")
        il = QGridLayout(info)
        self._zone_count = QLabel("Zones: 0")
        self._conn_count = QLabel("Connections: 0")
        il.addWidget(self._zone_count, 0, 0)
        il.addWidget(self._conn_count, 0, 1)
        layout.addWidget(info)

        layout.addStretch()

    def set_map(self, template_map: TemplateMap) -> None:
        """Populate the panel from a template map."""
        self._disconnect_all()
        self._template_map = template_map

        self._name.blockSignals(True)
        self._name.setText(template_map.name)
        self._name.blockSignals(False)
        self._name.textChanged.connect(self._on_name_changed)
        self._widgets.append(self._name)

        bind_spinbox(self._min_size, template_map, "min_size", on_change=self._on_change)
        self._widgets.append(self._min_size)
        bind_spinbox(self._max_size, template_map, "max_size", on_change=self._on_change)
        self._widgets.append(self._max_size)

        self._zone_count.setText(f"Zones: {len(template_map.zones)}")
        self._conn_count.setText(f"Connections: {len(template_map.connections)}")

    def _on_name_changed(self, text: str) -> None:
        if self._template_map:
            self._template_map.name = text
            self._on_change()

    def _on_change(self) -> None:
        self.map_changed.emit()

    def _disconnect_all(self) -> None:
        for w in self._widgets:
            disconnect_all(w)
            if isinstance(w, QLineEdit):
                try:
                    w.textChanged.disconnect()
                except RuntimeError:
                    pass
        self._widgets.clear()
