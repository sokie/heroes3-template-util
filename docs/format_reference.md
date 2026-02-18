# H3 RMG Template Format Reference

Both SOD and HOTA template packs are **tab-separated value (TSV)** files with CRLF line endings. Files begin with **3 header rows** followed by **data rows** containing map, zone, and connection definitions.

Multi-line values (e.g., pack descriptions) are enclosed in double quotes per standard CSV quoting rules.

## File structure overview

```
Row 1: Section headers    (Map, Zone, Connections, ...)
Row 2: Subsection headers (Type, Restrictions, Player towns, ...)
Row 3: Column headers     (Name, Id, human start, ...)
Row 4+: Data rows         (one row per zone/connection pair)
```

Each **template map** starts with a row where the Name column is non-empty. Subsequent rows (until the next map name) belong to the same map.

**Zone and connection data share rows.** Row *i* of a map contains zone *i* (left columns) and connection *i* (right columns). If a map has more connections than zones (or vice versa), the extra rows have one side empty.

---

## SOD format (85 columns)

File extension: `.txt`

### Section layout

| Section | Columns | Count | Description |
|---------|---------|-------|-------------|
| Map | 0-2 | 3 | Map name, size range |
| Zone ID | 3 | 1 | Zone identifier |
| Zone Type | 4-7 | 4 | human start, computer start, treasure, junction |
| Base Size | 8 | 1 | Zone base size |
| Restrictions | 9-12 | 4 | Position constraints (human/total min/max) |
| Ownership | 13 | 1 | Zone ownership |
| Player Towns | 14-17 | 4 | Min towns/castles, density |
| Neutral Towns | 18-21 | 4 | Min towns/castles, density |
| Towns Same Type | 22 | 1 | Flag |
| Town Types | 23-31 | 9 | One column per faction |
| Minimum Mines | 32-38 | 7 | One column per resource |
| Mine Density | 39-45 | 7 | One column per resource |
| Terrain | 46-54 | 9 | Match flag + 8 terrain types |
| Monsters | 55-66 | 12 | Strength + match + 10 factions |
| Treasure | 67-75 | 9 | 3 tiers x (low, high, density) |
| Connections | 76-84 | 9 | Zone pair, value, options, positions |

### Column reference

| Col | Header | Section | Notes |
|-----|--------|---------|-------|
| 0 | Name | Map | Map name (non-empty = new map) |
| 1 | Minimum Size | Map | |
| 2 | Maximum Size | Map | |
| 3 | Id | Zone | Zone identifier |
| 4 | human start | Zone Type | `x` if set |
| 5 | computer start | Zone Type | `x` if set |
| 6 | Treasure | Zone Type | `x` if set |
| 7 | Junction | Zone Type | `x` if set |
| 8 | Base Size | Zone | Integer |
| 9 | Minimum human positions | Restrictions | |
| 10 | Maximum human positions | Restrictions | |
| 11 | Minimum total positions | Restrictions | |
| 12 | Maximum total positions | Restrictions | |
| 13 | Ownership | Zone | |
| 14 | Minimum towns | Player Towns | |
| 15 | Minimum castles | Player Towns | |
| 16 | Town Density | Player Towns | |
| 17 | Castle Density | Player Towns | |
| 18 | Minimum towns | Neutral Towns | |
| 19 | Minimum castles | Neutral Towns | |
| 20 | Town Density | Neutral Towns | |
| 21 | Castle Density | Neutral Towns | |
| 22 | Towns are of same type | Zone | |
| 23 | Castle | Town Types | |
| 24 | Rampart | Town Types | |
| 25 | Tower | Town Types | |
| 26 | Inferno | Town Types | |
| 27 | Necropolis | Town Types | |
| 28 | Dungeon | Town Types | |
| 29 | Stronghold | Town Types | |
| 30 | Fortress | Town Types | |
| 31 | Elemental | Town Types | Maps to "Conflux" in HOTA |
| 32 | Wood | Min Mines | |
| 33 | Mercury | Min Mines | |
| 34 | Ore | Min Mines | |
| 35 | Sulfur | Min Mines | |
| 36 | Crystal | Min Mines | |
| 37 | Gems | Min Mines | |
| 38 | Gold | Min Mines | |
| 39 | Wood | Mine Density | |
| 40 | Mercury | Mine Density | |
| 41 | Ore | Mine Density | |
| 42 | Sulfur | Mine Density | |
| 43 | Crystal | Mine Density | |
| 44 | Gems | Mine Density | |
| 45 | Gold | Mine Density | |
| 46 | Match to town | Terrain | |
| 47 | Dirt | Terrain | |
| 48 | Sand | Terrain | |
| 49 | Grass | Terrain | |
| 50 | Snow | Terrain | |
| 51 | Swamp | Terrain | |
| 52 | Rough | Terrain | |
| 53 | Cave | Terrain | |
| 54 | Lava | Terrain | |
| 55 | Strength | Monsters | |
| 56 | Match to town | Monsters | |
| 57 | Neutral | Monster Factions | |
| 58 | Castle | Monster Factions | |
| 59 | Rampart | Monster Factions | |
| 60 | Tower | Monster Factions | |
| 61 | Inferno | Monster Factions | |
| 62 | Necropolis | Monster Factions | |
| 63 | Dungeon | Monster Factions | |
| 64 | Stronghold | Monster Factions | |
| 65 | Fortress | Monster Factions | |
| 66 | Forge | Monster Factions | Cut faction, no HOTA equivalent |
| 67 | Low | Treasure Tier 1 | |
| 68 | High | Treasure Tier 1 | |
| 69 | Density | Treasure Tier 1 | |
| 70 | Low | Treasure Tier 2 | |
| 71 | High | Treasure Tier 2 | |
| 72 | Density | Treasure Tier 2 | |
| 73 | Low | Treasure Tier 3 | |
| 74 | High | Treasure Tier 3 | |
| 75 | Density | Treasure Tier 3 | |
| 76 | Zone 1 | Connections | |
| 77 | Zone 2 | Connections | |
| 78 | Value | Connections | |
| 79 | Wide | Connections | |
| 80 | Border Guard | Connections | |
| 81 | Minimum human positions | Connections | |
| 82 | Maximum human positions | Connections | |
| 83 | Minimum total positions | Connections | |
| 84 | Maximum total positions | Connections | |

