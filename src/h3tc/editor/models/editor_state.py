"""Editor state: current pack, selection, dirty tracking."""

from pathlib import Path

from h3tc.models import TemplatePack


class EditorState:
    """Tracks the current editor state."""

    def __init__(self) -> None:
        self.pack: TemplatePack | None = None
        self.file_path: Path | None = None
        self.current_map_index: int = 0
        self.dirty: bool = False

    @property
    def current_map(self):
        if self.pack and 0 <= self.current_map_index < len(self.pack.maps):
            return self.pack.maps[self.current_map_index]
        return None

    @property
    def has_file(self) -> bool:
        return self.pack is not None

    def mark_dirty(self) -> None:
        self.dirty = True

    def mark_clean(self) -> None:
        self.dirty = False

    def reset(self) -> None:
        self.pack = None
        self.file_path = None
        self.current_map_index = 0
        self.dirty = False
