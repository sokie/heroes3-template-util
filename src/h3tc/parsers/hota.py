"""HOTA format parser for H3 template packs."""

import csv
import io
from pathlib import Path

from h3tc.constants import ZONE_OPTION_FIELDS, HotaCol
from h3tc.enums import MONSTER_FACTIONS_HOTA, RESOURCES, TERRAINS_HOTA, TOWN_FACTIONS_HOTA
from h3tc.models import (
    Connection,
    FieldCounts,
    MapOptions,
    PackMetadata,
    PositionConstraints,
    TemplatePack,
    TemplateMap,
    TownSettings,
    TreasureTier,
    Zone,
    ZoneOptions,
)
from h3tc.parsers.base import BaseParser


class HotaParser(BaseParser):
    def parse(self, filepath: Path) -> TemplatePack:
        raw = filepath.read_bytes()
        try:
            text = raw.decode("ascii")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        reader = csv.reader(io.StringIO(text), delimiter="\t", quotechar='"')
        rows = list(reader)

        header_rows = [rows[0], rows[1], rows[2]]
        data_rows = rows[3:]

        pack = TemplatePack(header_rows=header_rows)
        current_map: TemplateMap | None = None

        for row_num, row in enumerate(data_rows):
            while len(row) < HotaCol.TOTAL + 1:
                row.append("")

            # First data row (row 4) has field counts and pack metadata
            if row_num == 0:
                pack.field_counts = FieldCounts(
                    town=row[HotaCol.FIELD_COUNT_TOWN],
                    terrain=row[HotaCol.FIELD_COUNT_TERRAIN],
                    zone_type=row[HotaCol.FIELD_COUNT_ZONE_TYPE],
                    pack_new=row[HotaCol.FIELD_COUNT_PACK_NEW],
                    map_new=row[HotaCol.FIELD_COUNT_MAP_NEW],
                    zone_new=row[HotaCol.FIELD_COUNT_ZONE_NEW],
                    connection_new=row[HotaCol.FIELD_COUNT_CONN_NEW],
                )
                pack.metadata = PackMetadata(
                    name=row[HotaCol.PACK_NAME],
                    description=row[HotaCol.PACK_DESC],
                    town_selection=row[HotaCol.PACK_TOWN_SELECTION],
                    heroes=row[HotaCol.PACK_HEROES],
                    mirror=row[HotaCol.PACK_MIRROR],
                    tags=row[HotaCol.PACK_TAGS],
                    max_battle_rounds=row[HotaCol.PACK_MAX_BATTLE_ROUNDS],
                    forbid_hiring_heroes=row[HotaCol.PACK_FORBID_HIRING_HEROES],
                )

            map_name = row[HotaCol.MAP_NAME].strip()
            zone_id = row[HotaCol.ZONE_ID].strip()
            has_conn = any(
                row[j].strip()
                for j in range(HotaCol.CONN_ZONE1, HotaCol.CONN_MAX_TOTAL_POS + 1)
            )

            # New map starts when Map Name is non-empty
            if map_name:
                current_map = TemplateMap(
                    name=map_name,
                    min_size=row[HotaCol.MAP_MIN_SIZE],
                    max_size=row[HotaCol.MAP_MAX_SIZE],
                    options=MapOptions(
                        artifacts=row[HotaCol.MAP_ARTIFACTS],
                        combo_arts=row[HotaCol.MAP_COMBO_ARTS],
                        spells=row[HotaCol.MAP_SPELLS],
                        secondary_skills=row[HotaCol.MAP_SECONDARY_SKILLS],
                        objects=row[HotaCol.MAP_OBJECTS],
                        rock_blocks=row[HotaCol.MAP_ROCK_BLOCKS],
                        zone_sparseness=row[HotaCol.MAP_ZONE_SPARSENESS],
                        special_weeks_disabled=row[HotaCol.MAP_SPECIAL_WEEKS_DISABLED],
                        spell_research=row[HotaCol.MAP_SPELL_RESEARCH],
                        anarchy=row[HotaCol.MAP_ANARCHY],
                    ),
                )
                pack.maps.append(current_map)

            if current_map is None:
                continue

            if not zone_id and not has_conn:
                continue

            if zone_id:
                zone = self._parse_zone(row)
                current_map.zones.append(zone)

            if has_conn:
                conn = self._parse_connection(row)
                if not zone_id:
                    for j in range(HotaCol.ZONE_ID, HotaCol.CONN_ZONE1):
                        if row[j].strip():
                            conn.extra_zone_cols[j] = row[j]
                current_map.connections.append(conn)

        return pack

    def _parse_zone(self, row: list[str]) -> Zone:
        c = HotaCol

        town_types = {}
        for i, faction in enumerate(TOWN_FACTIONS_HOTA):
            town_types[faction] = row[c.TOWN_TYPES_START + i]

        min_mines = {}
        for i, resource in enumerate(RESOURCES):
            min_mines[resource] = row[c.MIN_MINES_START + i]

        mine_density = {}
        for i, resource in enumerate(RESOURCES):
            mine_density[resource] = row[c.MINE_DENSITY_START + i]

        terrains = {}
        for i, terrain in enumerate(TERRAINS_HOTA):
            terrains[terrain] = row[c.TERRAINS_START + i]

        monster_factions = {}
        for i, faction in enumerate(MONSTER_FACTIONS_HOTA):
            monster_factions[faction] = row[c.MONSTER_FACTIONS_START + i]

        treasure_tiers = []
        for tier in range(3):
            offset = c.TREASURE_START + tier * 3
            treasure_tiers.append(TreasureTier(
                low=row[offset],
                high=row[offset + 1],
                density=row[offset + 2],
            ))

        # Zone options
        zone_opt_values = [
            row[c.ZONE_OPTIONS_START + i] for i in range(c.ZONE_OPTIONS_COUNT)
        ]
        zone_options = ZoneOptions(**dict(zip(ZONE_OPTION_FIELDS, zone_opt_values)))

        return Zone(
            id=row[c.ZONE_ID],
            human_start=row[c.HUMAN_START],
            computer_start=row[c.COMPUTER_START],
            treasure=row[c.TREASURE],
            junction=row[c.JUNCTION],
            base_size=row[c.BASE_SIZE],
            positions=PositionConstraints(
                min_human=row[c.MIN_HUMAN_POS],
                max_human=row[c.MAX_HUMAN_POS],
                min_total=row[c.MIN_TOTAL_POS],
                max_total=row[c.MAX_TOTAL_POS],
            ),
            ownership=row[c.OWNERSHIP],
            player_towns=TownSettings(
                min_towns=row[c.PLAYER_MIN_TOWNS],
                min_castles=row[c.PLAYER_MIN_CASTLES],
                town_density=row[c.PLAYER_TOWN_DENSITY],
                castle_density=row[c.PLAYER_CASTLE_DENSITY],
            ),
            neutral_towns=TownSettings(
                min_towns=row[c.NEUTRAL_MIN_TOWNS],
                min_castles=row[c.NEUTRAL_MIN_CASTLES],
                town_density=row[c.NEUTRAL_TOWN_DENSITY],
                castle_density=row[c.NEUTRAL_CASTLE_DENSITY],
            ),
            towns_same_type=row[c.TOWNS_SAME_TYPE],
            town_types=town_types,
            min_mines=min_mines,
            mine_density=mine_density,
            terrain_match=row[c.TERRAIN_MATCH],
            terrains=terrains,
            monster_strength=row[c.MONSTER_STRENGTH],
            monster_match=row[c.MONSTER_MATCH],
            monster_factions=monster_factions,
            treasure_tiers=treasure_tiers,
            zone_options=zone_options,
        )

    def _parse_connection(self, row: list[str]) -> Connection:
        c = HotaCol
        return Connection(
            zone1=row[c.CONN_ZONE1],
            zone2=row[c.CONN_ZONE2],
            value=row[c.CONN_VALUE],
            wide=row[c.CONN_WIDE],
            border_guard=row[c.CONN_BORDER_GUARD],
            positions=PositionConstraints(
                min_human=row[c.CONN_MIN_HUMAN_POS],
                max_human=row[c.CONN_MAX_HUMAN_POS],
                min_total=row[c.CONN_MIN_TOTAL_POS],
                max_total=row[c.CONN_MAX_TOTAL_POS],
            ),
            road=row[c.CONN_ROAD],
            conn_type=row[c.CONN_TYPE],
            fictive=row[c.CONN_FICTIVE],
            portal_repulsion=row[c.CONN_PORTAL_REPULSION],
        )
