# File: build_windows_final.py
# Path: /home/herb/Desktop/AndyLibrary/build_windows_final.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 02:15PM

"""
Final Windows build script for AndyLibrary
Creates a complete Windows executable with documentation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def create_windows_exe():
    """Create the final Windows executable"""
    base_dir = Path(__file__).parent
    
    print("🏔️ AndyLibrary - Final Windows Build")
    print("=" * 50)
    
    # Step 1: Build the executable
    print("🔨 Building executable...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean", "--noconfirm", 
            str(base_dir / "build_windows_exe.spec")
        ], capture_output=True, text=True, cwd=base_dir)
        
        if result.returncode != 0:
            print("❌ Build failed!")
            print(result.stderr)
            return False
            
        print("✅ Build completed!")
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False
    
    # Step 2: Verify the executable
    exe_path = base_dir / "dist" / "AndyLibrary"
    if not exe_path.exists():
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✅ Executable created: {size_mb:.1f} MB")
    
    # Step 3: Create Windows-specific files
    dist_dir = base_dir / "dist"
    
    # Create batch file for easy Windows launch
    batch_content = f"""@echo off
title AndyLibrary - Grandson's Educational Library
echo.
echo 🏔️ AndyLibrary - Project Himalaya
echo Educational Library for Everyone
echo.
echo Starting your grandson's library...
echo.
AndyLibrary.exe
pause"""
    
    with open(dist_dir / "Start_AndyLibrary.bat", 'w') as f:
        f.write(batch_content)
    
    # Create comprehensive README
    readme_content = f"""# 📚 AndyLibrary - Grandson's Educational Library

## 🚀 Quick Start (Windows)

### Method 1: Double-click to start
1. Double-click `AndyLibrary.exe`
2. Wait for your web browser to open automatically
3. Click "Continue as Guest" to browse books
4. Start reading and learning!

### Method 2: Use the batch file
1. Double-click `Start_AndyLibrary.bat`
2. Follow the same steps as above

## 📖 What You Get

- 📚 **1,219+ Educational Books** across 26 categories
- 🔍 **Smart Search** - Find books by title, author, or topic
- 📖 **Built-in PDF Reader** - Read books directly in your browser
- 🌐 **100% Offline** - No internet connection required
- 🔒 **Privacy First** - All data stays on your computer

## 📁 Categories Include

✅ Accounting & Business        ✅ Artificial Intelligence
✅ Biology & Life Sciences      ✅ Chemistry & Materials
✅ Computer Science & IT        ✅ Electronics & Engineering
✅ Foreign Languages           ✅ Games & Recreation
✅ Geography & Earth Sciences   ✅ Health & Medicine
✅ History & Social Studies    ✅ Mathematics & Logic
✅ Physics & Astronomy         ✅ Programming Languages
✅ Psychology & Sociology      ✅ Reference & General
...and many more!

## 🖥️ System Requirements

- **Windows**: 7, 8, 10, or 11 (64-bit recommended)
- **Memory**: 2GB RAM minimum
- **Storage**: 200MB free disk space
- **Browser**: Chrome, Firefox, or Edge (any modern browser)

## ⚡ Smart Features

### Automatic Port Detection
- If port 8000 is busy, automatically finds another port
- Works around HP printer services and other conflicts
- No manual configuration needed!

### Instant Search
- Search as you type
- Find books by category, subject, or keywords
- Results update in real-time

### Educational Mission
Project Himalaya: "Getting education into the hands of people who can least afford it"

## 🛠️ Troubleshooting

### Browser Doesn't Open?
- Wait 10 seconds, then manually open your browser
- Go to: `http://localhost:8000` (or check the console for the actual port)

### Port Already in Use?
- The program automatically finds available ports
- Common alternatives: 8001, 8002, 8080, 3000

### Permission Issues?
- Right-click `AndyLibrary.exe` → "Run as administrator"
- Check Windows Firewall settings

### Still Having Issues?
- Close the program completely
- Restart your computer
- Try running `Start_AndyLibrary.bat` instead

## 🎯 How to Use

1. **Start the Program**: Double-click the .exe file
2. **Wait for Browser**: Your default browser will open automatically
3. **Guest Access**: Click "Continue as Guest (Limited Access)"
4. **Browse Books**: 
   - Use the search box to find specific topics
   - Click category filters on the left
   - Browse by subject areas
5. **Read Books**: Click any book cover to open the PDF reader
6. **Enjoy Learning**: Read, learn, and explore!

## 📊 What's Inside

This portable library contains:
- **Full Database**: 10.2MB of educational content metadata
- **Web Interface**: Modern, responsive design
- **Search Engine**: AI-powered content discovery
- **PDF Reader**: Built-in document viewer
- **Offline Mode**: 95% functionality without internet

## 🎓 Educational Value

Perfect for:
- **Students**: Homework help and research
- **Teachers**: Lesson planning and resources
- **Homeschooling**: Comprehensive curriculum support
- **Lifelong Learners**: Personal development and skills
- **Researchers**: Academic reference materials

## 💝 Special Message

This library was built with love for education and learning. 
It represents thousands of hours of curation to bring quality 
educational content to students who need it most.

Enjoy exploring, learning, and growing!

---
**Built**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version**: Standalone Windows Edition
**Size**: {size_mb:.1f} MB
**Books**: 1,219+ educational titles
**Categories**: 26 subject areas

© 2025 Project Himalaya - Educational Access Initiative
"""
    
    with open(dist_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create a quick setup guide
    setup_guide = """# 🚀 SETUP GUIDE - Read This First!

## Super Quick Start (30 seconds):

1. Extract this folder to your Desktop
2. Double-click "AndyLibrary.exe"
3. When browser opens, click "Continue as Guest"
4. Start browsing 1,219+ books!

## That's it! The library will automatically:
✅ Find an available port (8000, 8001, 8002, etc.)
✅ Start the web server
✅ Open your browser
✅ Load the library interface

## First Time Users:
- The program is 100% safe and offline
- No installation required
- No internet connection needed
- All data stays on your computer

## Having fun? 
Share this library with other students who need educational resources!

---
Project Himalaya: Getting education into hands that need it most
"""
    
    with open(dist_dir / "SETUP_GUIDE.txt", 'w', encoding='utf-8') as f:
        f.write(setup_guide)
    
    print("✅ Windows-specific files created:")
    print(f"   📂 {dist_dir / 'Start_AndyLibrary.bat'}")
    print(f"   📄 {dist_dir / 'README.txt'}")  
    print(f"   📋 {dist_dir / 'SETUP_GUIDE.txt'}")
    
    print("\n🎉 WINDOWS BUILD COMPLETE!")
    print("=" * 50)
    print(f"📦 Executable: {exe_path}")
    print(f"📁 Full package: {dist_dir}")
    print(f"💾 Total size: {size_mb:.1f} MB")
    print("\n💡 Ready to test on Windows!")
    print("🚀 Just run AndyLibrary.exe on any Windows machine")
    
    return True

if __name__ == "__main__":
    success = create_windows_exe()
    if not success:
        sys.exit(1)
    print("\n✅ Ready for your grandson! 🎓")