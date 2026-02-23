"""Theme settings dialog with color pickers and preset selector."""

import dataclasses

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from h3tc.editor.constants import (
    Theme,
    ThemeManager,
    THEME_HIGH_CONTRAST,
    THEME_LIGHT,
)
from h3tc.editor.models.theme_store import save_themes


# ── ColorButton helper ──────────────────────────────────────────────────


class ColorButton(QPushButton):
    """A button that shows its color and opens a QColorDialog on click."""

    color_changed = Signal(tuple)

    def __init__(self, color: tuple[int, ...], *, alpha: bool = False, parent=None):
        super().__init__(parent)
        self._color = color
        self._alpha = alpha
        self.setFixedSize(48, 28)
        self._update_style()
        self.clicked.connect(self._pick_color)

    @property
    def color(self) -> tuple[int, ...]:
        return self._color

    @color.setter
    def color(self, value: tuple[int, ...]) -> None:
        if self._color != value:
            self._color = value
            self._update_style()
            self.color_changed.emit(self._color)

    def set_color_silent(self, value: tuple[int, ...]) -> None:
        """Set color without emitting signal."""
        self._color = value
        self._update_style()

    def _update_style(self) -> None:
        c = self._color
        if len(c) == 4:
            bg = f"rgba({c[0]},{c[1]},{c[2]},{c[3]})"
        else:
            bg = f"rgb({c[0]},{c[1]},{c[2]})"
        self.setStyleSheet(
            f"background-color: {bg}; border: 1px solid #888; border-radius: 3px;"
        )

    def _pick_color(self) -> None:
        initial = QColor(*self._color)
        opts = QColorDialog.ColorDialogOption(0)
        if self._alpha:
            opts = QColorDialog.ColorDialogOption.ShowAlphaChannel
        chosen = QColorDialog.getColor(initial, self, "Pick Color", opts)
        if chosen.isValid():
            if self._alpha:
                self.color = (chosen.red(), chosen.green(), chosen.blue(), chosen.alpha())
            else:
                self.color = (chosen.red(), chosen.green(), chosen.blue())


# ── Player color labels ─────────────────────────────────────────────────

_PLAYER_LABELS = {
    "0": "Unowned",
    "1": "Player 1",
    "2": "Player 2",
    "3": "Player 3",
    "4": "Player 4",
    "5": "Player 5",
    "6": "Player 6",
    "7": "Player 7",
    "8": "Player 8",
}

_PRESET_NAMES = ["Default", "High Contrast", "Custom"]

_HARDCODED_PRESETS: dict[str, Theme] = {
    "Default": THEME_LIGHT,
    "High Contrast": THEME_HIGH_CONTRAST,
}


# ── ThemeDialog ─────────────────────────────────────────────────────────


