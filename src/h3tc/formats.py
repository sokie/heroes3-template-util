"""Format registry for template parsers and writers.

To add a new format, create a parser/writer with format_id, format_name,
and min_columns, then register it here.
"""

import csv
import io
from pathlib import Path

from h3tc.parsers.base import BaseParser
from h3tc.parsers.hota import HotaParser
from h3tc.parsers.hota18 import Hota18Parser
from h3tc.parsers.sod import SodParser

# All registered parsers
PARSERS: list[BaseParser] = [SodParser(), HotaParser(), Hota18Parser()]


def detect_format(filepath: Path) -> BaseParser:
    """Detect template format by inspecting header and data content.

    SOD files have "Map" at column 0 of the first header row.
    HOTA files have field counts at columns 0-6; the town field count
    distinguishes 1.7.x ("11") from 1.8.x ("12").
    """
    raw = filepath.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    reader = csv.reader(io.StringIO(text), delimiter="\t", quotechar='"')
    rows = list(reader)

    if not rows:
        return _get("sod")

    # SOD: first header row has "Map" at column 0
    if rows[0] and rows[0][0].strip() == "Map":
        return _get("sod")

    # HOTA family: check field_count town value in first data row (row index 3)
    if len(rows) > 3:
        town_count = rows[3][0].strip() if rows[3] else ""
        if town_count == "12":
            return _get("hota18")

    return _get("hota17")


def get_parser(format_id: str) -> BaseParser:
    """Get a parser by format ID."""
    return _get(format_id)


def _get(format_id: str) -> BaseParser:
    for parser in PARSERS:
        if parser.format_id == format_id:
            return parser
    raise ValueError(f"Unknown format: {format_id}")
