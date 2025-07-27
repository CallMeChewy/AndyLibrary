# Wine Setup for Windows Cross-Compilation

## Quick Wine Setup

```bash
# 1. Install Wine
sudo apt update
sudo apt install wine

# 2. Configure Wine
winecfg  # Select Windows 10 mode

# 3. Download Python for Windows
wget https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe

# 4. Install Python in Wine
wine python-3.11.0-amd64.exe
# Follow installer prompts, select "Add to PATH"

# 5. Test Wine Python
wine python --version

# 6. Install our dependencies
wine python -m pip install fastapi uvicorn aiofiles python-multipart pyinstaller

# 7. Build Windows exe
wine python -m PyInstaller standalone-library.spec --clean
```

Result: `dist/AndyLibrary-Standalone.exe` ready for Windows!