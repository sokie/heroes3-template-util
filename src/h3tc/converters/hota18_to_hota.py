"""Convert HOTA 1.8.x template packs to HOTA 1.7.x format."""

from h3tc.enums import MONSTER_FACTIONS_HOTA, TOWN_FACTIONS_HOTA
from h3tc.models import (
    Connection,
    TemplatePack,
    TemplateMap,
    Zone,
)


def hota18_to_hota(pack: TemplatePack) -> TemplatePack:
    """Convert a HOTA 1.8.x TemplatePack to HOTA 1.7.x format."""
    # Update field counts: town 12 -> 11
    field_counts = None
    if pack.field_counts:
        field_counts = pack.field_counts.model_copy(update={"town": "11"})

    header_rows = _build_hota_headers()

    hota_maps = []
    for tmap in pack.maps:
        hota_map = _convert_map(tmap)
        hota_maps.append(hota_map)

    return TemplatePack(
        metadata=pack.metadata.model_copy() if pack.metadata else None,
        field_counts=field_counts,
        maps=hota_maps,
        header_rows=header_rows,
    )


def _convert_map(tmap: TemplateMap) -> TemplateMap:
    """Convert a single map from HOTA 1.8.x to 1.7.x."""
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


def _convert_zone(zone: Zone) -> Zone:
    """Convert a zone from HOTA 1.8.x to 1.7.x — remove Bulwark."""
    # Town types: keep only HOTA 1.7.x factions
    town_types = {f: zone.town_types.get(f, "") for f in TOWN_FACTIONS_HOTA}

    # Monster factions: keep only HOTA 1.7.x factions
    monster_factions = {f: zone.monster_factions.get(f, "") for f in MONSTER_FACTIONS_HOTA}

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


def _build_hota_headers() -> list[list[str]]:
    """Build standard HOTA 1.7.x header rows."""
    from h3tc.converters.sod_to_hota import _build_hota_headers
    return _build_hota_headers()
