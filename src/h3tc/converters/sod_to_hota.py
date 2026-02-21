"""Convert SOD template packs to HOTA format."""

from h3tc.constants import SOD_TO_HOTA_DEFAULTS
from h3tc.enums import MONSTER_FACTIONS_HOTA, TERRAINS_HOTA, TOWN_FACTIONS_HOTA
from h3tc.models import (
    Connection,
    FieldCounts,
    MapOptions,
    PackMetadata,
    TemplatePack,
    TemplateMap,
    Zone,
    ZoneOptions,
)


def sod_to_hota(pack: TemplatePack, pack_name: str = "") -> TemplatePack:
    """Convert a SOD TemplatePack to HOTA format."""
    defaults = SOD_TO_HOTA_DEFAULTS

    fc_vals = defaults["field_counts"]
    field_counts = FieldCounts(
        town=fc_vals[0],
        terrain=fc_vals[1],
        zone_type=fc_vals[2],
        pack_new=fc_vals[3],
        map_new=fc_vals[4],
        zone_new=fc_vals[5],
        connection_new=fc_vals[6],
    )

    metadata = PackMetadata(name=pack_name)

    # Build HOTA header rows (3 rows)
    header_rows = _build_hota_headers()

    hota_maps = []
    for tmap in pack.maps:
        hota_map = _convert_map(tmap, defaults)
        hota_maps.append(hota_map)

    return TemplatePack(
        metadata=metadata,
        field_counts=field_counts,
        maps=hota_maps,
        header_rows=header_rows,
    )


def _convert_map(tmap: TemplateMap, defaults: dict) -> TemplateMap:
    """Convert a single map from SOD to HOTA."""
    zones = [_convert_zone(z, defaults) for z in tmap.zones]
    connections = [_convert_connection(c, defaults) for c in tmap.connections]

    return TemplateMap(
        name=tmap.name,
        min_size=tmap.min_size,
        max_size=tmap.max_size,
        options=MapOptions(
            artifacts="",
            combo_arts="",
            spells="",
            secondary_skills="",
            objects="",
            rock_blocks="",
            zone_sparseness="",
            special_weeks_disabled="x",
            spell_research="x",
            anarchy="x",
        ),
        zones=zones,
        connections=connections,
    )


def _any_enabled(values: dict[str, str], keys: list[str]) -> bool:
    """Check if any of the given keys have 'x' in the values dict."""
    return any(values.get(k, "").strip() == "x" for k in keys)


def _all_enabled(values: dict[str, str], keys: list[str]) -> bool:
    """Check if all given keys have 'x' in the values dict."""
    return all(values.get(k, "").strip() == "x" for k in keys)


# SOD-era keys for conditional enable checks
_SOD_TOWN_KEYS = [
    "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Conflux",
]
_SOD_TERRAIN_KEYS = [
    "Dirt", "Sand", "Grass", "Snow", "Swamp", "Rough", "Cave", "Lava",
]
_SOD_MONSTER_KEYS = [
    "Neutral", "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress",
]
# Includes Forge — used for Conflux auto-enable (only when all SOD factions on)
_SOD_MONSTER_KEYS_ALL = [
    "Neutral", "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Forge",
]


def _convert_zone(zone: Zone, defaults: dict) -> Zone:
    """Convert a zone from SOD to HOTA format."""
    # Town types: if any SOD factions enabled, also enable Cove/Factory
    any_towns_on = _any_enabled(zone.town_types, _SOD_TOWN_KEYS)
    town_types = {}
    for faction in TOWN_FACTIONS_HOTA:
        if faction in ("Cove", "Factory"):
            town_types[faction] = "x" if any_towns_on else ""
        else:
            town_types[faction] = zone.town_types.get(faction, "")

    # Terrains: if all SOD terrains enabled, also enable Highlands/Wasteland
    all_terrains_on = _all_enabled(zone.terrains, _SOD_TERRAIN_KEYS)
    terrains = {}
    for terrain in TERRAINS_HOTA:
        if terrain in ("Highlands", "Wasteland"):
            terrains[terrain] = "x" if all_terrains_on else ""
        else:
            terrains[terrain] = zone.terrains.get(terrain, "")

    # Monster factions: drop Forge; Cove/Factory enabled when any SOD faction on;
    # Conflux enabled only when all SOD factions (including Forge) are on
    any_monsters_on = _any_enabled(zone.monster_factions, _SOD_MONSTER_KEYS)
    all_monsters_on = _all_enabled(zone.monster_factions, _SOD_MONSTER_KEYS_ALL)
    monster_factions = {}
    for faction in MONSTER_FACTIONS_HOTA:
        if faction in zone.monster_factions:
            monster_factions[faction] = zone.monster_factions[faction]
        elif faction == "Conflux":
            monster_factions[faction] = "x" if all_monsters_on else ""
        elif faction in ("Cove", "Factory"):
            monster_factions[faction] = "x" if any_monsters_on else ""
        else:
            monster_factions[faction] = ""

    # Zone options from defaults
    zo_defaults = defaults["zone_options"]
    zone_options = ZoneOptions(**zo_defaults)

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
        terrains=terrains,
        monster_strength=zone.monster_strength,
        monster_match=zone.monster_match,
        monster_factions=monster_factions,
        treasure_tiers=[t.model_copy() for t in zone.treasure_tiers],
        zone_options=zone_options,
    )


