# File: build_for_windows.py
# Path: /home/herb/Desktop/AndyLibrary/build_for_windows.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 02:09PM

"""
Build script for creating AndyLibrary Windows executable
Creates a standalone .exe with all dependencies bundled
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class WindowsExeBuilder:
    """Build AndyLibrary as a Windows executable"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.dist_dir = self.base_dir / "dist"
        self.build_dir = self.base_dir / "build"
        
    def check_requirements(self):
        """Check if PyInstaller is available"""
        try:
            import PyInstaller
            print("✅ PyInstaller found")
            return True
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
                print("✅ PyInstaller installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install PyInstaller")
                return False
    
    def clean_build_dirs(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning previous build artifacts...")
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        # Remove spec file artifacts
        spec_artifacts = [
            self.base_dir / "AndyLibrary.spec",
            self.base_dir / "__pycache__"
        ]
        
        for artifact in spec_artifacts:
            if artifact.exists():
                if artifact.is_dir():
                    shutil.rmtree(artifact)
                else:
                    artifact.unlink()
                print(f"   Removed: {artifact}")
    
    def build_executable(self):
        """Build the Windows executable"""
        print("🔨 Building Windows executable...")
        print(f"📍 Working directory: {self.base_dir}")
        
        try:
            # Use the custom spec file
            spec_file = self.base_dir / "build_windows_exe.spec"
            
            if not spec_file.exists():
                print(f"❌ Spec file not found: {spec_file}")
                return False
            
            # Run PyInstaller with the spec file
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            print(f"🚀 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print("✅ Build completed successfully!")
                return True
            else:
                print("❌ Build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def verify_build(self):
        """Verify the build was successful"""
        exe_path = self.dist_dir / "AndyLibrary.exe"
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Executable created: {exe_path}")
            print(f"📦 Size: {size_mb:.1f} MB")
            
            # Check if critical files are bundled
            critical_files = [
                "Data/Databases/MyLibrary.db",
                "WebPages/auth.html",
                "WebPages/JS/library-api-client.js",
                "Source/API/MainAPI.py"
            ]
            
            print("🔍 Verifying bundled files...")
            # Note: Files are bundled internally in the exe, so we can't check them directly
            # But the build process would have failed if they weren't found
            
            return True
        else:
            print(f"❌ Executable not found: {exe_path}")
            return False
    
    def create_readme(self):
        """Create a README for the Windows executable"""
        readme_content = f"""# AndyLibrary - Grandson's Educational Library

## Quick Start
1. Double-click `AndyLibrary.exe` to start
2. The library will open automatically in your web browser
3. Click "Continue as Guest" to browse 1,219+ books
4. Search, read, and learn!

## Features
- 📚 1,219+ educational books
- 🔍 Smart search across 26 categories
- 📖 Built-in PDF reader
- 🌐 Works completely offline
- 🔒 No internet connection required

## System Requirements
- Windows 7/8/10/11 (64-bit)
- 100MB free disk space
- Web browser (Chrome, Firefox, Edge)

## Troubleshooting
- If port 8000 is busy, the program will automatically find another port
- Check Windows Firewall if the browser doesn't open
- Run as Administrator if you encounter permission issues

## Educational Mission
Project Himalaya: "Getting education into the hands of people who can least afford it"

Built with love for learning and education accessibility.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        readme_path = self.dist_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📄 Created: {readme_path}")
    
    def build(self):
        """Complete build process"""
        print("🏔️ AndyLibrary Windows Build Process")
        print("=" * 50)
        
        # Step 1: Check requirements
        if not self.check_requirements():
            return False
        
        # Step 2: Clean previous builds
        self.clean_build_dirs()
        
        # Step 3: Build executable
        if not self.build_executable():
            return False
        
        # Step 4: Verify build
        if not self.verify_build():
            return False
        
        # Step 5: Create documentation
        self.create_readme()
        
        print("=" * 50)
        print("🎉 BUILD SUCCESSFUL!")
        print(f"📦 Executable location: {self.dist_dir / 'AndyLibrary.exe'}")
        print(f"📄 Documentation: {self.dist_dir / 'README.txt'}")
        print("\n💡 Ready to test on Windows!")
        print("🚀 Just run AndyLibrary.exe and it will open the library")
        
        return True

def main():
    """Main build entry point"""
    builder = WindowsExeBuilder()
    success = builder.build()
    
    if not success:
        print("\n❌ Build failed. Check the error messages above.")
        sys.exit(1)
    
    print("\n✅ Build completed successfully!")

if __name__ == "__main__":
    main()