class ThemeDialog(QDialog):
    """Settings dialog for customizing the editor theme."""

    def __init__(self, themes: dict[str, Theme], active: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Theme Settings")
        self.setMinimumWidth(480)

        self._original_theme = dataclasses.replace(ThemeManager().theme)
        # Working copy of all 3 presets
        self._themes = {name: dataclasses.replace(t) for name, t in themes.items()}
        self._active = active

        self._build_ui()

        # Set initial combo selection and load widgets BEFORE connecting signals,
        # so _on_preset_changed doesn't snapshot uninitialized widget values.
        idx = _PRESET_NAMES.index(active) if active in _PRESET_NAMES else 0
        self._preset_combo.setCurrentIndex(idx)
        self._load_from_theme(self._themes[_PRESET_NAMES[idx]])
        self._update_revert_button()

        self._connect_signals()

    # ── Build UI ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Preset selector + Revert button
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self._preset_combo = QComboBox()
        for name in _PRESET_NAMES:
            self._preset_combo.addItem(name)
        preset_row.addWidget(self._preset_combo, 1)

        self._btn_revert = QPushButton("Revert to Defaults")
        preset_row.addWidget(self._btn_revert)
        layout.addLayout(preset_row)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_canvas_tab(), "Canvas")
        self._tabs.addTab(self._build_zones_tab(), "Zones")
        self._tabs.addTab(self._build_text_tab(), "Text")
        self._tabs.addTab(self._build_connections_tab(), "Connections")
        layout.addWidget(self._tabs)

        # Buttons
        self._buttons = QDialogButtonBox()
        self._btn_apply = self._buttons.addButton(QDialogButtonBox.StandardButton.Apply)
        self._btn_ok = self._buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self._btn_cancel = self._buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self._buttons)

    def _build_canvas_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        self._canvas_bg = ColorButton((238, 238, 240))
        form.addRow("Background:", self._canvas_bg)

        self._grid_color = ColorButton((215, 215, 215))
        form.addRow("Grid color:", self._grid_color)

        self._grid_minor_width = QDoubleSpinBox()
        self._grid_minor_width.setRange(0.1, 5.0)
        self._grid_minor_width.setSingleStep(0.1)
        form.addRow("Grid minor width:", self._grid_minor_width)

        self._grid_major_color = ColorButton((185, 185, 185))
        form.addRow("Grid major color:", self._grid_major_color)

        self._grid_major_width = QDoubleSpinBox()
        self._grid_major_width.setRange(0.1, 5.0)
        self._grid_major_width.setSingleStep(0.1)
        form.addRow("Grid major width:", self._grid_major_width)

        return w

    def _build_zones_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # Player colors grid
        group = QGroupBox("Player Colors")
        grid = QGridLayout(group)
        self._player_btns: dict[str, ColorButton] = {}
        for i, (pid, label) in enumerate(_PLAYER_LABELS.items()):
            row, col = divmod(i, 3)
            grid.addWidget(QLabel(label), row, col * 2)
            btn = ColorButton((180, 180, 180))
            self._player_btns[pid] = btn
            grid.addWidget(btn, row, col * 2 + 1)
        layout.addWidget(group)

        # Treasure colors
        group2 = QGroupBox("Treasure Colors")
        form2 = QFormLayout(group2)
        self._treasure_high = ColorButton((215, 195, 140))
        form2.addRow("High:", self._treasure_high)
        self._treasure_mid = ColorButton((190, 195, 205))
        form2.addRow("Mid:", self._treasure_mid)
        self._treasure_low = ColorButton((218, 218, 218))
        form2.addRow("Low:", self._treasure_low)
        layout.addWidget(group2)

        # Zone rendering
        group3 = QGroupBox("Zone Rendering")
        form3 = QFormLayout(group3)

        self._zone_border_width = QSpinBox()
        self._zone_border_width.setRange(1, 10)
        form3.addRow("Border width:", self._zone_border_width)

        self._zone_selected_border_width = QSpinBox()
        self._zone_selected_border_width.setRange(1, 10)
        form3.addRow("Selected border width:", self._zone_selected_border_width)

        self._zone_border_darken = QSpinBox()
        self._zone_border_darken.setRange(50, 255)
        form3.addRow("Border darken:", self._zone_border_darken)

        self._zone_corner_radius = QSpinBox()
        self._zone_corner_radius.setRange(0, 30)
        form3.addRow("Corner radius:", self._zone_corner_radius)

        layout.addWidget(group3)
        layout.addStretch()

        return w

    def _build_text_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        self._font_treasure = QSpinBox()
        self._font_treasure.setRange(8, 72)
        form.addRow("Treasure font size:", self._font_treasure)

        self._font_zone_id = QSpinBox()
        self._font_zone_id.setRange(8, 72)
        form.addRow("Zone ID font size:", self._font_zone_id)

        self._font_label = QSpinBox()
        self._font_label.setRange(8, 72)
        form.addRow("Label font size:", self._font_label)

        self._font_count = QSpinBox()
        self._font_count.setRange(8, 72)
        form.addRow("Count font size:", self._font_count)

        self._font_connection_label = QSpinBox()
        self._font_connection_label.setRange(8, 72)
        form.addRow("Connection label font size:", self._font_connection_label)

        self._text_shadow = QCheckBox("Enable text shadow")
        form.addRow("", self._text_shadow)

        return w

    def _build_connections_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        self._conn_label_color = ColorButton((200, 40, 40))
        form.addRow("Label color:", self._conn_label_color)

        self._conn_pill_bg = ColorButton((255, 255, 255, 220), alpha=True)
        form.addRow("Pill background:", self._conn_pill_bg)

        # Border: checkbox + color button
        border_row = QHBoxLayout()
        self._conn_border_enabled = QCheckBox("Border")
        border_row.addWidget(self._conn_border_enabled)
        self._conn_border_color = ColorButton((100, 100, 100))
        self._conn_border_color.setEnabled(False)
        border_row.addWidget(self._conn_border_color)
        border_row.addStretch()
        form.addRow("Label border:", border_row)

        self._conn_border_width = QDoubleSpinBox()
        self._conn_border_width.setRange(0.1, 5.0)
        self._conn_border_width.setSingleStep(0.1)
        form.addRow("Label border width:", self._conn_border_width)

        self._icon_outline_color = ColorButton((30, 30, 30))
        form.addRow("Icon outline:", self._icon_outline_color)

        return w

    # ── Signals ───────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        self._conn_border_enabled.toggled.connect(self._conn_border_color.setEnabled)
        self._btn_revert.clicked.connect(self._on_revert_defaults)
        self._btn_apply.clicked.connect(self._on_apply)
        self._btn_ok.clicked.connect(self._on_ok)
        self._btn_cancel.clicked.connect(self._on_cancel)

    def _on_preset_changed(self, index: int) -> None:
        # Snapshot current widgets into the previous preset
        prev_name = self._active
        self._themes[prev_name] = self._build_theme(prev_name)

        # Switch to new preset
        self._active = _PRESET_NAMES[index]
        self._load_from_theme(self._themes[self._active])
        self._update_revert_button()

    def _update_revert_button(self) -> None:
        """Enable Revert only for Default and High Contrast."""
        self._btn_revert.setEnabled(self._active in _HARDCODED_PRESETS)

    def _on_revert_defaults(self) -> None:
        """Reset the current preset to its hardcoded values."""
        if self._active not in _HARDCODED_PRESETS:
            return
        hardcoded = dataclasses.replace(_HARDCODED_PRESETS[self._active])
        self._themes[self._active] = hardcoded
        self._load_from_theme(hardcoded)

    # ── Theme <-> Widget mapping ─────────────────────────────────────

    def _load_from_theme(self, theme: Theme) -> None:
        """Populate all widgets from a Theme instance."""
        self._canvas_bg.set_color_silent(theme.canvas_bg)
        self._grid_color.set_color_silent(theme.grid_color)
        self._grid_minor_width.setValue(theme.grid_minor_width)
        self._grid_major_color.set_color_silent(theme.grid_major_color)
        self._grid_major_width.setValue(theme.grid_major_width)

        for pid, btn in self._player_btns.items():
            if pid in theme.zone_player_colors:
                btn.set_color_silent(theme.zone_player_colors[pid])

        self._treasure_high.set_color_silent(theme.zone_treasure_high)
        self._treasure_mid.set_color_silent(theme.zone_treasure_mid)
        self._treasure_low.set_color_silent(theme.zone_treasure_low)

        self._zone_border_width.setValue(theme.zone_border_width)
        self._zone_selected_border_width.setValue(theme.zone_selected_border_width)
        self._zone_border_darken.setValue(theme.zone_border_darken)
        self._zone_corner_radius.setValue(theme.zone_corner_radius)

        self._font_treasure.setValue(theme.font_treasure)
        self._font_zone_id.setValue(theme.font_zone_id)
        self._font_label.setValue(theme.font_label)
        self._font_count.setValue(theme.font_count)
        self._font_connection_label.setValue(theme.font_connection_label)
        self._text_shadow.setChecked(theme.text_shadow)

        self._conn_label_color.set_color_silent(theme.connection_label_color)
        self._conn_pill_bg.set_color_silent(theme.connection_label_pill_bg)

        if theme.connection_label_border is not None:
            self._conn_border_enabled.setChecked(True)
            self._conn_border_color.set_color_silent(theme.connection_label_border)
        else:
            self._conn_border_enabled.setChecked(False)

        self._conn_border_width.setValue(theme.connection_label_border_width)
        self._icon_outline_color.set_color_silent(theme.icon_outline_color)

    def _build_theme(self, name: str | None = None) -> Theme:
        """Construct a Theme from current widget values."""
        if name is None:
            name = self._active

        border = None
        if self._conn_border_enabled.isChecked():
            border = self._conn_border_color.color

        return Theme(
            name=name,
            canvas_bg=self._canvas_bg.color,
            grid_color=self._grid_color.color,
            grid_minor_width=self._grid_minor_width.value(),
            grid_major_color=self._grid_major_color.color,
            grid_major_width=self._grid_major_width.value(),
            zone_player_colors={pid: btn.color for pid, btn in self._player_btns.items()},
            zone_treasure_high=self._treasure_high.color,
            zone_treasure_mid=self._treasure_mid.color,
            zone_treasure_low=self._treasure_low.color,
            zone_border_width=self._zone_border_width.value(),
            zone_selected_border_width=self._zone_selected_border_width.value(),
            zone_border_darken=self._zone_border_darken.value(),
            zone_corner_radius=self._zone_corner_radius.value(),
            font_treasure=self._font_treasure.value(),
            font_zone_id=self._font_zone_id.value(),
            font_label=self._font_label.value(),
            font_count=self._font_count.value(),
            font_connection_label=self._font_connection_label.value(),
            text_shadow=self._text_shadow.isChecked(),
            connection_label_color=self._conn_label_color.color,
            connection_label_pill_bg=self._conn_pill_bg.color,
            connection_label_border=border,
            connection_label_border_width=self._conn_border_width.value(),
            icon_outline_color=self._icon_outline_color.color,
        )

    # ── Button handlers ──────────────────────────────────────────────

    def _on_apply(self) -> None:
        self._themes[self._active] = self._build_theme()
        ThemeManager().set_theme(self._themes[self._active])

    def _on_ok(self) -> None:
        self._themes[self._active] = self._build_theme()
        ThemeManager().set_theme(self._themes[self._active])
        save_themes(self._themes, self._active)
        self.accept()

    def _on_cancel(self) -> None:
        ThemeManager().set_theme(self._original_theme)
        self.reject()

    @property
    def themes(self) -> dict[str, Theme]:
        """Return the working copy of all presets (valid after OK)."""
        return self._themes

    @property
    def active(self) -> str:
        """Return the active preset name (valid after OK)."""
        return self._active