def _convert_connection(conn: Connection, defaults: dict) -> Connection:
    """Convert a connection from SOD to HOTA format."""
    conn_defaults = defaults["connection"]
    return Connection(
        zone1=conn.zone1,
        zone2=conn.zone2,
        value=conn.value,
        wide=conn.wide,
        border_guard=conn.border_guard,
        positions=conn.positions.model_copy(),
        road=conn_defaults["road"],
        conn_type=conn_defaults["conn_type"],
        fictive=conn_defaults["fictive"],
        portal_repulsion=conn_defaults["portal_repulsion"],
    )


def _build_hota_headers() -> list[list[str]]:
    """Build standard HOTA header rows."""
    # Row 1: section headers
    row1 = [""] * 139
    row1[15] = "Map"
    row1[28] = "Zone"
    row1[125] = "Connections"

    # Row 2: subsection headers
    row2 = [""] * 139
    row2[29] = "Type"
    row2[34] = "Restrictions"
    row2[39] = "Player towns"
    row2[43] = "Neutral towns"
    row2[48] = "Town types"
    row2[59] = "Minimum mines"
    row2[66] = "Mine Density"
    row2[73] = "Terrain"
    row2[84] = "Monsters"
    row2[98] = "Treasure"
    row2[107] = "Zone Options"
    row2[125] = "Zones"
    row2[130] = "Connection Options"
    row2[134] = "Restrictions"

    # Row 3: column headers
    row3 = [""] * 139
    # Field counts
    fc_names = ["Town", "Terrain", "Zone type", "Pack new", "Map new", "Zone new", "Connection new"]
    for i, name in enumerate(fc_names):
        row3[i] = name
    # Pack metadata
    row3[7] = "Pack name"
    row3[8] = "Description"
    row3[9] = "Town selection"
    row3[10] = "Heroes"
    row3[11] = "Mirror"
    row3[12] = "Tags"
    row3[13] = "Max battle rounds"
    row3[14] = "Forbid hiring heroes"
    # Map
    row3[15] = "Name"
    row3[16] = "Minimum Size"
    row3[17] = "Maximum Size"
    row3[18] = "Artifacts"
    row3[19] = "Combo arts"
    row3[20] = "Spells"
    row3[21] = "Secondary skills"
    row3[22] = "Objects"
    row3[23] = "Rock blocks"
    row3[24] = "Zone sparseness"
    row3[25] = "Special weeks disabled"
    row3[26] = "Spell research"
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
    # Town types
    for i, faction in enumerate(TOWN_FACTIONS_HOTA):
        row3[48 + i] = faction
    # Mines
    from h3tc.enums import RESOURCES
    for i, res in enumerate(RESOURCES):
        row3[59 + i] = res
        row3[66 + i] = res
    # Terrain
    row3[73] = "Match to town"
    for i, terrain in enumerate(TERRAINS_HOTA):
        row3[74 + i] = terrain
    # Monsters
    row3[84] = "Strength"
    row3[85] = "Match to town"
    for i, faction in enumerate(MONSTER_FACTIONS_HOTA):
        row3[86 + i] = faction
    # Treasure
    for tier in range(3):
        row3[98 + tier * 3] = "Low"
        row3[98 + tier * 3 + 1] = "High"
        row3[98 + tier * 3 + 2] = "Density"
    # Zone options
    zo_names = [
        "Placement", "Objects", "Min objects", "Image settings",
        "Force neutral creatures", "Allow non coherent road", "Zone repulsion",
        "Town hint", "Monsters disposition standard", "Monsters disposition custom",
        "Monsters joining percentage", "Monsters join only for money",
        "Min airship shipyards", "Airship shipyard density",
        "Terrain hint", "Allowed factions", "Faction hint", "Max block value",
    ]
    for i, name in enumerate(zo_names):
        row3[107 + i] = name
    # Connections
    row3[125] = "Zone 1"
    row3[126] = "Zone 2"
    row3[127] = "Value"
    row3[128] = "Wide"
    row3[129] = "Border Guard"
    row3[130] = "Road"
    row3[131] = "Type"
    row3[132] = "Fictive"
    row3[133] = "Portal repulsion"
    row3[134] = "Minimum human positions"
    row3[135] = "Maximum human positions"
    row3[136] = "Minimum total positions"
    row3[137] = "Maximum total positions"

    return [row1, row2, row3]
