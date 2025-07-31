# File: UploadToClaudeFolder.py
# Path: /home/herb/Desktop/AndyLibrary/Scripts/UploadToClaudeFolder.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-31
# Last Modified: 2025-07-31 02:15PM
"""
Upload Windows executable to ClaudeFolder on Google Drive for easy transfer
"""

import os
import sys
import json
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Source.API.GoogleDriveAPI import GoogleDriveAPI
from googleapiclient.http import MediaFileUpload

class ClaudeFolderUploader:
    """Upload files to ClaudeFolder on Google Drive"""
    
    def __init__(self):
        self.credentials_path = "Config/google_credentials.json"
        self.drive_api = GoogleDriveAPI(self.credentials_path)
        self.claude_folder_id = None
        
    def GetOrCreateClaudeFolder(self) -> str:
        """Get or create the ClaudeFolder on Google Drive"""
        if not self.drive_api.service:
            if not self.drive_api.Authenticate():
                print("❌ Failed to authenticate with Google Drive")
                return None
        
        try:
            # Search for existing ClaudeFolder
            query = "name='ClaudeFolder' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.drive_api.service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get('files', [])
            
            if folders:
                self.claude_folder_id = folders[0]['id']
                print(f"✅ Found ClaudeFolder: {self.claude_folder_id}")
                return self.claude_folder_id
            else:
                # Create ClaudeFolder
                folder_metadata = {
                    'name': 'ClaudeFolder',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'description': 'Claude Code workspace for file transfers'
                }
                
                folder = self.drive_api.service.files().create(
                    body=folder_metadata,
                    fields='id,name'
                ).execute()
                
                self.claude_folder_id = folder.get('id')
                print(f"✅ Created ClaudeFolder: {self.claude_folder_id}")
                return self.claude_folder_id
                
        except Exception as e:
            print(f"❌ Error with ClaudeFolder: {e}")
            return None
    
    def UploadExecutable(self, exe_path: str) -> bool:
        """Upload Windows executable to ClaudeFolder"""
        if not os.path.exists(exe_path):
            print(f"❌ Executable not found: {exe_path}")
            return False
        
        folder_id = self.GetOrCreateClaudeFolder()
        if not folder_id:
            return False
        
        try:
            filename = os.path.basename(exe_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            upload_name = f"GrandsonLibrary-{timestamp}.exe"
            
            print(f"📤 Uploading {filename} as {upload_name}...")
            
            # Check if file already exists
            query = f"name='{upload_name}' and '{folder_id}' in parents and trashed=false"
            results = self.drive_api.service.files().list(q=query, fields="files(id, name)").execute()
            existing_files = results.get('files', [])
            
            file_metadata = {
                'name': upload_name,
                'parents': [folder_id],
                'description': f'AndyLibrary Windows executable with comprehensive diagnostics - {timestamp}'
            }
            
            media = MediaFileUpload(exe_path, mimetype='application/x-msdownload')
            
            if existing_files:
                # Update existing file
                file_id = existing_files[0]['id']
                updated_file = self.drive_api.service.files().update(
                    fileId=file_id,
                    body={'name': upload_name, 'description': file_metadata['description']},
                    media_body=media,
                    fields='id,name,size,webViewLink'
                ).execute()
                
                print(f"✅ Updated executable in ClaudeFolder")
                print(f"📁 File ID: {updated_file.get('id')}")
                print(f"🔗 View: {updated_file.get('webViewLink')}")
                return True
            else:
                # Create new file
                file = self.drive_api.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,size,webViewLink'
                ).execute()
                
                print(f"✅ Uploaded executable to ClaudeFolder")
                print(f"📁 File ID: {file.get('id')}")
                print(f"📊 Size: {file.get('size')} bytes")
                print(f"🔗 View: {file.get('webViewLink')}")
                return True
                
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False

def main():
    """Upload the latest Windows executable to ClaudeFolder"""
    uploader = ClaudeFolderUploader()
    
    # Find the latest executable
    exe_paths = [
        "/home/herb/Desktop/qqq/GrandsonLibrary-Complete.exe",
        "/home/herb/Desktop/AndyLibrary/GrandsonLibrary-Complete.exe",
        "/home/herb/Desktop/qqq/GrandsonLibrary-Complete/GrandsonLibrary-Complete.exe"
    ]
    
    exe_path = None
    for path in exe_paths:
        if os.path.exists(path):
            exe_path = path
            print(f"📍 Found executable: {path}")
            break
    
    if not exe_path:
        print("❌ No Windows executable found")
        return False
    
    # Upload to ClaudeFolder
    success = uploader.UploadExecutable(exe_path)
    
    if success:
        print("\n🎉 SUCCESS: Windows executable uploaded to ClaudeFolder!")
        print("💡 You can now access it from any system with Google Drive access")
    else:
        print("\n❌ FAILED: Could not upload executable")
    
    return success

if __name__ == "__main__":
    main()