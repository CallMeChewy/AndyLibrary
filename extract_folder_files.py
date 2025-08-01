#!/usr/bin/env python3
# File: extract_folder_files.py
# Path: /home/herb/Desktop/AndyLibrary/extract_folder_files.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-01
# Last Modified: 2025-08-01 04:50PM

"""
Extract file IDs and information from trusted Google Drive folder
Uses pattern matching to find database files
"""

import requests
import re
import json
from pathlib import Path

def extract_folder_files():
    """Extract file information from Google Drive folder HTML"""
    
    trusted_folder_id = "1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP"
    folder_url = f"https://drive.google.com/drive/folders/{trusted_folder_id}"
    
    print("🔍 EXTRACTING FILES FROM TRUSTED FOLDER")
    print("=" * 50)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(folder_url, headers=headers, timeout=15)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to access folder: {response.status_code}")
            return
        
        content = response.text
        print(f"📊 Content length: {len(content)} characters")
        
        # Save raw HTML for inspection
        debug_file = Path(__file__).parent / "folder_content_debug.html" 
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Saved folder HTML to: {debug_file}")
        
        # Look for various file ID patterns in Google Drive HTML
        patterns = [
            # Standard file ID pattern
            r'"([a-zA-Z0-9_-]{25,})"',
            # File IDs with context
            r'data-id="([a-zA-Z0-9_-]{25,})"',
            # Alternative patterns  
            r'"id":"([a-zA-Z0-9_-]{25,})"',
            # File names with IDs
            r'"([a-zA-Z0-9_-]{25,})"[^"]*"([^"]*\.(?:db|sqlite|database)[^"]*)"',
        ]
        
        all_file_ids = set()
        potential_db_files = []
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            if isinstance(matches[0] if matches else None, tuple):
                # Tuple matches (ID, filename)
                for match in matches:
                    file_id = match[0]
                    filename = match[1] if len(match) > 1 else "unknown"
                    if len(file_id) >= 25:
                        potential_db_files.append((file_id, filename))
                        all_file_ids.add(file_id)
            else:
                # Simple ID matches
                for file_id in matches:
                    if len(file_id) >= 25:
                        all_file_ids.add(file_id)
        
        print(f"\n📄 Found {len(all_file_ids)} unique potential file IDs")
        print(f"📄 Found {len(potential_db_files)} potential database files")
        
        # Look for database-related keywords in the content
        db_keywords = ['MyLibrary', 'Library', '.db', 'database', 'sqlite', 'grandson']
        keyword_matches = {}
        
        for keyword in db_keywords:
            matches = len(re.findall(keyword, content, re.IGNORECASE))
            if matches > 0:
                keyword_matches[keyword] = matches
        
        if keyword_matches:
            print("\n🔍 Database-related keywords found:")
            for keyword, count in keyword_matches.items():
                print(f"  📌 '{keyword}': {count} matches")
        
        # Extract any JSON data that might contain file information
        json_patterns = [
            r'"files":\s*\[([^\]]+)\]',
            r'"items":\s*\[([^\]]+)\]',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"\n📋 Found JSON file data pattern: {len(matches[0])} characters")
        
        # If we found specific database files, test them
        if potential_db_files:
            print(f"\n🧪 TESTING {len(potential_db_files)} POTENTIAL DATABASE FILES:")
            
            for i, (file_id, filename) in enumerate(potential_db_files[:5]):  # Test first 5
                print(f"\n📄 Testing file {i+1}: {filename}")
                print(f"🔗 File ID: {file_id}")
                
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                
                try:
                    # Just check headers first to avoid downloading large files
                    head_response = requests.head(download_url, headers=headers, timeout=10)
                    print(f"📊 Head response: {head_response.status_code}")
                    
                    if 'content-length' in head_response.headers:
                        size = int(head_response.headers['content-length'])
                        print(f"📊 File size: {size:,} bytes")
                        
                        if size > 100000:  # Looks like a real database
                            print(f"✅ Potential database file found: {filename}")
                            print(f"🔗 Download URL: {download_url}")
                            
                            # Try a small download to verify
                            partial_response = requests.get(download_url, headers={**headers, 'Range': 'bytes=0-1023'}, timeout=10)
                            if partial_response.status_code in [200, 206]:
                                content_start = partial_response.content[:50]
                                if b'SQLite' in content_start or b'sqlite' in content_start.lower():
                                    print("🎯 CONFIRMED: This is a SQLite database file!")
                                    
                                    # Save this information
                                    result_file = Path(__file__).parent / "database_file_found.txt"
                                    with open(result_file, 'w') as f:
                                        f.write(f"Database File Found!\n")
                                        f.write(f"File ID: {file_id}\n")
                                        f.write(f"Filename: {filename}\n")
                                        f.write(f"Download URL: {download_url}\n")
                                        f.write(f"Size: {size:,} bytes\n")
                                    
                                    print(f"💾 Saved database info to: {result_file}")
                                    return file_id, filename, download_url
                    
                except Exception as e:
                    print(f"❌ Test error: {e}")
        
        # If no specific database files found, list some general file IDs
        if all_file_ids and not potential_db_files:
            print(f"\n📋 First 10 file IDs found (may need manual checking):")
            for i, file_id in enumerate(list(all_file_ids)[:10]):
                print(f"  {i+1}. {file_id}")
                
        return None
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return None

if __name__ == "__main__":
    result = extract_folder_files()
    
    if result:
        file_id, filename, download_url = result
        print(f"\n🎉 SUCCESS! Found database file:")
        print(f"📄 {filename}")
        print(f"🔗 {download_url}")
    else:
        print(f"\n⚠️  No database files automatically detected")
        print(f"💡 Check the saved HTML file for manual inspection")