#!/bin/bash
# File: build-windows-grandson.sh
# Path: /home/herb/Desktop/AndyLibrary/Standalone/build-windows-grandson.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 04:15PM

# Build Grandson's Library for Windows using Wine/CrossPlatform approach

set -e  # Exit on any error

echo "🎓 BUILDING GRANDSON'S LIBRARY FOR WINDOWS 🎓"
echo "=" * 60
echo "🍷 Using cross-platform build for Windows compatibility"
echo ""

# Check if we're in the right directory
if [[ ! -f "GrandsonLibrary.py" ]]; then
    echo "❌ Error: GrandsonLibrary.py not found"
    echo "Please run this script from the Standalone directory"
    exit 1
fi

# Check for database
DATABASE_FOUND=false
DB_SIZE=""

if [[ -f "MyLibrary.db" ]]; then
    echo "✅ Database found in Standalone directory"
    DB_SIZE=$(du -h MyLibrary.db | cut -f1)
    DATABASE_FOUND=true
elif [[ -f "../Data/Databases/MyLibrary.db" ]]; then
    echo "✅ Database found in main Data directory"
    echo "📥 Copying database for grandson..."
    cp "../Data/Databases/MyLibrary.db" .
    DB_SIZE=$(du -h MyLibrary.db | cut -f1)
    DATABASE_FOUND=true
else
    echo "⚠️ No database found - grandson will get demo library"
    echo "This is okay for testing, but he'll want the real library!"
fi

if [[ "$DATABASE_FOUND" == true ]]; then
    echo "📊 Grandson's library size: $DB_SIZE"
fi

# Create Windows-compatible spec file
echo "🔄 Creating Windows-compatible build configuration..."

cat > grandson-library-windows.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Windows-compatible PyInstaller spec for Grandson's Educational Library

import os
from pathlib import Path

# Get paths
spec_dir = Path(SPECPATH)
app_dir = spec_dir.parent
standalone_dir = spec_dir
webpages_dir = app_dir / "WebPages"
main_db_path = app_dir / "Data" / "Databases" / "MyLibrary.db"
standalone_db_path = standalone_dir / "MyLibrary.db"

# Collect data files for grandson's library
data_files = []

# Include WebPages directory (simplified web interface)
if webpages_dir.exists():
    for root, dirs, files in os.walk(webpages_dir):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(app_dir)
            data_files.append((str(file_path), str(relative_path.parent)))
    print(f"📁 Including WebPages directory: {len([f for f in data_files if 'WebPages' in f[1]])} files")

# Include database - grandson gets grandpa's library!
database_included = False
possible_db_paths = [
    main_db_path,           # Main database location
    standalone_db_path,     # Database in standalone directory
    app_dir / "MyLibrary.db"  # Database in app root
]

for db_path in possible_db_paths:
    if db_path.exists():
        print(f"📚 Including grandson's library database: {db_path}")
        data_files.append((str(db_path), '.'))  # Bundle in root of EXE
        database_included = True
        break

if not database_included:
    print("⚠️ WARNING: No database found to bundle!")
    print("Grandson will get a demo library instead")

print(f"📦 Total files for grandson: {len(data_files)}")

a = Analysis(
    ['GrandsonLibrary.py'],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        # FastAPI and web server
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
        # HTTP requests for Google Drive
        'requests',
        'requests.adapters',
        'requests.auth',
        'urllib3',
        'urllib3.util',
        # Basic utilities
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
        # Remove heavy dependencies grandson doesn't need
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
        'sklearn',
        'nltk',
        'spacy'
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
    upx=False,  # Disable UPX - more reliable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console so grandson can see what's happening
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Could add a nice education icon later
)
EOF

# Check for virtual environment
if [[ ! -d "venv" ]]; then
    echo "🔄 Creating virtual environment for build..."
    python3 -m venv venv
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "🔄 Installing build requirements..."
pip install --upgrade pip
pip install pyinstaller
pip install fastapi uvicorn requests

echo "🔄 Cleaning previous builds..."
rm -rf build dist __pycache__ *.spec.backup

echo "🔄 Building Windows-compatible executable..."
echo "   (This may take a few minutes - making it perfect for grandson!)"

# Build using the Windows-compatible spec
pyinstaller --clean grandson-library-windows.spec

# Check if build succeeded - look for the actual executable name
EXECUTABLE_NAME=""
if [[ -f "dist/GrandsonLibrary.exe" ]]; then
    EXECUTABLE_NAME="GrandsonLibrary.exe"
elif [[ -f "dist/GrandsonLibrary" ]]; then
    EXECUTABLE_NAME="GrandsonLibrary"
    # Rename to .exe for Windows compatibility
    mv "dist/GrandsonLibrary" "dist/GrandsonLibrary.exe"
    EXECUTABLE_NAME="GrandsonLibrary.exe"
fi

if [[ -n "$EXECUTABLE_NAME" && -f "dist/$EXECUTABLE_NAME" ]]; then
    EXE_SIZE=$(du -h "dist/$EXECUTABLE_NAME" | cut -f1)
    echo ""
    echo "🎉 BUILD SUCCESSFUL FOR GRANDSON! 🎉"
    echo "📄 Executable: dist/$EXECUTABLE_NAME"
    echo "📊 EXE Size: $EXE_SIZE"
    if [[ "$DATABASE_FOUND" == true ]]; then
        echo "📚 Database: Included ($DB_SIZE)"
    else
        echo "📚 Database: Demo version included"
    fi
    echo ""
    echo "🧪 TESTING STEPS:"
    echo "1. Test locally first with: timeout 10s ./dist/$EXECUTABLE_NAME"
    echo "2. Copy to Windows machine for full testing"
    echo "3. Make sure it opens browser and shows setup page"
    echo "4. Test with your Google Drive share link"
    echo ""
    echo "📋 FOR GRANDSON:"
    echo "1. Copy dist/$EXECUTABLE_NAME to his Windows computer"
    echo "2. Tell him to double-click it"
    echo "3. He'll see a setup page asking for Grandpa's Google Drive link"
    echo "4. He enters your link and your name"
    echo "5. App downloads your library automatically"
    echo "6. No technical knowledge required - it just works!"
    echo ""
    echo "🐧 LINUX CONVERSION AMMUNITION:"
    echo "1. 'See how much easier this would be on Linux?'"
    echo "2. 'No Windows updates interrupting your reading!'"
    echo "3. 'Better security and no spyware!'"
    echo "4. 'Plus LibreOffice is better than MS Office!' 😄"
else
    echo ""
    echo "❌ BUILD FAILED!"
    echo "Expected executable not found in dist/ directory"
    echo "Contents of dist/:"
    ls -la dist/ 2>/dev/null || echo "No dist directory found"
    exit 1
fi

echo ""
echo "✅ Grandson's library is ready for Windows deployment!"
echo "   Now to work on that LibreOffice conversion... 😉"