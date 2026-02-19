"""Format detection and parser registry.

Format detection cannot rely on column count alone because SOD files
from the original game editor are padded with ~98 trailing empty columns
(85 active columns padded to 183 total). This makes SOD files appear
wider than HOTA files (138 or 140 columns), breaking any "widest first"
heuristic.

Instead, detection inspects the file structure:
  - SOD: header row 1 starts with "Map" at column 0
  - HOTA: header row 1 starts with "Pack" (or similar), and the first
    data row (row 4) contains a field_count at column 0 that identifies
    the sub-version ("11" = 1.7.x, "12" = 1.8.x)
"""

from pathlib import Path

from h3tc.parsers.base import BaseParser
from h3tc.parsers.hota import HotaParser
from h3tc.parsers.hota18 import Hota18Parser
from h3tc.parsers.sod import SodParser

# All registered parsers
PARSERS: list[BaseParser] = [SodParser(), HotaParser(), Hota18Parser()]

# Town field-count values that identify HOTA sub-versions
_HOTA_TOWN_COUNTS = {
    "12": "hota18",  # HOTA 1.8.x — 12 town factions (adds Bulwark)
    "11": "hota17",  # HOTA 1.7.x — 11 town factions
}


def detect_format(filepath: Path) -> BaseParser:
    """Detect template format by inspecting header and data rows.

    Only reads the first 4 lines of the file.
    """
    rows = _read_first_rows(filepath, count=4)

    if not rows:
        return _get("sod")

    # SOD files have "Map" as the very first cell (header row 1, column 0).
    # HOTA files never start with "Map" — they start with "Pack" or a
    # field-count label.
    first_cell = rows[0][0].strip() if rows[0] else ""
    if first_cell == "Map":
        return _get("sod")

    # HOTA family: the first data row (row index 3) has the town field count
    # at column 0, which tells us the sub-version.
    if len(rows) > 3 and rows[3]:
        town_count = rows[3][0].strip()
        format_id = _HOTA_TOWN_COUNTS.get(town_count, "hota17")
        return _get(format_id)

    return _get("hota17")


def _read_first_rows(filepath: Path, count: int) -> list[list[str]]:
    """Read the first N tab-delimited rows from a file."""
    raw = filepath.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    rows = []
    for line in text.split("\n")[:count]:
        line = line.rstrip("\r")
        if line:
            rows.append(line.split("\t"))
    return rows


def get_parser(format_id: str) -> BaseParser:
    """Get a parser by format ID."""
    return _get(format_id)


def _get(format_id: str) -> BaseParser:
    for parser in PARSERS:
        if parser.format_id == format_id:
            return parser
    raise ValueError(f"Unknown format: {format_id}")
