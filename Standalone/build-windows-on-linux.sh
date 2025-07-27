#!/bin/bash
# File: build-windows-on-linux.sh
# Path: /home/herb/Desktop/AndyLibrary/Standalone/build-windows-on-linux.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 10:47AM

echo "🍷 CROSS-COMPILING WINDOWS EXE ON LINUX WITH WINE"
echo "================================================="

# Check if Wine is installed
if ! command -v wine &> /dev/null; then
    echo "❌ Wine not found. Installing..."
    echo "Run: sudo apt install wine"
    echo "Then download Python for Windows and install with:"
    echo "wine python-3.11.0-amd64.exe"
    exit 1
fi

echo "🔍 Checking Wine Python installation..."
if ! wine python --version &> /dev/null; then
    echo "❌ Windows Python not found in Wine"
    echo "Please install Python for Windows in Wine first:"
    echo "1. Download: https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
    echo "2. Run: wine python-3.11.0-amd64.exe"
    exit 1
fi

echo "✅ Wine Python found"
echo "🔧 Installing dependencies in Wine..."

wine python -m pip install --upgrade pip
wine python -m pip install fastapi uvicorn aiofiles python-multipart starlette anyio sniffio h11 pydantic pydantic_core typing_extensions annotated-types pyinstaller

echo "🔨 Building Windows executable..."
wine python -m PyInstaller standalone-library.spec --clean --noconfirm

echo "🎉 Build complete!"
if [ -f "dist/AndyLibrary-Standalone.exe" ]; then
    echo "✅ Windows executable created: dist/AndyLibrary-Standalone.exe"
    ls -la dist/
else
    echo "❌ Build failed - check output above"
fi