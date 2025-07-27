#!/usr/bin/env python3
# File: StandaloneAndyLibrary.py
# Path: /home/herb/Desktop/AndyLibrary/Standalone/StandaloneAndyLibrary.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 10:15AM

"""
Standalone AndyLibrary - Simplified version without registration/authentication
Direct database setup and library access for testing and preview
"""

import os
import sys
import json
import socket
import sqlite3
import shutil
import urllib.request
import threading
import webbrowser
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

# Google Drive integration
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

class StandaloneAndyLibrary:
    """Simplified standalone library system"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.app_dir = self.script_dir.parent
        self.data_dir = self.script_dir / "Data"
        self.database_path = self.data_dir / "MyLibrary.db"
        self.port = 8000
        self.app = None
        self.server_thread = None
        
        # Create data directory
        self.data_dir.mkdir(exist_ok=True)
        
    def find_available_port(self, start_port=8000):
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise Exception("No available ports found")
    
    def check_database(self):
        """Check if database exists and is valid"""
        if not self.database_path.exists():
            return False, "Database not found"
        
        try:
            conn = sqlite3.connect(str(self.database_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            conn.close()
            return True, f"Database ready with {count} books"
        except Exception as e:
            return False, f"Database error: {e}"
    
    def download_database(self):
        """Download database from main installation"""
        # Try multiple possible locations for the source database
        possible_paths = [
            self.app_dir / "Data" / "Databases" / "MyLibrary.db",
            Path("/home/herb/Desktop/AndyLibrary/Data/Databases/MyLibrary.db"),
            self.script_dir.parent / "Data" / "Databases" / "MyLibrary.db",
            Path("../Data/Databases/MyLibrary.db").resolve(),
            # Check if database is bundled with executable
            self.script_dir / "MyLibrary.db",
            Path("MyLibrary.db").resolve()
        ]
        
        for source_db in possible_paths:
            if source_db.exists():
                print(f"📥 Copying database from {source_db}...")
                shutil.copy2(source_db, self.database_path)
                return True
                
        # Try Google Drive download if available
        if GOOGLE_DRIVE_AVAILABLE:
            print("🌐 Attempting Google Drive download...")
            if self.download_from_google_drive():
                return True
                
        # Create minimal database if none found
        print("⚠️ No source database found, creating minimal test database...")
        try:
            conn = sqlite3.connect(str(self.database_path))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    category TEXT,
                    file_size INTEGER,
                    thumbnail BLOB
                )
            """)
            cursor.execute("""
                INSERT INTO books (id, title, author, category, file_size) 
                VALUES (1, 'Test Book - Database Not Found', 'AndyLibrary System', 'System', 1024)
            """)
            conn.commit()
            conn.close()
            print("✅ Created minimal test database")
            return True
        except Exception as e:
            print(f"❌ Failed to create test database: {e}")
            return False

    def download_from_google_drive(self):
        """Download database from Google Drive"""
        try:
            print("🔍 Searching for MyLibrary.db on Google Drive...")
            
            # Try using a known public Google Drive link for MyLibrary.db
            # This would need to be updated with the actual public share link
            public_urls = [
                "https://drive.google.com/uc?id=1g6zCz1ZKK7K1V2Y5r8c9a8h5l2P1S3M4&export=download",
                "https://drive.google.com/uc?id=REPLACE_WITH_ACTUAL_FILE_ID&export=download"
            ]
            
            for url in public_urls:
                try:
                    print(f"📥 Attempting download from: {url[:50]}...")
                    urllib.request.urlretrieve(url, self.database_path)
                    
                    # Verify the downloaded file
                    if self.database_path.exists() and self.database_path.stat().st_size > 100000:  # At least 100KB
                        print("✅ Database downloaded successfully from Google Drive")
                        return True
                    else:
                        print(f"⚠️ Downloaded file too small ({self.database_path.stat().st_size} bytes)")
                        self.database_path.unlink(missing_ok=True)
                        
                except Exception as download_error:
                    print(f"⚠️ Download attempt failed: {download_error}")
                    continue
                    
            print("❌ All Google Drive download attempts failed")
            return False
                
        except Exception as e:
            print(f"❌ Google Drive download error: {e}")
            return False
    
    def setup_database(self):
        """Setup database for standalone use"""
        valid, message = self.check_database()
        if valid:
            print(f"✅ {message}")
            return True
        
        print(f"⚠️ {message}")
        print("🔄 Setting up database...")
        
        if self.download_database():
            valid, message = self.check_database()
            if valid:
                print(f"✅ {message}")
                return True
        
        print("❌ Failed to setup database")
        return False
    
    def create_fastapi_app(self):
        """Create FastAPI application"""
        app = FastAPI(title="Standalone AndyLibrary", version="1.0.0")
        
        # Mount static files
        webpages_dir = self.app_dir / "WebPages"
        if webpages_dir.exists():
            app.mount("/static", StaticFiles(directory=str(webpages_dir)), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            """Serve the main library interface"""
            desktop_html = webpages_dir / "desktop-library.html"
            if desktop_html.exists():
                with open(desktop_html, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Modify title for standalone version
                    content = content.replace(
                        "Anderson's Library - Professional Edition",
                        "AndyLibrary - Standalone Preview"
                    )
                    return content
            return "<h1>Library interface not found</h1>"
        
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
        
        @app.get("/api/thumbnails/{book_id}")
        async def get_thumbnail(book_id: int):
            """Get book thumbnail"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT thumbnail FROM books WHERE id = ?", (book_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    return Response(content=result[0], media_type="image/jpeg")
                else:
                    raise HTTPException(status_code=404, detail="Thumbnail not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/database/info")
        async def database_info():
            """Get database information"""
            try:
                if not self.database_path.exists():
                    return {"available": False, "message": "Database not found"}
                
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM books")
                book_count = cursor.fetchone()[0]
                conn.close()
                
                file_size = self.database_path.stat().st_size / (1024 * 1024)  # MB
                
                return {
                    "available": True,
                    "total_books": book_count,
                    "file_size_mb": f"{file_size:.1f}",
                    "source": "Local Standalone"
                }
            except Exception as e:
                return {"available": False, "message": str(e)}
        
        @app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "version": "standalone"}
        
        @app.post("/api/shutdown")
        async def shutdown():
            """Shutdown endpoint"""
            def stop_server():
                import time
                time.sleep(1)
                os._exit(0)
            
            threading.Thread(target=stop_server, daemon=True).start()
            return {"message": "Shutting down..."}
        
        return app
    
    def start_server(self):
        """Start the FastAPI server"""
        try:
            self.port = self.find_available_port()
            self.app = self.create_fastapi_app()
            
            print(f"🚀 Starting Standalone AndyLibrary on port {self.port}")
            print(f"📚 Database: {self.database_path}")
            print(f"🌐 Access: http://127.0.0.1:{self.port}")
            print(f"📖 Opening browser in 3 seconds...")
            
            # Open browser after brief delay
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
            print(f"❌ Server error: {e}")

def main():
    """Main entry point"""
    print("🔥 STANDALONE ANDYLIBRARY - PREVIEW VERSION 🔥")
    print("=" * 60)
    print("📚 Simplified library access without registration")
    print("🎯 Perfect for testing and preview")
    print("=" * 60)
    
    try:
        print("🔄 Step 1: Creating standalone instance...")
        library = StandaloneAndyLibrary()
        print(f"✅ Instance created. Data directory: {library.data_dir}")
        
        print("🔄 Step 2: Setting up database...")
        if not library.setup_database():
            print("\n❌ Database setup failed. Debug info:")
            print(f"   - Database path: {library.database_path}")
            print(f"   - Data directory exists: {library.data_dir.exists()}")
            print(f"   - Google Drive available: {GOOGLE_DRIVE_AVAILABLE}")
            try:
                input("\nPress Enter to exit...")
            except EOFError:
                pass  # Handle non-interactive execution
            return
        
        print("🔄 Step 3: Starting server...")
        library.start_server()
        
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        try:
            input("\nPress Enter to exit...")
        except EOFError:
            pass  # Handle non-interactive execution

if __name__ == "__main__":
    main()