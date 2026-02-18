"""Column index mappings for SOD and HOTA template formats.

All indices are 0-based. This is the single source of truth for parsers and writers.
"""


class SodCol:
    """SOD format column indices (0-based). 85 active columns, padded to 183."""

    # Map section (cols 0-2)
    NAME = 0
    MIN_SIZE = 1
    MAX_SIZE = 2

    # Zone identification (col 3)
    ZONE_ID = 3

    # Zone type (cols 4-7)
    HUMAN_START = 4
    COMPUTER_START = 5
    TREASURE = 6
    JUNCTION = 7

    # Zone base (col 8)
    BASE_SIZE = 8

    # Position constraints (cols 9-12)
    MIN_HUMAN_POS = 9
    MAX_HUMAN_POS = 10
    MIN_TOTAL_POS = 11
    MAX_TOTAL_POS = 12

    # Ownership (col 13)
    OWNERSHIP = 13

    # Player towns (cols 14-17)
    PLAYER_MIN_TOWNS = 14
    PLAYER_MIN_CASTLES = 15
    PLAYER_TOWN_DENSITY = 16
    PLAYER_CASTLE_DENSITY = 17

    # Neutral towns (cols 18-21)
    NEUTRAL_MIN_TOWNS = 18
    NEUTRAL_MIN_CASTLES = 19
    NEUTRAL_TOWN_DENSITY = 20
    NEUTRAL_CASTLE_DENSITY = 21

    # Towns same type (col 22)
    TOWNS_SAME_TYPE = 22

    # Town types - 9 factions (cols 23-31)
    TOWN_TYPES_START = 23
    TOWN_TYPES_END = 31  # inclusive (Elemental)
    TOWN_TYPE_COUNT = 9

    # Minimum mines - 7 resources (cols 32-38)
    MIN_MINES_START = 32
    MIN_MINES_END = 38  # inclusive

    # Mine density - 7 resources (cols 39-45)
    MINE_DENSITY_START = 39
    MINE_DENSITY_END = 45  # inclusive

    # Terrain match (col 46)
    TERRAIN_MATCH = 46

    # Terrain types - 8 types (cols 47-54)
    TERRAINS_START = 47
    TERRAINS_END = 54  # inclusive
    TERRAIN_COUNT = 8

    # Monster strength (col 55)
    MONSTER_STRENGTH = 55

    # Monster match (col 56)
    MONSTER_MATCH = 56

    # Monster factions - 10 factions (cols 57-66), last is Forge
    MONSTER_FACTIONS_START = 57
    MONSTER_FACTIONS_END = 66  # inclusive (Forge)
    MONSTER_FACTION_COUNT = 10

    # Treasure - 3 tiers x 3 fields (cols 67-75)
    TREASURE_START = 67
    TREASURE_END = 75  # inclusive

    # Connections (cols 76-84)
    CONN_ZONE1 = 76
    CONN_ZONE2 = 77
    CONN_VALUE = 78
    CONN_WIDE = 79
    CONN_BORDER_GUARD = 80
    CONN_MIN_HUMAN_POS = 81
    CONN_MAX_HUMAN_POS = 82
    CONN_MIN_TOTAL_POS = 83
    CONN_MAX_TOTAL_POS = 84

    ACTIVE_COLS = 85
    PADDED_TOTAL = 183


