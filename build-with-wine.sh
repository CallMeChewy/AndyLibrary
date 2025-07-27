#!/bin/bash
# Build Windows EXE using Wine on Linux

echo "🏗️ Building Windows EXE with Wine..."

# Set Wine environment
export WINEPREFIX="$HOME/.wine"

# Install dependencies in Wine Python
echo "Installing dependencies..."
wine python -m pip install -r requirements.txt
wine python -m pip install pyinstaller

# Build the executable
echo "Building executable..."
wine python -m PyInstaller \
    --onefile \
    --windowed \
    --name "MyApp" \
    --distpath "./dist-windows" \
    your_main_script.py

echo "✅ Build complete!"
echo "Windows executable: ./dist-windows/MyApp.exe"

# Test the executable in Wine
echo "Testing executable..."
wine ./dist-windows/MyApp.exe