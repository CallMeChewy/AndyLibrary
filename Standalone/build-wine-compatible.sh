#!/bin/bash
# File: build-wine-compatible.sh
# Path: /home/herb/Desktop/AndyLibrary/Standalone/build-wine-compatible.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-27
# Last Modified: 2025-07-27 11:59PM

echo "🍷 BUILDING WINE-COMPATIBLE WINDOWS EXE"
echo "========================================"

# Create Wine-compatible PyInstaller spec
cat > wine-compatible.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['StandaloneAndyLibrary.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols.websockets.auto',
        'fastapi',
        'sqlite3',
        'pathlib',
        'threading',
        'webbrowser'
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
    name='AndyLibrary-Wine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression for Wine compatibility
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch='x86_64',  # Explicit 64-bit target
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,  # No UAC requirements
    uac_uiaccess=False,
)
EOF

echo "[1/4] Activating virtual environment..."
source venv/bin/activate

echo "[2/4] Installing Wine-compatible PyInstaller..."
pip install pyinstaller==5.13.2  # Use stable version known to work with Wine

echo "[3/4] Building with Wine-friendly settings..."
pyinstaller wine-compatible.spec --clean --noconfirm

echo "[4/4] Testing executable..."
if [ -f "dist/AndyLibrary-Wine.exe" ]; then
    echo "✅ Wine-compatible EXE created: dist/AndyLibrary-Wine.exe"
    ls -la dist/AndyLibrary-Wine.exe
    
    echo ""
    echo "🍷 Testing with Wine..."
    if command -v wine &> /dev/null; then
        echo "Wine version: $(wine --version)"
        wine dist/AndyLibrary-Wine.exe --version 2>/dev/null || echo "ℹ️ Use 'wine dist/AndyLibrary-Wine.exe' to run"
    else
        echo "ℹ️ Wine not available for testing"
    fi
else
    echo "❌ Build failed - no executable created"
fi