"""Main window for the SOD Visual Template Editor."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from h3tc.editor.canvas.scene import TemplateScene
from h3tc.editor.canvas.view import TemplateView
from h3tc.editor.models.editor_state import EditorState
from h3tc.editor.models.layout_store import load_layout, save_layout
from h3tc.editor.panels.connection_panel import ConnectionPanel
from h3tc.editor.panels.map_panel import MapPanel
from h3tc.editor.panels.map_selector import MapSelector
from h3tc.editor.panels.zone_panel import ZonePanel
from h3tc.models import (
    Connection,
    PositionConstraints,
    TemplatePack,
    TemplateMap,
    TownSettings,
    TreasureTier,
    Zone,
    ZoneOptions,
)
from h3tc.enums import MONSTER_FACTIONS_SOD, TERRAINS_SOD
from h3tc.converters.hota_to_sod import hota_to_sod
from h3tc.converters.sod_to_hota import sod_to_hota
from h3tc.converters.hota_to_hota18 import hota_to_hota18
from h3tc.converters.hota18_to_hota import hota18_to_hota
from h3tc.formats import detect_format, get_parser
from h3tc.writers.sod import SodWriter
from h3tc.writers.hota import HotaWriter
from h3tc.writers.hota18 import Hota18Writer


class MainWindow(QMainWindow):
    """Main editor window with canvas, toolbar, and property panels."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("H3TC - SOD Template Editor")
        self.setMinimumSize(1000, 650)
        self.resize(1280, 800)

        self._state = EditorState()
        self._writer = SodWriter()

        self._build_actions()
        self._build_toolbar()
        self._build_ui()
        self._build_menubar()
        self._build_statusbar()
        self._connect_signals()
        self._update_title()

    # ── Build UI ─────────────────────────────────────────────────────────

    def _build_actions(self) -> None:
        self._act_new = QAction("New", self)
        self._act_new.setShortcut(QKeySequence.StandardKey.New)
        self._act_new.setToolTip("New template")

        self._act_open = QAction("Open", self)
        self._act_open.setShortcut(QKeySequence.StandardKey.Open)
        self._act_open.setToolTip("Open template (.txt or .h3t)")

        self._act_save = QAction("Save", self)
        self._act_save.setShortcut(QKeySequence.StandardKey.Save)
        self._act_save.setToolTip("Save template")

        self._act_save_as = QAction("Save As...", self)
        self._act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self._act_save_as.setToolTip("Save template as...")

        self._act_add_zone = QAction("Add Zone", self)
        self._act_add_zone.setToolTip("Add a new zone")

        self._act_add_connection = QAction("Add Connection", self)
        self._act_add_connection.setToolTip("Add a connection between two zones")

        self._act_delete = QAction("Delete", self)
        self._act_delete.setShortcut(QKeySequence.StandardKey.Delete)
        self._act_delete.setToolTip("Delete selected item(s)")

        self._act_convert = QAction("Convert File...", self)
        self._act_convert.setToolTip("Convert a template file between formats")

        self._act_zoom_fit = QAction("Zoom to Fit", self)
        self._act_zoom_fit.setShortcut(QKeySequence("Ctrl+0"))
        self._act_zoom_fit.setToolTip("Zoom to fit all zones")

        self._act_spread = QAction("Spread", self)
        self._act_spread.setShortcut(QKeySequence("Ctrl+="))
        self._act_spread.setToolTip("Increase distance between zones")

        self._act_compact = QAction("Compact", self)
        self._act_compact.setShortcut(QKeySequence("Ctrl+-"))
        self._act_compact.setToolTip("Decrease distance between zones")

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self._act_new)
        toolbar.addAction(self._act_open)
        toolbar.addAction(self._act_save)
        toolbar.addSeparator()
        toolbar.addAction(self._act_add_zone)
        toolbar.addAction(self._act_add_connection)
        toolbar.addAction(self._act_delete)
        toolbar.addSeparator()
        toolbar.addAction(self._act_zoom_fit)
        toolbar.addAction(self._act_spread)
        toolbar.addAction(self._act_compact)

    def _build_menubar(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("&File")
        file_menu.addAction(self._act_new)
        file_menu.addAction(self._act_open)
        file_menu.addSeparator()
        file_menu.addAction(self._act_save)
        file_menu.addAction(self._act_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self._act_convert)

        edit_menu = mb.addMenu("&Edit")
        edit_menu.addAction(self._act_add_zone)
        edit_menu.addAction(self._act_add_connection)
        edit_menu.addSeparator()
        edit_menu.addAction(self._act_delete)

        view_menu = mb.addMenu("&View")
        view_menu.addAction(self._act_zoom_fit)
        view_menu.addAction(self._act_spread)
        view_menu.addAction(self._act_compact)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)

        # Map selector (visible only for multi-map packs)
        self._map_selector = MapSelector()
        self._map_selector.setVisible(False)
        outer.addWidget(self._map_selector)

        # Main splitter: canvas left, panels right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Canvas
        self._scene = TemplateScene()
        self._view = TemplateView()
        self._view.setScene(self._scene)
        splitter.addWidget(self._view)

        # Right panel stack: map panel, zone panel, connection panel
        self._right_panel = QWidget()
        right_layout = QVBoxLayout(self._right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)

        self._map_panel = MapPanel()
        right_layout.addWidget(self._map_panel)

        self._panel_stack = QStackedWidget()
        self._empty_panel = QWidget()  # Shown when nothing selected
        self._zone_panel = ZonePanel()
        self._connection_panel = ConnectionPanel()
        self._panel_stack.addWidget(self._empty_panel)
        self._panel_stack.addWidget(self._zone_panel)
        self._panel_stack.addWidget(self._connection_panel)
        right_layout.addWidget(self._panel_stack, 1)

        splitter.addWidget(self._right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([800, 350])

        outer.addWidget(splitter, 1)

    def _build_statusbar(self) -> None:
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Ready")

    def _connect_signals(self) -> None:
        # Actions
        self._act_new.triggered.connect(self._on_new)
        self._act_open.triggered.connect(self._on_open)
        self._act_save.triggered.connect(self._on_save)
        self._act_save_as.triggered.connect(self._on_save_as)
        self._act_convert.triggered.connect(self._on_convert)
        self._act_add_zone.triggered.connect(self._on_add_zone)
        self._act_add_connection.triggered.connect(self._on_add_connection)
        self._act_delete.triggered.connect(self._on_delete)
        self._act_zoom_fit.triggered.connect(self._view.zoom_to_fit)
        self._act_spread.triggered.connect(lambda: self._on_spread_compact(1.3))
        self._act_compact.triggered.connect(lambda: self._on_spread_compact(0.7))

        # Scene selection
        self._scene.zone_selected.connect(self._on_zone_selected)
        self._scene.connection_selected.connect(self._on_connection_selected)
        self._scene.selection_cleared.connect(self._on_selection_cleared)
        self._scene.scene_modified.connect(self._on_modified)

        # Panels
        self._zone_panel.zone_changed.connect(self._on_zone_panel_changed)
        self._connection_panel.connection_changed.connect(
            self._on_connection_panel_changed
        )
        self._map_panel.map_changed.connect(self._on_modified)

        # Map selector
        self._map_selector.map_selected.connect(self._on_map_selected)

    # ── File Operations ──────────────────────────────────────────────────

    def open_file(self, filepath: str | Path) -> None:
        """Open a template file. Non-SOD formats are converted to SOD."""
        filepath = Path(filepath)
        if not filepath.exists():
            QMessageBox.warning(self, "Error", f"File not found: {filepath}")
            return

        try:
            parser = detect_format(filepath)
            pack = parser.parse(filepath)
            source_format = parser.format_name

            # Convert non-SOD formats to SOD for editing
            if parser.format_id != "sod":
                pack = hota_to_sod(pack)
        except Exception as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to parse:\n{e}")
            return

        self._state.pack = pack
        self._state.file_path = filepath
        self._state.current_map_index = 0
        self._state.mark_clean()

        # Load layout sidecar
        layouts = load_layout(filepath)

        # Setup map selector
        self._map_selector.set_pack(pack)
        self._map_selector.set_visible_if_multi(pack)

        # Load first map
        self._load_current_map(layouts)
        self._update_title()
        fmt = f"{source_format} → SOD" if source_format != "SOD" else "SOD"
        self._statusbar.showMessage(
            f"Opened: {filepath.name} ({len(pack.maps)} map(s), {fmt})"
        )

    def _load_current_map(
        self, layouts: dict[str, dict[str, tuple[float, float]]] | None = None
    ) -> None:
        tm = self._state.current_map
        if not tm:
            return

        positions = None
        if layouts and tm.name in layouts:
            positions = layouts[tm.name]

        self._scene.load_map(tm, positions)
        self._map_panel.set_map(tm)
        self._panel_stack.setCurrentWidget(self._empty_panel)

        # Fit view after loading
        from PySide6.QtCore import QTimer

        QTimer.singleShot(50, self._view.zoom_to_fit)

    def _on_new(self) -> None:
        if not self._check_unsaved():
            return

        # Create a minimal new template
        zone = _make_default_zone("1", human_start=True, ownership="1")
        tm = TemplateMap(name="New Template", min_size="72", max_size="108")
        tm.zones.append(zone)

        pack = TemplatePack(
            header_rows=_default_header_rows(),
            maps=[tm],
        )

        self._state.pack = pack
        self._state.file_path = None
        self._state.current_map_index = 0
        self._state.mark_dirty()

        self._map_selector.set_pack(pack)
        self._map_selector.set_visible_if_multi(pack)
        self._load_current_map()
        self._update_title()
        self._statusbar.showMessage("New template created")

    def _on_open(self) -> None:
        if not self._check_unsaved():
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Template",
            "",
            "All Templates (*.txt *.h3t);;SOD Templates (*.txt);;HOTA Templates (*.h3t);;All Files (*)",
        )
        if path:
            self.open_file(path)

    def _on_save(self) -> None:
        if self._state.file_path:
            self._save_to(self._state.file_path)
        else:
            self._on_save_as()

    def _on_save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save SOD Template",
            "",
            "SOD Templates (*.txt);;All Files (*)",
        )
        if path:
            self._save_to(Path(path))

    def _on_convert(self) -> None:
        from h3tc.editor.convert_dialog import ConvertDialog

        dialog = ConvertDialog(self)
        if dialog.exec() != ConvertDialog.DialogCode.Accepted:
            return

        try:
            parser = get_parser(dialog.input_format_id)
            pack = parser.parse(dialog.input_path)

            from_fmt = dialog.input_format_id
            to_fmt = dialog.output_format_id

            if from_fmt == "sod" and to_fmt == "hota17":
                pack = sod_to_hota(pack, pack_name=dialog.pack_name or dialog.input_path.stem)
            elif from_fmt == "sod" and to_fmt == "hota18":
                pack = sod_to_hota(pack, pack_name=dialog.pack_name or dialog.input_path.stem)
                pack = hota_to_hota18(pack)
            elif from_fmt == "hota17" and to_fmt == "sod":
                pack = hota_to_sod(pack)
            elif from_fmt == "hota17" and to_fmt == "hota18":
                pack = hota_to_hota18(pack)
            elif from_fmt == "hota18" and to_fmt == "sod":
                pack = hota_to_sod(pack)
            elif from_fmt == "hota18" and to_fmt == "hota17":
                pack = hota18_to_hota(pack)

            writers = {"sod": SodWriter, "hota17": HotaWriter, "hota18": Hota18Writer}
            writers[to_fmt]().write(pack, dialog.output_path)

            self._statusbar.showMessage(
                f"Converted: {dialog.input_path.name} → {dialog.output_path.name}"
            )
            QMessageBox.information(
                self,
                "Conversion Complete",
                f"Successfully converted to {dialog.output_path.name}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Conversion Error", f"Failed to convert:\n{e}")

    def _validate_and_fix(self) -> list[str]:
        """Validate all zones and auto-fix missing terrain/monster defaults.

        Returns list of fix descriptions applied.
        """
        fixes = []
        if not self._state.pack:
            return fixes

        for tm in self._state.pack.maps:
            for zone in tm.zones:
                zid = zone.id.strip()

                # Check terrain: at least one must be enabled
                has_terrain = any(
                    zone.terrains.get(t, "").strip().lower() == "x"
                    for t in TERRAINS_SOD
                )
                # terrain_match counts as having terrain configured
                if not has_terrain and zone.terrain_match.strip().lower() != "x":
                    zone.terrains["Dirt"] = "x"
                    fixes.append(
                        f"Zone {zid}: no terrain enabled, added Dirt"
                    )

                # Check monsters: at least one faction must be enabled
                has_monster = any(
                    zone.monster_factions.get(f, "").strip().lower() == "x"
                    for f in MONSTER_FACTIONS_SOD
                )
                # monster_match counts as having monsters configured
                if not has_monster and zone.monster_match.strip().lower() != "x":
                    zone.monster_factions["Neutral"] = "x"
                    fixes.append(
                        f"Zone {zid}: no monster faction enabled, added Neutral"
                    )

        return fixes

    def _save_to(self, filepath: Path) -> None:
        if not self._state.pack:
            return

        # Validate and auto-fix before saving
        fixes = self._validate_and_fix()
        if fixes:
            fix_text = "\n".join(f"  - {f}" for f in fixes)
            QMessageBox.information(
                self,
                "Auto-corrections Applied",
                f"The following issues were fixed before saving:\n\n{fix_text}",
            )
            # Refresh canvas to reflect changes
            if self._state.current_map:
                for zone in self._state.current_map.zones:
                    self._scene.refresh_zone(zone)

        try:
            self._writer.write(self._state.pack, filepath)

            # Save layout sidecar
            layouts = {}
            for m in self._state.pack.maps:
                if m is self._state.current_map:
                    layouts[m.name] = self._scene.get_zone_positions()
                # For maps not currently loaded, we'd need stored positions
                # For now, save current map positions
            save_layout(filepath, layouts)

            self._state.file_path = filepath
            self._state.mark_clean()
            self._update_title()
            self._statusbar.showMessage(f"Saved: {filepath.name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save:\n{e}")

    def _check_unsaved(self) -> bool:
        """Check for unsaved changes. Returns True if OK to proceed."""
        if not self._state.dirty:
            return True
        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save first?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if result == QMessageBox.StandardButton.Save:
            self._on_save()
            return not self._state.dirty
        if result == QMessageBox.StandardButton.Discard:
            return True
        return False

    # ── Edit Operations ──────────────────────────────────────────────────

    def _on_add_zone(self) -> None:
        if not self._state.current_map:
            return

        # Find next available zone ID
        existing_ids = {z.id.strip() for z in self._state.current_map.zones}
        next_id = 1
        while str(next_id) in existing_ids:
            next_id += 1

        zone = _make_default_zone(str(next_id))

        # Place near center of current view
        center = self._view.mapToScene(self._view.viewport().rect().center())
        self._scene.add_zone(zone, center.x(), center.y())
        self._map_panel.set_map(self._state.current_map)
        self._statusbar.showMessage(f"Added zone #{next_id}")

    def _on_add_connection(self) -> None:
        if not self._state.current_map:
            return

        selected = self._scene.selectedItems()
        from h3tc.editor.canvas.zone_item import ZoneItem

        zone_items = [item for item in selected if isinstance(item, ZoneItem)]
        if len(zone_items) != 2:
            self._statusbar.showMessage(
                "Select exactly 2 zones to create a connection"
            )
            return

        z1_id = zone_items[0].zone.id.strip()
        z2_id = zone_items[1].zone.id.strip()

        # Check if connection already exists
        for conn in self._state.current_map.connections:
            if (
                (conn.zone1.strip() == z1_id and conn.zone2.strip() == z2_id)
                or (conn.zone1.strip() == z2_id and conn.zone2.strip() == z1_id)
            ):
                self._statusbar.showMessage(
                    f"Connection already exists between {z1_id} and {z2_id}"
                )
                return

        connection = Connection(
            zone1=z1_id,
            zone2=z2_id,
            value="45000",
            wide="",
            border_guard="",
            positions=PositionConstraints(),
        )
        self._scene.add_connection(connection)
        self._map_panel.set_map(self._state.current_map)
        self._statusbar.showMessage(f"Added connection {z1_id} - {z2_id}")

    def _on_spread_compact(self, factor: float) -> None:
        """Spread or compact zones while preserving viewport center."""
        # Remember current view center in scene coords
        center = self._view.mapToScene(self._view.viewport().rect().center())
        self._scene.scale_zone_distances(factor)
        # Restore view center so zoom/pan doesn't shift
        self._view.centerOn(center)

    def _on_delete(self) -> None:
        if not self._scene.selectedItems():
            return
        self._scene.delete_selected()
        self._panel_stack.setCurrentWidget(self._empty_panel)
        if self._state.current_map:
            self._map_panel.set_map(self._state.current_map)
        self._statusbar.showMessage("Deleted selected item(s)")

    # ── Selection Handling ───────────────────────────────────────────────

    def _on_zone_selected(self, zone) -> None:
        self._zone_panel.set_zone(zone)
        self._panel_stack.setCurrentWidget(self._zone_panel)

    def _on_connection_selected(self, connection) -> None:
        self._connection_panel.set_connection(connection)
        self._panel_stack.setCurrentWidget(self._connection_panel)

    def _on_selection_cleared(self) -> None:
        self._panel_stack.setCurrentWidget(self._empty_panel)

    # ── Panel Change Callbacks ───────────────────────────────────────────

    def _on_zone_panel_changed(self) -> None:
        self._state.mark_dirty()
        self._update_title()
        # Refresh the zone visual on the canvas
        selected = self._scene.selectedItems()
        from h3tc.editor.canvas.zone_item import ZoneItem

        for item in selected:
            if isinstance(item, ZoneItem):
                self._scene.refresh_zone(item.zone)

    def _on_connection_panel_changed(self) -> None:
        self._state.mark_dirty()
        self._update_title()
        selected = self._scene.selectedItems()
        from h3tc.editor.canvas.connection_item import ConnectionItem

        for item in selected:
            if isinstance(item, ConnectionItem):
                self._scene.refresh_connection(item.connection)

    def _on_modified(self) -> None:
        self._state.mark_dirty()
        self._update_title()

    def _on_map_selected(self, index: int) -> None:
        if not self._state.pack or index < 0:
            return
        # Save current map positions before switching
        if self._state.current_map:
            pass  # TODO: persist positions across map switches
        self._state.current_map_index = index
        self._load_current_map()

    # ── UI Helpers ───────────────────────────────────────────────────────

    def _update_title(self) -> None:
        title = "H3TC - SOD Template Editor"
        if self._state.file_path:
            title = f"{self._state.file_path.name} - {title}"
        elif self._state.pack:
            title = f"Untitled - {title}"
        if self._state.dirty:
            title = f"* {title}"
        self.setWindowTitle(title)

    def closeEvent(self, event) -> None:
        if self._check_unsaved():
            event.accept()
        else:
            event.ignore()