Some files pad rows to 183 columns with empty trailing cells.

---

## HOTA format (138 columns)

File extension: `.h3t`

### Section layout

| Section | Columns | Count | Description |
|---------|---------|-------|-------------|
| Field Counts | 0-6 | 7 | Schema metadata (row 4 only) |
| Pack Metadata | 7-14 | 8 | Pack name, description, options (row 4 only) |
| Map | 15-27 | 13 | Map name, size, options |
| Zone ID | 28 | 1 | Zone identifier |
| Zone Type | 29-32 | 4 | human start, computer start, treasure, junction |
| Base Size | 33 | 1 | Zone base size |
| Restrictions | 34-37 | 4 | Position constraints |
| Ownership | 38 | 1 | Zone ownership |
| Player Towns | 39-42 | 4 | Min towns/castles, density |
| Neutral Towns | 43-46 | 4 | Min towns/castles, density |
| Towns Same Type | 47 | 1 | Flag |
| Town Types | 48-58 | 11 | 9 SOD factions + Cove, Factory |
| Minimum Mines | 59-65 | 7 | One column per resource |
| Mine Density | 66-72 | 7 | One column per resource |
| Terrain | 73-83 | 11 | Match flag + 8 SOD terrains + Highlands, Wasteland |
| Monsters | 84-97 | 14 | Strength + match + 12 factions |
| Treasure | 98-106 | 9 | 3 tiers x (low, high, density) |
| Zone Options | 107-124 | 18 | HOTA-only zone configuration |
| Connections | 125-137 | 13 | 9 SOD fields + road, type, fictive, portal repulsion |

### Special rows

**Row 4** (first data row) carries pack-level data alongside the first map's first zone:

- Columns 0-6: Field counts (schema version metadata)
- Columns 7-14: Pack metadata (name, description, options)
- Columns 15+: Normal map/zone/connection data

### Column reference - Pack & Map (cols 0-27)

| Col | Header | Section | Notes |
|-----|--------|---------|-------|
| 0 | Town | Field Counts | Number of town factions |
| 1 | Terrain | Field Counts | Number of terrain types |
| 2 | Zone type | Field Counts | Number of zone types |
| 3 | Pack new | Field Counts | |
| 4 | Map new | Field Counts | |
| 5 | Zone new | Field Counts | |
| 6 | Connection new | Field Counts | |
| 7 | Name | Pack Metadata | Pack name |
| 8 | Description | Pack Metadata | May contain multi-line quoted text |
| 9 | Town selection | Pack Metadata | |
| 10 | Heroes | Pack Metadata | |
| 11 | Mirror | Pack Metadata | |
| 12 | Tags | Pack Metadata | |
| 13 | Max Battle Rounds | Pack Metadata | |
| 14 | Forbid Hiring Heroes | Pack Metadata | |
| 15 | Name | Map | Map name (non-empty = new map) |
| 16 | Minimum Size | Map | |
| 17 | Maximum Size | Map | |
| 18 | Artifacts | Map Options | |
| 19 | Combo Arts | Map Options | |
| 20 | Spells | Map Options | |
| 21 | Secondary skills | Map Options | |
| 22 | Objects | Map Options | |
| 23 | Rock blocks | Map Options | |
| 24 | Zone sparseness | Map Options | |
| 25 | Special weeks disabled | Map Options | |
| 26 | Spell Research | Map Options | |
| 27 | Anarchy | Map Options | |

### Column reference - Zone (cols 28-106)

