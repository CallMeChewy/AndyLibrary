#!/usr/bin/env python3
# File: RemoteClientSetup.py
# Path: /home/herb/Desktop/AndyLibrary/Standalone/RemoteClientSetup.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 02:45PM

"""
Remote Client Setup for AndyLibrary
Handles setup for users accessing shared Google Drive library
Provides simple interface for entering share link and downloading library
"""

import os
import sys
import json
import sqlite3
import shutil
import requests
import threading
import webbrowser
import tempfile
import urllib.parse
import re
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse

class RemoteClientSetup:
    """Setup client for remote users accessing shared Google Drive"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.app_dir = self.script_dir.parent
        self.data_dir = self.script_dir / "Data"
        self.config_path = self.data_dir / "remote_config.json"
        self.database_path = self.data_dir / "MyLibrary.db"
        self.port = 8002
        self.app = None
        
        # Create data directory
        self.data_dir.mkdir(exist_ok=True)
        
        # Check if running as PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            self.webpages_dir = Path(sys._MEIPASS) / "WebPages"
        else:
            self.webpages_dir = self.app_dir / "WebPages"
        
        # Load or create config
        self.config = self.load_config()
    
    def load_config(self):
        """Load remote configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
        
        # Default config
        return {
            "setup_complete": False,
            "google_drive_folder_url": "",
            "google_drive_folder_id": "",
            "library_owner": "",
            "last_sync": None,
            "database_info": {}
        }
    
    def save_config(self):
        """Save remote configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False
    
    def extract_folder_id_from_url(self, url):
        """Extract Google Drive folder ID from share URL"""
        try:
            # Common Google Drive share URL patterns:
            # https://drive.google.com/drive/folders/FOLDER_ID?usp=sharing
            # https://drive.google.com/drive/u/0/folders/FOLDER_ID
            # https://drive.google.com/open?id=FOLDER_ID
            
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
    
    def test_folder_access(self, folder_id):
        """Test if Google Drive folder is publicly accessible"""
        try:
            # Try to access folder metadata via public API
            api_url = f"https://www.googleapis.com/drive/v3/files/{folder_id}"
            params = {
                'fields': 'id,name,webViewLink,createdTime,parents'
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                folder_info = response.json()
                print(f"✅ Folder accessible: {folder_info.get('name', 'Unknown')}")
                return True, folder_info
            else:
                print(f"❌ Folder not accessible: HTTP {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ Folder access test failed: {e}")
            return False, None
    
    def find_database_in_folder(self, folder_id):
        """Find MyLibrary.db in the shared Google Drive folder"""
        try:
            print(f"🔍 Searching for MyLibrary.db in folder {folder_id}...")
            
            # Search for .db files in the folder
            api_url = "https://www.googleapis.com/drive/v3/files"
            params = {
                'q': f"'{folder_id}' in parents and name contains '.db'",
                'fields': 'files(id,name,size,mimeType,webContentLink,downloadUrl)'
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                files = response.json().get('files', [])
                
                # Look for MyLibrary.db specifically
                for file in files:
                    if 'MyLibrary.db' in file['name']:
                        print(f"✅ Found database: {file['name']} ({file.get('size', 'unknown')} bytes)")
                        return file
                
                # If not found, show available .db files
                if files:
                    print("⚠️ MyLibrary.db not found, but found these database files:")
                    for file in files:
                        print(f"  - {file['name']}")
                    return files[0]  # Use first .db file found
                else:
                    print("❌ No database files found in folder")
                    return None
            else:
                print(f"❌ Failed to search folder: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Database search failed: {e}")
            return None
    
    def download_database_from_drive(self, file_info):
        """Download database file from Google Drive"""
        try:
            print(f"📥 Downloading {file_info['name']}...")
            
            # Use webContentLink or construct direct download URL
            file_id = file_info['id']
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            response = requests.get(download_url, timeout=60)
            
            if response.status_code == 200:
                # Save database
                with open(self.database_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify database
                if self.verify_database():
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
    
    def verify_database(self):
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
                self.config["database_info"] = {
                    "books_count": count,
                    "size_bytes": self.database_path.stat().st_size,
                    "last_verified": datetime.now().isoformat()
                }
                return True
            else:
                print("⚠️ Database has no books")
                return False
                
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
    
    def create_setup_app(self):
        """Create FastAPI setup application"""
        app = FastAPI(title="AndyLibrary Remote Setup", version="1.0.0")
        
        # Mount static files if available
        if self.webpages_dir.exists():
            app.mount("/static", StaticFiles(directory=str(self.webpages_dir)), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def setup_page():
            """Show setup page"""
            if self.config["setup_complete"]:
                return self.create_status_page()
            else:
                return self.create_setup_page()
        
        @app.post("/setup")
        async def process_setup(share_url: str = Form(...), owner_name: str = Form(...)):
            """Process setup form"""
            try:
                print(f"🔄 Processing setup with URL: {share_url}")
                
                # Extract folder ID from URL
                folder_id = self.extract_folder_id_from_url(share_url)
                if not folder_id:
                    return JSONResponse({
                        "success": False,
                        "error": "Invalid Google Drive share URL. Please check the URL and try again."
                    })
                
                print(f"📂 Extracted folder ID: {folder_id}")
                
                # Test folder access
                accessible, folder_info = self.test_folder_access(folder_id)
                if not accessible:
                    return JSONResponse({
                        "success": False,
                        "error": "Cannot access the shared folder. Make sure it's set to 'Anyone with the link can view'."
                    })
                
                # Find database in folder
                db_file = self.find_database_in_folder(folder_id)
                if not db_file:
                    return JSONResponse({
                        "success": False,
                        "error": "MyLibrary.db not found in the shared folder. Please contact the library owner."
                    })
                
                # Download database
                if not self.download_database_from_drive(db_file):
                    return JSONResponse({
                        "success": False,
                        "error": "Failed to download the database. Please try again."
                    })
                
                # Update config
                self.config.update({
                    "setup_complete": True,
                    "google_drive_folder_url": share_url,
                    "google_drive_folder_id": folder_id,
                    "library_owner": owner_name,
                    "last_sync": datetime.now().isoformat()
                })
                
                self.save_config()
                
                return JSONResponse({
                    "success": True,
                    "message": f"Successfully connected to {owner_name}'s library!",
                    "books_count": self.config["database_info"].get("books_count", 0)
                })
                
            except Exception as e:
                return JSONResponse({
                    "success": False,
                    "error": f"Setup failed: {str(e)}"
                })
        
        @app.get("/library", response_class=HTMLResponse)
        async def library_interface():
            """Show library interface after setup"""
            if not self.config["setup_complete"]:
                return RedirectResponse("/")
            
            # Serve library interface
            desktop_html = self.webpages_dir / "desktop-library.html"
            if desktop_html.exists():
                with open(desktop_html, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = content.replace(
                        "Anderson's Library - Professional Edition",
                        f"{self.config['library_owner']}'s Educational Library"
                    )
                    return content
            else:
                return "<h1>Library Interface Not Found</h1>"
        
        @app.get("/api/status")
        async def get_status():
            """Get setup and connection status"""
            return {
                "setup_complete": self.config["setup_complete"],
                "library_owner": self.config.get("library_owner", ""),
                "database_available": self.database_path.exists(),
                "books_count": self.config.get("database_info", {}).get("books_count", 0),
                "last_sync": self.config.get("last_sync")
            }
        
        # Add standard API endpoints if database is available
        if self.database_path.exists():
            self.add_library_endpoints(app)
        
        return app
    
    def add_library_endpoints(self, app):
        """Add library API endpoints"""
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
    
    def create_setup_page(self):
        """Create HTML setup page"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AndyLibrary - Remote Setup</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        .setup-title {{ font-size: 2em; margin-bottom: 10px; color: #2c3e50; }}
        .setup-subtitle {{ font-size: 1.1em; color: #7f8c8d; margin-bottom: 30px; }}
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
        .form-input:focus {{ border-color: #667eea; outline: none; }}
        .setup-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        .instructions {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
            text-align: left; 
        }}
        .step {{ margin-bottom: 15px; }}
        .step-number {{ 
            background: #667eea; 
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
        #result {{ margin-top: 20px; padding: 15px; border-radius: 8px; display: none; }}
        .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
    </style>
</head>
<body>
    <div class="setup-container">
        <h1 class="setup-title">📚 AndyLibrary Remote Setup</h1>
        <p class="setup-subtitle">Connect to a shared educational library</p>
        
        <div class="instructions">
            <div class="step">
                <span class="step-number">1</span>
                <strong>Get the share link:</strong> Ask the library owner for their Google Drive folder share link
            </div>
            <div class="step">
                <span class="step-number">2</span>
                <strong>Paste the link:</strong> The link should look like:<br>
                <code>https://drive.google.com/drive/folders/...</code>
            </div>
            <div class="step">
                <span class="step-number">3</span>
                <strong>Access library:</strong> The app will download and setup your library automatically
            </div>
        </div>
        
        <form id="setupForm">
            <div class="form-group">
                <label class="form-label" for="shareUrl">Google Drive Share Link:</label>
                <input 
                    type="url" 
                    id="shareUrl" 
                    class="form-input" 
                    placeholder="https://drive.google.com/drive/folders/..." 
                    required
                >
            </div>
            
            <div class="form-group">
                <label class="form-label" for="ownerName">Library Owner Name:</label>
                <input 
                    type="text" 
                    id="ownerName" 
                    class="form-input" 
                    placeholder="e.g., Mr. Anderson, Dr. Smith, etc." 
                    required
                >
            </div>
            
            <button type="submit" class="setup-button">🚀 Connect to Library</button>
        </form>
        
        <div id="result"></div>
    </div>
    
    <script>
        document.getElementById('setupForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const button = document.querySelector('.setup-button');
            const result = document.getElementById('result');
            
            button.textContent = '⏳ Connecting...';
            button.disabled = true;
            result.style.display = 'none';
            
            const formData = new FormData();
            formData.append('share_url', document.getElementById('shareUrl').value);
            formData.append('owner_name', document.getElementById('ownerName').value);
            
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
                        <strong>✅ Success!</strong><br>
                        ${{data.message}}<br>
                        Books available: ${{data.books_count}}<br>
                        <a href="/library" style="color: #155724; text-decoration: underline;">Open Library →</a>
                    `;
                    
                    setTimeout(() => {{
                        window.location.href = '/library';
                    }}, 3000);
                }} else {{
                    result.className = 'error';
                    result.innerHTML = `<strong>❌ Error:</strong><br>${{data.error}}`;
                }}
            }} catch (error) {{
                result.style.display = 'block';
                result.className = 'error';
                result.innerHTML = `<strong>❌ Network Error:</strong><br>${{error.message}}`;
            }}
            
            button.textContent = '🚀 Connect to Library';
            button.disabled = false;
        }});
    </script>
</body>
</html>
"""
    
    def create_status_page(self):
        """Create HTML status page for configured setup"""
        books_count = self.config.get("database_info", {}).get("books_count", 0)
        owner = self.config.get("library_owner", "Unknown")
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AndyLibrary - {owner}'s Library</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 20px;
        }}
        .status-container {{ /* Same styles as setup-container */ }}
        .library-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }}
        .library-button:hover {{ transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="status-container">
        <h1>📚 {owner}'s Educational Library</h1>
        <p>Successfully connected! {books_count} books available.</p>
        <br>
        <a href="/library" class="library-button">📖 Open Library</a>
        <a href="/" class="library-button">⚙️ Reconfigure</a>
    </div>
</body>
</html>
"""
    
    def start_setup(self):
        """Start the setup application"""
        try:
            print("🔥 ANDYLIBRARY REMOTE CLIENT SETUP 🔥")
            print("=" * 50)
            
            # Find available port
            import socket
            for port in range(8002, 8020):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('127.0.0.1', port))
                        self.port = port
                        break
                except OSError:
                    continue
            
            # Create and start app
            self.app = self.create_setup_app()
            
            print(f"🚀 Starting setup on port {self.port}")
            print(f"🌐 Access: http://127.0.0.1:{self.port}")
            
            if self.config["setup_complete"]:
                print(f"✅ Already connected to {self.config['library_owner']}'s library")
                print(f"📚 {self.config.get('database_info', {}).get('books_count', 0)} books available")
            else:
                print("📋 Setup required - opening browser...")
            
            # Open browser
            def open_browser():
                import time
                time.sleep(2)
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
            print(f"❌ Setup error: {e}")

def main():
    """Main entry point"""
    client = RemoteClientSetup()
    client.start_setup()

if __name__ == "__main__":
    main()