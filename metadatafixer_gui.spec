# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Song Metadata Fixer GUI
Bundles the GUI script into a single executable with required data files.
"""

from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path

block_cipher = None

hiddenimports = [
    'mutagen',
    'mutagen.mp4',
    'mutagen.flac',
    'PIL',
    'customtkinter',
]

datas = [
    ('config.json', '.'),
]

# Analysis
a = Analysis(
    ['app_gui.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='metadatafixer-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed application
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='metadatafixer-gui',
)
