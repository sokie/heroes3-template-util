"""SOD Visual Template Editor for H3 Template Converter."""


def launch(filepath: str | None = None) -> None:
    """Launch the visual template editor.

    Args:
        filepath: Optional path to a .txt template file to open on launch.
    """
    import sys

    from PySide6.QtWidgets import QApplication

    from h3tc.editor.main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    if filepath:
        window.open_file(filepath)
    window.show()
    sys.exit(app.exec())