| Col | Header | Section | Notes |
|-----|--------|---------|-------|
| 28 | Id | Zone | Zone identifier |
| 29 | human start | Zone Type | |
| 30 | computer start | Zone Type | |
| 31 | Treasure | Zone Type | |
| 32 | Junction | Zone Type | |
| 33 | Base Size | Zone | |
| 34 | Minimum human positions | Restrictions | |
| 35 | Maximum human positions | Restrictions | |
| 36 | Minimum total positions | Restrictions | |
| 37 | Maximum total positions | Restrictions | |
| 38 | Ownership | Zone | |
| 39-42 | Min towns, Min castles, Town/Castle Density | Player Towns | |
| 43-46 | Min towns, Min castles, Town/Castle Density | Neutral Towns | |
| 47 | Towns are of same type | Zone | |
| 48 | Castle | Town Types | |
| 49 | Rampart | Town Types | |
| 50 | Tower | Town Types | |
| 51 | Inferno | Town Types | |
| 52 | Necropolis | Town Types | |
| 53 | Dungeon | Town Types | |
| 54 | Stronghold | Town Types | |
| 55 | Fortress | Town Types | |
| 56 | Conflux | Town Types | SOD calls this "Elemental" |
| 57 | Cove | Town Types | HOTA-only |
| 58 | Factory | Town Types | HOTA-only |
| 59-65 | Wood..Gold | Min Mines | Same 7 resources as SOD |
| 66-72 | Wood..Gold | Mine Density | Same 7 resources as SOD |
| 73 | Match to town | Terrain | |
| 74-81 | Dirt..Lava | Terrain | Same 8 as SOD |
| 82 | Highlands | Terrain | HOTA-only |
| 83 | Wasteland | Terrain | HOTA-only |
| 84 | Strength | Monsters | |
| 85 | Match to town | Monsters | |
| 86 | Neutral | Monster Factions | |
| 87-94 | Castle..Fortress | Monster Factions | Same 8 as SOD |
| 95 | Conflux | Monster Factions | HOTA-only (SOD has no equivalent) |
| 96 | Cove | Monster Factions | HOTA-only |
| 97 | Factory | Monster Factions | HOTA-only |
| 98-106 | Low, High, Density (x3) | Treasure | 3 tiers, same as SOD |

### Column reference - Zone Options (cols 107-124, HOTA-only)

| Col | Header | Description |
|-----|--------|-------------|
| 107 | Placement | `ground` or `underground` |
| 108 | Objects | Object settings |
| 109 | Minimum objects | |
| 110 | Image settings | |
| 111 | Force neutral creatures | |
| 112 | Allow non-coherent road | |
| 113 | Zone repulsion | |
| 114 | Town Hint | |
| 115 | Monsters disposition (standard) | Default: `3` |
| 116 | Monsters disposition (custom) | |
| 117 | Monsters joining percentage | Default: `1` |
| 118 | Monsters join only for money | Default: `x` |
| 119 | Minimum airship shipyards | |
| 120 | Airship shipyard Density | |
| 121 | Terrain Hint | |
| 122 | Allowed Factions | |
| 123 | Faction Hint | |
| 124 | Max block value | |

### Column reference - Connections (cols 125-137)

| Col | Header | Notes |
|-----|--------|-------|
| 125 | Zone 1 | |
| 126 | Zone 2 | |
| 127 | Value | |
| 128 | Wide | |
| 129 | Border Guard | |
| 130 | Road | HOTA-only, default: `+` |
| 131 | Type | HOTA-only, default: `ground` |
| 132 | Fictive | HOTA-only |
| 133 | Portal repulsion | HOTA-only |
| 134 | Minimum human positions | |
| 135 | Maximum human positions | |
| 136 | Minimum total positions | |
| 137 | Maximum total positions | |

---

## Differences summary

| Feature | SOD | HOTA |
|---------|-----|------|
| File extension | `.txt` | `.h3t` |
| Column count | 85 | 138 |
| Pack metadata | None | Name, description, options (cols 7-14) |
| Field counts | None | Schema metadata (cols 0-6) |
| Map options | None | Artifacts, spells, skills, etc. (cols 18-27) |
| Town factions | 9 (Elemental) | 11 (+Cove, +Factory, Elemental→Conflux) |
| Terrain types | 8 | 10 (+Highlands, +Wasteland) |
| Monster factions | 10 (incl. Forge) | 12 (+Conflux, +Cove, +Factory, -Forge) |
| Zone options | None | 18 fields (cols 107-124) |
| Connection fields | 9 | 13 (+Road, +Type, +Fictive, +Portal repulsion) |

### Faction name mapping

| SOD | HOTA | Notes |
|-----|------|-------|
| Elemental | Conflux | Same faction, renamed |
| Forge | *(none)* | Cut faction, only in SOD monster list |
| *(none)* | Cove | HOTA-only faction |
| *(none)* | Factory | HOTA-only faction |
