#!/usr/bin/env python3
# File: GrandsonLibrary.py
# Path: /home/herb/Desktop/AndyLibrary/Standalone/GrandsonLibrary.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 03:00PM

"""
Grandson's Educational Library - Standalone Google Drive Access
No registration, no authentication, but connects to Grandpa's Google Drive
Downloads database and accesses books from shared Google Drive folder
"""

import os
import sys
import json
import socket
import sqlite3
import shutil
import threading
import webbrowser
import requests
import urllib.parse
import re
import time
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

class GrandsonLibrary:
    """Library for grandson - accesses Grandpa's Google Drive (no registration)"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.app_dir = self.script_dir.parent
        self.data_dir = self.script_dir / "Data"
        self.database_path = self.data_dir / "MyLibrary.db"
        self.config_path = self.data_dir / "grandpa_config.json"
        self.port = 8080  # Use different port to avoid conflicts
        self.app = None
        
        # Google Drive configuration - HARD CODED FOR GRANDSON
        # Granddaddy's shared Google Drive folder
        self.google_drive_folder_id = "1BpODcF8qf6VYZbxvQw8JbfHQ2n8r4X9m"  # TEMP - will change soon
        self.google_drive_folder_url = "https://drive.google.com/drive/folders/1BpODcF8qf6VYZbxvQw8JbfHQ2n8r4X9m?usp=sharing"
        self.grandpa_name = "Granddaddy"
        
        # Create data directory
        self.data_dir.mkdir(exist_ok=True)
        
        # Check if running as PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # Running as EXE - WebPages should be in the bundle
            self.webpages_dir = Path(sys._MEIPASS) / "WebPages"
        else:
            # Running as script - WebPages relative to parent
            self.webpages_dir = self.app_dir / "WebPages"
        
        # Load existing config if available
        self.load_config()
    
    def load_config(self):
        """Load configuration with Grandpa's Google Drive info"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.google_drive_folder_id = config.get('folder_id')
                    self.google_drive_folder_url = config.get('folder_url')
                    self.grandpa_name = config.get('grandpa_name', 'Grandpa')
                    print(f"✅ Loaded config for {self.grandpa_name}'s library")
                    return True
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
        return False
    
    def save_config(self):
        """Save configuration"""
        try:
            config = {
                'folder_id': self.google_drive_folder_id,
                'folder_url': self.google_drive_folder_url, 
                'grandpa_name': self.grandpa_name,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False
    
    def extract_folder_id_from_url(self, url):
        """Extract Google Drive folder ID from share URL"""
        try:
            patterns = [
                r'/folders/([a-zA-Z0-9_-]+)',
                r'[?&]id=([a-zA-Z0-9_-]+)',
                r'/d/([a-zA-Z0-9_-]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            print(f"❌ URL parsing error: {e}")
            return None
    
    def background_database_update(self):
        """Update database in background without blocking startup"""
        try:
            print("🔄 Checking for database updates...")
            
            # Create temporary database path
            temp_db_path = self.data_dir / "MyLibrary_temp.db"
            
            # Download to temporary location
            if self.download_database_to_path(temp_db_path):
                # Verify the new database
                try:
                    conn = sqlite3.connect(str(temp_db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM books")
                    new_count = cursor.fetchone()[0]
                    conn.close()
                    
                    # Get current database count for comparison
                    current_count = self.get_book_count()
                    
                    if new_count != current_count:
                        print(f"📚 Library update available: {new_count} books (was {current_count})")
                        # Replace current database with updated one
                        if self.database_path.exists():
                            self.database_path.unlink()  # Remove old database
                        temp_db_path.rename(self.database_path)  # Move new database
                        print("✅ Library updated successfully!")
                    else:
                        print("✅ Library is up to date")
                        temp_db_path.unlink()  # Remove temp file
                        
                except Exception as e:
                    print(f"⚠️ Database update verification failed: {e}")
                    if temp_db_path.exists():
                        temp_db_path.unlink()
            else:
                print("⚠️ No updates available from Granddaddy's Google Drive")
                
        except Exception as e:
            print(f"⚠️ Background update error: {e}")
    
    def download_database_to_path(self, target_path):
        """Download database to specific path"""
        if not self.google_drive_folder_id:
            return False
            
        try:
            # Search for MyLibrary.db in the folder
            api_url = "https://www.googleapis.com/drive/v3/files"
            params = {
                'q': f"'{self.google_drive_folder_id}' in parents and name contains '.db'",
                'fields': 'files(id,name,size,mimeType)'
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                files = response.json().get('files', [])
                
                # Look for MyLibrary.db specifically
                db_file = None
                for file in files:
                    if 'MyLibrary.db' in file['name']:
                        db_file = file
                        break
                
                if not db_file and files:
                    db_file = files[0]  # Use first .db file found
                
                if db_file:
                    # Download the database
                    file_id = db_file['id']
                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                    
                    response = requests.get(download_url, timeout=60)
                    
                    if response.status_code == 200:
                        # Save database
                        with open(target_path, 'wb') as f:
                            f.write(response.content)
                        return True
                    else:
                        print(f"❌ Download failed: HTTP {response.status_code}")
                        return False
                else:
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"❌ Database download error: {e}")
            return False

    def download_database_from_drive(self):
        """Download database from Grandpa's Google Drive"""
        print(f"📥 Downloading library from {self.grandpa_name}'s Google Drive...")
        
        if self.download_database_to_path(self.database_path):
            # Verify database
            if self.verify_database():
                print(f"✅ Downloaded {self.grandpa_name}'s library successfully!")
                return True
            else:
                print("❌ Downloaded database failed verification")
                return False
        else:
            print("❌ Failed to download database from Google Drive")
            return False
    
    def verify_database(self):
        """Verify the downloaded database"""
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
                print(f"📚 Database verified: {count} books from {self.grandpa_name}")
                return True
            else:
                print("⚠️ Database has no books")
                return False
                
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
    
    def download_book_from_drive(self, book_title):
        """Download a specific book from Google Drive"""
        if not self.google_drive_folder_id:
            return None
            
        try:
            print(f"📖 Looking for book: {book_title}")
            
            # Search for the book file in the folder
            api_url = "https://www.googleapis.com/drive/v3/files"
            params = {
                'q': f"'{self.google_drive_folder_id}' in parents and name contains '{book_title[:20]}'",
                'fields': 'files(id,name,size,mimeType,webContentLink)'
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                files = response.json().get('files', [])
                
                if files:
                    book_file = files[0]  # Use first match
                    file_id = book_file['id']
                    
                    # Return download URL - let browser handle the download
                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                    return download_url
                else:
                    print(f"📖 Book file not found: {book_title}")
                    return None
            else:
                print(f"❌ Search failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Book search error: {e}")
            return None
    
    def needs_setup(self):
        """Check if Google Drive setup is needed - now with hard-coded links"""
        # Since we have hard-coded folder ID, only check if database exists
        return not self.database_path.exists()
    
    def setup_database(self):
        """Setup database for grandson's use with auto-download"""
        print("🔄 Setting up library database...")
        
        # Check if we should download fresh database from Google Drive
        should_download = False
        
        if not self.database_path.exists():
            print("📥 No local database found - downloading from Granddaddy's Google Drive...")
            should_download = True
        else:
            # Check database age - download if older than 1 day
            db_age_hours = (time.time() - self.database_path.stat().st_mtime) / 3600
            if db_age_hours > 24:
                print(f"📅 Database is {db_age_hours:.1f} hours old - checking for updates...")
                should_download = True
        
        # Download fresh database if needed
        if should_download and self.google_drive_folder_id:
            # For first-time setup, download synchronously
            if not self.database_path.exists():
                print("🌐 Downloading latest library from Granddaddy...")
                if self.download_database_from_drive():
                    print("✅ Latest library downloaded successfully!")
                else:
                    print("⚠️ Download failed - will use fallback database")
            else:
                # For updates, download in background to minimize startup time
                print("🔄 Checking for library updates in background...")
                threading.Thread(target=self.background_database_update, daemon=True).start()
        
        # Verify database exists and works
        if self.database_path.exists():
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM books")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"✅ Database ready with {count} books")
                return True
            except Exception as e:
                print(f"⚠️ Database issue: {e}")
        
        # Try to find database from various sources
        possible_sources = []
        
        # Check if running as PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # Running as EXE - check bundled database
            bundled_db = Path(sys._MEIPASS) / "Data" / "Databases" / "MyLibrary.db"
            possible_sources.append(bundled_db)
            print(f"🔍 Checking bundled database: {bundled_db}")
        
        # Add other possible locations
        possible_sources.extend([
            self.app_dir / "Data" / "Databases" / "MyLibrary.db",
            Path("/home/herb/Desktop/AndyLibrary/Data/Databases/MyLibrary.db"),
            self.script_dir / "MyLibrary.db",
            Path("MyLibrary.db")
        ])
        
        for source_db in possible_sources:
            if source_db.exists():
                print(f"📥 Copying database from {source_db}...")
                shutil.copy2(source_db, self.database_path)
                
                # Verify it worked
                try:
                    conn = sqlite3.connect(str(self.database_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM books")
                    count = cursor.fetchone()[0]
                    conn.close()
                    print(f"✅ Database setup complete with {count} books")
                    return True
                except Exception as e:
                    print(f"❌ Database verification failed: {e}")
                    continue
        
        # If no database found, create a simple demo
        print("⚠️ No database found, creating demo library...")
        try:
            conn = sqlite3.connect(str(self.database_path))
            cursor = conn.cursor()
            
            # Create books table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    category TEXT,
                    file_size INTEGER,
                    thumbnail BLOB,
                    description TEXT
                )
            """)
            
            # Insert sample books for grandson
            demo_books = [
                (1, "Python Programming for Beginners", "John Doe", "Programming", 2048000, None, "Learn Python programming from scratch"),
                (2, "Introduction to Computer Science", "Jane Smith", "Computer Science", 3072000, None, "Fundamentals of computer science"),
                (3, "Mathematics for High School", "Bob Johnson", "Mathematics", 1536000, None, "Comprehensive math curriculum"),
                (4, "World History", "Alice Brown", "History", 2560000, None, "Explore world history"),
                (5, "Biology Basics", "Dr. Wilson", "Science", 1792000, None, "Introduction to biology"),
                (6, "Chemistry Fundamentals", "Prof. Davis", "Science", 2304000, None, "Basic chemistry concepts"),
                (7, "English Literature", "Mary Johnson", "Literature", 1920000, None, "Classic literature collection"),
                (8, "Physics Made Simple", "Dr. Lee", "Science", 2816000, None, "Physics for beginners"),
                (9, "Art and Design", "Sarah Miller", "Arts", 4096000, None, "Introduction to art and design"),
                (10, "Geography Explorer", "Mike Turner", "Geography", 1280000, None, "Discover world geography")
            ]
            
            cursor.executemany("""
                INSERT INTO books (id, title, author, category, file_size, thumbnail, description) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, demo_books)
            
            conn.commit()
            conn.close()
            print("✅ Demo library created with 10 educational books")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create demo library: {e}")
            return False
    
    def create_library_app(self):
        """Create simple FastAPI library application"""
        app = FastAPI(
            title="Grandson's Educational Library", 
            version="1.0.0",
            description="A simple educational library - no login required!"
        )
        
        # Mount static files (CSS, JS, images)
        if self.webpages_dir.exists():
            app.mount("/static", StaticFiles(directory=str(self.webpages_dir)), name="static")
            print("✅ Web interface files loaded")
        else:
            print(f"⚠️ Web interface not found at: {self.webpages_dir}")
        
        # Add favicon endpoint
        @app.get("/favicon.ico")
        async def favicon():
            """Serve favicon"""
            favicon_path = self.webpages_dir / "favicon.ico"
            if favicon_path.exists():
                return FileResponse(str(favicon_path))
            else:
                raise HTTPException(status_code=404, detail="Favicon not found")
        
        # Add direct asset access for compatibility
        @app.get("/BowersWorld.png")
        async def bowers_world_png():
            """Serve BowersWorld.png for compatibility"""
            asset_path = self.webpages_dir / "assets" / "BowersWorld.png"
            if asset_path.exists():
                return FileResponse(str(asset_path))
            else:
                raise HTTPException(status_code=404, detail="Asset not found")
        
        @app.get("/", response_class=HTMLResponse)
        async def library_home():
            """Serve setup page or library interface"""
            if self.needs_setup():
                return self.create_setup_page()
            else:
                return self.serve_library_interface()
        
        @app.post("/setup")
        async def process_setup(request: Request):
            """Process Google Drive setup"""
            try:
                form = await request.form()
                share_url = form.get('share_url', '').strip()
                grandpa_name = form.get('grandpa_name', 'Grandpa').strip()
                
                if not share_url:
                    return JSONResponse({
                        "success": False,
                        "error": "Please provide Grandpa's Google Drive share link"
                    })
                
                # Extract folder ID
                folder_id = self.extract_folder_id_from_url(share_url)
                if not folder_id:
                    return JSONResponse({
                        "success": False,
                        "error": "Invalid Google Drive link. Please check the link and try again."
                    })
                
                # Save configuration
                self.google_drive_folder_id = folder_id
                self.google_drive_folder_url = share_url
                self.grandpa_name = grandpa_name
                
                # Download database
                if self.download_database_from_drive():
                    self.save_config()
                    book_count = self.get_book_count()
                    return JSONResponse({
                        "success": True,
                        "message": f"Connected to {grandpa_name}'s library!",
                        "books_count": book_count
                    })
                else:
                    return JSONResponse({
                        "success": False,
                        "error": "Failed to download library. Please check the link and try again."
                    })
                    
            except Exception as e:
                return JSONResponse({
                    "success": False,
                    "error": f"Setup failed: {str(e)}"
                })
        
        @app.get("/library", response_class=HTMLResponse)
        async def library_interface():
            """Serve library interface after setup"""
            if self.needs_setup():
                return RedirectResponse("/")
            else:
                return self.serve_library_interface()
        
        @app.get("/api/health")
        async def health_check():
            """Health check - always healthy for grandson!"""
            book_count = self.get_book_count()
            return {
                "status": "healthy",
                "message": "Grandson's library is ready!",
                "books_available": book_count,
                "version": "1.0.0"
            }
        
        @app.get("/api/categories")
        async def get_categories():
            """Get all book categories"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category")
                categories = [row[0] for row in cursor.fetchall()]
                conn.close()
                return categories  # Return array directly for JavaScript .sort() compatibility
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        @app.get("/api/books/search")
        async def search_books(query: str = "", category: str = "", limit: int = 100):
            """Search books - simple and fast"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                
                sql = "SELECT id, title, author, category, file_size, thumbnail, description FROM books WHERE 1=1"
                params = []
                
                if query:
                    sql += " AND (title LIKE ? OR author LIKE ? OR description LIKE ?)"
                    query_param = f"%{query}%"
                    params.extend([query_param, query_param, query_param])
                
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
                        "author": row[2] or "Unknown Author",
                        "category": row[3] or "General",
                        "file_size": row[4] or 0,
                        "has_thumbnail": row[5] is not None,
                        "description": row[6] or "Educational content"
                    })
                
                conn.close()
                return {"books": books, "count": len(books), "total_available": self.get_book_count()}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
        
        @app.get("/api/books/{book_id}")
        async def get_book_details(book_id: int):
            """Get detailed information about a specific book"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, author, category, file_size, thumbnail, description 
                    FROM books WHERE id = ?
                """, (book_id,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return {
                        "id": result[0],
                        "title": result[1],
                        "author": result[2] or "Unknown Author",
                        "category": result[3] or "General",
                        "file_size": result[4] or 0,
                        "has_thumbnail": result[5] is not None,
                        "description": result[6] or "Educational content"
                    }
                else:
                    raise HTTPException(status_code=404, detail="Book not found")
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        @app.get("/api/thumbnails/{book_id}")
        async def get_thumbnail(book_id: int):
            """Get book thumbnail image"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT thumbnail FROM books WHERE id = ?", (book_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    return Response(content=result[0], media_type="image/jpeg")
                else:
                    # Return a simple placeholder
                    raise HTTPException(status_code=404, detail="Thumbnail not available")
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Thumbnail error: {str(e)}")
        
        @app.get("/api/stats")
        async def get_library_stats():
            """Get library statistics"""
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                
                # Count books by category
                cursor.execute("SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY COUNT(*) DESC")
                categories = dict(cursor.fetchall())
                
                # Total books
                cursor.execute("SELECT COUNT(*) FROM books")
                total_books = cursor.fetchone()[0]
                
                # Database size
                db_size_mb = self.database_path.stat().st_size / (1024 * 1024) if self.database_path.exists() else 0
                
                conn.close()
                
                return {
                    "total_books": total_books,
                    "categories": categories,
                    "database_size_mb": round(db_size_mb, 2),
                    "last_updated": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")
        
        @app.get("/api/books/{book_id}/download")
        async def download_book(book_id: int):
            """Get download link for a book from Google Drive"""
            try:
                # Get book title from database
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT title FROM books WHERE id = ?", (book_id,))
                result = cursor.fetchone()
                conn.close()
                
                if not result:
                    raise HTTPException(status_code=404, detail="Book not found")
                
                book_title = result[0]
                
                # Get download URL from Google Drive
                download_url = self.download_book_from_drive(book_title)
                
                if download_url:
                    return {"download_url": download_url, "title": book_title}
                else:
                    raise HTTPException(status_code=404, detail="Book file not found on Google Drive")
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
        
        @app.get("/api/setup-status")
        async def setup_status():
            """Get setup status"""
            return {
                "needs_setup": self.needs_setup(),
                "grandpa_name": self.grandpa_name,
                "database_available": self.database_path.exists(),
                "books_count": self.get_book_count() if self.database_path.exists() else 0
            }
        
        @app.get("/api/database/info")
        async def database_info():
            """Get database information for enhanced interface"""
            try:
                if not self.database_path.exists():
                    return {"error": "Database not found", "books_count": 0}
                
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM books")
                count = cursor.fetchone()[0]
                conn.close()
                
                return {
                    "status": "connected",
                    "books_count": count,
                    "database_path": str(self.database_path),
                    "last_updated": datetime.fromtimestamp(self.database_path.stat().st_mtime).isoformat()
                }
            except Exception as e:
                return {"error": str(e), "books_count": 0}
        
        @app.get("/api/mode")
        async def get_mode():
            """Get application mode for enhanced interface"""
            return {
                "mode": "standalone",
                "title": f"{self.grandpa_name}'s Educational Library", 
                "subtitle": "Educational Books for Learning",
                "authentication_required": False,
                "auto_download": True
            }
        
        return app
    
    def get_book_count(self):
        """Get total number of books"""
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
    
    def serve_library_interface(self):
        """Serve the main library interface"""
        # Try to use the enhanced desktop library interface
        library_files = [
            "desktop-library-enhanced.html",
            "desktop-library.html", 
            "bowersworld.html"
        ]
        
        for filename in library_files:
            library_html = self.webpages_dir / filename
            if library_html.exists():
                print(f"📖 Serving library interface: {filename}")
                with open(library_html, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Customize for grandson
                    content = content.replace(
                        "Anderson's Library - Professional Edition",
                        f"🎓 {self.grandpa_name}'s Educational Library"
                    )
                    content = content.replace(
                        "BowersWorld Educational Library",
                        f"🎓 {self.grandpa_name}'s Educational Library"
                    )
                    # Remove any authentication references
                    content = content.replace("Sign In", "")
                    content = content.replace("Login", "")
                    content = content.replace("Register", "")
                    
                    return content
        
        # Fallback simple interface
        return self.create_simple_interface()
    
    def create_setup_page(self):
        """Create the initial setup page for grandson"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎓 Setup Grandson's Library</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 20px;
        }}
        .setup-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            width: 100%;
            max-width: 600px;
            text-align: center;
            color: #333;
        }}
        .setup-title {{ font-size: 2.5em; margin-bottom: 10px; color: #2E7D32; }}
        .setup-subtitle {{ font-size: 1.2em; color: #666; margin-bottom: 30px; }}
        .instructions {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
            text-align: left; 
        }}
        .step {{ margin-bottom: 15px; }}
        .step-number {{ 
            background: #4CAF50; 
            color: white; 
            width: 24px; 
            height: 24px; 
            border-radius: 50%; 
            display: inline-flex; 
            align-items: center; 
            justify-content: center; 
            margin-right: 10px; 
            font-size: 14px; 
        }}
        .form-group {{ margin-bottom: 20px; text-align: left; }}
        .form-label {{ display: block; margin-bottom: 8px; font-weight: 500; color: #2c3e50; }}
        .form-input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        .form-input:focus {{ border-color: #4CAF50; outline: none; }}
        .setup-button {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }}
        .setup-button:hover {{ transform: translateY(-2px); }}
        #result {{ margin-top: 20px; padding: 15px; border-radius: 8px; display: none; }}
        .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
    </style>
</head>
<body>
    <div class="setup-container">
        <h1 class="setup-title">🎓 Grandson's Library Setup</h1>
        <p class="setup-subtitle">Connect to Grandpa's educational books</p>
        
        <div class="instructions">
            <div class="step">
                <span class="step-number">1</span>
                <strong>Get Grandpa's link:</strong> Ask Grandpa for his Google Drive folder share link
            </div>
            <div class="step">
                <span class="step-number">2</span>
                <strong>Paste the link below:</strong> The link should look like:<br>
                <code>https://drive.google.com/drive/folders/...</code>
            </div>
            <div class="step">
                <span class="step-number">3</span>
                <strong>Start reading:</strong> The app will download all the books automatically!
            </div>
        </div>
        
        <form id="setupForm">
            <div class="form-group">
                <label class="form-label" for="shareUrl">Grandpa's Google Drive Link:</label>
                <input 
                    type="url" 
                    id="shareUrl" 
                    name="share_url"
                    class="form-input" 
                    placeholder="https://drive.google.com/drive/folders/..." 
                    required
                >
            </div>
            
            <div class="form-group">
                <label class="form-label" for="grandpaName">Grandpa's Name:</label>
                <input 
                    type="text" 
                    id="grandpaName" 
                    name="grandpa_name"
                    class="form-input" 
                    placeholder="Grandpa, Mr. Anderson, etc." 
                    value="Grandpa"
                    required
                >
            </div>
            
            <button type="submit" class="setup-button">🚀 Connect to Grandpa's Library</button>
        </form>
        
        <div id="result"></div>
    </div>
    
    <script>
        document.getElementById('setupForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const button = document.querySelector('.setup-button');
            const result = document.getElementById('result');
            
            button.textContent = '⏳ Connecting to Grandpa...';
            button.disabled = true;
            result.style.display = 'none';
            
            const formData = new FormData(document.getElementById('setupForm'));
            
            try {{
                const response = await fetch('/setup', {{
                    method: 'POST',
                    body: formData
                }});
                
                const data = await response.json();
                
                result.style.display = 'block';
                
                if (data.success) {{
                    result.className = 'success';
                    result.innerHTML = `
                        <strong>🎉 Success!</strong><br>
                        ${{data.message}}<br>
                        Books available: ${{data.books_count}}<br>
                        <strong>Opening your library now...</strong>
                    `;
                    
                    setTimeout(() => {{
                        window.location.href = '/library';
                    }}, 2000);
                }} else {{
                    result.className = 'error';
                    result.innerHTML = `<strong>❌ Error:</strong><br>${{data.error}}`;
                }}
            }} catch (error) {{
                result.style.display = 'block';
                result.className = 'error';
                result.innerHTML = `<strong>❌ Network Error:</strong><br>${{error.message}}`;
            }}
            
            button.textContent = '🚀 Connect to Grandpa\\'s Library';
            button.disabled = false;
        }});
    </script>
</body>
</html>
"""
    
    def create_simple_interface(self):
        """Create a simple HTML interface if web files not found"""
        book_count = self.get_book_count()
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎓 Grandson's Educational Library</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            min-height: 100vh;
            color: #333;
        }}
        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .title {{ font-size: 2.5em; color: #2E7D32; margin-bottom: 10px; }}
        .subtitle {{ font-size: 1.2em; color: #666; }}
        .stats {{ background: #fff; margin: 20px; padding: 20px; border-radius: 10px; text-align: center; }}
        .book-count {{ font-size: 3em; color: #4CAF50; font-weight: bold; }}
        .message {{ font-size: 1.3em; margin-top: 20px; color: #333; }}
        .api-links {{ margin: 20px; text-align: center; }}
        .api-link {{ 
            display: inline-block; 
            background: #4CAF50; 
            color: white; 
            padding: 10px 20px; 
            margin: 5px; 
            border-radius: 5px; 
            text-decoration: none; 
        }}
        .api-link:hover {{ background: #45a049; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">🎓 Grandson's Educational Library</h1>
        <p class="subtitle">Your personal collection of educational books</p>
    </div>
    
    <div class="stats">
        <div class="book-count">{book_count}</div>
        <div class="message">Educational books ready to explore!</div>
    </div>
    
    <div class="api-links">
        <a href="/api/categories" class="api-link">📚 View Categories</a>
        <a href="/api/books/search" class="api-link">🔍 Browse All Books</a>
        <a href="/api/stats" class="api-link">📊 Library Stats</a>
        <a href="/api/health" class="api-link">💚 System Status</a>
    </div>
    
    <script>
        // Simple interface - could be enhanced later
        console.log('🎓 Grandson\\'s Library is ready!');
        console.log('📚 Books available: {book_count}');
    </script>
</body>
</html>
"""
    
    def find_available_port(self, start_port=8000):
        """Find an available port"""
        for port in range(start_port, start_port + 50):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise Exception("No available ports found")
    
    def start_library(self):
        """Start the library for grandson"""
        try:
            print("🎓 GRANDSON'S EDUCATIONAL LIBRARY 🎓")
            print("=" * 50)
            print("📚 No registration needed - just books!")
            print("🚀 Starting up...")
            
            # Setup everything
            if not self.setup_database():
                print("\n❌ Library setup failed")
                input("Press Enter to exit...")
                return
            
            # Find available port
            self.port = self.find_available_port()
            
            # Create the app
            self.app = self.create_library_app()
            
            book_count = self.get_book_count()
            print(f"\n✅ Library ready!")
            print(f"📚 Books available: {book_count}")
            print(f"🌐 Access at: http://127.0.0.1:{self.port}")
            print(f"🎯 Opening browser in 3 seconds...")
            print(f"\n💡 Tip: Bookmark this page for easy access!")
            
            # Open browser automatically
            def open_browser():
                import time
                time.sleep(3)
                webbrowser.open(f"http://127.0.0.1:{self.port}")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            # Start the server
            uvicorn.run(
                self.app,
                host="127.0.0.1",
                port=self.port,
                log_level="error",  # Minimal logging for grandson
                access_log=False
            )
            
        except KeyboardInterrupt:
            print("\n👋 Library closed. See you next time!")
        except Exception as e:
            print(f"\n❌ Library error: {e}")
            print("\nFull error details:")
            import traceback
            traceback.print_exc()
            print("\n" + "="*50)
            print("The library encountered an error.")
            print("Press Enter to close...")
            input()

def main():
    """Main entry point with error handling for Windows"""
    try:
        print("🎓 GRANDSON'S LIBRARY STARTING...")
        print("If you see this message, the EXE is working!")
        print("=" * 50)
        
        library = GrandsonLibrary()
        library.start_library()
        
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED: {e}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        print("\n" + "="*50)
        print("Press Enter to close this window...")
        input()

if __name__ == "__main__":
    main()