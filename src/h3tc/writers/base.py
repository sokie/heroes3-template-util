"""Abstract base writer for H3 template formats."""

from abc import ABC, abstractmethod
from pathlib import Path

from h3tc.models import TemplatePack


class BaseWriter(ABC):
    """Base class for template writers."""

    # Subclasses must set these
    format_id: str = ""
    format_name: str = ""

    @abstractmethod
    def write(self, pack: TemplatePack, filepath: Path) -> None:
        ...
