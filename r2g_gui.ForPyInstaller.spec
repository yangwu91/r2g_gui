# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [
        './src/scripts/r2g.gui.py',
        "./src/r2g_gui/main/operations.py",
        "./src/r2g_gui/main/ui_main.py"
    ],
    pathex=['./src'],
    binaries=[],
    datas=[
        ("./src/r2g_gui", "r2g_gui"),
    ],
    hiddenimports=['six', 'chardet', 'idna', 'urllib3', 'certifi', 'websocket', 'requests', 'docker', 'r2g_gui'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='r2g',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    icon='.\\src\\r2g_gui\\images\\logo.ico',
    upx=True,
    console=False
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='r2g'
)
app = BUNDLE(
    coll,
    name='r2g.app',
    icon="./src/r2g_gui/images/logo.icns",
    bundle_identifier="bioinformatics.drwu.r2g"
)
