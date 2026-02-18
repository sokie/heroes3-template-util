"""Format-agnostic data models for H3 template packs.

All cell values are stored as str to preserve exact formatting for roundtrip fidelity.
Optional[str] where None = "not present in source format", "" = "present but blank".
"""

from pydantic import BaseModel
from typing import Optional


class PositionConstraints(BaseModel):
    min_human: str = ""
    max_human: str = ""
    min_total: str = ""
    max_total: str = ""


class TownSettings(BaseModel):
    min_towns: str = ""
    min_castles: str = ""
    town_density: str = ""
    castle_density: str = ""


class TreasureTier(BaseModel):
    low: str = ""
    high: str = ""
    density: str = ""


class ZoneOptions(BaseModel):
    """HOTA-only zone options (18 fields)."""

    placement: Optional[str] = None
    objects: Optional[str] = None
    min_objects: Optional[str] = None
    image_settings: Optional[str] = None
    force_neutral_creatures: Optional[str] = None
    allow_non_coherent_road: Optional[str] = None
    zone_repulsion: Optional[str] = None
    town_hint: Optional[str] = None
    monsters_disposition_standard: Optional[str] = None
    monsters_disposition_custom: Optional[str] = None
    monsters_joining_percentage: Optional[str] = None
    monsters_join_only_for_money: Optional[str] = None
    min_airship_shipyards: Optional[str] = None
    airship_shipyard_density: Optional[str] = None
    terrain_hint: Optional[str] = None
    allowed_factions: Optional[str] = None
    faction_hint: Optional[str] = None
    max_block_value: Optional[str] = None


class Zone(BaseModel):
    id: str = ""
    human_start: str = ""
    computer_start: str = ""
    treasure: str = ""
    junction: str = ""
    base_size: str = ""
    positions: PositionConstraints = PositionConstraints()
    ownership: str = ""
    player_towns: TownSettings = TownSettings()
    neutral_towns: TownSettings = TownSettings()
    towns_same_type: str = ""
    town_types: dict[str, str] = {}
    min_mines: dict[str, str] = {}
    mine_density: dict[str, str] = {}
    terrain_match: str = ""
    terrains: dict[str, str] = {}
    monster_strength: str = ""
    monster_match: str = ""
    monster_factions: dict[str, str] = {}
    treasure_tiers: list[TreasureTier] = []
    zone_options: ZoneOptions = ZoneOptions()


class Connection(BaseModel):
    zone1: str = ""
    zone2: str = ""
    value: str = ""
    wide: str = ""
    border_guard: str = ""
    positions: PositionConstraints = PositionConstraints()
    # HOTA-only fields
    road: Optional[str] = None
    conn_type: Optional[str] = None
    fictive: Optional[str] = None
    portal_repulsion: Optional[str] = None
    # Extra columns from zone area on connection-only rows (for roundtrip)
    extra_zone_cols: dict[int, str] = {}


class MapOptions(BaseModel):
    """HOTA-only map options."""

    artifacts: Optional[str] = None
    combo_arts: Optional[str] = None
    spells: Optional[str] = None
    secondary_skills: Optional[str] = None
    objects: Optional[str] = None
    rock_blocks: Optional[str] = None
    zone_sparseness: Optional[str] = None
    special_weeks_disabled: Optional[str] = None
    spell_research: Optional[str] = None
    anarchy: Optional[str] = None


class TemplateMap(BaseModel):
    name: str = ""
    min_size: str = ""
    max_size: str = ""
    options: MapOptions = MapOptions()
    zones: list[Zone] = []
    connections: list[Connection] = []


class PackMetadata(BaseModel):
    """HOTA pack metadata."""

    name: str = ""
    description: str = ""
    town_selection: str = ""
    heroes: str = ""
    mirror: str = ""
    tags: str = ""
    max_battle_rounds: str = ""
    forbid_hiring_heroes: str = ""


class FieldCounts(BaseModel):
    """HOTA field count row (first 7 cols of row 4)."""

    town: str = ""
    terrain: str = ""
    zone_type: str = ""
    pack_new: str = ""
    map_new: str = ""
    zone_new: str = ""
    connection_new: str = ""


class TemplatePack(BaseModel):
    metadata: Optional[PackMetadata] = None
    field_counts: Optional[FieldCounts] = None
    maps: list[TemplateMap] = []
    # Store original headers for roundtrip fidelity
    header_rows: list[list[str]] = []
