# -*- mode: python ; coding: utf-8 -*-
"""
Spec PyInstaller pour générer l'exécutable Bolt V1.0 Beta.
Inclut les assets (icônes, images, CSV) utilisés par l'interface Tk.
"""

from pathlib import Path
import sys

# __file__ peut ne pas etre defini quand le spec est exec via exec(); on fallback sur cwd.
if "__file__" in globals():
    PROJECT_ROOT = Path(__file__).resolve().parent
else:
    PROJECT_ROOT = Path.cwd()
ASSETS_DIR = PROJECT_ROOT / "assets"
SCRIPT_PATH = PROJECT_ROOT / "src" / "bolt_app" / "gui.py"

a = Analysis(
    [str(SCRIPT_PATH)],
    pathex=[str(PROJECT_ROOT / "src")],
    binaries=[],
    datas=[
        (str(ASSETS_DIR / "Bolt_logo.png"), "assets"),
        (str(ASSETS_DIR / "Bolt_logo.ico"), "assets"),
        (str(ASSETS_DIR / "Schema_technique.png"), "assets"),
        (str(ASSETS_DIR / "construction_image.png"), "assets"),
        (str(ASSETS_DIR / "Pas-std.csv"), "assets"),
        (str(ASSETS_DIR / "Frottement.csv"), "assets"),
        (str(ASSETS_DIR / "Trou_passage.csv"), "assets"),
        (str(ASSETS_DIR / "Tete_vis.csv"), "assets"),
        (str(ASSETS_DIR / "img" / "Hexagonale.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "CHC Cylindrique.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "CHC fraisee.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "CHC bombee.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "bombee fendue.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "Vis_bombee_philips_pozidriv.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "Bombee Torx.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "Schema_appui_direct.png"), "assets/img"),
        (str(ASSETS_DIR / "img" / "Schema_appui_rondelle.png"), "assets/img"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Bolt",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(ASSETS_DIR / "Bolt_logo.ico")],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Bolt",
)
