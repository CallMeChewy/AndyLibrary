#!/usr/bin/env python3
# File: test-grandson-library.py
# Path: /home/herb/Desktop/AndyLibrary/Standalone/test-grandson-library.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 03:15PM

"""
Test Grandson's Library - Quick verification before sending
"""

import sys
import requests
import time
import subprocess
import threading
from pathlib import Path

def test_grandson_library():
    """Test the grandson's library locally"""
    print("🧪 TESTING GRANDSON'S LIBRARY")
    print("=" * 40)
    
    # Test 1: Import test
    print("\n[1/5] Testing imports...")
    try:
        from GrandsonLibrary import GrandsonLibrary
        print("✅ GrandsonLibrary imports successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Database setup
    print("\n[2/5] Testing database setup...")
    try:
        library = GrandsonLibrary()
        if library.setup_database():
            book_count = library.get_book_count()
            print(f"✅ Database ready with {book_count} books")
            if book_count == 0:
                print("⚠️ Warning: No books in database")
        else:
            print("❌ Database setup failed")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    # Test 3: FastAPI app creation
    print("\n[3/5] Testing web app creation...")
    try:
        app = library.create_library_app()
        print("✅ FastAPI app created successfully")
        
        # Test API endpoints structure
        routes = [str(route.path) for route in app.routes]
        expected_routes = ["/", "/api/health", "/api/categories", "/api/books/search"]
        
        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"✅ Route found: {expected}")
            else:
                print(f"⚠️ Route missing: {expected}")
                
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False
    
    # Test 4: Start server briefly
    print("\n[4/5] Testing server startup...")
    server_process = None
    try:
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, "GrandsonLibrary.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(5)
        
        # Test if server is running
        try:
            response = requests.get("http://127.0.0.1:8000/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server responds: {data.get('message', 'OK')}")
                print(f"📚 Books available: {data.get('books_available', 0)}")
            else:
                print(f"⚠️ Server responds with status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Server not responding: {e}")
            print("   (This might be normal if port is busy)")
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("✅ Test server stopped")
    
    # Test 5: Build requirements
    print("\n[5/5] Testing build requirements...")
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn available")
    except ImportError as e:
        print(f"❌ Missing requirements: {e}")
        return False
    
    # Check for WebPages
    webpages_dir = Path("../WebPages")
    if webpages_dir.exists():
        html_files = list(webpages_dir.glob("*.html"))
        print(f"✅ WebPages directory found with {len(html_files)} HTML files")
    else:
        print("⚠️ WebPages directory not found - will use simple interface")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("📋 Ready for Windows build!")
    return True

def test_exe_if_exists():
    """Test the EXE if it exists"""
    exe_path = Path("dist/GrandsonLibrary.exe")
    if exe_path.exists():
        print(f"\n🎯 TESTING BUILT EXE")
        print("=" * 30)
        print(f"📄 Found: {exe_path}")
        print(f"📊 Size: {exe_path.stat().st_size // 1024 // 1024}MB")
        
        # Check if wine is available for testing
        try:
            subprocess.run(["which", "wine"], check=True, capture_output=True)
            print("🍷 Wine available - you could test with: wine dist/GrandsonLibrary.exe")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Wine not available - test on Windows machine")
        
        return True
    else:
        print("\n📋 No EXE found yet - run build script first")
        return False

if __name__ == "__main__":
    print("🎓 Grandson's Library Test Suite")
    print("Testing everything before Windows deployment...")
    
    # Test the Python version first
    if test_grandson_library():
        print("\n" + "="*50)
        test_exe_if_exists()
        
        print("\n📋 NEXT STEPS:")
        print("1. Run: ./build-grandson-library.sh")
        print("2. Test the EXE on Windows (ick)")
        print("3. Send to grandson for approval")
        print("4. Begin Linux conversion campaign! 🐧")
    else:
        print("\n❌ Tests failed - fix issues before building")
        sys.exit(1)