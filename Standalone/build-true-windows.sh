#!/bin/bash
# File: build-true-windows.sh
# Path: /home/herb/Desktop/AndyLibrary/Standalone/build-true-windows.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 05:00PM

# Build TRUE Windows EXE for Grandson using Wine + Windows Python

set -e

echo "🍷 BUILDING TRUE WINDOWS EXE FOR GRANDSON 🍷"
echo "=" * 60
echo "Using Wine to create actual Windows executable"
echo ""

# Check if Wine is installed
if ! command -v wine &> /dev/null; then
    echo "❌ Wine not installed. Installing Wine..."
    sudo apt update
    sudo apt install -y wine
fi

# Check for Windows Python in Wine
WINE_PYTHON="/home/herb/.wine/drive_c/Python311/python.exe"
if [[ ! -f "$WINE_PYTHON" ]]; then
    echo "❌ Windows Python not found in Wine"
    echo "Please install Python for Windows in Wine first:"
    echo "1. Download Python 3.11 Windows installer"
    echo "2. Run: wine python-3.11.x-amd64.exe"
    echo "3. Install to C:\\Python311"
    exit 1
fi

echo "✅ Found Windows Python in Wine"

# Create Windows-specific spec file
echo "🔄 Creating Windows-specific build configuration..."

cat > grandson-true-windows.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# TRUE Windows PyInstaller spec for Grandson's Library

import os
from pathlib import Path

# Get paths - adjust for Wine environment
spec_dir = Path(SPECPATH)
app_dir = spec_dir.parent
webpages_dir = app_dir / "WebPages"

# Data files for grandson
data_files = []

# Include WebPages if available
if webpages_dir.exists():
    for root, dirs, files in os.walk(webpages_dir):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(app_dir)
            data_files.append((str(file_path), str(relative_path.parent)))

# Include database
db_paths = ["MyLibrary.db", "../Data/Databases/MyLibrary.db"]
for db_path in db_paths:
    if Path(db_path).exists():
        data_files.append((str(Path(db_path).resolve()), '.'))
        break

a = Analysis(
    ['GrandsonLibrary.py'],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.websockets_impl', 
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'fastapi.routing',
        'fastapi.responses', 
        'fastapi.staticfiles',
        'requests',
        'requests.adapters',
        'requests.auth',
        'urllib3',
        'urllib3.util',
        'sqlite3',
        'threading',
        'webbrowser',
        'pathlib',
        'shutil', 
        'json',
        'socket',
        're'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy',
        'PIL', 'cv2', 'torch', 'tensorflow', 'sklearn'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GrandsonLibrary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Setup Wine environment
echo "🍷 Setting up Wine environment..."
export WINEARCH=win64
export WINEPREFIX="$HOME/.wine"

# Install requirements in Wine Python
echo "🔄 Installing Python packages in Wine..."
wine "$WINE_PYTHON" -m pip install --upgrade pip
wine "$WINE_PYTHON" -m pip install pyinstaller fastapi uvicorn requests

# Build using Wine Python
echo "🔄 Building Windows EXE using Wine Python..."
wine "$WINE_PYTHON" -m PyInstaller --clean grandson-true-windows.spec

# Check if build succeeded
if [[ -f "dist/GrandsonLibrary.exe" ]]; then
    EXE_SIZE=$(du -h "dist/GrandsonLibrary.exe" | cut -f1)
    echo ""
    echo "🎉 TRUE WINDOWS EXE BUILT! 🎉" 
    echo "📄 Executable: dist/GrandsonLibrary.exe"
    echo "📊 Size: $EXE_SIZE"
    echo "🖥️ Platform: Windows x64"
    echo ""
    echo "✅ This should work on Windows now!"
    echo "Copy dist/GrandsonLibrary.exe to Windows and test"
else
    echo "❌ Build failed - check Wine setup"
    exit 1
fi
EOF

chmod +x build-true-windows.sh