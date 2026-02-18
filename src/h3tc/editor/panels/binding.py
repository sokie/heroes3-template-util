"""Helpers to bind Qt widgets to str model fields on Pydantic models."""

from typing import Any, Callable

from PySide6.QtWidgets import QCheckBox, QComboBox, QSpinBox


def bind_spinbox(
    spinbox: QSpinBox,
    obj: Any,
    field: str,
    *,
    sub_obj: str | None = None,
    dict_key: str | None = None,
    on_change: Callable[[], None] | None = None,
) -> None:
    """Bind a QSpinBox to a str field.

    Args:
        spinbox: The spinbox widget.
        obj: The Pydantic model instance.
        field: The field name on the model (or sub-model).
        sub_obj: If set, access obj.<sub_obj>.<field> instead of obj.<field>.
        dict_key: If set, access obj.<field>[dict_key] (field is a dict).
        on_change: Optional callback when value changes.
    """
    target = getattr(obj, sub_obj) if sub_obj else obj

    # Read current value
    if dict_key is not None:
        raw = getattr(target, field).get(dict_key, "")
    else:
        raw = getattr(target, field)
    try:
        val = int(raw) if raw.strip() else 0
    except (ValueError, AttributeError):
        val = 0

    spinbox.blockSignals(True)
    spinbox.setValue(val)
    spinbox.blockSignals(False)

    def _on_value_changed(new_val: int) -> None:
        t = getattr(obj, sub_obj) if sub_obj else obj
        if dict_key is not None:
            getattr(t, field)[dict_key] = str(new_val) if new_val != 0 else ""
        else:
            setattr(t, field, str(new_val) if new_val != 0 else "")
        if on_change:
            on_change()

    spinbox.valueChanged.connect(_on_value_changed)


def bind_checkbox(
    checkbox: QCheckBox,
    obj: Any,
    field: str,
    *,
    sub_obj: str | None = None,
    dict_key: str | None = None,
    on_change: Callable[[], None] | None = None,
) -> None:
    """Bind a QCheckBox to a str field where 'x' = checked, '' = unchecked."""
    target = getattr(obj, sub_obj) if sub_obj else obj

    if dict_key is not None:
        raw = getattr(target, field).get(dict_key, "")
    else:
        raw = getattr(target, field)

    checkbox.blockSignals(True)
    checkbox.setChecked(raw.strip().lower() == "x")
    checkbox.blockSignals(False)

    def _on_toggled(checked: bool) -> None:
        t = getattr(obj, sub_obj) if sub_obj else obj
        val = "x" if checked else ""
        if dict_key is not None:
            getattr(t, field)[dict_key] = val
        else:
            setattr(t, field, val)
        if on_change:
            on_change()

    checkbox.toggled.connect(_on_toggled)


def bind_combo_index(
    combo: QComboBox,
    obj: Any,
    field: str,
    *,
    values: list[str] | None = None,
    on_change: Callable[[], None] | None = None,
) -> None:
    """Bind a QComboBox to a str field using item data or index mapping.

    Args:
        combo: The combobox widget (items should already be added).
        obj: The Pydantic model.
        field: The field name.
        values: If provided, map combo index to these str values.
        on_change: Optional callback.
    """
    raw = getattr(obj, field).strip()

    combo.blockSignals(True)
    if values:
        try:
            idx = values.index(raw)
        except ValueError:
            idx = 0
        combo.setCurrentIndex(idx)
    else:
        idx = combo.findText(raw)
        if idx >= 0:
            combo.setCurrentIndex(idx)
    combo.blockSignals(False)

    def _on_index_changed(index: int) -> None:
        if values:
            val = values[index] if 0 <= index < len(values) else ""
        else:
            val = combo.currentText()
        setattr(obj, field, val)
        if on_change:
            on_change()

    combo.currentIndexChanged.connect(_on_index_changed)


def disconnect_all(widget) -> None:
    """Disconnect all signals from a widget, ignoring errors."""
    try:
        if isinstance(widget, QSpinBox):
            widget.valueChanged.disconnect()
        elif isinstance(widget, QCheckBox):
            widget.toggled.disconnect()
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.disconnect()
    except RuntimeError:
        pass  # No connections
