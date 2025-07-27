@echo off
REM File: build.bat
REM Path: /home/herb/Desktop/AndyLibrary/Standalone/build.bat
REM Standard: AIDEV-PascalCase-2.1
REM Created: 2025-07-26
REM Last Modified: 2025-07-26 10:22AM

echo.
echo ================================================================
echo  ANDYLIBRARY STANDALONE - BUILD SCRIPT
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install -r requirements-standalone.txt

echo [4/5] Building executable with PyInstaller...
pyinstaller standalone-library.spec --clean --noconfirm

echo [5/5] Build complete!
echo.

if exist "dist\AndyLibrary-Standalone.exe" (
    echo ✅ SUCCESS: Executable created at dist\AndyLibrary-Standalone.exe
    echo.
    echo To test the standalone version:
    echo 1. Copy dist\AndyLibrary-Standalone.exe to target Windows machine
    echo 2. Ensure MyLibrary.db is available in the main AndyLibrary installation
    echo 3. Run the executable
    echo.
    set /p CHOICE="Open dist folder? (y/n): "
    if /i "%CHOICE%"=="y" (
        explorer dist
    )
) else (
    echo ❌ FAILED: Executable not found. Check the build log for errors.
)

echo.
pause