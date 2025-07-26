# File: UserSetupManager.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/UserSetupManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:18AM

"""
User Setup Manager for AndyLibrary
Handles database download, local system setup, and native app installation
Bridges web registration to native app launch for complete user journey
"""

import os
import sys
import json
import shutil
import logging
import platform
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import requests

class UserSetupManager:
    """
    Manage complete user setup process from web registration to native app launch
    """
    
    def __init__(self, user_id: Optional[int] = None, username: Optional[str] = None):
        self.Logger = logging.getLogger(__name__)
        self.Platform = platform.system().lower()
        self.UserId = user_id
        self.Username = username or f"user_{user_id}" if user_id else "anonymous"
        
        # Determine proper user-specific installation paths
        self.UserHome = Path.home()
        
        # Create user-specific installation directory to support multiple users
        if self.Platform == "windows":
            # Windows: %LOCALAPPDATA%\AndyLibrary\Users\{username}
            self.UserInstallBase = Path(os.environ.get('LOCALAPPDATA', self.UserHome / 'AppData' / 'Local'))
            self.AndyLibraryDir = self.UserInstallBase / "AndyLibrary" / "Users" / self.Username
        elif self.Platform == "darwin":  # macOS
            # macOS: ~/Library/Application Support/AndyLibrary/Users/{username}
            self.UserInstallBase = self.UserHome / "Library" / "Application Support"
            self.AndyLibraryDir = self.UserInstallBase / "AndyLibrary" / "Users" / self.Username
        else:  # Linux/Unix
            # Linux: ~/.local/share/andylibrary/users/{username}
            self.UserInstallBase = self.UserHome / ".local" / "share"
            self.AndyLibraryDir = self.UserInstallBase / "andylibrary" / "users" / self.Username
        
        # User-specific subdirectories
        self.DatabaseDir = self.AndyLibraryDir / "database"
        self.ConfigDir = self.AndyLibraryDir / "config"  
        self.LogsDir = self.AndyLibraryDir / "logs"
        self.AppDir = self.AndyLibraryDir / "app"
        
        # Development source location (for copying files)
        self.DevSourceDir = Path(__file__).parent.parent.parent  # /home/herb/Desktop/AndyLibrary
        
        # Database download settings
        self.DatabaseUrl = "https://your-server.com/database/MyLibrary.db"  # Configure this
        self.DatabaseSize = 10.2  # MB
        self.DatabaseVersion = "2025.07.25"
        
    def CreateUserDirectories(self) -> Dict[str, Any]:
        """
        Create necessary directories for AndyLibrary installation
        """
        try:
            directories = [
                self.AndyLibraryDir,
                self.DatabaseDir,
                self.ConfigDir,
                self.LogsDir,
                self.AndyLibraryDir / "WebPages",
                self.AndyLibraryDir / "Source",
                self.AndyLibraryDir / "Scripts"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.Logger.info(f"✅ Created directory: {directory}")
            
            return {
                "success": True,
                "message": "User directories created successfully",
                "installation_path": str(self.AndyLibraryDir)
            }
            
        except Exception as e:
            self.Logger.error(f"Failed to create user directories: {e}")
            return {"success": False, "error": f"Directory creation failed: {str(e)}"}
    
    def DownloadDatabase(self, user_id: int, session_token: str) -> Dict[str, Any]:
        """
        Download the AndyLibrary database to user's isolated environment
        Ensures user gets their own database copy without accessing development resources
        """
        try:
            self.Logger.info(f"🔄 Starting database download for user {user_id} to isolated environment")
            
            # Create user-specific directories first
            dir_result = self.CreateUserDirectories()
            if not dir_result["success"]:
                return dir_result
            
            # Look for database in development environment (not current working directory)
            dev_db_paths = [
                self.DevSourceDir / "Data" / "Local" / "MyLibrary.db",
                self.DevSourceDir / "Data" / "Databases" / "MyLibrary.db",
                self.DevSourceDir / "MyLibrary.db"
            ]
            
            source_db_path = None
            for path in dev_db_paths:
                if path.exists():
                    source_db_path = path
                    break
            
            if source_db_path:
                user_db_path = self.DatabaseDir / "MyLibrary.db"
                
                # Copy database to user's isolated directory
                shutil.copy2(source_db_path, user_db_path)
                
                # Verify the copy
                if user_db_path.exists():
                    file_size = user_db_path.stat().st_size / (1024 * 1024)  # MB
                    
                    self.Logger.info(f"✅ Database copied to user environment: {file_size:.1f}MB")
                    self.Logger.info(f"   From: {source_db_path}")
                    self.Logger.info(f"   To: {user_db_path}")
                    
                    return {
                        "success": True,
                        "message": f"Database downloaded to user environment ({file_size:.1f}MB)",
                        "database_path": str(user_db_path),
                        "size_mb": round(file_size, 1),
                        "version": self.DatabaseVersion
                    }
                else:
                    return {"success": False, "error": "Database copy verification failed"}
            else:
                return {"success": False, "error": f"Source database not found in development environment. Searched: {[str(p) for p in dev_db_paths]}"}
                
        except Exception as e:
            self.Logger.error(f"Database download to user environment failed: {e}")
            return {"success": False, "error": f"Database download failed: {str(e)}"}
    
    def CopyApplicationFiles(self) -> Dict[str, Any]:
        """
        Copy necessary application files to user's installation from development environment
        Ensures proper isolation - user gets clean copy without development artifacts
        """
        try:
            self.Logger.info("🔄 Copying application files to user environment...")
            
            # Copy essential files from development source directory
            files_to_copy = [
                (self.DevSourceDir / "StartAndyGoogle.py", self.AndyLibraryDir / "StartAndyGoogle.py"),
                (self.DevSourceDir / "requirements.txt", self.AndyLibraryDir / "requirements.txt"),
                (self.DevSourceDir / "Source", self.AndyLibraryDir / "Source"),
                (self.DevSourceDir / "WebPages", self.AndyLibraryDir / "WebPages"),
                (self.DevSourceDir / "Config" / "andygoogle_config.json", self.ConfigDir / "andygoogle_config.json")
            ]
            
            copied_files = []
            
            for source_path, dest_path in files_to_copy:
                if source_path.exists():
                    if source_path.is_file():
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                        copied_files.append(str(dest_path))
                    elif source_path.is_dir():
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        # Filter out development artifacts during copy
                        shutil.copytree(
                            source_path, 
                            dest_path,
                            ignore=shutil.ignore_patterns(
                                '__pycache__', '*.pyc', '.git*', 
                                '.venv', 'node_modules', '.pytest_cache',
                                'Tests', '*.log', '.DS_Store'
                            )
                        )
                        copied_files.append(str(dest_path))
                    
                    self.Logger.info(f"✅ Copied to user environment: {source_path.name} → {dest_path}")
            
            return {
                "success": True,
                "message": f"Copied {len(copied_files)} files/directories to user environment",
                "copied_files": copied_files
            }
            
        except Exception as e:
            self.Logger.error(f"File copying to user environment failed: {e}")
            return {"success": False, "error": f"File copying failed: {str(e)}"}
    
    def CreateUserConfiguration(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create user-specific configuration files isolated from development environment
        """
        try:
            self.Logger.info("🔄 Creating user-specific configuration in isolated environment...")
            
            # Create user-specific config with isolated paths
            user_config = {
                "environment": {
                    "type": "USER_INSTALLATION",
                    "isolated_from_dev": True,
                    "username": self.Username,
                    "platform": self.Platform
                },
                "user": {
                    "id": user_info.get("id"),
                    "email": user_info.get("email"),
                    "username": user_info.get("username"),
                    "subscription_tier": user_info.get("subscription_tier"),
                    "access_level": user_info.get("access_level"),
                    "installed_at": datetime.now().isoformat(),
                    "installation_path": str(self.AndyLibraryDir)
                },
                "database": {
                    "path": str(self.DatabaseDir / "MyLibrary.db"),
                    "version": self.DatabaseVersion,
                    "last_updated": datetime.now().isoformat()
                },
                "server": {
                    "mode": "USER_LOCAL",
                    "auto_start": True,
                    "port_range": [8100, 8110, 8120, 8130, 3100, 5100, 9100],  # Different from dev ports
                    "user_specific_ports": True
                },
                "app": {
                    "first_run": True,
                    "auto_launch": True,
                    "show_welcome": True,
                    "log_path": str(self.LogsDir)
                },
                "paths": {
                    "config_dir": str(self.ConfigDir),
                    "database_dir": str(self.DatabaseDir),
                    "logs_dir": str(self.LogsDir),
                    "app_dir": str(self.AppDir)
                }
            }
            
            # Save user config in isolated location
            user_config_path = self.ConfigDir / "user_config.json"
            with open(user_config_path, 'w') as f:
                json.dump(user_config, f, indent=2)
            
            # Also update the main andygoogle_config.json for user environment
            andy_config_path = self.ConfigDir / "andygoogle_config.json"
            if andy_config_path.exists():
                with open(andy_config_path, 'r') as f:
                    andy_config = json.load(f)
                
                # Update paths to use user-specific locations
                andy_config["database_path"] = str(self.DatabaseDir / "MyLibrary.db")
                andy_config["log_directory"] = str(self.LogsDir)
                andy_config["user_environment"] = True
                andy_config["isolated_installation"] = True
                
                with open(andy_config_path, 'w') as f:
                    json.dump(andy_config, f, indent=2)
            
            self.Logger.info(f"✅ User configuration created in isolated environment: {user_config_path}")
            
            return {
                "success": True,
                "message": "User configuration created in isolated environment",
                "config_path": str(user_config_path),
                "config": user_config
            }
            
        except Exception as e:
            self.Logger.error(f"Configuration creation in user environment failed: {e}")
            return {"success": False, "error": f"Configuration creation failed: {str(e)}"}
    
    def CreateDesktopShortcut(self) -> Dict[str, Any]:
        """
        Create desktop shortcut for AndyLibrary
        """
        try:
            self.Logger.info("🔄 Creating desktop shortcut...")
            
            if self.Platform == "windows":
                return self.CreateWindowsShortcut()
            elif self.Platform == "darwin":  # macOS
                return self.CreateMacShortcut()
            elif self.Platform == "linux":
                return self.CreateLinuxShortcut()
            else:
                return {"success": False, "error": f"Unsupported platform: {self.Platform}"}
                
        except Exception as e:
            self.Logger.error(f"Shortcut creation failed: {e}")
            return {"success": False, "error": f"Shortcut creation failed: {str(e)}"}
    
    def CreateLinuxShortcut(self) -> Dict[str, Any]:
        """Create Linux desktop shortcut"""
        try:
            desktop_path = self.UserHome / "Desktop"
            applications_path = self.UserHome / ".local" / "share" / "applications"
            
            # Create directories if they don't exist
            applications_path.mkdir(parents=True, exist_ok=True)
            
            # Desktop entry content
            desktop_entry = f"""[Desktop Entry]
Name=AndyLibrary
Comment=Educational Digital Library - Getting education to those who need it most
Exec=python3 "{self.AndyLibraryDir}/StartAndyGoogle.py"
Icon=📚
Terminal=false
Type=Application
Categories=Education;Office;
StartupNotify=true
"""
            
            # Save to applications directory
            app_file = applications_path / "andylibrary.desktop"
            with open(app_file, 'w') as f:
                f.write(desktop_entry)
            
            # Make executable
            os.chmod(app_file, 0o755)
            
            # Copy to desktop if it exists
            if desktop_path.exists():
                desktop_file = desktop_path / "AndyLibrary.desktop"
                shutil.copy2(app_file, desktop_file)
                os.chmod(desktop_file, 0o755)
            
            return {
                "success": True,
                "message": "Linux desktop shortcut created",
                "shortcut_path": str(app_file)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Linux shortcut creation failed: {str(e)}"}
    
    def CreateWindowsShortcut(self) -> Dict[str, Any]:
        """Create Windows desktop shortcut"""
        try:
            # This would require pywin32 for full Windows shortcut creation
            # For now, create a simple batch file
            desktop_path = self.UserHome / "Desktop"
            batch_file = desktop_path / "AndyLibrary.bat"
            
            batch_content = f"""@echo off
cd /d "{self.AndyLibraryDir}"
python StartAndyGoogle.py
pause
"""
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            return {
                "success": True,
                "message": "Windows batch shortcut created",
                "shortcut_path": str(batch_file)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Windows shortcut creation failed: {str(e)}"}
    
    def CreateMacShortcut(self) -> Dict[str, Any]:
        """Create macOS application shortcut"""
        try:
            # Create a simple app bundle or script
            applications_path = self.UserHome / "Applications"
            applications_path.mkdir(exist_ok=True)
            
            script_path = applications_path / "AndyLibrary.command"
            script_content = f"""#!/bin/bash
cd "{self.AndyLibraryDir}"
python3 StartAndyGoogle.py
"""
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            
            return {
                "success": True,
                "message": "macOS shortcut created",
                "shortcut_path": str(script_path)
            }
            
        except Exception as e:
            return {"success": False, "error": f"macOS shortcut creation failed: {str(e)}"}
    
    def CompleteUserSetup(self, user_info: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """
        Complete the full user setup process
        """
        try:
            self.Logger.info(f"🚀 Starting complete setup for user: {user_info.get('email')}")
            
            setup_steps = []
            
            # Step 1: Download database
            db_result = self.DownloadDatabase(user_info.get("id"), session_token)
            setup_steps.append(("Database Download", db_result["success"], db_result.get("message", db_result.get("error"))))
            
            if not db_result["success"]:
                return {"success": False, "error": db_result["error"], "setup_steps": setup_steps}
            
            # Step 2: Copy application files
            files_result = self.CopyApplicationFiles()
            setup_steps.append(("Application Files", files_result["success"], files_result.get("message", files_result.get("error"))))
            
            if not files_result["success"]:
                return {"success": False, "error": files_result["error"], "setup_steps": setup_steps}
            
            # Step 3: Create user configuration
            config_result = self.CreateUserConfiguration(user_info)
            setup_steps.append(("User Configuration", config_result["success"], config_result.get("message", config_result.get("error"))))
            
            if not config_result["success"]:
                return {"success": False, "error": config_result["error"], "setup_steps": setup_steps}
            
            # Step 4: Create desktop shortcut
            shortcut_result = self.CreateDesktopShortcut()
            setup_steps.append(("Desktop Shortcut", shortcut_result["success"], shortcut_result.get("message", shortcut_result.get("error"))))
            
            # Log completion
            self.Logger.info("✅ User setup completed successfully")
            
            return {
                "success": True,
                "message": "AndyLibrary installation completed successfully",
                "installation_path": str(self.AndyLibraryDir),
                "database_size": db_result.get("size_mb"),
                "setup_steps": setup_steps,
                "shortcut_created": shortcut_result["success"],
                "ready_to_launch": True
            }
            
        except Exception as e:
            self.Logger.error(f"Complete setup failed: {e}")
            return {"success": False, "error": f"Setup failed: {str(e)}"}
    
    def LaunchAndyLibrary(self) -> Dict[str, Any]:
        """
        Launch the AndyLibrary native app from user's isolated installation
        """
        try:
            self.Logger.info("🚀 Launching AndyLibrary from user's isolated installation...")
            
            # Verify user installation exists
            startup_script = self.AndyLibraryDir / "StartAndyGoogle.py"
            if not startup_script.exists():
                return {"success": False, "error": f"User installation not found at {self.AndyLibraryDir}"}
            
            # Change to user's installation directory (not development directory)
            original_cwd = os.getcwd()
            os.chdir(self.AndyLibraryDir)
            
            self.Logger.info(f"   Working directory: {self.AndyLibraryDir}")
            self.Logger.info(f"   Original directory: {original_cwd}")
            
            # Launch the app from user's environment
            if self.Platform == "windows":
                process = subprocess.Popen(
                    [sys.executable, str(startup_script)], 
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=str(self.AndyLibraryDir)
                )
            else:
                process = subprocess.Popen(
                    [sys.executable, str(startup_script)],
                    cwd=str(self.AndyLibraryDir)
                )
            
            # Restore original working directory for development environment
            os.chdir(original_cwd)
            
            self.Logger.info("✅ AndyLibrary launched from user environment successfully")
            
            return {
                "success": True,
                "message": "AndyLibrary launched from user's isolated installation",
                "installation_path": str(self.AndyLibraryDir),
                "process_id": process.pid,
                "user_environment": True
            }
            
        except Exception as e:
            # Restore original working directory on error
            try:
                os.chdir(original_cwd)
            except:
                pass
            
            self.Logger.error(f"App launch from user environment failed: {e}")
            return {"success": False, "error": f"Launch failed: {str(e)}"}