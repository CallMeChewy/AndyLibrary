# File: AndyLibraryStandalone.py
# Path: /home/herb/Desktop/AndyLibrary/AndyLibraryStandalone.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 02:09PM

"""
AndyLibrary Standalone Windows .exe Launcher
Grandson's Educational Library - Self-contained executable
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "Source"))

try:
    from Core.DriveManager import DriveManager
    from Core.DatabaseManager import DatabaseManager
except ImportError as e:
    print(f"Warning: Could not import database managers: {e}")
    DriveManager = None
    DatabaseManager = None
import json
import socket
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
    SCRIPT_DIR = Path(sys.executable).parent
    # Set working directory to the bundled resources
    os.chdir(BASE_DIR)
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    SCRIPT_DIR = BASE_DIR
    os.chdir(SCRIPT_DIR)

# Ensure required paths exist
sys.path.insert(0, str(BASE_DIR))

class AndyLibraryStandalone:
    """Standalone launcher for AndyLibrary Windows executable"""
    
    def __init__(self):
        self.script_dir = BASE_DIR  # Use BASE_DIR for bundled resources
        self.base_dir = BASE_DIR
        self.port = None
        self.server_process = None
        
    def find_available_port(self, start_port=8000, max_attempts=20):
        """Find an available port - MANDATORY per CLAUDE.md requirements"""
        print(f"🔍 Searching for available port starting from {start_port}...")
        
        for port in range(start_port, start_port + max_attempts):
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_socket.bind(('127.0.0.1', port))
                test_socket.close()
                
                if port != start_port:
                    print(f"✅ Found available port: {port} (port {start_port} was busy)")
                
                return port
                
            except OSError:
                if port == 8000:
                    print(f"⚠️ Port 8000 busy (common: HP printer service)")
                elif port == 8080:
                    print(f"⚠️ Port 8080 busy (common: Tomcat, other web servers)")
                continue
        
        raise RuntimeError("No available ports found in range")
    
    def start_server(self):
        """Start the FastAPI server with automatic port discovery"""
        try:
            # Find available port
            self.port = self.find_available_port(8000)
            
            print("🚀 Starting AndyLibrary for your Grandson...")
            print("=" * 60)
            print(f"📍 Working directory: {self.script_dir}")
            print(f"🌐 Library URL: http://127.0.0.1:{self.port}")
            print(f"📚 Direct Library: http://127.0.0.1:{self.port}/library")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # Set environment for local mode
            os.environ['ANDYGOOGLE_MODE'] = 'local'
            
            # Import and start FastAPI server
            from Source.API.MainAPI import app
            import uvicorn
            
            # Start server in a separate thread
            def run_server():
                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=self.port,
                    log_level="error",  # Reduce log noise for end users
                    access_log=False
                )
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait for server to start
            time.sleep(2)
            
            # Open web browser to library
            library_url = f"http://127.0.0.1:{self.port}/library"
            print(f"🌐 Opening browser to: {library_url}")
            webbrowser.open(library_url)
            
            print("\n✅ AndyLibrary is ready!")
            print("📖 Browse 1,219 books across 26 categories")
            print("🔍 Search, read, and learn!")
            print("\n💡 Close this window to stop the library")
            print("=" * 60)
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 AndyLibrary stopped. Happy learning!")
                
        except Exception as e:
            print(f"❌ Error starting AndyLibrary: {e}")
            print("\n🛠️ Troubleshooting tips:")
            print("1. Make sure no other programs are using ports 8000-8020")
            print("2. Try running as administrator")
            print("3. Check Windows Firewall settings")
            print("\nClosing in 10 seconds...")
            time.sleep(10)
            sys.exit(1)


def InitializeWindowsDatabase():
    """Initialize database for Windows standalone executable"""
    print("🔄 Initializing Windows database...")
    
    try:
        # Check if we have database managers available
        if DriveManager is None:
            print("⚠️ DriveManager not available - using local database if present")
            return CheckLocalDatabase()
        
        # Initialize DriveManager
        config_path = Path(__file__).parent / "Config" / "andygoogle_config.json"
        drive_manager = DriveManager(str(config_path))
        
        # Initialize database (will download from Google Drive if needed)
        if drive_manager.InitializeDatabase():
            print("✅ Database initialized successfully")
            return True
        else:
            print("⚠️ Google Drive sync failed - checking for local database")
            return CheckLocalDatabase()
            
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        return CheckLocalDatabase()

def CheckLocalDatabase():
    """Check if local database exists and is valid"""
    db_paths = [
        Path(__file__).parent / "Data" / "Databases" / "MyLibrary.db",
        Path(__file__).parent / "Data" / "Local" / "cached_library.db"
    ]
    
    for db_path in db_paths:
        if db_path.exists() and db_path.stat().st_size > 100000:  # At least 100KB
            print(f"✅ Using local database: {db_path}")
            return True
    
    print("❌ No valid database found - application may not function properly")
    return False

def main():
    """Main entry point for standalone executable"""
    print("🏔️ AndyLibrary - Project Himalaya")
    print("Educational Library for Everyone")
    print("Getting education into the hands of people who can least afford it")
    print("=" * 60)
    
    try:
        launcher = AndyLibraryStandalone()
        launcher.start_server()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        print("Closing in 10 seconds...")
        time.sleep(10)
        sys.exit(1)

if __name__ == "__main__":
    main()