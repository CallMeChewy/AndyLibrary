#!/usr/bin/env python3
# Test build script to verify packaging will work

import os
import sys
import subprocess
from pathlib import Path

def test_packaging_readiness():
    """Test if we can package the standalone version"""
    
    print("🧪 TESTING PACKAGING READINESS")
    print("=" * 50)
    
    # Test imports
    print("\n[1/4] Testing critical imports...")
    try:
        import fastapi
        import uvicorn
        import sqlite3
        import webbrowser
        import threading
        print("✅ All critical imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test database access
    print("\n[2/4] Testing database access...")
    db_path = Path("Data/MyLibrary.db")
    if db_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ Database accessible with {count} books")
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    else:
        print("⚠️ Database not found, but that's expected for clean build")
    
    # Test WebPages directory
    print("\n[3/4] Testing WebPages access...")
    webpages_dir = Path("../WebPages")
    if webpages_dir.exists():
        required_files = ["desktop-library.html", "CSS", "JS"]
        missing = []
        for file in required_files:
            if not (webpages_dir / file).exists():
                missing.append(file)
        
        if missing:
            print(f"⚠️ Missing WebPages files: {missing}")
        else:
            print("✅ WebPages directory structure looks good")
    else:
        print("❌ WebPages directory not found")
        return False
    
    # Test PyInstaller availability
    print("\n[4/4] Testing PyInstaller availability...")
    try:
        result = subprocess.run([sys.executable, "-c", "import PyInstaller"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyInstaller available")
        else:
            print("❌ PyInstaller not available - install with: pip install pyinstaller")
            return False
    except Exception as e:
        print(f"❌ PyInstaller test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 PACKAGING READINESS: READY")
    print("✅ All tests passed - ready for PyInstaller build")
    return True

if __name__ == "__main__":
    success = test_packaging_readiness()
    if not success:
        print("\n❌ Some tests failed. Please fix issues before packaging.")
        sys.exit(1)
    else:
        print("\n🚀 Ready to build with PyInstaller!")
        print("Run: ./build.sh (Linux/Mac) or build.bat (Windows)")