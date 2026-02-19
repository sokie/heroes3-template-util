"""SOD format writer for H3 template packs."""

import csv
import io
from pathlib import Path

from h3tc.constants import SodCol
from h3tc.enums import MONSTER_FACTIONS_SOD, RESOURCES, TERRAINS_SOD, TOWN_FACTIONS_SOD
from h3tc.models import Connection, TemplatePack, TemplateMap, Zone
from h3tc.writers.base import BaseWriter


class SodWriter(BaseWriter):
    format_id = "sod"
    format_name = "SOD"

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
        for tmap in pack.maps:
            self._write_map(writer, tmap)

        text = output.getvalue()
        try:
            filepath.write_bytes(text.encode("ascii"))
        except UnicodeEncodeError:
            filepath.write_bytes(text.encode("latin-1"))

    def _write_map(self, writer: csv.writer, tmap: TemplateMap) -> None:
        zones = tmap.zones
        conns = tmap.connections
        max_rows = max(len(zones), len(conns), 1)  # At least 1 row for map name

        for i in range(max_rows):
            row = [""] * SodCol.ACTIVE_COLS

            # Map name only on first row
            if i == 0:
                row[SodCol.NAME] = tmap.name
                row[SodCol.MIN_SIZE] = tmap.min_size
                row[SodCol.MAX_SIZE] = tmap.max_size

            # Zone data
            if i < len(zones):
                self._fill_zone(row, zones[i])

            # Connection data
            if i < len(conns):
                self._fill_connection(row, conns[i])

            writer.writerow(row)

    def _fill_zone(self, row: list[str], zone: Zone) -> None:
        c = SodCol
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

        # Town types - map canonical names back to SOD column positions
        for i, sod_name in enumerate(TOWN_FACTIONS_SOD):
            canonical = "Conflux" if sod_name == "Elemental" else sod_name
            row[c.TOWN_TYPES_START + i] = zone.town_types.get(canonical, "")

        # Min mines
        for i, resource in enumerate(RESOURCES):
            row[c.MIN_MINES_START + i] = zone.min_mines.get(resource, "")

        # Mine density
        for i, resource in enumerate(RESOURCES):
            row[c.MINE_DENSITY_START + i] = zone.mine_density.get(resource, "")

        row[c.TERRAIN_MATCH] = zone.terrain_match

        # Terrains
        for i, terrain in enumerate(TERRAINS_SOD):
            row[c.TERRAINS_START + i] = zone.terrains.get(terrain, "")

        row[c.MONSTER_STRENGTH] = zone.monster_strength
        row[c.MONSTER_MATCH] = zone.monster_match

        # Monster factions - write all SOD factions including Forge
        for i, faction in enumerate(MONSTER_FACTIONS_SOD):
            row[c.MONSTER_FACTIONS_START + i] = zone.monster_factions.get(faction, "")

        # Treasure tiers
        for tier_idx, tier in enumerate(zone.treasure_tiers):
            offset = c.TREASURE_START + tier_idx * 3
            row[offset] = tier.low
            row[offset + 1] = tier.high
            row[offset + 2] = tier.density

    def _fill_connection(self, row: list[str], conn: Connection) -> None:
        c = SodCol
        # Restore extra zone-area columns from connection-only rows
        for col_idx, val in conn.extra_zone_cols.items():
            if col_idx < len(row):
                row[col_idx] = val
        row[c.CONN_ZONE1] = conn.zone1
        row[c.CONN_ZONE2] = conn.zone2
        row[c.CONN_VALUE] = conn.value
        row[c.CONN_WIDE] = conn.wide
        row[c.CONN_BORDER_GUARD] = conn.border_guard
        row[c.CONN_MIN_HUMAN_POS] = conn.positions.min_human
        row[c.CONN_MAX_HUMAN_POS] = conn.positions.max_human
        row[c.CONN_MIN_TOTAL_POS] = conn.positions.min_total
        row[c.CONN_MAX_TOTAL_POS] = conn.positions.max_total
