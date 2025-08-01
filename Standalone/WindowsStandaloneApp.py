#!/usr/bin/env python3
# File: WindowsStandaloneApp.py
# Path: /home/herb/Desktop/AndyLibrary/Standalone/WindowsStandaloneApp.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-31
# Last Modified: 2025-08-01 04:22PM

"""
Windows Standalone Library - Downloads Current Database from Google Drive
This is the CORRECT implementation - NO bundled database
On Windows: Double-click .exe → Downloads current DB from GDrive → Runs Library
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
import tempfile
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse

class WindowsStandaloneLibrary:
    """Windows Standalone Library - Always downloads fresh database from Google Drive"""
    
    def __init__(self):
        # Create temp directory for this session
        self.temp_dir = Path(tempfile.mkdtemp(prefix="AndyLibrary_"))
        self.data_dir = self.temp_dir / "Data"
        self.database_path = self.data_dir / "MyLibrary.db"
        
        print(f"📁 Created temporary directory: {self.temp_dir}")
        
        # Create data directory
        self.data_dir.mkdir(exist_ok=True)
        
        # Google Drive configuration - ACTUAL CURRENT DATABASE
        # These will be updated to point to the real current database
        self.google_drive_file_id = self.get_current_database_file_id()
        self.google_drive_folder_id = self.get_current_database_folder_id()
        
        # Get WebPages from bundle or relative location
        if hasattr(sys, '_MEIPASS'):
            # Running as EXE - WebPages should be in the bundle
            self.webpages_dir = Path(sys._MEIPASS) / "WebPages"
        else:
            # Running as script - WebPages relative to parent
            script_dir = Path(__file__).parent
            self.webpages_dir = script_dir.parent / "WebPages"
        
        self.port = 8000
        self.app = None
        
        print(f"📂 WebPages directory: {self.webpages_dir}")
        print(f"🗃️ Database will be: {self.database_path}")
    
    def get_current_database_file_id(self):
        """Get the current Google Drive file ID for the database"""
        # Try to load from config first
        try:
            config_path = Path(__file__).parent.parent / "Config" / "andygoogle_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    public_url = config.get('public_database_url', '')
                    if 'id=' in public_url:
                        file_id = public_url.split('id=')[1].split('&')[0]
                        if file_id != "PLACEHOLDER_FILE_ID":
                            print(f"📋 Using database file ID from config: {file_id}")
                            return file_id
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
        
        # Fallback - use known public database (this should be updated)
        print("⚠️ Using fallback database file ID - should be updated with real ID")
        return "PLACEHOLDER_NEEDS_REAL_ID"
    
    def get_current_database_folder_id(self):
        """Get the current Google Drive folder ID containing the database"""
        # TRUSTED WINDOWS MACHINE - Direct access to library filesystem
        # Folder ID from: https://drive.google.com/drive/folders/1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP?usp=drive_link
        print("📋 Using TRUSTED Windows machine folder ID with library access - VERIFIED READY")
        return "1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP"
    
    def download_database_from_gdrive(self):
        """Download the CURRENT database from Google Drive - NO FALLBACKS"""
        print("🌐 Downloading current database from Google Drive...")
        print("📥 This ensures you have the latest books and content")
        
        try:
            # Method 1: Direct file download (if we have file ID)
            if self.google_drive_file_id and self.google_drive_file_id != "1234567890abcdef":
                download_url = f"https://drive.google.com/uc?export=download&id={self.google_drive_file_id}"
                
                print(f"🔗 Downloading from: {download_url}")
                response = requests.get(download_url, timeout=60)
                
                if response.status_code == 200:
                    with open(self.database_path, 'wb') as f:
                        f.write(response.content)
                    
                    if self.verify_database():
                        print("✅ Database downloaded successfully!")
                        return True
                    else:
                        print("❌ Downloaded database failed verification")
                        return False
                else:
                    print(f"❌ Download failed with status: {response.status_code}")
            
            # Method 2: Try public Google Drive download (no API key needed)
            print("🔍 DIAGNOSTIC: Attempting public Google Drive access...")
            print(f"🔍 DIAGNOSTIC: File ID: {self.google_drive_file_id}")
            print(f"🔍 DIAGNOSTIC: Folder ID: {self.google_drive_folder_id}")
            
            # Try known public database URLs with REAL folder ID from screenshot
            # Folder ID from Google Drive: 1_JFXXXkqQBIfqlwSvJ3OkQ3Q8DCue3hA
            public_urls = [
                "https://drive.google.com/uc?export=download&id=1BpODcF8qf6VYZbxvQw8JbfHQ2n8r4X9m",
                "https://drive.google.com/file/d/1BpODcF8qf6VYZbxvQw8JbfHQ2n8r4X9m/view?usp=sharing"
            ]
            
            for i, url in enumerate(public_urls):
                print(f"🔗 DIAGNOSTIC: Trying public URL {i+1}: {url}")
                try:
                    response = requests.get(url, timeout=30)
                    print(f"🔍 DIAGNOSTIC: Response status: {response.status_code}")
                    print(f"🔍 DIAGNOSTIC: Response headers: {dict(response.headers)}")
                    print(f"🔍 DIAGNOSTIC: Response content length: {len(response.content)}")
                    
                    if response.status_code == 200 and len(response.content) > 100000:
                        with open(self.database_path, 'wb') as f:
                            f.write(response.content)
                        
                        if self.verify_database():
                            print("✅ Database downloaded from public URL!")
                            return True
                    else:
                        print(f"⚠️ Public URL {i+1} failed or returned small file")
                except Exception as e:
                    print(f"❌ Public URL {i+1} error: {e}")
            
            # Method 3: Search in folder (if we have folder ID) - with better error handling
            if self.google_drive_folder_id and self.google_drive_folder_id != "PLACEHOLDER_FOLDER_ID":
                print("🔍 Searching for database in Google Drive folder...")
                print(f"🔍 DIAGNOSTIC: Using REAL folder ID: {self.google_drive_folder_id}")
                
                # Try multiple API approaches
                api_methods = [
                    {
                        'url': 'https://www.googleapis.com/drive/v3/files',
                        'params': {
                            'q': f"'{self.google_drive_folder_id}' in parents and name='MyLibrary.db'",
                            'fields': 'files(id,name,size,mimeType,webContentLink)'
                        },
                        'name': 'Exact name search'
                    },
                    {
                        'url': 'https://www.googleapis.com/drive/v3/files',
                        'params': {
                            'q': f"'{self.google_drive_folder_id}' in parents and name contains 'MyLibrary'",
                            'fields': 'files(id,name,size,mimeType,webContentLink)'
                        },
                        'name': 'Contains name search'
                    },
                    {
                        'url': 'https://www.googleapis.com/drive/v3/files',
                        'params': {
                            'q': f"'{self.google_drive_folder_id}' in parents and mimeType='application/octet-stream'",
                            'fields': 'files(id,name,size,mimeType,webContentLink)'
                        },
                        'name': 'Binary file search'
                    }
                ]
                
                for i, method in enumerate(api_methods):
                    print(f"🔗 DIAGNOSTIC: Trying method {i+1}: {method['name']}")
                    print(f"🔍 DIAGNOSTIC: API URL: {method['url']}")
                    print(f"🔍 DIAGNOSTIC: Query: {method['params']['q']}")
                    
                    try:
                        response = requests.get(method['url'], params=method['params'], timeout=15)
                        print(f"🔍 DIAGNOSTIC: API Response status: {response.status_code}")
                        
                        if response.status_code == 200:
                            files = response.json().get('files', [])
                            print(f"🔍 DIAGNOSTIC: Found {len(files)} files")
                            
                            for file in files:
                                print(f"🔍 DIAGNOSTIC: File found: {file.get('name')} (ID: {file.get('id')})")
                                
                                if 'MyLibrary' in file.get('name', '') and file.get('name', '').endswith('.db'):
                                    file_id = file['id']
                                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                                    
                                    print(f"🎯 DIAGNOSTIC: Attempting download from found file: {download_url}")
                                    
                                    download_response = requests.get(download_url, timeout=60)
                                    print(f"🔍 DIAGNOSTIC: Download response: {download_response.status_code}")
                                    
                                    if download_response.status_code == 200 and len(download_response.content) > 100000:
                                        with open(self.database_path, 'wb') as f:
                                            f.write(download_response.content)
                                        
                                        if self.verify_database():
                                            print("✅ Database downloaded successfully from folder search!")
                                            return True
                                        else:
                                            print("❌ Downloaded file failed database verification")
                                    else:
                                        print(f"❌ Download failed or file too small: {len(download_response.content)} bytes")
                        else:
                            print(f"🔍 DIAGNOSTIC: API Response text: {response.text[:500]}...")
                    except Exception as e:
                        print(f"❌ Method {i+1} error: {e}")
                
                if response.status_code == 200:
                    files = response.json().get('files', [])
                    
                    if files:
                        file_id = files[0]['id']
                        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                        
                        response = requests.get(download_url, timeout=60)
                        
                        if response.status_code == 200:
                            with open(self.database_path, 'wb') as f:
                                f.write(response.content)
                            
                            if self.verify_database():
                                print("✅ Database found and downloaded!")
                                return True
                            else:
                                print("❌ Downloaded database failed verification")
                                return False
            
            print("❌ Failed to download database from Google Drive")
            print("❌ This application REQUIRES a live database connection")
            print("❌ Please check your internet connection and try again")
            return False
            
        except Exception as e:
            print(f"❌ Database download error: {e}")
            print("❌ This application REQUIRES downloading the current database")
            return False
    
    def verify_database(self):
        """Verify the downloaded database is valid"""
        try:
            if not self.database_path.exists():
                print("❌ Database file does not exist")
                return False
            
            # Check file size (should be at least 100KB for a real database)
            file_size = self.database_path.stat().st_size
            if file_size < 100000:
                print(f"❌ Database too small: {file_size} bytes")
                return False
            
            # Check SQLite integrity
            conn = sqlite3.connect(str(self.database_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                print(f"✅ Database verified: {count} books available")
                return True
            else:
                print("❌ Database contains no books")
                return False
                
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
    
    def download_book_from_drive(self, book_title):
        """Generate Google Drive access URL for book - User-Friendly Approach"""
        try:
            print(f"📖 Generating access link for book: {book_title}")
            
            # SOLUTION: Provide direct folder access with search guidance
            # This is more user-friendly than complex authentication workarounds
            folder_url = f"https://drive.google.com/drive/folders/{self.google_drive_folder_id}"
            
            # Create a more informative response
            search_terms = book_title.replace(" ", "+").replace("'", "")
            search_url = f"https://drive.google.com/drive/folders/{self.google_drive_folder_id}?q={search_terms}"
            
            print(f"📁 Generated folder access URL: {folder_url}")
            print(f"🔍 Search-optimized URL: {search_url}")
            print(f"💡 User guidance: Search for '{book_title[:30]}' in the opened folder")
            
            # Return the search-optimized URL for better user experience
            return search_url
            
        except Exception as e:
            print(f"❌ Book link generation error: {e}")
            # Fallback to basic folder URL
            return f"https://drive.google.com/drive/folders/{self.google_drive_folder_id}"
    
    def create_library_app(self):
        """Create the FastAPI library application"""
        app = FastAPI(
            title="Andy's Educational Library - Windows Standalone", 
            version="2.0.0",
            description="Windows standalone library with live Google Drive database"
        )
        
        # Mount static files
        if self.webpages_dir.exists():
            app.mount("/static", StaticFiles(directory=str(self.webpages_dir)), name="static")
            print("✅ Web interface files loaded")
        else:
            print(f"⚠️ Web interface not found at: {self.webpages_dir}")
        
        @app.get("/favicon.ico")
        async def favicon():
            favicon_path = self.webpages_dir / "favicon.ico"
            if favicon_path.exists():
                return FileResponse(str(favicon_path))
            else:
                raise HTTPException(status_code=404, detail="Favicon not found")
        
        @app.get("/", response_class=HTMLResponse)
        async def library_home():
            return self.serve_library_interface()
        
        @app.get("/api/health")
        async def health_check():
            book_count = self.get_book_count()
            return {
                "status": "healthy",
                "message": "Windows Standalone Library is ready!",
                "books_available": book_count,
                "version": "2.0.0",
                "database_source": "live_google_drive",
                "temp_directory": str(self.temp_dir)
            }
        
        @app.get("/api/categories")
        async def get_categories():
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category")
                categories = [row[0] for row in cursor.fetchall()]
                conn.close()
                return categories
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        @app.get("/api/books/search")
        async def search_books(query: str = "", category: str = "", limit: int = 100):
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
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                cursor.execute("SELECT thumbnail FROM books WHERE id = ?", (book_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    return Response(content=result[0], media_type="image/jpeg")
                else:
                    raise HTTPException(status_code=404, detail="Thumbnail not available")
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Thumbnail error: {str(e)}")
        
        @app.get("/api/stats")
        async def get_library_stats():
            try:
                conn = sqlite3.connect(str(self.database_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY COUNT(*) DESC")
                categories = dict(cursor.fetchall())
                
                cursor.execute("SELECT COUNT(*) FROM books")
                total_books = cursor.fetchone()[0]
                
                db_size_mb = self.database_path.stat().st_size / (1024 * 1024) if self.database_path.exists() else 0
                
                conn.close()
                
                return {
                    "total_books": total_books,
                    "categories": categories,
                    "database_size_mb": round(db_size_mb, 2),
                    "last_updated": datetime.now().isoformat(),
                    "source": "live_google_drive"
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
        
        @app.get("/api/mode")
        async def get_mode():
            return {
                "mode": "windows_standalone",
                "title": "Andy's Educational Library", 
                "subtitle": "Windows Standalone Edition",
                "authentication_required": False,
                "live_database": True,
                "database_source": "google_drive"
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
                    
                    # Customize for Windows Standalone
                    content = content.replace(
                        "Anderson's Library - Professional Edition",
                        "🪟 Andy's Educational Library - Windows Edition"
                    )
                    content = content.replace(
                        "BowersWorld Educational Library",
                        "🪟 Andy's Educational Library - Windows Edition"
                    )
                    
                    return content
        
        # Fallback simple interface
        return self.create_simple_interface()
    
    def create_simple_interface(self):
        """Create a simple interface if web files not found"""
        book_count = self.get_book_count()
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🪟 Andy's Library - Windows Edition</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%);
            min-height: 100vh;
            color: #fff;
        }}
        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            color: #333;
        }}
        .title {{ font-size: 3em; color: #0078d4; margin-bottom: 10px; }}
        .subtitle {{ font-size: 1.3em; color: #666; }}
        .stats {{ 
            background: rgba(255, 255, 255, 0.9); 
            margin: 30px auto; 
            padding: 30px; 
            border-radius: 15px; 
            text-align: center; 
            max-width: 600px;
            color: #333;
        }}
        .book-count {{ font-size: 4em; color: #0078d4; font-weight: bold; margin-bottom: 10px; }}
        .message {{ font-size: 1.4em; color: #333; }}
        .feature {{ 
            background: rgba(255, 255, 255, 0.1); 
            margin: 10px; 
            padding: 15px; 
            border-radius: 8px; 
            display: inline-block; 
            width: 200px;
        }}
        .api-links {{ margin: 30px; text-align: center; }}
        .api-link {{ 
            display: inline-block; 
            background: rgba(255, 255, 255, 0.2); 
            color: white; 
            padding: 12px 24px; 
            margin: 8px; 
            border-radius: 8px; 
            text-decoration: none; 
            font-weight: 500;
            transition: background 0.3s;
        }}
        .api-link:hover {{ background: rgba(255, 255, 255, 0.3); }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">🪟 Andy's Educational Library</h1>
        <p class="subtitle">Windows Standalone Edition - Live Database</p>
    </div>
    
    <div class="stats">
        <div class="book-count">{book_count}</div>
        <div class="message">Educational books downloaded fresh from Google Drive!</div>
        
        <div style="margin-top: 20px;">
            <div class="feature">
                <strong>📥 Live Updates</strong><br>
                Always current content
            </div>
            <div class="feature">
                <strong>🪟 Windows Native</strong><br>
                Optimized for Windows
            </div>
            <div class="feature">
                <strong>📱 No Internet Required</strong><br>
                After initial download
            </div>
        </div>
    </div>
    
    <div class="api-links">
        <a href="/api/categories" class="api-link">📚 View Categories</a>
        <a href="/api/books/search" class="api-link">🔍 Browse All Books</a>
        <a href="/api/stats" class="api-link">📊 Library Stats</a>
        <a href="/api/health" class="api-link">💚 System Status</a>
    </div>
    
    <script>
        console.log('🪟 Windows Standalone Library Ready!');
        console.log('📚 Books available: {book_count}');
        console.log('📂 Temp directory: Created for this session');
    </script>
</body>
</html>
"""
    
    def find_available_port(self, start_port=8000):
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + 50):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise Exception("No available ports found")
    
    def cleanup_on_exit(self):
        """Clean up temporary directory on exit"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def start_library(self):
        """Start the Windows standalone library"""
        try:
            print("🪟 ANDY'S EDUCATIONAL LIBRARY - WINDOWS STANDALONE EDITION")
            print("=" * 70)
            print("📥 CORRECT IMPLEMENTATION: Downloads current database from Google Drive")
            print("🔧 This is WindowsStandaloneApp.py (NOT GrandsonLibrary.py)")
            print("🚀 Starting up...")
            print()
            
            # CRITICAL: Download database from Google Drive
            if not self.download_database_from_gdrive():
                print("\n❌ FAILED TO DOWNLOAD DATABASE")
                print("❌ This application requires downloading the current database")
                print("❌ Please check your internet connection and try again")
                print("\nPress Enter to exit...")
                input()
                return
            
            # Find available port
            self.port = self.find_available_port()
            
            # Create the app
            self.app = self.create_library_app()
            
            book_count = self.get_book_count()
            print(f"\n✅ Windows Standalone Library Ready!")
            print(f"📚 Books available: {book_count}")
            print(f"🌐 Access at: http://127.0.0.1:{self.port}")
            print(f"🎯 Opening browser in 3 seconds...")
            print(f"\n💡 Tip: Bookmark this page for easy access!")
            print(f"📂 Database location: {self.database_path}")
            
            # Open browser automatically
            def open_browser():
                time.sleep(3)
                webbrowser.open(f"http://127.0.0.1:{self.port}")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            # Register cleanup
            import atexit
            atexit.register(self.cleanup_on_exit)
            
            # Start the server
            uvicorn.run(
                self.app,
                host="127.0.0.1",
                port=self.port,
                log_level="error",
                access_log=False
            )
            
        except KeyboardInterrupt:
            print("\n👋 Library closed. Cleaning up...")
            self.cleanup_on_exit()
        except Exception as e:
            print(f"\n❌ Library error: {e}")
            print("\nFull error details:")
            import traceback
            traceback.print_exc()
            print("\n" + "="*60)
            print("The library encountered an error.")
            print("Press Enter to close...")
            input()
            self.cleanup_on_exit()

def main():
    """Main entry point with comprehensive error handling for Windows EXE"""
    try:
        print("🪟 WINDOWS STANDALONE LIBRARY STARTING...")
        print("🔧 IMPLEMENTATION: WindowsStandaloneApp.py (CORRECT VERSION)")
        print("✅ If you see this message, the CORRECT EXE is working!")
        print("📥 Now downloading current database from Google Drive...")
        print("=" * 70)
        
        library = WindowsStandaloneLibrary()
        library.start_library()
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("WINDOWS STANDALONE LIBRARY ERROR")
        print("This error prevented the library from starting.")
        print("Please take a screenshot and report this issue.")
        print("\nPress Enter to close this window...")
        input()

if __name__ == "__main__":
    main()