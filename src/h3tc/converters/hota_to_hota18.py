"""Convert HOTA 1.7.x template packs to HOTA 1.8.x format."""

from h3tc.enums import (
    MONSTER_FACTIONS_HOTA18,
    TERRAINS_HOTA,
    TOWN_FACTIONS_HOTA,
    TOWN_FACTIONS_HOTA18,
)
from h3tc.models import (
    Connection,
    FieldCounts,
    TemplatePack,
    TemplateMap,
    Zone,
)


def hota_to_hota18(pack: TemplatePack) -> TemplatePack:
    """Convert a HOTA 1.7.x TemplatePack to HOTA 1.8.x format."""
    # Update field counts: town 11 -> 12
    field_counts = None
    if pack.field_counts:
        field_counts = pack.field_counts.model_copy(update={"town": "12"})

    header_rows = _build_hota18_headers()

    hota18_maps = []
    for tmap in pack.maps:
        hota18_map = _convert_map(tmap)
        hota18_maps.append(hota18_map)

    return TemplatePack(
        metadata=pack.metadata.model_copy() if pack.metadata else None,
        field_counts=field_counts,
        maps=hota18_maps,
        header_rows=header_rows,
    )


def _convert_map(tmap: TemplateMap) -> TemplateMap:
    """Convert a single map from HOTA 1.7.x to 1.8.x."""
    zones = [_convert_zone(z) for z in tmap.zones]
    connections = [_copy_connection(c) for c in tmap.connections]

    return TemplateMap(
        name=tmap.name,
        min_size=tmap.min_size,
        max_size=tmap.max_size,
        options=tmap.options.model_copy() if tmap.options else None,
        zones=zones,
        connections=connections,
    )


def _all_enabled(values: dict[str, str], keys: list[str]) -> bool:
    """Check if all given keys have 'x' in the values dict."""
    return all(values.get(k, "").strip() == "x" for k in keys)


def _convert_zone(zone: Zone) -> Zone:
    """Convert a zone from HOTA 1.7.x to 1.8.x — add Bulwark."""
    # Town types: add Bulwark (enable if all existing factions enabled)
    all_towns_on = _all_enabled(zone.town_types, TOWN_FACTIONS_HOTA)
    town_types = dict(zone.town_types)
    town_types["Bulwark"] = "x" if all_towns_on else ""

    # Monster factions: add Bulwark
    hota_monster_keys = [
        "Neutral", "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
        "Dungeon", "Stronghold", "Fortress", "Conflux", "Cove", "Factory",
    ]
    all_monsters_on = _all_enabled(zone.monster_factions, hota_monster_keys)
    monster_factions = dict(zone.monster_factions)
    monster_factions["Bulwark"] = "x" if all_monsters_on else ""

    return Zone(
        id=zone.id,
        human_start=zone.human_start,
        computer_start=zone.computer_start,
        treasure=zone.treasure,
        junction=zone.junction,
        base_size=zone.base_size,
        positions=zone.positions.model_copy(),
        ownership=zone.ownership,
        player_towns=zone.player_towns.model_copy(),
        neutral_towns=zone.neutral_towns.model_copy(),
        towns_same_type=zone.towns_same_type,
        town_types=town_types,
        min_mines=dict(zone.min_mines),
        mine_density=dict(zone.mine_density),
        terrain_match=zone.terrain_match,
        terrains=dict(zone.terrains),
        monster_strength=zone.monster_strength,
        monster_match=zone.monster_match,
        monster_factions=monster_factions,
        treasure_tiers=[t.model_copy() for t in zone.treasure_tiers],
        zone_options=zone.zone_options.model_copy(),
    )


def _copy_connection(conn: Connection) -> Connection:
    """Copy a connection (no changes needed between 1.7.x and 1.8.x)."""
    return Connection(
        zone1=conn.zone1,
        zone2=conn.zone2,
        value=conn.value,
        wide=conn.wide,
        border_guard=conn.border_guard,
        positions=conn.positions.model_copy(),
        road=conn.road,
        conn_type=conn.conn_type,
        fictive=conn.fictive,
        portal_repulsion=conn.portal_repulsion,
    )


