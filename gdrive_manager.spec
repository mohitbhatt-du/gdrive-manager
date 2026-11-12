# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification file for GDrive Manager."""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

block_cipher = None

project_dir = Path(SPECPATH).resolve()

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")
pystray_datas, pystray_binaries, pystray_hiddenimports = collect_all("pystray")

datas = [
    (str(project_dir / "assets"), "assets"),
    (str(project_dir / "bin" / "rclone"), "bin/rclone"),
] + ctk_datas + pystray_datas

binaries = ctk_binaries + pystray_binaries

hiddenimports = [
    "customtkinter",
    "pystray",
    "pystray._win32",
    "keyring",
    "keyring.backends",
    "keyring.backends.Windows",
    "win32api",
    "win32file",
    "win32con",
    "PIL",
    "PIL.Image",
    "PIL.ImageDraw",
] + ctk_hiddenimports + pystray_hiddenimports

a = Analysis(
    [str(project_dir / "main.py")],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

icon_path = str(project_dir / "assets" / "branding" / "icon.ico")
if not os.path.exists(icon_path):
    icon_path = str(project_dir / "assets" / "icons" / "app_icon.ico")
if not os.path.exists(icon_path):
    icon_path = None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GDriveManager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="GDriveManager",
)
