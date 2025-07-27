# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['StandaloneAndyLibrary.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../WebPages', 'WebPages'),  # Include WebPages directory from parent
    ],
    hiddenimports=[
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off', 
        'uvicorn.protocols.websockets.auto',
        'fastapi',
        'sqlite3',
        'pathlib',
        'threading',
        'webbrowser',
        'google.auth',
        'google.auth.transport.requests',
        'googleapiclient.discovery',
        'googleapiclient.http'
    ],
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
    name='AndyLibrary-Standalone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX for compatibility
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
    uac_uiaccess=False,
)