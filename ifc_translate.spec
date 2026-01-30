# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for IFC Translate Tool

This spec file configures bundling of the application with all necessary
dependencies, including ifcopenshell's native C++ wrapper and ifcpatch recipes.

Build command (run from project root):
    pyinstaller ifc_translate.spec

Output: dist/IFC Translate Tool/ (directory with executable and dependencies)
"""

from PyInstaller.utils.hooks import collect_all

# Collect ifcopenshell (includes native C++ wrapper DLLs)
ifcopenshell_datas, ifcopenshell_binaries, ifcopenshell_hiddenimports = collect_all('ifcopenshell')

# Collect ifcpatch (includes recipe files)
ifcpatch_datas, ifcpatch_binaries, ifcpatch_hiddenimports = collect_all('ifcpatch')

# Collect platformdirs (cross-platform directory handling)
platformdirs_datas, platformdirs_binaries, platformdirs_hiddenimports = collect_all('platformdirs')

# Combine collected data
datas = ifcopenshell_datas + ifcpatch_datas + platformdirs_datas
binaries = ifcopenshell_binaries + ifcpatch_binaries + platformdirs_binaries
hiddenimports = ifcopenshell_hiddenimports + ifcpatch_hiddenimports + platformdirs_hiddenimports

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IFC Translate Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid DLL corruption
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX to avoid DLL corruption
    upx_exclude=[],
    name='IFC Translate Tool',
)
