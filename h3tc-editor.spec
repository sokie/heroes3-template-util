# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

icons_dir = os.path.join("src", "h3tc", "editor", "icons")

a = Analysis(
    ["launcher.py"],
    pathex=["src"],
    binaries=[],
    datas=[
        (icons_dir, os.path.join("h3tc", "editor", "icons")),
    ],
    hiddenimports=[
        "h3tc",
        "h3tc.cli",
        "h3tc.models",
        "h3tc.enums",
        "h3tc.constants",
        "h3tc.formats",
        "h3tc.parsers",
        "h3tc.parsers.base",
        "h3tc.parsers.sod",
        "h3tc.parsers.hota",
        "h3tc.parsers.hota18",
        "h3tc.writers",
        "h3tc.writers.base",
        "h3tc.writers.sod",
        "h3tc.writers.hota",
        "h3tc.writers.hota18",
        "h3tc.converters",
        "h3tc.converters.sod_to_hota",
        "h3tc.converters.hota_to_sod",
        "h3tc.converters.hota_to_hota18",
        "h3tc.converters.hota18_to_hota",
        "h3tc.editor",
        "h3tc.editor.main_window",
        "h3tc.editor.constants",
        "h3tc.editor.convert_dialog",
        "h3tc.editor.canvas",
        "h3tc.editor.canvas.scene",
        "h3tc.editor.canvas.view",
        "h3tc.editor.canvas.zone_item",
        "h3tc.editor.canvas.connection_item",
        "h3tc.editor.canvas.icons",
        "h3tc.editor.canvas.layout",
        "h3tc.editor.panels",
        "h3tc.editor.panels.zone_panel",
        "h3tc.editor.panels.connection_panel",
        "h3tc.editor.panels.map_panel",
        "h3tc.editor.panels.map_selector",
        "h3tc.editor.panels.binding",
        "h3tc.editor.models",
        "h3tc.editor.models.editor_state",
        "h3tc.editor.models.layout_store",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="h3tc-editor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
)
