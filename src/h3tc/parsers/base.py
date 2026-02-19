"""Abstract base parser for H3 template formats."""

from abc import ABC, abstractmethod
from pathlib import Path

from h3tc.models import TemplatePack


class BaseParser(ABC):
    """Base class for template parsers."""

    # Subclasses must set these
    format_id: str = ""
    format_name: str = ""
    min_columns: int = 0

    @abstractmethod
    def parse(self, filepath: Path) -> TemplatePack:
        ...
