"""HOTA format writer for H3 template packs."""

import csv
import io
from pathlib import Path

from h3tc.constants import ZONE_OPTION_FIELDS, HotaCol
from h3tc.enums import MONSTER_FACTIONS_HOTA, RESOURCES, TERRAINS_HOTA, TOWN_FACTIONS_HOTA
from h3tc.models import Connection, TemplatePack, TemplateMap, Zone
from h3tc.writers.base import BaseWriter


class HotaWriter(BaseWriter):
    def write(self, pack: TemplatePack, filepath: Path) -> None:
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter="\t",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n",
        )

        # Write header rows
        for header_row in pack.header_rows:
            writer.writerow(header_row)

        # Write data rows
        first_data_row = True
        for tmap in pack.maps:
            self._write_map(writer, pack, tmap, first_data_row)
            first_data_row = False

        text = output.getvalue()
        try:
            filepath.write_bytes(text.encode("ascii"))
        except UnicodeEncodeError:
            filepath.write_bytes(text.encode("latin-1"))

    def _write_map(
        self,
        writer: csv.writer,
        pack: TemplatePack,
        tmap: TemplateMap,
        first_data_row: bool,
    ) -> None:
        zones = tmap.zones
        conns = tmap.connections
        max_rows = max(len(zones), len(conns), 1)  # At least 1 row for map name

        for i in range(max_rows):
            row = [""] * (HotaCol.TOTAL + 1)

            # First data row of first map: field counts + pack metadata
            if first_data_row and i == 0 and pack.field_counts and pack.metadata:
                fc = pack.field_counts
                row[HotaCol.FIELD_COUNT_TOWN] = fc.town
                row[HotaCol.FIELD_COUNT_TERRAIN] = fc.terrain
                row[HotaCol.FIELD_COUNT_ZONE_TYPE] = fc.zone_type
                row[HotaCol.FIELD_COUNT_PACK_NEW] = fc.pack_new
                row[HotaCol.FIELD_COUNT_MAP_NEW] = fc.map_new
                row[HotaCol.FIELD_COUNT_ZONE_NEW] = fc.zone_new
                row[HotaCol.FIELD_COUNT_CONN_NEW] = fc.connection_new

                pm = pack.metadata
                row[HotaCol.PACK_NAME] = pm.name
                row[HotaCol.PACK_DESC] = pm.description
                row[HotaCol.PACK_TOWN_SELECTION] = pm.town_selection
                row[HotaCol.PACK_HEROES] = pm.heroes
                row[HotaCol.PACK_MIRROR] = pm.mirror
                row[HotaCol.PACK_TAGS] = pm.tags
                row[HotaCol.PACK_MAX_BATTLE_ROUNDS] = pm.max_battle_rounds
                row[HotaCol.PACK_FORBID_HIRING_HEROES] = pm.forbid_hiring_heroes

            # Map name on first row of each map
            if i == 0:
                row[HotaCol.MAP_NAME] = tmap.name
                row[HotaCol.MAP_MIN_SIZE] = tmap.min_size
                row[HotaCol.MAP_MAX_SIZE] = tmap.max_size

                opts = tmap.options
                if opts.artifacts is not None:
                    row[HotaCol.MAP_ARTIFACTS] = opts.artifacts
                if opts.combo_arts is not None:
                    row[HotaCol.MAP_COMBO_ARTS] = opts.combo_arts
                if opts.spells is not None:
                    row[HotaCol.MAP_SPELLS] = opts.spells
                if opts.secondary_skills is not None:
                    row[HotaCol.MAP_SECONDARY_SKILLS] = opts.secondary_skills
                if opts.objects is not None:
                    row[HotaCol.MAP_OBJECTS] = opts.objects
                if opts.rock_blocks is not None:
                    row[HotaCol.MAP_ROCK_BLOCKS] = opts.rock_blocks
                if opts.zone_sparseness is not None:
                    row[HotaCol.MAP_ZONE_SPARSENESS] = opts.zone_sparseness
                if opts.special_weeks_disabled is not None:
                    row[HotaCol.MAP_SPECIAL_WEEKS_DISABLED] = opts.special_weeks_disabled
                if opts.spell_research is not None:
                    row[HotaCol.MAP_SPELL_RESEARCH] = opts.spell_research
                if opts.anarchy is not None:
                    row[HotaCol.MAP_ANARCHY] = opts.anarchy

            if i < len(zones):
                self._fill_zone(row, zones[i])

            if i < len(conns):
                self._fill_connection(row, conns[i])

            writer.writerow(row)

    def _fill_zone(self, row: list[str], zone: Zone) -> None:
        c = HotaCol
        row[c.ZONE_ID] = zone.id
        row[c.HUMAN_START] = zone.human_start
        row[c.COMPUTER_START] = zone.computer_start
        row[c.TREASURE] = zone.treasure
        row[c.JUNCTION] = zone.junction
        row[c.BASE_SIZE] = zone.base_size

        row[c.MIN_HUMAN_POS] = zone.positions.min_human
        row[c.MAX_HUMAN_POS] = zone.positions.max_human
        row[c.MIN_TOTAL_POS] = zone.positions.min_total
        row[c.MAX_TOTAL_POS] = zone.positions.max_total

        row[c.OWNERSHIP] = zone.ownership

        row[c.PLAYER_MIN_TOWNS] = zone.player_towns.min_towns
        row[c.PLAYER_MIN_CASTLES] = zone.player_towns.min_castles
        row[c.PLAYER_TOWN_DENSITY] = zone.player_towns.town_density
        row[c.PLAYER_CASTLE_DENSITY] = zone.player_towns.castle_density

        row[c.NEUTRAL_MIN_TOWNS] = zone.neutral_towns.min_towns
        row[c.NEUTRAL_MIN_CASTLES] = zone.neutral_towns.min_castles
        row[c.NEUTRAL_TOWN_DENSITY] = zone.neutral_towns.town_density
        row[c.NEUTRAL_CASTLE_DENSITY] = zone.neutral_towns.castle_density

        row[c.TOWNS_SAME_TYPE] = zone.towns_same_type

        for i, faction in enumerate(TOWN_FACTIONS_HOTA):
            row[c.TOWN_TYPES_START + i] = zone.town_types.get(faction, "")

        for i, resource in enumerate(RESOURCES):
            row[c.MIN_MINES_START + i] = zone.min_mines.get(resource, "")

        for i, resource in enumerate(RESOURCES):
            row[c.MINE_DENSITY_START + i] = zone.mine_density.get(resource, "")

        row[c.TERRAIN_MATCH] = zone.terrain_match

        for i, terrain in enumerate(TERRAINS_HOTA):
            row[c.TERRAINS_START + i] = zone.terrains.get(terrain, "")

        row[c.MONSTER_STRENGTH] = zone.monster_strength
        row[c.MONSTER_MATCH] = zone.monster_match

        for i, faction in enumerate(MONSTER_FACTIONS_HOTA):
            row[c.MONSTER_FACTIONS_START + i] = zone.monster_factions.get(faction, "")

        for tier_idx, tier in enumerate(zone.treasure_tiers):
            offset = c.TREASURE_START + tier_idx * 3
            row[offset] = tier.low
            row[offset + 1] = tier.high
            row[offset + 2] = tier.density

        # Zone options
        zo = zone.zone_options
        for i, field in enumerate(ZONE_OPTION_FIELDS):
            val = getattr(zo, field)
            if val is not None:
                row[c.ZONE_OPTIONS_START + i] = val

    def _fill_connection(self, row: list[str], conn: Connection) -> None:
        c = HotaCol
        for col_idx, val in conn.extra_zone_cols.items():
            if col_idx < len(row):
                row[col_idx] = val
        row[c.CONN_ZONE1] = conn.zone1
        row[c.CONN_ZONE2] = conn.zone2
        row[c.CONN_VALUE] = conn.value
        row[c.CONN_WIDE] = conn.wide
        row[c.CONN_BORDER_GUARD] = conn.border_guard
        if conn.road is not None:
            row[c.CONN_ROAD] = conn.road
        if conn.conn_type is not None:
            row[c.CONN_TYPE] = conn.conn_type
        if conn.fictive is not None:
            row[c.CONN_FICTIVE] = conn.fictive
        if conn.portal_repulsion is not None:
            row[c.CONN_PORTAL_REPULSION] = conn.portal_repulsion
        row[c.CONN_MIN_HUMAN_POS] = conn.positions.min_human
        row[c.CONN_MAX_HUMAN_POS] = conn.positions.max_human
        row[c.CONN_MIN_TOTAL_POS] = conn.positions.min_total
        row[c.CONN_MAX_TOTAL_POS] = conn.positions.max_total
