"""SOD format parser for H3 template packs."""

import csv
import io
from pathlib import Path

from h3tc.constants import SodCol
from h3tc.enums import MONSTER_FACTIONS_SOD, RESOURCES, TERRAINS_SOD, TOWN_FACTIONS_SOD
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
from h3tc.parsers.base import BaseParser

# Canonical names: SOD "Elemental" -> "Conflux"
_SOD_TOWN_CANONICAL = [
    f if f != "Elemental" else "Conflux" for f in TOWN_FACTIONS_SOD
]


class SodParser(BaseParser):
    format_id = "sod"
    format_name = "SOD"

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

        for row in data_rows:
            # Pad row to minimum width for parsing
            while len(row) < SodCol.ACTIVE_COLS:
                row.append("")

            name = row[SodCol.NAME].strip()
            zone_id = row[SodCol.ZONE_ID].strip()
            has_conn = any(
                row[j].strip()
                for j in range(SodCol.CONN_ZONE1, SodCol.CONN_MAX_TOTAL_POS + 1)
            )

            # New map starts when Name column is non-empty
            if name:
                current_map = TemplateMap(
                    name=name,
                    min_size=row[SodCol.MIN_SIZE],
                    max_size=row[SodCol.MAX_SIZE],
                )
                pack.maps.append(current_map)

            # Skip empty rows (no zone, no connection)
            if not zone_id and not has_conn:
                continue

            if current_map is None:
                continue

            # Parse zone if zone ID is present
            if zone_id:
                zone = self._parse_zone(row)
                current_map.zones.append(zone)

            # Parse connection if any connection column has data
            if has_conn:
                conn = self._parse_connection(row)
                # Capture extra zone-area columns on connection-only rows
                if not zone_id:
                    for j in range(SodCol.ZONE_ID, SodCol.CONN_ZONE1):
                        if row[j].strip():
                            conn.extra_zone_cols[j] = row[j]
                current_map.connections.append(conn)

        return pack

    def _parse_zone(self, row: list[str]) -> Zone:
        c = SodCol

        town_types = {}
        for i, faction in enumerate(_SOD_TOWN_CANONICAL):
            town_types[faction] = row[c.TOWN_TYPES_START + i]

        min_mines = {}
        for i, resource in enumerate(RESOURCES):
            min_mines[resource] = row[c.MIN_MINES_START + i]

        mine_density = {}
        for i, resource in enumerate(RESOURCES):
            mine_density[resource] = row[c.MINE_DENSITY_START + i]

        terrains = {}
        for i, terrain in enumerate(TERRAINS_SOD):
            terrains[terrain] = row[c.TERRAINS_START + i]

        # Monster factions (keep all including Forge for roundtrip)
        monster_factions = {}
        for i, faction in enumerate(MONSTER_FACTIONS_SOD):
            monster_factions[faction] = row[c.MONSTER_FACTIONS_START + i]

        treasure_tiers = []
        for tier in range(3):
            offset = c.TREASURE_START + tier * 3
            treasure_tiers.append(TreasureTier(
                low=row[offset],
                high=row[offset + 1],
                density=row[offset + 2],
            ))

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
            zone_options=ZoneOptions(),
        )

    def _parse_connection(self, row: list[str]) -> Connection:
        c = SodCol
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
            road=None,
            conn_type=None,
            fictive=None,
            portal_repulsion=None,
        )
