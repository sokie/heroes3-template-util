"""Canonical faction, terrain, and resource lists for H3 template formats."""

# Town factions in canonical order
# SOD has 9 (Elemental instead of Conflux), HOTA has 11 (adds Cove, Factory)
TOWN_FACTIONS_SOD = [
    "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Elemental",
]

TOWN_FACTIONS_HOTA = [
    "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Conflux", "Cove", "Factory",
]

TOWN_FACTIONS_HOTA18 = [
    "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Conflux", "Cove", "Factory", "Bulwark",
]

# Monster factions in canonical order (Neutral first, then town factions)
# SOD has Neutral + 9 town factions + Forge (11 total)
# HOTA has Neutral + 11 town factions (Conflux, Cove, Factory added; no Forge) = 12 total
MONSTER_FACTIONS_SOD = [
    "Neutral", "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Forge",
]

MONSTER_FACTIONS_HOTA = [
    "Neutral", "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Conflux", "Cove", "Factory",
]

MONSTER_FACTIONS_HOTA18 = [
    "Neutral", "Castle", "Rampart", "Tower", "Inferno", "Necropolis",
    "Dungeon", "Stronghold", "Fortress", "Conflux", "Cove", "Factory", "Bulwark",
]

# Terrain types
TERRAINS_SOD = [
    "Dirt", "Sand", "Grass", "Snow", "Swamp", "Rough", "Cave", "Lava",
]

TERRAINS_HOTA = [
    "Dirt", "Sand", "Grass", "Snow", "Swamp", "Rough", "Cave", "Lava",
    "Highlands", "Wasteland",
]

# Resources (same in both formats)
RESOURCES = ["Wood", "Mercury", "Ore", "Sulfur", "Crystal", "Gems", "Gold"]

# Zone types
ZONE_TYPES = ["human_start", "computer_start", "Treasure", "Junction"]
