#!/bin/bash
# File: build.sh
# Path: /home/herb/Desktop/AndyLibrary/Standalone/build.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 10:23AM

echo ""
echo "================================================================"
echo " ANDYLIBRARY STANDALONE - BUILD SCRIPT"
echo "================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

echo "[1/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install -r requirements-standalone.txt

echo "[4/5] Building executable with PyInstaller..."
pyinstaller standalone-library.spec --clean --noconfirm

echo "[5/5] Build complete!"
echo ""

if [ -f "dist/AndyLibrary-Standalone" ]; then
    echo "✅ SUCCESS: Executable created at dist/AndyLibrary-Standalone"
    echo ""
    echo "To test the standalone version:"
    echo "1. Copy dist/AndyLibrary-Standalone to target machine"
    echo "2. Ensure MyLibrary.db is available in the main AndyLibrary installation"
    echo "3. Run the executable"
    echo ""
    
    # Make executable
    chmod +x dist/AndyLibrary-Standalone
    
    read -p "Open dist folder? (y/n): " choice
    if [[ $choice == [Yy]* ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open dist
        elif command -v open &> /dev/null; then
            open dist
        else
            echo "Please check the dist/ folder manually"
        fi
    fi
else
    echo "❌ FAILED: Executable not found. Check the build log for errors."
fi

echo ""
read -p "Press Enter to continue..."