def _build_hota18_headers() -> list[list[str]]:
    """Build standard HOTA 1.8.x header rows (141 columns)."""
    from h3tc.enums import RESOURCES

    total = 141  # TOTAL + 1 for trailing

    # Row 1: section headers
    row1 = [""] * total
    row1[0] = "Pack"
    row1[15] = "Map"
    row1[28] = "Zone"
    row1[127] = "Connections"

    # Row 2: subsection headers
    row2 = [""] * total
    row2[0] = "Field count"
    row2[7] = "Options"
    row2[29] = "Type"
    row2[34] = "Restrictions"
    row2[39] = "Player towns"
    row2[43] = "Neutral towns"
    row2[48] = "Town types"
    row2[60] = "Minimum mines"
    row2[67] = "Mine Density"
    row2[74] = "Terrain"
    row2[85] = "Monsters"
    row2[100] = "Treasure"
    row2[109] = "Options"
    row2[127] = "Zones"
    row2[132] = "Options"
    row2[136] = "Restrictions"

    # Row 3: column headers
    row3 = [""] * total
    # Field counts
    fc_names = ["Town", "Terrain", "Zone type", "Pack new", "Map new", "Zone new", "Connection new"]
    for i, name in enumerate(fc_names):
        row3[i] = name
    # Pack metadata
    row3[7] = "Name"
    row3[8] = "Description"
    row3[9] = "Town selection"
    row3[10] = "Heroes"
    row3[11] = "Mirror"
    row3[12] = "Tags"
    row3[13] = "Max Battle Rounds"
    row3[14] = "Forbid Hiring Heroes"
    # Map
    row3[15] = "Name"
    row3[16] = "Minimum Size"
    row3[17] = "Maximum Size"
    row3[18] = "Artifacts"
    row3[19] = "Combo Arts"
    row3[20] = "Spells"
    row3[21] = "Secondary skills"
    row3[22] = "Objects"
    row3[23] = "Rock blocks"
    row3[24] = "Zone sparseness"
    row3[25] = "Special weeks disabled"
    row3[26] = "Spell Research"
    row3[27] = "Anarchy"
    # Zone core
    row3[28] = "Id"
    row3[29] = "human start"
    row3[30] = "computer start"
    row3[31] = "Treasure"
    row3[32] = "Junction"
    row3[33] = "Base Size"
    row3[34] = "Minimum human positions"
    row3[35] = "Maximum human positions"
    row3[36] = "Minimum total positions"
    row3[37] = "Maximum total positions"
    row3[38] = "Ownership"
    # Player towns
    row3[39] = "Minimum towns"
    row3[40] = "Minimum castles"
    row3[41] = "Town Density"
    row3[42] = "Castle Density"
    # Neutral towns
    row3[43] = "Minimum towns"
    row3[44] = "Minimum castles"
    row3[45] = "Town Density"
    row3[46] = "Castle Density"
    row3[47] = "Towns are of same type"
    # Town types (12 factions)
    for i, faction in enumerate(TOWN_FACTIONS_HOTA18):
        row3[48 + i] = faction
    # Mines
    for i, res in enumerate(RESOURCES):
        row3[60 + i] = res
        row3[67 + i] = res
    # Terrain
    row3[74] = "Match to town"
    for i, terrain in enumerate(TERRAINS_HOTA):
        row3[75 + i] = terrain
    # Monsters
    row3[85] = "Strength"
    row3[86] = "Match to town"
    for i, faction in enumerate(MONSTER_FACTIONS_HOTA18):
        row3[87 + i] = faction
    # Treasure
    for tier in range(3):
        row3[100 + tier * 3] = "Low"
        row3[100 + tier * 3 + 1] = "High"
        row3[100 + tier * 3 + 2] = "Density"
    # Zone options
    zo_names = [
        "Placement", "Objects", "Minimum objects", "Image settings",
        "Force neutral creatures", "Allow non-coherent road", "Zone repulsion",
        "Town Hint", "Monsters disposition (standard)", "Monsters disposition (custom)",
        "Monsters joining percentage", "Monsters join only for money",
        "Minimum airship shipyards", "Airship shipyard Density",
        "Terrain Hint", "Allowed Factions", "Faction Hint", "Max block value",
    ]
    for i, name in enumerate(zo_names):
        row3[109 + i] = name
    # Connections
    row3[127] = "Zone 1"
    row3[128] = "Zone 2"
    row3[129] = "Value"
    row3[130] = "Wide"
    row3[131] = "Border Guard"
    row3[132] = "Road"
    row3[133] = "Type"
    row3[134] = "Fictive"
    row3[135] = "Portal repulsion"
    row3[136] = "Minimum human positions"
    row3[137] = "Maximum human positions"
    row3[138] = "Minimum total positions"
    row3[139] = "Maximum total positions"

    return [row1, row2, row3]
