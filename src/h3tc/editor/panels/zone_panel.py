"""Zone property panel with 5 tabs matching the HOTA template editor layout (SOD only)."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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

from h3tc.editor.panels.binding import (
    bind_checkbox,
    bind_combo_index,
    bind_spinbox,
    disconnect_all,
)
from h3tc.enums import (
    MONSTER_FACTIONS_SOD,
    RESOURCES,
    TERRAINS_SOD,
    TOWN_FACTIONS_SOD,
)
from h3tc.models import Zone

# SOD uses "Elemental" but internally stores as "Conflux"
_SOD_TOWN_CANONICAL = [
    f if f != "Elemental" else "Conflux" for f in TOWN_FACTIONS_SOD
]

# Zone type options
_ZONE_TYPES = ["Human Start", "Computer Start", "Treasure", "Junction"]
_ZONE_TYPE_FIELDS = ["human_start", "computer_start", "treasure", "junction"]

# Monster strength options (SOD values are text)
_MONSTER_STRENGTHS = [
    ("None", ""),
    ("Weak", "weak"),
    ("Average", "normal"),
    ("Strong", "strong"),
]


def _make_spinbox(minimum: int = 0, maximum: int = 99999) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setFixedWidth(70)
    return spin


def _make_checkbox(label: str) -> QCheckBox:
    return QCheckBox(label)


class ZonePanel(QWidget):
    """Zone settings panel with 5 tabs: General, Towns, Content, Terrain, Monsters."""

    zone_changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._zone: Zone | None = None
        self._widgets: list = []  # Track all bound widgets for cleanup

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel("Zone Settings")
        self._title.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        layout.addWidget(self._title)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._build_general_tab()
        self._build_towns_tab()
        self._build_content_tab()
        self._build_terrain_tab()
        self._build_monsters_tab()

    def set_zone(self, zone: Zone) -> None:
        """Populate the panel from a zone model."""
        self._disconnect_all()
        self._zone = zone
        self._title.setText(f"Zone Settings - #{zone.id.strip()}")
        self._populate_general()
        self._populate_towns()
        self._populate_content()
        self._populate_terrain()
        self._populate_monsters()

    def _on_change(self) -> None:
        self.zone_changed.emit()

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

    def _bind_combo(self, combo, obj, field, **kwargs) -> None:
        bind_combo_index(combo, obj, field, on_change=self._on_change, **kwargs)
        self._widgets.append(combo)

    # ── Tab 1: General ──────────────────────────────────────────────────

    def _build_general_tab(self) -> None:
        tab = QWidget()
        main = QVBoxLayout(tab)

        # General group
        grp = QGroupBox("General")
        g = QGridLayout(grp)

        g.addWidget(QLabel("Zone ID"), 0, 0)
        self._zone_id = _make_spinbox(1, 999)
        g.addWidget(self._zone_id, 0, 1)

        g.addWidget(QLabel("Size"), 1, 0)
        self._base_size = _make_spinbox(1, 99999)
        g.addWidget(self._base_size, 1, 1)

        g.addWidget(QLabel("Type"), 2, 0)
        self._zone_type = QComboBox()
        self._zone_type.addItems(_ZONE_TYPES)
        self._zone_type.setFixedWidth(140)
        g.addWidget(self._zone_type, 2, 1)

        g.addWidget(QLabel("Owner"), 3, 0)
        self._owner = QComboBox()
        self._owner.addItems(
            ["None", "Player 1", "Player 2", "Player 3", "Player 4",
             "Player 5", "Player 6", "Player 7", "Player 8"]
        )
        self._owner.setFixedWidth(140)
        g.addWidget(self._owner, 3, 1)

        main.addWidget(grp)

        # Requirements group
        req = QGroupBox("Requirements")
        rg = QGridLayout(req)
        rg.addWidget(QLabel("Human Positions"), 0, 0)
        self._pos_min_human = _make_spinbox()
        self._pos_max_human = _make_spinbox()
        rg.addWidget(self._pos_min_human, 0, 1)
        rg.addWidget(QLabel("to"), 0, 2)
        rg.addWidget(self._pos_max_human, 0, 3)

        rg.addWidget(QLabel("Total Positions"), 1, 0)
        self._pos_min_total = _make_spinbox()
        self._pos_max_total = _make_spinbox()
        rg.addWidget(self._pos_min_total, 1, 1)
        rg.addWidget(QLabel("to"), 1, 2)
        rg.addWidget(self._pos_max_total, 1, 3)

        main.addWidget(req)
        main.addStretch()

        self._tabs.addTab(tab, "General")

    def _populate_general(self) -> None:
        z = self._zone

        self._bind_spin(self._zone_id, z, "id")
        self._bind_spin(self._base_size, z, "base_size")

        # Zone type: find which type flag is set
        self._zone_type.blockSignals(True)
        type_idx = 0
        for i, field in enumerate(_ZONE_TYPE_FIELDS):
            if getattr(z, field).strip().lower() == "x":
                type_idx = i
                break
        self._zone_type.setCurrentIndex(type_idx)
        self._zone_type.blockSignals(False)
        self._zone_type.currentIndexChanged.connect(self._on_zone_type_changed)
        self._widgets.append(self._zone_type)

        # Owner
        self._owner.blockSignals(True)
        try:
            owner_val = int(z.ownership) if z.ownership.strip() else 0
        except ValueError:
            owner_val = 0
        self._owner.setCurrentIndex(owner_val)
        self._owner.blockSignals(False)
        self._owner.currentIndexChanged.connect(self._on_owner_changed)
        self._widgets.append(self._owner)

        # Enable/disable owner based on type
        self._owner.setEnabled(type_idx == 0)  # Only for Human Start

        # Position constraints
        self._bind_spin(self._pos_min_human, z, "min_human", sub_obj="positions")
        self._bind_spin(self._pos_max_human, z, "max_human", sub_obj="positions")
        self._bind_spin(self._pos_min_total, z, "min_total", sub_obj="positions")
        self._bind_spin(self._pos_max_total, z, "max_total", sub_obj="positions")

    def _on_zone_type_changed(self, index: int) -> None:
        if not self._zone:
            return
        for i, field in enumerate(_ZONE_TYPE_FIELDS):
            setattr(self._zone, field, "x" if i == index else "")
        self._owner.setEnabled(index == 0)
        if index != 0:
            self._zone.ownership = ""
            self._owner.blockSignals(True)
            self._owner.setCurrentIndex(0)
            self._owner.blockSignals(False)
        self._on_change()

    def _on_owner_changed(self, index: int) -> None:
        if not self._zone:
            return
        self._zone.ownership = str(index) if index > 0 else ""
        self._on_change()

    # ── Tab 2: Towns and Castles ─────────────────────────────────────────

    def _build_towns_tab(self) -> None:
        tab = QWidget()
        main = QVBoxLayout(tab)

        # Player Towns & Castles
        h = QHBoxLayout()

        pg = QGroupBox("Player Towns && Castles")
        pl = QGridLayout(pg)
        pl.addWidget(QLabel("Minimum Towns"), 0, 0)
        self._pt_min_towns = _make_spinbox()
        pl.addWidget(self._pt_min_towns, 0, 1)
        pl.addWidget(QLabel("Towns density"), 1, 0)
        self._pt_town_density = _make_spinbox()
        pl.addWidget(self._pt_town_density, 1, 1)
        pl.addWidget(QLabel("Minimum Castles"), 2, 0)
        self._pt_min_castles = _make_spinbox()
        pl.addWidget(self._pt_min_castles, 2, 1)
        pl.addWidget(QLabel("Castles density"), 3, 0)
        self._pt_castle_density = _make_spinbox()
        pl.addWidget(self._pt_castle_density, 3, 1)
        h.addWidget(pg)

        ng = QGroupBox("Neutral Towns && Castles")
        nl = QGridLayout(ng)
        nl.addWidget(QLabel("Minimum Towns"), 0, 0)
        self._nt_min_towns = _make_spinbox()
        nl.addWidget(self._nt_min_towns, 0, 1)
        nl.addWidget(QLabel("Towns density"), 1, 0)
        self._nt_town_density = _make_spinbox()
        nl.addWidget(self._nt_town_density, 1, 1)
        nl.addWidget(QLabel("Minimum Castles"), 2, 0)
        self._nt_min_castles = _make_spinbox()
        nl.addWidget(self._nt_min_castles, 2, 1)
        nl.addWidget(QLabel("Castles density"), 3, 0)
        self._nt_castle_density = _make_spinbox()
        nl.addWidget(self._nt_castle_density, 3, 1)
        h.addWidget(ng)

        main.addLayout(h)

        # Allowed Towns
        ag = QGroupBox("Allowed Towns")
        al_layout = QVBoxLayout(ag)
        grid = QGridLayout()
        self._town_checks: dict[str, QCheckBox] = {}
        for i, (sod_name, canonical) in enumerate(
            zip(TOWN_FACTIONS_SOD, _SOD_TOWN_CANONICAL)
        ):
            cb = QCheckBox(sod_name)
            self._town_checks[canonical] = cb
            grid.addWidget(cb, i // 3, i % 3)
        al_layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_none = QPushButton("Select None")
        btn_all.clicked.connect(lambda: self._set_all_town_checks(True))
        btn_none.clicked.connect(lambda: self._set_all_town_checks(False))
        btn_row.addWidget(btn_all)
        btn_row.addWidget(btn_none)
        btn_row.addStretch()
        al_layout.addLayout(btn_row)
        main.addWidget(ag)

        # Town Type Rules
        rules = QGroupBox("Town Type Rules")
        rl = QVBoxLayout(rules)
        self._towns_same_type = QCheckBox("All towns/castles have same type")
        rl.addWidget(self._towns_same_type)
        main.addWidget(rules)

        main.addStretch()
        self._tabs.addTab(tab, "Towns and Castles")

    def _set_all_town_checks(self, checked: bool) -> None:
        for cb in self._town_checks.values():
            cb.setChecked(checked)

    def _populate_towns(self) -> None:
        z = self._zone
        self._bind_spin(self._pt_min_towns, z, "min_towns", sub_obj="player_towns")
        self._bind_spin(self._pt_town_density, z, "town_density", sub_obj="player_towns")
        self._bind_spin(self._pt_min_castles, z, "min_castles", sub_obj="player_towns")
        self._bind_spin(self._pt_castle_density, z, "castle_density", sub_obj="player_towns")

        self._bind_spin(self._nt_min_towns, z, "min_towns", sub_obj="neutral_towns")
        self._bind_spin(self._nt_town_density, z, "town_density", sub_obj="neutral_towns")
        self._bind_spin(self._nt_min_castles, z, "min_castles", sub_obj="neutral_towns")
        self._bind_spin(self._nt_castle_density, z, "castle_density", sub_obj="neutral_towns")

        for canonical, cb in self._town_checks.items():
            self._bind_check(cb, z, "town_types", dict_key=canonical)

        self._bind_check(self._towns_same_type, z, "towns_same_type")

    # ── Tab 3: Content ───────────────────────────────────────────────────

    def _build_content_tab(self) -> None:
        tab = QWidget()
        main = QVBoxLayout(tab)

        # Treasure
        tg = QGroupBox("Treasure")
        tl = QGridLayout(tg)
        tl.addWidget(QLabel("low"), 0, 1)
        tl.addWidget(QLabel("high"), 0, 2)
        tl.addWidget(QLabel("density"), 0, 3)

        self._treasure_spins: list[tuple[QSpinBox, QSpinBox, QSpinBox]] = []
        tier_labels = ["Tier 1", "Tier 2", "Tier 3"]
        for row, label in enumerate(tier_labels, 1):
            tl.addWidget(QLabel(label), row, 0)
            low = _make_spinbox(0, 999999)
            high = _make_spinbox(0, 999999)
            density = _make_spinbox(0, 999)
            tl.addWidget(low, row, 1)
            tl.addWidget(high, row, 2)
            tl.addWidget(density, row, 3)
            self._treasure_spins.append((low, high, density))
        main.addWidget(tg)

        # Mines & special objects
        mg = QGroupBox("Mines && special objects")
        ml = QGridLayout(mg)
        ml.addWidget(QLabel("type"), 0, 0)
        ml.addWidget(QLabel("min count"), 0, 1)
        ml.addWidget(QLabel("density"), 0, 2)

        self._mine_spins: dict[str, tuple[QSpinBox, QSpinBox]] = {}
        for row, resource in enumerate(RESOURCES, 1):
            ml.addWidget(QLabel(resource), row, 0)
            min_count = _make_spinbox()
            density = _make_spinbox()
            ml.addWidget(min_count, row, 1)
            ml.addWidget(density, row, 2)
            self._mine_spins[resource] = (min_count, density)
        main.addWidget(mg)

        main.addStretch()
        self._tabs.addTab(tab, "Content")

    def _populate_content(self) -> None:
        z = self._zone

        for tier_idx, (low, high, density) in enumerate(self._treasure_spins):
            if tier_idx < len(z.treasure_tiers):
                tier = z.treasure_tiers[tier_idx]
                self._bind_spin(low, tier, "low")
                self._bind_spin(high, tier, "high")
                self._bind_spin(density, tier, "density")

        for resource, (min_spin, dens_spin) in self._mine_spins.items():
            self._bind_spin(min_spin, z, "min_mines", dict_key=resource)
            self._bind_spin(dens_spin, z, "mine_density", dict_key=resource)

    # ── Tab 4: Terrain ───────────────────────────────────────────────────

    def _build_terrain_tab(self) -> None:
        tab = QWidget()
        main = QVBoxLayout(tab)

        # Allowed Terrains
        tg = QGroupBox("Allowed Terrains")
        tl = QVBoxLayout(tg)
        grid = QGridLayout()
        self._terrain_checks: dict[str, QCheckBox] = {}
        for i, terrain in enumerate(TERRAINS_SOD):
            cb = QCheckBox(terrain)
            self._terrain_checks[terrain] = cb
            grid.addWidget(cb, i // 3, i % 3)
        tl.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_none = QPushButton("Select None")
        btn_all.clicked.connect(lambda: self._set_all_terrain_checks(True))
        btn_none.clicked.connect(lambda: self._set_all_terrain_checks(False))
        btn_row.addWidget(btn_all)
        btn_row.addWidget(btn_none)
        btn_row.addStretch()
        tl.addLayout(btn_row)
        main.addWidget(tg)

        # Match to town
        self._terrain_match = QCheckBox("Match to town")
        main.addWidget(self._terrain_match)

        main.addStretch()
        self._tabs.addTab(tab, "Terrain")

    def _set_all_terrain_checks(self, checked: bool) -> None:
        for cb in self._terrain_checks.values():
            cb.setChecked(checked)

    def _populate_terrain(self) -> None:
        z = self._zone
        for terrain, cb in self._terrain_checks.items():
            self._bind_check(cb, z, "terrains", dict_key=terrain)
        self._bind_check(self._terrain_match, z, "terrain_match")

    # ── Tab 5: Monsters ──────────────────────────────────────────────────

    def _build_monsters_tab(self) -> None:
        tab = QWidget()
        main = QVBoxLayout(tab)

        # General
        gg = QGroupBox("General")
        gl = QGridLayout(gg)
        gl.addWidget(QLabel("Strength"), 0, 0)
        self._monster_strength = QComboBox()
        for label, _ in _MONSTER_STRENGTHS:
            self._monster_strength.addItem(label)
        self._monster_strength.setFixedWidth(120)
        gl.addWidget(self._monster_strength, 0, 1)
        main.addWidget(gg)

        # Monster Type
        mg = QGroupBox("Monster Type")
        ml = QVBoxLayout(mg)

        self._monster_match = QCheckBox("Match to town")
        ml.addWidget(self._monster_match)

        grid = QGridLayout()
        self._monster_checks: dict[str, QCheckBox] = {}
        for i, faction in enumerate(MONSTER_FACTIONS_SOD):
            cb = QCheckBox(faction)
            self._monster_checks[faction] = cb
            grid.addWidget(cb, i // 3, i % 3)
        ml.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_none = QPushButton("Select None")
        btn_all.clicked.connect(lambda: self._set_all_monster_checks(True))
        btn_none.clicked.connect(lambda: self._set_all_monster_checks(False))
        btn_row.addWidget(btn_all)
        btn_row.addWidget(btn_none)
        btn_row.addStretch()
        ml.addLayout(btn_row)
        main.addWidget(mg)

        main.addStretch()
        self._tabs.addTab(tab, "Monsters")

    def _set_all_monster_checks(self, checked: bool) -> None:
        for cb in self._monster_checks.values():
            cb.setChecked(checked)

    def _populate_monsters(self) -> None:
        z = self._zone

        # Monster strength
        self._monster_strength.blockSignals(True)
        raw = z.monster_strength.strip()
        idx = 0
        for i, (_, val) in enumerate(_MONSTER_STRENGTHS):
            if val == raw:
                idx = i
                break
        self._monster_strength.setCurrentIndex(idx)
        self._monster_strength.blockSignals(False)
        self._monster_strength.currentIndexChanged.connect(
            self._on_monster_strength_changed
        )
        self._widgets.append(self._monster_strength)

        self._bind_check(self._monster_match, z, "monster_match")

        for faction, cb in self._monster_checks.items():
            self._bind_check(cb, z, "monster_factions", dict_key=faction)

    def _on_monster_strength_changed(self, index: int) -> None:
        if not self._zone:
            return
        _, val = _MONSTER_STRENGTHS[index]
        self._zone.monster_strength = val
        self._on_change()
