# h3tc - Heroes of Might and Magic 3 Template Converter

Convert random map generator (RMG) template packs between **SOD** (Shadow of Death), **HOTA 1.7.x**, and **HOTA 1.8.x** (Horn of the Abyss) formats.

## Requirements

- Python 3.10+

## Installation

```bash
pip install -e .
```

## Supported formats

| Format | ID | Extension | Active columns | Description |
|--------|----|-----------|----------------|-------------|
| SOD | `sod` | `.txt` | 85 | Shadow of Death — 9 town factions |
| HOTA 1.7.x | `hota17` | `.h3t` | 138 | Horn of the Abyss — 11 town factions (adds Cove, Factory) |
| HOTA 1.8.x | `hota18` | `.h3t` | 140 | Horn of the Abyss — 12 town factions (adds Bulwark) |

> **Note:** SOD files from the original game editor are padded to 183 columns with trailing empty tabs, even though only 85 contain data. Format auto-detection inspects the header structure rather than column count to handle this correctly.

## Usage

### CLI

```bash
# Convert SOD to HOTA 1.7.x
h3tc convert input.txt output.h3t --to hota17 --pack-name "My Pack"

# Convert SOD to HOTA 1.8.x
h3tc convert input.txt output.h3t --to hota18 --pack-name "My Pack"

# Convert HOTA 1.7.x to SOD
h3tc convert input.h3t output.txt --to sod

# Convert HOTA 1.8.x to SOD
h3tc convert input.h3t output.txt --to sod

# Convert between HOTA versions
h3tc convert input.h3t output.h3t --to hota18   # 1.7.x → 1.8.x
h3tc convert input.h3t output.h3t --to hota17   # 1.8.x → 1.7.x

# Rewrite (normalize) a file in the same format
h3tc convert input.h3t output.h3t --to hota17

# Auto-detect input format (default behavior)
h3tc convert templates/jebus_converted.h3t output.txt --to sod
```

Or run as a module:

```bash
python -m h3tc convert input.txt output.h3t --to hota17
```

### Options

| Option | Description |
|--------|-------------|
| `--to` (required) | Output format: `sod`, `hota17`, or `hota18` |
| `--from` | Input format (auto-detected if omitted) |
| `--pack-name` | Pack name for SOD→HOTA conversion (defaults to input filename) |

The input format is auto-detected by inspecting file content — you rarely need `--from`.

### Python API

```python
from pathlib import Path
from h3tc.parsers.sod import SodParser
from h3tc.parsers.hota import HotaParser
from h3tc.parsers.hota18 import Hota18Parser
from h3tc.writers.sod import SodWriter
from h3tc.writers.hota import HotaWriter
from h3tc.writers.hota18 import Hota18Writer
from h3tc.converters.sod_to_hota import sod_to_hota
from h3tc.converters.hota_to_sod import hota_to_sod
from h3tc.converters.hota_to_hota18 import hota_to_hota18
from h3tc.converters.hota18_to_hota import hota18_to_hota
from h3tc.formats import detect_format

# Auto-detect and parse any format
parser = detect_format(Path("template.h3t"))
pack = parser.parse(Path("template.h3t"))

# Convert SOD → HOTA 1.7.x
hota_pack = sod_to_hota(pack, pack_name="My Pack")

# Convert HOTA 1.7.x → HOTA 1.8.x
hota18_pack = hota_to_hota18(hota_pack)

# Write
Hota18Writer().write(hota18_pack, Path("output.h3t"))
```

## Visual Template Editor

A graphical editor for SOD templates built with PySide6. View and edit zones, connections, and all template properties visually.

The editor auto-detects and opens any supported format (SOD, HOTA 1.7.x, HOTA 1.8.x). Non-SOD formats are automatically converted to SOD for editing.

![Editor UI](screenshots/editor-ui.png)

### Features

- Opens any format — SOD, HOTA 1.7.x, and HOTA 1.8.x files are all auto-detected
- Zoomable, pannable canvas with drag-to-move zones
- Zone icons showing treasure value, monster strength, castles, towns, and resource mines
- Player zones colored by player (blue, red, green, purple, etc.)
- Treasure zones colored gray or gold based on treasure richness
- Connection lines with guard values displayed as red labels
- Property panel with 5 tabs: General, Towns and Castles, Content, Terrain, Monsters
- Spread/Compact buttons to adjust zone spacing
- Force-directed auto-layout for initial zone positioning
- Layout positions saved to JSON sidecar files

### Running the editor

Install with the GUI dependency:

