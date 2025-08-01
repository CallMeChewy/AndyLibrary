# File: build_windows_exe.spec
# Path: /home/herb/Desktop/AndyLibrary/build_windows_exe.spec
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 02:09PM

"""
PyInstaller spec file for AndyLibrary Windows .exe
Creates a standalone executable with all dependencies bundled
"""

import os
from pathlib import Path

# Get the base directory
base_dir = Path(SPECPATH)

# Define data files to include
datas = [
    # Include the entire Source directory
    (str(base_dir / 'Source'), 'Source'),
    
    # Include WebPages directory with all static files
    (str(base_dir / 'WebPages'), 'WebPages'),
    
    # Include Data directory structure but exclude databases
    (str(base_dir / 'Data' / 'Cache'), 'Data/Cache'),
    (str(base_dir / 'Data' / 'Covers'), 'Data/Covers'),
    (str(base_dir / 'Data' / 'HTML'), 'Data/HTML'),
    (str(base_dir / 'Data' / 'Local'), 'Data/Local'),
    (str(base_dir / 'Data' / 'Logs'), 'Data/Logs'),
    (str(base_dir / 'Data' / 'Text'), 'Data/Text'),
    (str(base_dir / 'Data' / 'Thumbs'), 'Data/Thumbs'),
    # NOTE: Databases intentionally excluded - will be downloaded from Google Drive on first run
    
    # Include Config directory
    (str(base_dir / 'Config'), 'Config'),
    
    # Include any additional required files
    (str(base_dir / 'CLAUDE.md'), '.'),
    
    # Include the FULL DATABASE for offline operation
    (str(base_dir / 'Standalone' / 'GrandsonLibrary_Full.db'), 'Standalone'),
]

# Hidden imports that PyInstaller might miss - COMPREHENSIVE LIST
hiddenimports = [
    # FastAPI and Uvicorn core
    'fastapi',
    'fastapi.routing',
    'fastapi.responses',
    'fastapi.staticfiles',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'uvicorn',
    'uvicorn.main',
    'uvicorn.server',
    'uvicorn.config',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    
    # Starlette (FastAPI dependency)
    'starlette',
    'starlette.applications',
    'starlette.middleware',
    'starlette.middleware.base',
    'starlette.middleware.cors',
    'starlette.responses',
    'starlette.staticfiles',
    'starlette.routing',
    'starlette.requests',
    'starlette.background',
    
    # Python standard library
    'sqlite3',
    'json',
    'pathlib',
    'datetime',
    'socket',
    'threading',
    'webbrowser',
    'platform',
    'os',
    'sys',
    'time',
    'shutil',
    'urllib.parse',
    're',
    
    # Third-party dependencies
    'requests',
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic.types',
    'cryptography',
    'cryptography.fernet',
    'psutil',
    
    # Google API libraries (optional)
    'google.auth',
    'google_auth_oauthlib',
    'google.oauth2.credentials',
    'googleapiclient',
    'googleapiclient.discovery',
    'googleapiclient.errors',
    
    # AsyncIO support
    'asyncio',
    'asyncio.events',
    'asyncio.coroutines',
    
    # Typing support
    'typing',
    'typing_extensions',
    
    # Email and networking
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    
    # Additional utilities
    'collections',
    'functools',
    'itertools',
    'traceback',
]

# Analysis configuration
a = Analysis(
    ['AndyLibraryStandalone.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AndyLibrary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX on Windows for better compatibility
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console window so users can see status messages
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
    version_file=None,
)