class HotaCol:
    """HOTA format column indices (0-based). 138 columns."""

    # Field counts (cols 0-6)
    FIELD_COUNT_TOWN = 0
    FIELD_COUNT_TERRAIN = 1
    FIELD_COUNT_ZONE_TYPE = 2
    FIELD_COUNT_PACK_NEW = 3
    FIELD_COUNT_MAP_NEW = 4
    FIELD_COUNT_ZONE_NEW = 5
    FIELD_COUNT_CONN_NEW = 6

    # Pack metadata (cols 7-14)
    PACK_NAME = 7
    PACK_DESC = 8
    PACK_TOWN_SELECTION = 9
    PACK_HEROES = 10
    PACK_MIRROR = 11
    PACK_TAGS = 12
    PACK_MAX_BATTLE_ROUNDS = 13
    PACK_FORBID_HIRING_HEROES = 14

    # Map section (cols 15-27)
    MAP_NAME = 15
    MAP_MIN_SIZE = 16
    MAP_MAX_SIZE = 17
    MAP_ARTIFACTS = 18
    MAP_COMBO_ARTS = 19
    MAP_SPELLS = 20
    MAP_SECONDARY_SKILLS = 21
    MAP_OBJECTS = 22
    MAP_ROCK_BLOCKS = 23
    MAP_ZONE_SPARSENESS = 24
    MAP_SPECIAL_WEEKS_DISABLED = 25
    MAP_SPELL_RESEARCH = 26
    MAP_ANARCHY = 27

    # Zone identification (col 28)
    ZONE_ID = 28

    # Zone type (cols 29-32)
    HUMAN_START = 29
    COMPUTER_START = 30
    TREASURE = 31
    JUNCTION = 32

    # Zone base (col 33)
    BASE_SIZE = 33

    # Position constraints (cols 34-37)
    MIN_HUMAN_POS = 34
    MAX_HUMAN_POS = 35
    MIN_TOTAL_POS = 36
    MAX_TOTAL_POS = 37

    # Ownership (col 38)
    OWNERSHIP = 38

    # Player towns (cols 39-42)
    PLAYER_MIN_TOWNS = 39
    PLAYER_MIN_CASTLES = 40
    PLAYER_TOWN_DENSITY = 41
    PLAYER_CASTLE_DENSITY = 42

    # Neutral towns (cols 43-46)
    NEUTRAL_MIN_TOWNS = 43
    NEUTRAL_MIN_CASTLES = 44
    NEUTRAL_TOWN_DENSITY = 45
    NEUTRAL_CASTLE_DENSITY = 46

    # Towns same type (col 47)
    TOWNS_SAME_TYPE = 47

    # Town types - 11 factions (cols 48-58)
    TOWN_TYPES_START = 48
    TOWN_TYPES_END = 58  # inclusive (Factory)
    TOWN_TYPE_COUNT = 11

    # Minimum mines - 7 resources (cols 59-65)
    MIN_MINES_START = 59
    MIN_MINES_END = 65  # inclusive

    # Mine density - 7 resources (cols 66-72)
    MINE_DENSITY_START = 66
    MINE_DENSITY_END = 72  # inclusive

    # Terrain match (col 73)
    TERRAIN_MATCH = 73

    # Terrain types - 10 types (cols 74-83)
    TERRAINS_START = 74
    TERRAINS_END = 83  # inclusive (Wasteland)
    TERRAIN_COUNT = 10

    # Monster strength (col 84)
    MONSTER_STRENGTH = 84

    # Monster match (col 85)
    MONSTER_MATCH = 85

    # Monster factions - 12 factions (cols 86-97)
    MONSTER_FACTIONS_START = 86
    MONSTER_FACTIONS_END = 97  # inclusive (Factory)
    MONSTER_FACTION_COUNT = 12

    # Treasure - 3 tiers x 3 fields (cols 98-106)
    TREASURE_START = 98
    TREASURE_END = 106  # inclusive

    # Zone options (cols 107-124)
    ZONE_OPT_PLACEMENT = 107
    ZONE_OPT_OBJECTS = 108
    ZONE_OPT_MIN_OBJECTS = 109
    ZONE_OPT_IMAGE_SETTINGS = 110
    ZONE_OPT_FORCE_NEUTRAL = 111
    ZONE_OPT_ALLOW_NON_COHERENT_ROAD = 112
    ZONE_OPT_ZONE_REPULSION = 113
    ZONE_OPT_TOWN_HINT = 114
    ZONE_OPT_MONSTERS_DISP_STANDARD = 115
    ZONE_OPT_MONSTERS_DISP_CUSTOM = 116
    ZONE_OPT_MONSTERS_JOINING_PCT = 117
    ZONE_OPT_MONSTERS_JOIN_MONEY = 118
    ZONE_OPT_MIN_AIRSHIP_SHIPYARDS = 119
    ZONE_OPT_AIRSHIP_SHIPYARD_DENSITY = 120
    ZONE_OPT_TERRAIN_HINT = 121
    ZONE_OPT_ALLOWED_FACTIONS = 122
    ZONE_OPT_FACTION_HINT = 123
    ZONE_OPT_MAX_BLOCK_VALUE = 124

    ZONE_OPTIONS_START = 107
    ZONE_OPTIONS_END = 124  # inclusive
    ZONE_OPTIONS_COUNT = 18

    # Connections (cols 125-137)
    CONN_ZONE1 = 125
    CONN_ZONE2 = 126
    CONN_VALUE = 127
    CONN_WIDE = 128
    CONN_BORDER_GUARD = 129
    CONN_ROAD = 130
    CONN_TYPE = 131
    CONN_FICTIVE = 132
    CONN_PORTAL_REPULSION = 133
    CONN_MIN_HUMAN_POS = 134
    CONN_MAX_HUMAN_POS = 135
    CONN_MIN_TOTAL_POS = 136
    CONN_MAX_TOTAL_POS = 137

    TOTAL = 138


