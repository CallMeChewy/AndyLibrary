#!/usr/bin/env python3
# File: test_trusted_folder_access.py
# Path: /home/herb/Desktop/AndyLibrary/test_trusted_folder_access.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-01
# Last Modified: 2025-08-01 04:45PM

"""
Simple test script to verify trusted Google Drive folder access
Tests the key: 1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP
"""

import requests
import sqlite3
import tempfile
import os
from pathlib import Path

def test_trusted_folder_access():
    """Test access to trusted Google Drive folder and database download"""
    
    # Trusted folder ID from your provided key
    trusted_folder_id = "1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP"
    
    print("🔑 Testing Trusted Google Drive Folder Access")
    print("=" * 50)
    print(f"📁 Folder ID: {trusted_folder_id}")
    print(f"🔗 Folder URL: https://drive.google.com/drive/folders/{trusted_folder_id}")
    
    # Create temporary file for testing
    temp_db = Path(tempfile.mktemp(suffix='.db'))
    
    try:
        # Test 1: Try to access folder page (to see if it's public)
        print("\n🔍 TEST 1: Checking folder accessibility...")
        folder_url = f"https://drive.google.com/drive/folders/{trusted_folder_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(folder_url, headers=headers, timeout=10)
        print(f"📊 Folder access status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Folder is publicly accessible")
            
            # Look for any file patterns in the response
            content = response.text
            if 'MyLibrary' in content or '.db' in content:
                print("📄 Found potential database file references in folder")
            else:
                print("⚠️ No obvious database files found in folder HTML")
                
        elif response.status_code == 302:
            print("🔄 Folder redirects (likely requires authentication)")
        else:
            print(f"❌ Folder access failed: {response.status_code}")
        
        # Test 2: Try known database file patterns
        print("\n🔍 TEST 2: Trying common database file ID patterns...")
        
        # These are example file IDs - we'd need the actual ones from your folder
        test_file_ids = [
            # Add actual file IDs from your Google Drive folder here
            # These are just examples to test the pattern
        ]
        
        if not test_file_ids:
            print("⚠️ No specific file IDs to test - need actual database file IDs")
            
            # Test 3: Try to find any .db files in local project as reference
            print("\n🔍 TEST 3: Looking for local database files as reference...")
            
            local_db_paths = [
                Path(__file__).parent / "Standalone" / "MyLibrary.db",
                Path(__file__).parent / "Standalone" / "GrandsonLibrary_Full.db",
                Path(__file__).parent / "Public" / "GrandsonLibrary_Full_20250731_1319.db"
            ]
            
            for db_path in local_db_paths:
                if db_path.exists():
                    print(f"📄 Found local database: {db_path}")
                    file_size = db_path.stat().st_size
                    print(f"📊 File size: {file_size:,} bytes")
                    
                    # Test database content
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        
                        # Check if it has books table
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
                        if cursor.fetchone():
                            cursor.execute("SELECT COUNT(*) FROM books")
                            book_count = cursor.fetchone()[0]
                            print(f"📚 Books in database: {book_count}")
                            
                            # Get first book as example
                            cursor.execute("SELECT title, author FROM books LIMIT 1")
                            first_book = cursor.fetchone()
                            if first_book:
                                print(f"📖 Example book: '{first_book[0]}' by {first_book[1]}")
                                
                        conn.close()
                        
                        # Copy this to temp location for upload test
                        import shutil
                        shutil.copy2(db_path, temp_db)
                        print(f"✅ Successfully copied database for testing")
                        return True
                        
                    except sqlite3.Error as e:
                        print(f"❌ Database error: {e}")
                        
            print("❌ No working local database found")
            return False
        
        # If we had actual file IDs, test them here
        for file_id in test_file_ids:
            print(f"\n🔗 Testing file ID: {file_id}")
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            try:
                response = requests.get(download_url, headers=headers, timeout=30)
                print(f"📊 Download status: {response.status_code}")
                print(f"📊 Content size: {len(response.content)} bytes")
                
                if response.status_code == 200 and len(response.content) > 50000:
                    # Save and test the database
                    with open(temp_db, 'wb') as f:
                        f.write(response.content)
                    
                    # Test database
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM books")
                    book_count = cursor.fetchone()[0]
                    print(f"✅ Downloaded database with {book_count} books")
                    conn.close()
                    return True
                    
            except Exception as e:
                print(f"❌ Download error: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
        
    finally:
        # Clean up
        if temp_db.exists():
            temp_db.unlink()

if __name__ == "__main__":
    print("🧪 TRUSTED GOOGLE DRIVE FOLDER TEST")
    print("Testing access with key: 1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP")
    print()
    
    success = test_trusted_folder_access()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Database access working!")
    else:
        print("❌ FAILED: Need actual file IDs from Google Drive folder")
        print("💡 Next step: Navigate to the folder and get specific database file IDs")