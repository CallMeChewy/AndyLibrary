#!/bin/bash
# Wine Setup Script - Run Windows Python on Linux

echo "🍷 Setting up Wine for Windows Python builds..."

# Install Wine
sudo apt update
sudo apt install wine winetricks -y

# Configure Wine
winecfg  # This opens a GUI - set to Windows 10

# Download Python for Windows
cd /tmp
wget https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe

# Install Python in Wine
wine python-3.11.8-amd64.exe

# Install pip packages in Wine Python
wine python -m pip install --upgrade pip
wine python -m pip install pyinstaller
wine python -m pip install your-requirements

echo "✅ Wine setup complete!"
echo "Now you can run: wine python -m PyInstaller your_script.py"