# Zone option field names in order (for models)
ZONE_OPTION_FIELDS = [
    "placement",
    "objects",
    "min_objects",
    "image_settings",
    "force_neutral_creatures",
    "allow_non_coherent_road",
    "zone_repulsion",
    "town_hint",
    "monsters_disposition_standard",
    "monsters_disposition_custom",
    "monsters_joining_percentage",
    "monsters_join_only_for_money",
    "min_airship_shipyards",
    "airship_shipyard_density",
    "terrain_hint",
    "allowed_factions",
    "faction_hint",
    "max_block_value",
]

# Header rows for SOD format (3 rows)
SOD_HEADERS = [
    # Row 1: section headers
    ["Map", "", "", "Zone"] + [""] * 72 + ["Connections"] + [""] * 8 + [""] * 98,
    # Row 2: subsection headers
    ["", "", "", "", "Type", "", "", "", "", "Restrictions", "", "", "",
     "", "Player towns", "", "", "", "Neutral towns", "", "", "",
     "Town types", "", "", "", "", "", "", "", "",
     "Minimum mines", "", "", "", "", "", "",
     "Mine Density", "", "", "", "", "", "",
     "Terrain", "", "", "", "", "", "", "", "",
     "Monsters", "", "", "", "", "", "", "", "", "", "",
     "Treasure", "", "", "", "", "", "", "", "",
     "Zones", "", "", "", "Restrictions", "", "", "", ""] + [""] * 98,
    # Row 3: column headers (will be built from actual file)
]

# Default conversion values for SOD -> HOTA
SOD_TO_HOTA_DEFAULTS = {
    "field_counts": ["11", "10", "4", "8", "10", "18", "4"],
    "zone_options": {
        "placement": "",
        "objects": "",
        "min_objects": "",
        "image_settings": "",
        "force_neutral_creatures": "",
        "allow_non_coherent_road": "",
        "zone_repulsion": "",
        "town_hint": "",
        "monsters_disposition_standard": "3",
        "monsters_disposition_custom": "",
        "monsters_joining_percentage": "1",
        "monsters_join_only_for_money": "x",
        "min_airship_shipyards": "",
        "airship_shipyard_density": "",
        "terrain_hint": "",
        "allowed_factions": "",
        "faction_hint": "",
        "max_block_value": "",
    },
    "connection": {
        "road": "",
        "conn_type": "",
        "fictive": "",
        "portal_repulsion": "",
    },
}
