#!/bin/bash
# File: build-with-database.sh
# Path: /home/herb/Desktop/AndyLibrary/Standalone/build-with-database.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 02:20PM

# Build Windows EXE with database bundled for AndyLibrary

set -e  # Exit on any error

echo "🔥 BUILDING ANDYLIBRARY WINDOWS EXE WITH DATABASE 🔥"
echo "=" * 60

# Check if we're in the right directory
if [[ ! -f "StandaloneAndyLibrary.py" ]]; then
    echo "❌ Error: StandaloneAndyLibrary.py not found"
    echo "Please run this script from the Standalone directory"
    exit 1
fi

# Check for database
DATABASE_FOUND=false
if [[ -f "MyLibrary.db" ]]; then
    echo "✅ Database found in Standalone directory: $(du -h MyLibrary.db | cut -f1)"
    DATABASE_FOUND=true
elif [[ -f "../Data/Databases/MyLibrary.db" ]]; then
    echo "✅ Database found in main Data directory"
    echo "📥 Copying database to Standalone directory..."
    cp "../Data/Databases/MyLibrary.db" .
    DATABASE_FOUND=true
else
    echo "❌ ERROR: MyLibrary.db not found!"
    echo "Searched locations:"
    echo "  - $(pwd)/MyLibrary.db"  
    echo "  - $(pwd)/../Data/Databases/MyLibrary.db"
    echo ""
    echo "Please ensure the database exists before building."
    exit 1
fi

if [[ "$DATABASE_FOUND" == true ]]; then
    DB_SIZE=$(du -h MyLibrary.db | cut -f1)
    echo "📊 Database size: $DB_SIZE"
fi

# Check for virtual environment
if [[ ! -d "venv" ]]; then
    echo "🔄 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "🔄 Installing/updating requirements..."
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements-standalone.txt

echo "🔄 Cleaning previous builds..."
rm -rf build dist *.spec.backup

echo "🔄 Building Windows EXE with database..."
pyinstaller --clean standalone-with-database.spec

# Check if build succeeded
if [[ -f "dist/AndyLibrary-Standalone-WithDB.exe" ]]; then
    EXE_SIZE=$(du -h "dist/AndyLibrary-Standalone-WithDB.exe" | cut -f1)
    echo ""
    echo "🎉 BUILD SUCCESSFUL! 🎉"
    echo "📄 Executable: dist/AndyLibrary-Standalone-WithDB.exe"
    echo "📊 EXE Size: $EXE_SIZE"
    echo "📚 Database: Bundled inside EXE"
    echo ""
    echo "📋 Next steps:"
    echo "1. Copy dist/AndyLibrary-Standalone-WithDB.exe to your Windows machine"
    echo "2. Run the EXE - it should now have access to the database"
    echo "3. The app will automatically extract and use the bundled database"
    echo ""
    echo "🔍 If issues persist, check the console output when running the EXE"
    echo "   The app will show database connection status and paths"
else
    echo ""
    echo "❌ BUILD FAILED!"
    echo "Check the output above for errors"
    exit 1
fi

echo "✅ Build process complete!"