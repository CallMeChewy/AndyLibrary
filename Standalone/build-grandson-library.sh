#!/bin/bash
# File: build-grandson-library.sh
# Path: /home/herb/Desktop/AndyLibrary/Standalone/build-grandson-library.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 03:10PM

# Build Grandson's Educational Library - Simple and Clean!

set -e  # Exit on any error

echo "🎓 BUILDING GRANDSON'S EDUCATIONAL LIBRARY 🎓"
echo "=" * 60
echo "📚 No registration, no auth, just books!"
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

echo "🔄 Building Windows EXE for grandson..."
echo "   (This may take a few minutes - making it perfect for him!)"
pyinstaller --clean grandson-library.spec

# Check if build succeeded
if [[ -f "dist/GrandsonLibrary.exe" ]]; then
    EXE_SIZE=$(du -h "dist/GrandsonLibrary.exe" | cut -f1)
    echo ""
    echo "🎉 BUILD SUCCESSFUL FOR GRANDSON! 🎉"
    echo "📄 Executable: dist/GrandsonLibrary.exe"
    echo "📊 EXE Size: $EXE_SIZE"
    if [[ "$DATABASE_FOUND" == true ]]; then
        echo "📚 Database: Included ($DB_SIZE)"
    else
        echo "📚 Database: Demo version included"
    fi
    echo ""
    echo "📋 TESTING STEPS:"
    echo "1. Test locally first: 'wine dist/GrandsonLibrary.exe' (if wine installed)"
    echo "2. Or copy to Windows VM/machine for testing"
    echo "3. Make sure it opens browser and shows library"
    echo "4. Check that books load and search works"
    echo ""
    echo "📋 FOR GRANDSON:"
    echo "1. Copy dist/GrandsonLibrary.exe to his Windows computer"
    echo "2. Tell him to double-click it"
    echo "3. Browser should open automatically with his library"
    echo "4. No setup needed - it just works!"
    echo ""
    echo "🐧 LINUX CONVERSION PLAN:"
    echo "1. Show grandson how much easier this would be on Linux"
    echo "2. Demonstrate superior package management"
    echo "3. Mention the lack of Windows (ick) issues"
    echo "4. Convert the family to the penguin side! 🐧"
else
    echo ""
    echo "❌ BUILD FAILED!"
    echo "Check the output above for errors"
    exit 1
fi

echo ""
echo "✅ Grandson's library is ready to deploy!"
echo "   Now to convince the family about Linux... 😄"