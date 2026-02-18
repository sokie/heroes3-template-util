"""Connection property panel matching the HOTA editor layout (SOD fields only)."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from h3tc.editor.panels.binding import bind_checkbox, bind_spinbox, disconnect_all
from h3tc.models import Connection


def _make_spinbox(minimum: int = 0, maximum: int = 99999) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setFixedWidth(80)
    return spin


class ConnectionPanel(QWidget):
    """Connection settings panel for SOD connections."""

    connection_changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._connection: Connection | None = None
        self._widgets: list = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel("Connection Settings")
        self._title.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        layout.addWidget(self._title)

        # Main properties
        pg = QGroupBox("Properties")
        pl = QGridLayout(pg)

        pl.addWidget(QLabel("Zone 1"), 0, 0)
        self._zone1 = _make_spinbox(1, 999)
        pl.addWidget(self._zone1, 0, 1)

        pl.addWidget(QLabel("Zone 2"), 1, 0)
        self._zone2 = _make_spinbox(1, 999)
        pl.addWidget(self._zone2, 1, 1)

        pl.addWidget(QLabel("Value"), 2, 0)
        self._value = _make_spinbox(0, 999999)
        pl.addWidget(self._value, 2, 1)

        self._wide = QCheckBox("Wide")
        pl.addWidget(self._wide, 3, 0, 1, 2)

        self._border_guard = QCheckBox("Border Guard")
        pl.addWidget(self._border_guard, 4, 0, 1, 2)

        layout.addWidget(pg)

        # Position requirements
        rg = QGroupBox("Connection occurrence requirements")
        rl = QGridLayout(rg)

        rl.addWidget(QLabel("Human Positions"), 0, 0)
        self._pos_min_human = _make_spinbox()
        self._pos_max_human = _make_spinbox()
        rl.addWidget(self._pos_min_human, 0, 1)
        rl.addWidget(QLabel("to"), 0, 2)
        rl.addWidget(self._pos_max_human, 0, 3)

        rl.addWidget(QLabel("Total Positions"), 1, 0)
        self._pos_min_total = _make_spinbox()
        self._pos_max_total = _make_spinbox()
        rl.addWidget(self._pos_min_total, 1, 1)
        rl.addWidget(QLabel("to"), 1, 2)
        rl.addWidget(self._pos_max_total, 1, 3)

        layout.addWidget(rg)
        layout.addStretch()

    def set_connection(self, connection: Connection) -> None:
        """Populate the panel from a connection model."""
        self._disconnect_all()
        self._connection = connection

        z1 = connection.zone1.strip()
        z2 = connection.zone2.strip()
        self._title.setText(f"Connection Settings - {z1} ↔ {z2}")

        self._bind_spin(self._zone1, connection, "zone1")
        self._bind_spin(self._zone2, connection, "zone2")
        self._bind_spin(self._value, connection, "value")
        self._bind_check(self._wide, connection, "wide")
        self._bind_check(self._border_guard, connection, "border_guard")

        self._bind_spin(self._pos_min_human, connection, "min_human", sub_obj="positions")
        self._bind_spin(self._pos_max_human, connection, "max_human", sub_obj="positions")
        self._bind_spin(self._pos_min_total, connection, "min_total", sub_obj="positions")
        self._bind_spin(self._pos_max_total, connection, "max_total", sub_obj="positions")

    def _on_change(self) -> None:
        self.connection_changed.emit()

    def _disconnect_all(self) -> None:
        for w in self._widgets:
            disconnect_all(w)
        self._widgets.clear()

    def _bind_spin(self, spin, obj, field, **kwargs) -> None:
        bind_spinbox(spin, obj, field, on_change=self._on_change, **kwargs)
        self._widgets.append(spin)

    def _bind_check(self, cb, obj, field, **kwargs) -> None:
        bind_checkbox(cb, obj, field, on_change=self._on_change, **kwargs)
        self._widgets.append(cb)