# ── Helper Functions ─────────────────────────────────────────────────────


def _make_default_zone(
    zone_id: str,
    *,
    human_start: bool = False,
    computer_start: bool = False,
    treasure: bool = False,
    junction: bool = False,
    ownership: str = "",
) -> Zone:
    """Create a new zone with sensible defaults."""
    # If no type specified, default to treasure
    if not any([human_start, computer_start, treasure, junction]):
        treasure = True

    return Zone(
        id=zone_id,
        human_start="x" if human_start else "",
        computer_start="x" if computer_start else "",
        treasure="x" if treasure else "",
        junction="x" if junction else "",
        base_size="30" if (human_start or computer_start) else "10",
        positions=PositionConstraints(),
        ownership=ownership,
        player_towns=TownSettings(
            min_towns="1" if human_start else "",
            min_castles="1" if human_start else "",
            town_density="",
            castle_density="",
        ),
        neutral_towns=TownSettings(),
        towns_same_type="",
        town_types={},
        min_mines={},
        mine_density={},
        terrain_match="x" if (human_start or computer_start) else "",
        terrains={"Dirt": "x"},
        monster_strength="weak" if treasure else "",
        monster_match="",
        monster_factions={"Neutral": "x"},
        treasure_tiers=[
            TreasureTier(low="12000", high="22000", density="1"),
            TreasureTier(low="5000", high="16000", density="6"),
            TreasureTier(low="300", high="3000", density="14"),
        ]
        if treasure
        else [TreasureTier(), TreasureTier(), TreasureTier()],
        zone_options=ZoneOptions(),
    )


def _default_header_rows() -> list[list[str]]:
    """Create default SOD header rows."""
    from h3tc.constants import SodCol

    row1 = [""] * SodCol.ACTIVE_COLS
    row1[0] = "Map"
    row1[3] = "Zone"
    row1[76] = "Connections"

    row2 = [""] * SodCol.ACTIVE_COLS
    row2[4] = "Type"
    row2[9] = "Restrictions"
    row2[14] = "Player towns"
    row2[18] = "Neutral towns"
    row2[22] = "Town types"
    row2[32] = "Minimum mines"
    row2[39] = "Mine Density"
    row2[46] = "Terrain"
    row2[55] = "Monsters"
    row2[67] = "Treasure"
    row2[76] = "Zones"
    row2[80] = "Restrictions"

    row3 = [""] * SodCol.ACTIVE_COLS
    row3[0] = "Name"
    row3[1] = "min size"
    row3[2] = "max size"
    row3[3] = "ID"
    row3[4] = "human"
    row3[5] = "computer"
    row3[6] = "Treasure"
    row3[7] = "Junction"
    row3[8] = "base size"

    return [row1, row2, row3]
