"""HOTA 1.8.x format parser for H3 template packs."""

from h3tc.constants import Hota18Col
from h3tc.enums import MONSTER_FACTIONS_HOTA18, TERRAINS_HOTA, TOWN_FACTIONS_HOTA18
from h3tc.parsers.hota import HotaParser


class Hota18Parser(HotaParser):
    format_id = "hota18"
    format_name = "HOTA 1.8.x"

    _col = Hota18Col
    _town_factions = TOWN_FACTIONS_HOTA18
    _monster_factions = MONSTER_FACTIONS_HOTA18
    _terrains = TERRAINS_HOTA
