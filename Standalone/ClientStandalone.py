#!/usr/bin/env python3
# File: ClientStandalone.py
# Path: /home/herb/Desktop/AndyLibrary/Standalone/ClientStandalone.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 02:30PM

"""
Client Standalone - Connects to desktop AndyLibrary server
Downloads database and sets up user environment from desktop server
"""

import os
import sys
import json
import socket
import sqlite3
import shutil
import requests
import threading
import webbrowser
import tempfile
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

class ClientStandalone:
    """Client that connects to desktop AndyLibrary server"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.app_dir = self.script_dir.parent
        self.data_dir = self.script_dir / "Data"
        self.database_path = self.data_dir / "MyLibrary.db"
        self.port = 8001  # Different port than desktop server
        self.app = None
        self.desktop_server_url = None
        
        # Create data directory
        self.data_dir.mkdir(exist_ok=True)
        
        # Check if running as PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            self.webpages_dir = Path(sys._MEIPASS) / "WebPages"
        else:
            self.webpages_dir = self.app_dir / "WebPages"
    
    def find_desktop_server(self):
        """Find the desktop AndyLibrary server"""
        # Possible desktop server locations
        possible_hosts = [
            "127.0.0.1",    # Same machine
            "localhost",    # Same machine
            "192.168.1.100", # Common local IP - replace with your desktop IP
            "192.168.0.100"  # Common local IP - replace with your desktop IP
        ]
        
        # Possible ports from config
        possible_ports = [8080, 8081, 8082, 3000, 8000, 8010, 8090, 5000, 9000]
        
        print("🔍 Searching for desktop AndyLibrary server...")
        
        for host in possible_hosts:
            for port in possible_ports:
                try:
                    url = f"http://{host}:{port}"
                    print(f"🔍 Trying {url}...")
                    
                    # Quick connection test
                    response = requests.get(f"{url}/api/health", timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        if "AndyLibrary" in str(data) or "library" in str(data).lower():
                            print(f"✅ Found desktop server at {url}")
                            self.desktop_server_url = url
                            return True
                            
                except requests.exceptions.RequestException:
                    continue
                except Exception as e:
                    print(f"⚠️ Error testing {host}:{port} - {e}")
                    continue
        
        print("❌ Desktop server not found!")
        print("\n🔧 SOLUTION:")
        print("1. On your desktop, run: python StartAndyGoogle.py")
        print("2. Make sure desktop server starts successfully")
        print("3. Note the port number (usually 8080 or 8000)")
        print("4. Update the IP address in this client if needed")
        
        return False
    
    def download_database_from_desktop(self):
        """Download database from desktop server"""
        if not self.desktop_server_url:
            return False
            
        try:
            print(f"📥 Downloading database from {self.desktop_server_url}...")
            
            # Try database download endpoint
            db_url = f"{self.desktop_server_url}/api/database/download"
            response = requests.get(db_url, timeout=30)
            
            if response.status_code == 200:
                # Save database
                with open(self.database_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify database
                if self.verify_downloaded_database():
                    print("✅ Database downloaded and verified successfully")
                    return True
                else:
                    print("❌ Downloaded database failed verification")
                    return False
            else:
                print(f"❌ Database download failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Database download error: {e}")
            return False
    
    def verify_downloaded_database(self):
        """Verify the downloaded database is valid"""
        try:
            if not self.database_path.exists():
                return False
                
            # Check file size
            if self.database_path.stat().st_size < 100000:  # Less than 100KB
                print(f"⚠️ Database too small: {self.database_path.stat().st_size} bytes")
                return False
            
            # Check SQLite integrity
            conn = sqlite3.connect(str(self.database_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                print(f"✅ Database verified: {count} books")
                return True
            else:
                print("⚠️ Database has no books")
                return False
                
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
    
    def setup_user_environment(self):
        """Setup user environment from desktop database"""
        print("🔄 Setting up user environment...")
        
        # First, find and connect to desktop server
        if not self.find_desktop_server():
            print("❌ Cannot setup user environment without desktop server")
            return False
        
        # Download database from desktop
        if not self.download_database_from_desktop():
            print("❌ Failed to download database from desktop")
            return False
        
        print("✅ User environment setup complete")
        return True
    
    def create_fastapi_app(self):
        """Create FastAPI application"""
        app = FastAPI(title="AndyLibrary Client", version="1.0.0")
        
        # Mount static files
        if self.webpages_dir.exists():
            app.mount("/static", StaticFiles(directory=str(self.webpages_dir)), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            """Serve the main library interface"""
            desktop_html = self.webpages_dir / "desktop-library.html"
            
            if desktop_html.exists():
                with open(desktop_html, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = content.replace(
                        "Anderson's Library - Professional Edition",
                        "AndyLibrary - Remote Client"
                    )
                    return content
            else:
                return "<h1>AndyLibrary Remote Client</h1><p>Connected to desktop server</p>"
        
        @app.get("/api/categories")
        async def get_categories():
            """Get book categories"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category")
                categories = [row[0] for row in cursor.fetchall()]
                conn.close()
                return {"categories": categories}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/books/search")
        async def search_books(query: str = "", category: str = "", limit: int = 50):
            """Search books"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                
                sql = "SELECT id, title, author, category, file_size, thumbnail FROM books WHERE 1=1"
                params = []
                
                if query:
                    sql += " AND (title LIKE ? OR author LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])
                
                if category:
                    sql += " AND category = ?"
                    params.append(category)
                
                sql += " ORDER BY title LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                books = []
                for row in cursor.fetchall():
                    books.append({
                        "id": row[0],
                        "title": row[1],
                        "author": row[2] or "Unknown",
                        "category": row[3],
                        "file_size": row[4],
                        "has_thumbnail": row[5] is not None
                    })
                
                conn.close()
                return {"books": books, "count": len(books)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/status")
        async def get_status():
            """Get connection status"""
            return {
                "status": "connected" if self.desktop_server_url else "disconnected",
                "desktop_server": self.desktop_server_url,
                "database_available": self.database_path.exists(),
                "database_books": self.get_book_count()
            }
        
        return app
    
    def get_book_count(self):
        """Get number of books in database"""
        try:
            if not self.database_path.exists():
                return 0
            conn = sqlite3.connect(str(self.database_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def find_available_port(self, start_port=8001):
        """Find an available port"""
        for port in range(start_port, start_port + 50):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise Exception("No available ports found")
    
    def start_client(self):
        """Start the client application"""
        try:
            print("🔥 ANDYLIBRARY REMOTE CLIENT 🔥")
            print("=" * 50)
            print("📡 Connecting to desktop server...")
            
            # Setup user environment (connect to desktop and download DB)
            if not self.setup_user_environment():
                print("\n❌ Failed to setup user environment")
                print("\n💡 Make sure:")
                print("1. Desktop AndyLibrary server is running")
                print("2. Run 'python StartAndyGoogle.py' on your desktop")
                print("3. Check firewall settings")
                input("\nPress Enter to exit...")
                return
            
            # Start client server
            self.port = self.find_available_port()
            self.app = self.create_fastapi_app()
            
            print(f"\n🚀 Starting client on port {self.port}")
            print(f"🌐 Access: http://127.0.0.1:{self.port}")
            print(f"📡 Connected to: {self.desktop_server_url}")
            print(f"📚 Books available: {self.get_book_count()}")
            
            # Open browser
            def open_browser():
                import time
                time.sleep(3)
                webbrowser.open(f"http://127.0.0.1:{self.port}")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            # Start server
            uvicorn.run(
                self.app,
                host="127.0.0.1",
                port=self.port,
                log_level="warning",
                access_log=False
            )
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        except Exception as e:
            print(f"❌ Client error: {e}")

def main():
    """Main entry point"""
    client = ClientStandalone()
    client.start_client()

if __name__ == "__main__":
    main()