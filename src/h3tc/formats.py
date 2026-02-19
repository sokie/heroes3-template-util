"""Format registry for template parsers and writers.

To add a new format, create a parser/writer with format_id, format_name,
and min_columns, then register it here.
"""

from pathlib import Path

from h3tc.parsers.base import BaseParser
from h3tc.parsers.hota import HotaParser
from h3tc.parsers.hota18 import Hota18Parser
from h3tc.parsers.sod import SodParser

# Registered parsers, ordered by min_columns descending so detection
# checks the most specific (widest) format first.
PARSERS: list[BaseParser] = sorted(
    [SodParser(), HotaParser(), Hota18Parser()],
    key=lambda p: p.min_columns,
    reverse=True,
)


def detect_format(filepath: Path) -> BaseParser:
    """Detect template format by column count and return the matching parser."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        for line in f:
            cols = len(line.rstrip("\r\n").split("\t"))
            for parser in PARSERS:
                if cols >= parser.min_columns:
                    return parser
    # Default to SOD
    return next(p for p in PARSERS if p.format_id == "sod")


def get_parser(format_id: str) -> BaseParser:
    """Get a parser by format ID."""
    for parser in PARSERS:
        if parser.format_id == format_id:
            return parser
    raise ValueError(f"Unknown format: {format_id}")
