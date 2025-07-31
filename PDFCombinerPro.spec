# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the current directory
current_dir = Path('.').resolve()

block_cipher = None

# Define data files to include
datas = [
    (str(current_dir / 'config'), 'config'),
    (str(current_dir / 'core'), 'core'),
    (str(current_dir / 'gui'), 'gui'),
    (str(current_dir / 'utils'), 'utils'),
]

# Check for valid icon files
icon_path = None
if sys.platform == 'win32':
    icon_file = current_dir / 'assets' / 'icon.ico'
    if icon_file.exists() and icon_file.stat().st_size > 100:  # Bigger than placeholder
        icon_path = str(icon_file)
elif sys.platform == 'darwin':
    icon_file = current_dir / 'assets' / 'icon.icns'
    if icon_file.exists() and icon_file.stat().st_size > 100:  # Bigger than placeholder
        icon_path = str(icon_file)

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'fitz',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.pdfgen.canvas',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.platypus',
    'PIL',
    'PIL._imaging',
    'inquirer',
    'blessed',
]

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFCombinerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

# Create app bundle on macOS
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PDFCombinerPro.app',
        icon=icon_path,
        bundle_identifier='com.pdfcombinerpro.app',
    )
