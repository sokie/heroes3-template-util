# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

icons_dir = os.path.join("src", "h3tc", "editor", "icons")

a = Analysis(
    [os.path.join("src", "h3tc", "editor", "__init__.py")],
    pathex=["src"],
    binaries=[],
    datas=[
        (icons_dir, os.path.join("h3tc", "editor", "icons")),
    ],
    hiddenimports=[
        "h3tc",
        "h3tc.cli",
        "h3tc.editor",
        "h3tc.editor.main_window",
        "h3tc.models",
        "h3tc.enums",
        "h3tc.constants",
        "h3tc.parsers",
        "h3tc.writers",
        "h3tc.converters",
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