```bash
pip install -e ".[gui]"
```

Launch from the CLI:

```bash
# Open any template file directly (format auto-detected)
h3tc editor templates/sod_complete/Jebus\ Cross/rmg.txt
h3tc editor templates/hota_original_template_pack.h3t
h3tc editor templates/jebus_converted.h3t

# Or launch and use File > Open
h3tc editor
```

Or run as a module:

```bash
python -m h3tc editor path/to/template
```

## What gets converted

### SOD → HOTA 1.7.x

Shared fields (zone data, connections, mines, terrains, monsters, treasure) are preserved exactly. HOTA-only fields receive sensible defaults:

- **Pack metadata**: empty (name from `--pack-name` or filename)
- **Map options**: all empty
- **Town types**: Cove and Factory added (empty)
- **Terrains**: Highlands and Wasteland added (empty)
- **Monster factions**: Conflux, Cove, Factory added as enabled (`x`); Forge dropped
- **Zone options**: `placement=ground`, `monsters_disposition_standard=3`, `monsters_joining_percentage=1`, `monsters_join_only_for_money=x`
- **Connection extras**: `road=+`, `type=ground`

### HOTA 1.7.x → HOTA 1.8.x

Adds the Bulwark faction:

- **Town types**: Bulwark added (enabled if all existing factions are enabled, empty otherwise)
- **Monster factions**: Bulwark added (same logic)
- **Field counts**: town count updated from 11 to 12

### HOTA 1.8.x → HOTA 1.7.x

Removes the Bulwark faction:

- **Town types**: Bulwark removed
- **Monster factions**: Bulwark removed
- **Field counts**: town count updated from 12 to 11

### HOTA → SOD

HOTA-only fields are stripped:

- Pack metadata, field counts, map options removed
- Cove, Factory (and Bulwark for 1.8.x) town types removed
- Highlands, Wasteland terrains removed
- Conflux, Cove, Factory (and Bulwark for 1.8.x) monster factions removed; Forge column added as `x`
- Zone options removed
- Connection road, type, fictive, portal repulsion removed

## Testing

```bash
pip install -e ".[dev]"
pytest
```

Tests validate roundtrip fidelity against 60 SOD and 36 HOTA template files, plus HOTA 1.8.x parsing, roundtrip, and all conversion paths.

## Project structure

```
src/h3tc/
├── cli.py              # CLI entry point
├── models.py           # Format-agnostic Pydantic data models
├── enums.py            # Faction, terrain, resource lists
├── constants.py        # Column index mappings (SOD: 85, HOTA17: 138, HOTA18: 140)
├── formats.py          # Format detection and parser registry
├── parsers/
│   ├── sod.py          # SOD format parser
│   ├── hota.py         # HOTA 1.7.x format parser
│   └── hota18.py       # HOTA 1.8.x format parser
├── writers/
│   ├── sod.py          # SOD format writer
│   ├── hota.py         # HOTA 1.7.x format writer
│   └── hota18.py       # HOTA 1.8.x format writer
├── converters/
│   ├── sod_to_hota.py      # SOD → HOTA 1.7.x conversion
│   ├── hota_to_sod.py      # HOTA → SOD conversion
│   ├── hota_to_hota18.py   # HOTA 1.7.x → 1.8.x conversion
│   └── hota18_to_hota.py   # HOTA 1.8.x → 1.7.x conversion
└── editor/             # Visual template editor (PySide6)
    ├── __init__.py     # launch() entry point
    ├── main_window.py  # Main window, toolbar, panels
    ├── constants.py    # Visual constants (colors, sizes, zoom)
    ├── canvas/
    │   ├── view.py     # Zoomable/pannable QGraphicsView
    │   ├── scene.py    # Zone/connection item management
    │   ├── zone_item.py    # Zone rendering with icons
    │   ├── connection_item.py  # Connection lines with labels
    │   ├── layout.py   # Force-directed auto-layout
    │   └── icons.py    # Vector icon drawing (QPainter)
    ├── panels/
    │   ├── zone_panel.py       # Zone property editor (5 tabs)
    │   ├── connection_panel.py # Connection property editor
    │   ├── map_panel.py        # Map name/size panel
    │   ├── map_selector.py     # Multi-map pack selector
    │   └── binding.py          # Widget ↔ model data binding
    └── models/
        ├── editor_state.py     # Editor state tracking
        └── layout_store.py     # JSON sidecar for positions
```

## Format details

See [docs/format_reference.md](docs/format_reference.md) for a detailed column-by-column reference of both formats.
