"""Abstract base parser for H3 template formats."""

from abc import ABC, abstractmethod
from pathlib import Path

from h3tc.models import TemplatePack


class BaseParser(ABC):
    @abstractmethod
    def parse(self, filepath: Path) -> TemplatePack:
        ...
