# File: CreatePublicDatabase.py
# Path: /home/herb/Desktop/AndyLibrary/Scripts/CreatePublicDatabase.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-31
# Last Modified: 2025-07-31 02:20PM
"""
Create a publicly accessible database copy for Windows executable fallback
"""

import os
import shutil
import sqlite3
from datetime import datetime

def CreatePublicDatabaseCopy():
    """Create a public copy of the full database"""
    
    # Source database (full 1,219 books)
    source_db = "/home/herb/Desktop/AndyLibrary/Data/Databases/MyLibrary.db"
    
    # Create public directory in AndyLibrary
    public_dir = "/home/herb/Desktop/AndyLibrary/Public"
    os.makedirs(public_dir, exist_ok=True)
    
    # Target database with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    target_db = os.path.join(public_dir, f"GrandsonLibrary_Full_{timestamp}.db")
    
    if not os.path.exists(source_db):
        print(f"❌ Source database not found: {source_db}")
        return None
    
    try:
        # Copy the database
        print(f"📋 Copying database...")
        print(f"   From: {source_db}")
        print(f"   To: {target_db}")
        
        shutil.copy2(source_db, target_db)
        
        # Verify the copy
        with sqlite3.connect(target_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
        
        print(f"✅ Database copied successfully!")
        print(f"📊 Books: {book_count}")
        print(f"📋 Tables: {table_count}")
        print(f"📁 Size: {os.path.getsize(target_db):,} bytes")
        
        # Create a stable link
        stable_link = os.path.join(public_dir, "GrandsonLibrary_Latest.db")
        if os.path.exists(stable_link):
            os.remove(stable_link)
        os.symlink(os.path.basename(target_db), stable_link)
        
        print(f"🔗 Stable link created: {stable_link}")
        
        return target_db
        
    except Exception as e:
        print(f"❌ Error copying database: {e}")
        return None

def CreateSimpleHTTPServer():
    """Create a simple HTTP server config for serving the database"""
    
    server_script = "/home/herb/Desktop/AndyLibrary/Scripts/DatabaseServer.py"
    
    server_content = '''# File: DatabaseServer.py
# Simple HTTP server for database downloads
import http.server
import socketserver
import os
from pathlib import Path

class DatabaseHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/home/herb/Desktop/AndyLibrary/Public", **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Content-Disposition', 'attachment')
        super().end_headers()

def serve_database(port=8080):
    """Serve database files on specified port"""
    for port_try in range(port, port + 10):
        try:
            with socketserver.TCPServer(("", port_try), DatabaseHandler) as httpd:
                print(f"🌐 Database server running on http://localhost:{port_try}")
                print(f"📥 Database URL: http://localhost:{port_try}/GrandsonLibrary_Latest.db")
                httpd.serve_forever()
        except OSError:
            continue
    print("❌ No available ports found")

if __name__ == "__main__":
    serve_database()
'''
    
    with open(server_script, 'w') as f:
        f.write(server_content)
    
    print(f"📝 HTTP server script created: {server_script}")
    print(f"💡 Run with: python {server_script}")

def main():
    """Create public database and server setup"""
    print("🚀 Creating public database for Windows executable...")
    
    # Create the database copy
    db_path = CreatePublicDatabaseCopy()
    
    if db_path:
        # Create HTTP server script
        CreateSimpleHTTPServer()
        
        print("\n🎉 SUCCESS: Public database created!")
        print("\n📋 Next steps:")
        print("1. Database is ready in /home/herb/Desktop/AndyLibrary/Public/")
        print("2. Windows executable will use this as fallback")
        print("3. Run DatabaseServer.py if you need local HTTP access")
        
        return True
    else:
        print("\n❌ FAILED: Could not create public database")
        return False

if __name__ == "__main__":
    main()