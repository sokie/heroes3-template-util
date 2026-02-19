"""Convert dialog for converting template files between formats."""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QVBoxLayout,
)

from h3tc.formats import detect_format

# format_id -> (display name, file filter, default extension)
_FORMATS = {
    "sod": ("SOD", "SOD Templates (*.txt)", ".txt"),
    "hota17": ("HOTA 1.7.x", "HOTA Templates (*.h3t)", ".h3t"),
    "hota18": ("HOTA 1.8.x", "HOTA Templates (*.h3t)", ".h3t"),
}


class ConvertDialog(QDialog):
    """Dialog for converting a template file between formats."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Convert Template File")
        self.setMinimumWidth(500)

        self._input_path: Path | None = None
        self._input_format_id: str | None = None
        self._output_path: Path | None = None

        self._build_ui()
        self._connect_signals()
        self._update_convert_button()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Input file
        input_row = QHBoxLayout()
        self._input_edit = QLineEdit()
        self._input_edit.setReadOnly(True)
        self._input_edit.setPlaceholderText("Select input file...")
        input_row.addWidget(self._input_edit)
        self._input_browse = QPushButton("Browse...")
        input_row.addWidget(self._input_browse)
        form.addRow("Input file:", input_row)

        # Detected format
        self._format_label = QLabel("—")
        form.addRow("Detected format:", self._format_label)

        # Output format
        self._output_format_combo = QComboBox()
        form.addRow("Output format:", self._output_format_combo)

        # Pack name (hidden by default)
        self._pack_name_edit = QLineEdit()
        self._pack_name_edit.setPlaceholderText("Pack name for HOTA output")
        self._pack_name_label = QLabel("Pack name:")
        form.addRow(self._pack_name_label, self._pack_name_edit)
        self._pack_name_label.setVisible(False)
        self._pack_name_edit.setVisible(False)

        # Output file
        output_row = QHBoxLayout()
        self._output_edit = QLineEdit()
        self._output_edit.setReadOnly(True)
        self._output_edit.setPlaceholderText("Select output file...")
        output_row.addWidget(self._output_edit)
        self._output_browse = QPushButton("Browse...")
        output_row.addWidget(self._output_browse)
        form.addRow("Output file:", output_row)

        layout.addLayout(form)

        # Buttons
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
        )
        self._convert_btn = self._buttons.addButton(
            "Convert", QDialogButtonBox.ButtonRole.AcceptRole
        )
        self._convert_btn.setEnabled(False)
        layout.addWidget(self._buttons)

    def _connect_signals(self) -> None:
        self._input_browse.clicked.connect(self._on_browse_input)
        self._output_browse.clicked.connect(self._on_browse_output)
        self._output_format_combo.currentIndexChanged.connect(
            self._on_output_format_changed
        )
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

    def _on_browse_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input Template",
            "",
            "All Templates (*.txt *.h3t);;SOD Templates (*.txt);;HOTA Templates (*.h3t);;All Files (*)",
        )
        if not path:
            return

        self._input_path = Path(path)
        self._input_edit.setText(str(self._input_path))

        # Detect format
        try:
            parser = detect_format(self._input_path)
            self._input_format_id = parser.format_id
            self._format_label.setText(parser.format_name)
        except Exception:
            self._input_format_id = None
            self._format_label.setText("Unknown")
            self._update_convert_button()
            return

        # Rebuild output format combo (exclude detected input format)
        self._output_format_combo.blockSignals(True)
        self._output_format_combo.clear()
        for fmt_id, (display_name, _, _) in _FORMATS.items():
            if fmt_id != self._input_format_id:
                self._output_format_combo.addItem(display_name, fmt_id)
        self._output_format_combo.blockSignals(False)

        # Auto-suggest output path and update pack name visibility
        self._on_output_format_changed()

        # Set default pack name
        self._pack_name_edit.setText(self._input_path.stem)

        self._update_convert_button()

    def _on_output_format_changed(self) -> None:
        fmt_id = self._output_format_combo.currentData()
        if not fmt_id or not self._input_path:
            return

        # Update output file suggestion
        _, _, ext = _FORMATS[fmt_id]
        suggested = self._input_path.with_suffix(ext)
        # Avoid overwriting input file
        if suggested == self._input_path:
            suggested = self._input_path.with_stem(
                self._input_path.stem + "_converted"
            ).with_suffix(ext)
        self._output_path = suggested
        self._output_edit.setText(str(suggested))

        # Show pack name row only for SOD -> HOTA conversions
        show_pack = self._input_format_id == "sod" and fmt_id in (
            "hota17",
            "hota18",
        )
        self._pack_name_label.setVisible(show_pack)
        self._pack_name_edit.setVisible(show_pack)

        self._update_convert_button()

    def _on_browse_output(self) -> None:
        fmt_id = self._output_format_combo.currentData()
        if not fmt_id:
            return

        _, file_filter, _ = _FORMATS[fmt_id]
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Converted Template",
            str(self._output_path) if self._output_path else "",
            f"{file_filter};;All Files (*)",
        )
        if path:
            self._output_path = Path(path)
            self._output_edit.setText(str(self._output_path))
            self._update_convert_button()

    def _update_convert_button(self) -> None:
        enabled = (
            self._input_path is not None
            and self._input_format_id is not None
            and self._output_format_combo.currentData() is not None
            and self._output_path is not None
        )
        self._convert_btn.setEnabled(enabled)

    # ── Public properties (read after exec()) ─────────────────────────

    @property
    def input_path(self) -> Path:
        return self._input_path

    @property
    def input_format_id(self) -> str:
        return self._input_format_id

    @property
    def output_path(self) -> Path:
        return self._output_path

    @property
    def output_format_id(self) -> str:
        return self._output_format_combo.currentData()

    @property
    def pack_name(self) -> str:
        return self._pack_name_edit.text().strip()
