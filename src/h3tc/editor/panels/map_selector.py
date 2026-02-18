"""Dropdown to select the active map in a multi-map template pack."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget

from h3tc.models import TemplatePack


class MapSelector(QWidget):
    """Combo box for switching between maps in a pack."""

    map_selected = Signal(int)  # emits map index

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        layout.addWidget(QLabel("Map:"))
        self._combo = QComboBox()
        self._combo.setMinimumWidth(200)
        layout.addWidget(self._combo, 1)

        self._combo.currentIndexChanged.connect(self.map_selected.emit)

    def set_pack(self, pack: TemplatePack) -> None:
        """Populate from a template pack."""
        self._combo.blockSignals(True)
        self._combo.clear()
        for i, m in enumerate(pack.maps):
            label = m.name if m.name else f"Map {i + 1}"
            self._combo.addItem(label)
        self._combo.blockSignals(False)

        if pack.maps:
            self._combo.setCurrentIndex(0)

    @property
    def current_index(self) -> int:
        return self._combo.currentIndex()

    def set_visible_if_multi(self, pack: TemplatePack) -> None:
        """Only show the selector if there are multiple maps."""
        self.setVisible(len(pack.maps) > 1)
