"""Map settings panel for name and size."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from h3tc.editor.panels.binding import disconnect_all
from h3tc.models import TemplateMap

# Map size options: (id_str, display_label)
# Ordered by ID value, matching HOTA editor dropdown.
MAP_SIZES: list[tuple[str, str]] = [
    ("1", "36x36 (S) without underground"),
    ("2", "36x36 (S) with underground"),
    ("4", "72x72 (M) without underground"),
    ("8", "72x72 (M) with underground"),
    ("9", "108x108 (L) without underground"),
    ("16", "144x144 (XL) without underground"),
    ("18", "108x108 (L) with underground"),
    ("25", "180x180 (H) without underground"),
    ("32", "144x144 (XL) with underground"),
    ("36", "216x216 (XH) without underground"),
    ("49", "252x252 (G) without underground"),
    ("50", "180x180 (H) with underground"),
    ("72", "216x216 (XH) with underground"),
    ("99", "252x252 (G) with underground"),
]

_SIZE_IDS = [s[0] for s in MAP_SIZES]


def _make_size_combo() -> QComboBox:
    combo = QComboBox()
    for id_str, label in MAP_SIZES:
        combo.addItem(f"{id_str} — {label}", userData=id_str)
    combo.setMinimumWidth(240)
    return combo


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
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c2c2c; padding: 6px 4px;")
        layout.addWidget(title)

        grp = QGroupBox("Map")
        g = QGridLayout(grp)

        g.addWidget(QLabel("Name"), 0, 0)
        self._name = QLineEdit()
        g.addWidget(self._name, 0, 1)

        g.addWidget(QLabel("Minimal Size"), 1, 0)
        self._min_size = _make_size_combo()
        g.addWidget(self._min_size, 1, 1)

        g.addWidget(QLabel("Maximal Size"), 2, 0)
        self._max_size = _make_size_combo()
        g.addWidget(self._max_size, 2, 1)

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

        # Set min size combo
        self._min_size.blockSignals(True)
        min_idx = self._index_for_size(template_map.min_size)
        self._min_size.setCurrentIndex(min_idx)
        self._min_size.blockSignals(False)
        self._min_size.currentIndexChanged.connect(self._on_min_size_changed)
        self._widgets.append(self._min_size)

        # Set max size combo
        self._max_size.blockSignals(True)
        max_idx = self._index_for_size(template_map.max_size)
        self._max_size.setCurrentIndex(max_idx)
        self._max_size.blockSignals(False)
        self._max_size.currentIndexChanged.connect(self._on_max_size_changed)
        self._widgets.append(self._max_size)

        self._zone_count.setText(f"Zones: {len(template_map.zones)}")
        self._conn_count.setText(f"Connections: {len(template_map.connections)}")

    def _index_for_size(self, size_str: str) -> int:
        """Find combo index for a size ID string."""
        val = size_str.strip()
        try:
            return _SIZE_IDS.index(val)
        except ValueError:
            return 0

    def _on_min_size_changed(self, index: int) -> None:
        if not self._template_map:
            return
        min_id = self._min_size.currentData()
        self._template_map.min_size = min_id

        # Enforce min <= max
        max_idx = self._max_size.currentIndex()
        if max_idx < index:
            self._max_size.blockSignals(True)
            self._max_size.setCurrentIndex(index)
            self._max_size.blockSignals(False)
            self._template_map.max_size = min_id

        self._on_change()

    def _on_max_size_changed(self, index: int) -> None:
        if not self._template_map:
            return
        max_id = self._max_size.currentData()
        self._template_map.max_size = max_id

        # Enforce min <= max
        min_idx = self._min_size.currentIndex()
        if min_idx > index:
            self._min_size.blockSignals(True)
            self._min_size.setCurrentIndex(index)
            self._min_size.blockSignals(False)
            self._template_map.min_size = max_id

        self._on_change()

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
