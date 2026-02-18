"""Convert HOTA template packs to SOD format."""

from h3tc.enums import MONSTER_FACTIONS_SOD, TERRAINS_SOD, TOWN_FACTIONS_SOD
from h3tc.models import (
    Connection,
    TemplatePack,
    TemplateMap,
    Zone,
    ZoneOptions,
)


def hota_to_sod(pack: TemplatePack) -> TemplatePack:
    """Convert a HOTA TemplatePack to SOD format."""
    # Build SOD header rows from original or generate defaults
    header_rows = _build_sod_headers()

    sod_maps = []
    for tmap in pack.maps:
        sod_map = _convert_map(tmap)
        sod_maps.append(sod_map)

    return TemplatePack(
        metadata=None,
        field_counts=None,
        maps=sod_maps,
        header_rows=header_rows,
    )


def _convert_map(tmap: TemplateMap) -> TemplateMap:
    """Convert a single map from HOTA to SOD."""
    zones = [_convert_zone(z) for z in tmap.zones]
    connections = [_convert_connection(c) for c in tmap.connections]

    return TemplateMap(
        name=tmap.name,
        min_size=tmap.min_size,
        max_size=tmap.max_size,
        zones=zones,
        connections=connections,
    )


def _convert_zone(zone: Zone) -> Zone:
    """Convert a zone from HOTA to SOD format."""
    # Town types: map to SOD factions, Elemental = Conflux
    town_types = {}
    for sod_name in TOWN_FACTIONS_SOD:
        canonical = "Conflux" if sod_name == "Elemental" else sod_name
        town_types[canonical] = zone.town_types.get(canonical, "")

    # Terrains: keep only SOD terrains (drop Highlands, Wasteland)
    terrains = {}
    for terrain in TERRAINS_SOD:
        terrains[terrain] = zone.terrains.get(terrain, "")

    # Monster factions: drop Conflux/Cove/Factory, add Forge as "x"
    monster_factions = {}
    for faction in MONSTER_FACTIONS_SOD:
        if faction == "Forge":
            monster_factions[faction] = "x"
        elif faction in zone.monster_factions:
            monster_factions[faction] = zone.monster_factions[faction]
        else:
            monster_factions[faction] = ""

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
        zone_options=ZoneOptions(),  # Strip all zone options
    )


def _convert_connection(conn: Connection) -> Connection:
    """Convert a connection from HOTA to SOD format."""
    return Connection(
        zone1=conn.zone1,
        zone2=conn.zone2,
        value=conn.value,
        wide=conn.wide,
        border_guard=conn.border_guard,
        positions=conn.positions.model_copy(),
        road=None,
        conn_type=None,
        fictive=None,
        portal_repulsion=None,
    )


def _build_sod_headers() -> list[list[str]]:
    """Build standard SOD header rows."""
    from h3tc.enums import RESOURCES

    # Row 1: section headers
    row1 = [""] * 85
    row1[0] = "Map"
    row1[3] = "Zone"
    row1[76] = "Connections"

    # Row 2: subsection headers
    row2 = [""] * 85
    row2[4] = "Type"
    row2[9] = "Restrictions"
    row2[14] = "Player towns"
    row2[18] = "Neutral towns"
    row2[23] = "Town types"
    row2[32] = "Minimum mines"
    row2[39] = "Mine Density"
    row2[46] = "Terrain"
    row2[55] = "Monsters"
    row2[67] = "Treasure"
    row2[76] = "Zones"
    row2[80] = "Restrictions"

    # Row 3: column headers
    row3 = [""] * 85
    row3[0] = "Name"
    row3[1] = "Minimum Size"
    row3[2] = "Maximum Size"
    row3[3] = "Id"
    row3[4] = "human start"
    row3[5] = "computer start"
    row3[6] = "Treasure"
    row3[7] = "Junction"
    row3[8] = "Base Size"
    row3[9] = "Minimum human positions"
    row3[10] = "Maximum human positions"
    row3[11] = "Minimum total positions"
    row3[12] = "Maximum total positions"
    row3[13] = "Ownership"
    row3[14] = "Minimum towns"
    row3[15] = "Minimum castles"
    row3[16] = "Town Density"
    row3[17] = "Castle Density"
    row3[18] = "Minimum towns"
    row3[19] = "Minimum castles"
    row3[20] = "Town Density"
    row3[21] = "Castle Density"
    row3[22] = "Towns are of same type"
    for i, faction in enumerate(TOWN_FACTIONS_SOD):
        row3[23 + i] = faction
    for i, res in enumerate(RESOURCES):
        row3[32 + i] = res
        row3[39 + i] = res
    row3[46] = "Match to town"
    for i, terrain in enumerate(TERRAINS_SOD):
        row3[47 + i] = terrain
    row3[55] = "Strength"
    row3[56] = "Match to town"
    for i, faction in enumerate(MONSTER_FACTIONS_SOD):
        row3[57 + i] = faction
    for tier in range(3):
        row3[67 + tier * 3] = "Low"
        row3[67 + tier * 3 + 1] = "High"
        row3[67 + tier * 3 + 2] = "Density"
    row3[76] = "Zone 1"
    row3[77] = "Zone 2"
    row3[78] = "Value"
    row3[79] = "Wide"
    row3[80] = "Border Guard"
    row3[81] = "Minimum human positions"
    row3[82] = "Maximum human positions"
    row3[83] = "Minimum total positions"
    row3[84] = "Maximum total positions"

    return [row1, row2, row3]
