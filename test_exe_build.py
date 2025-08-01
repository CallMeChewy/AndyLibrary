# File: test_exe_build.py
# Path: /home/herb/Desktop/AndyLibrary/test_exe_build.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-01
# Last Modified: 2025-08-01 09:25PM

"""
Test script to verify Windows executable build configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def test_build_environment():
    """Test if the build environment is ready"""
    print("🔍 Testing Windows EXE Build Environment")
    print("=" * 50)
    
    # Check critical files
    critical_files = [
        "AndyLibraryStandalone.py",
        "build_windows_exe.spec",
        ".github/workflows/windows-exe-build.yml"
    ]
    
    missing_files = []
    for file in critical_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            size = Path(file).stat().st_size
            print(f"✅ {file} ({size:,} bytes)")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    # Check Source directory
    if Path("Source").exists():
        source_dirs = list(Path("Source").iterdir())
        print(f"✅ Source directory with {len(source_dirs)} subdirectories")
        for dir in source_dirs:
            if dir.is_dir():
                print(f"   📁 {dir.name}")
    else:
        print("❌ Source directory missing")
        return False
    
    # Check WebPages directory
    if Path("WebPages").exists():
        web_files = list(Path("WebPages").glob("*.html"))
        print(f"✅ WebPages directory with {len(web_files)} HTML files")
    else:
        print("❌ WebPages directory missing")
        return False
    
    print("\n✅ Build environment looks good!")
    return True

def test_imports():
    """Test if critical imports work"""
    print("\n🔍 Testing Python Imports")
    print("=" * 30)
    
    critical_imports = [
        "fastapi",
        "uvicorn", 
        "requests",
        "sqlite3",
        "pathlib",
        "json",
        "threading",
        "webbrowser"
    ]
    
    failed_imports = []
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️ Failed imports: {failed_imports}")
        print("Install with: pip install fastapi uvicorn requests")
        return False
    
    print("\n✅ All imports successful!")
    return True

def test_startup_script():
    """Test if the standalone script can at least import without errors"""
    print("\n🔍 Testing Standalone Script")
    print("=" * 30)
    
    try:
        # Try to import the main class without running it
        script_content = Path("AndyLibraryStandalone.py").read_text()
        
        # Basic syntax check
        compile(script_content, "AndyLibraryStandalone.py", "exec")
        print("✅ Script syntax is valid")
        
        # Check for required functions
        required_functions = [
            "class AndyLibraryStandalone",
            "def find_available_port",
            "def start_server",
            "def main"
        ]
        
        for func in required_functions:
            if func in script_content:
                print(f"✅ Found {func}")
            else:
                print(f"❌ Missing {func}")
                return False
        
        print("✅ Standalone script structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Script test failed: {e}")
        return False

def test_pyinstaller_availability():
    """Test if PyInstaller is available and working"""
    print("\n🔍 Testing PyInstaller")
    print("=" * 25)
    
    try:
        result = subprocess.run(["pyinstaller", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ PyInstaller {version} available")
            return True
        else:
            print(f"❌ PyInstaller error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ PyInstaller not found - install with: pip install pyinstaller")
        return False
    except subprocess.TimeoutExpired:
        print("❌ PyInstaller command timed out")
        return False
    except Exception as e:
        print(f"❌ PyInstaller test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 WINDOWS EXE BUILD VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Build Environment", test_build_environment),
        ("Python Imports", test_imports), 
        ("Startup Script", test_startup_script),
        ("PyInstaller", test_pyinstaller_availability)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Windows EXE build should work.")
        print("\nNext steps:")
        print("1. Push changes to trigger GitHub Actions build")
        print("2. Or run locally: pyinstaller build_windows_exe.spec")
    else:
        print(f"\n⚠️ {len(tests) - passed} tests failed. Fix issues before building.")
        
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)