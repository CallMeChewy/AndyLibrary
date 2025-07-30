# File: WindowsDatabaseSyncFix.py
# Path: /home/herb/Desktop/AndyLibrary/Scripts/WindowsDatabaseSyncFix.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 21:45PM
"""
Complete fix implementation for Windows executable database sync issues.
Implements all necessary modifications to resolve placeholder database problem.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

class WindowsDatabaseSyncFixer:
    """Implements comprehensive fixes for Windows database sync issues"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixes_applied = []
        self.backup_files = []
    
    def ApplyAllFixes(self):
        """Apply all necessary fixes for Windows database sync"""
        print("🔧 Applying Windows Database Sync Fixes")
        print("=" * 50)
        
        # Fix 1: Modify PyInstaller spec to exclude placeholder database
        self.FixPyInstallerSpec()
        
        # Fix 2: Add database initialization to standalone startup
        self.FixStandaloneStartup()
        
        # Fix 3: Create Windows-specific database initialization
        self.CreateWindowsDatabaseInit()
        
        # Fix 4: Update startup logic to check database
        self.FixMainStartupLogic()
        
        # Fix 5: Create database validation helper
        self.CreateDatabaseValidator()
        
        # Summary
        self.PrintFixSummary()
    
    def FixPyInstallerSpec(self):
        """Fix PyInstaller spec to not include placeholder database"""
        print("🔧 Fixing PyInstaller spec file...")
        
        spec_file = self.project_root / "build_windows_exe.spec"
        if not spec_file.exists():
            print("❌ PyInstaller spec file not found")
            return
        
        # Create backup
        backup_file = spec_file.with_suffix('.spec.backup')
        shutil.copy2(spec_file, backup_file)
        self.backup_files.append(backup_file)
        
        # Read current spec
        with open(spec_file, 'r') as f:
            content = f.read()
        
        # Replace database inclusion with conditional logic
        new_content = content.replace(
            "# Include Data directory with databases\n    (str(base_dir / 'Data'), 'Data'),",
            """# Include Data directory structure but exclude databases
    (str(base_dir / 'Data' / 'Cache'), 'Data/Cache'),
    (str(base_dir / 'Data' / 'Covers'), 'Data/Covers'),
    (str(base_dir / 'Data' / 'HTML'), 'Data/HTML'),
    (str(base_dir / 'Data' / 'Local'), 'Data/Local'),
    (str(base_dir / 'Data' / 'Logs'), 'Data/Logs'),
    (str(base_dir / 'Data' / 'Text'), 'Data/Text'),
    (str(base_dir / 'Data' / 'Thumbs'), 'Data/Thumbs'),
    # NOTE: Databases intentionally excluded - will be downloaded from Google Drive on first run"""
        )
        
        # Write updated spec
        with open(spec_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Updated PyInstaller spec to exclude databases")
        self.fixes_applied.append("PyInstaller spec updated to exclude databases")
    
    def FixStandaloneStartup(self):
        """Fix standalone startup to initialize database"""
        print("🔧 Fixing standalone startup logic...")
        
        standalone_file = self.project_root / "AndyLibraryStandalone.py"
        if not standalone_file.exists():
            print("❌ Standalone file not found")
            return
        
        # Create backup
        backup_file = standalone_file.with_suffix('.py.backup')
        shutil.copy2(standalone_file, backup_file)
        self.backup_files.append(backup_file)
        
        # Read current content
        with open(standalone_file, 'r') as f:
            content = f.read()
        
        # Add database initialization import and logic
        if "from Source.Core.DriveManager import DriveManager" not in content:
            # Add import after existing imports
            import_section = "import os\nimport sys"
            new_import_section = """import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "Source"))

try:
    from Core.DriveManager import DriveManager
    from Core.DatabaseManager import DatabaseManager
except ImportError as e:
    print(f"Warning: Could not import database managers: {e}")
    DriveManager = None
    DatabaseManager = None"""
            
            content = content.replace(import_section, new_import_section)
        
        # Add database initialization function
        if "def InitializeWindowsDatabase():" not in content:
            init_function = '''
def InitializeWindowsDatabase():
    """Initialize database for Windows standalone executable"""
    print("🔄 Initializing Windows database...")
    
    try:
        # Check if we have database managers available
        if DriveManager is None:
            print("⚠️ DriveManager not available - using local database if present")
            return CheckLocalDatabase()
        
        # Initialize DriveManager
        config_path = Path(__file__).parent / "Config" / "andygoogle_config.json"
        drive_manager = DriveManager(str(config_path))
        
        # Initialize database (will download from Google Drive if needed)
        if drive_manager.InitializeDatabase():
            print("✅ Database initialized successfully")
            return True
        else:
            print("⚠️ Google Drive sync failed - checking for local database")
            return CheckLocalDatabase()
            
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        return CheckLocalDatabase()

def CheckLocalDatabase():
    """Check if local database exists and is valid"""
    db_paths = [
        Path(__file__).parent / "Data" / "Databases" / "MyLibrary.db",
        Path(__file__).parent / "Data" / "Local" / "cached_library.db"
    ]
    
    for db_path in db_paths:
        if db_path.exists() and db_path.stat().st_size > 100000:  # At least 100KB
            print(f"✅ Using local database: {db_path}")
            return True
    
    print("❌ No valid database found - application may not function properly")
    return False
'''
            # Insert before main function
            if "def main():" in content:
                content = content.replace("def main():", init_function + "\ndef main():")
            else:
                content += init_function
        
        # Add database check to main function
        if "if __name__ == '__main__':" in content:
            main_section = content.split("if __name__ == '__main__':")[1]
            if "InitializeWindowsDatabase()" not in main_section:
                # Add database initialization call
                new_main_section = '''if __name__ == '__main__':
    print("🚀 Starting AndyLibrary Windows Standalone")
    print("=" * 50)
    
    # Initialize database first
    if not InitializeWindowsDatabase():
        print("❌ Database initialization failed")
        input("Press Enter to continue anyway...")
    
    # Continue with normal startup''' + main_section.strip()
                
                content = content.split("if __name__ == '__main__':")[0] + new_main_section
        
        # Write updated content
        with open(standalone_file, 'w') as f:
            f.write(content)
        
        print("✅ Updated standalone startup with database initialization")
        self.fixes_applied.append("Standalone startup updated with database initialization")
    
    def CreateWindowsDatabaseInit(self):
        """Create Windows-specific database initialization script"""
        print("🔧 Creating Windows database initialization helper...")
        
        init_file = self.project_root / "Source" / "Utils" / "WindowsDatabaseInit.py"
        init_content = '''# File: WindowsDatabaseInit.py
# Path: Source/Utils/WindowsDatabaseInit.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 21:45PM
"""
Windows-specific database initialization utilities.
Handles database setup and Google Drive sync for Windows executables.
"""

import os
import sys
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

class WindowsDatabaseInitializer:
    """Handle database initialization for Windows executables"""
    
    def __init__(self, app_directory: Optional[Path] = None):
        self.app_dir = app_directory or Path(sys.executable).parent
        self.data_dir = self.app_dir / "Data"
        self.config_dir = self.app_dir / "Config"
        
    def InitializeDatabase(self) -> bool:
        """Initialize database with fallback options"""
        print("🔄 Windows Database Initialization")
        
        # Step 1: Try Google Drive sync
        if self.TryGoogleDriveSync():
            return True
        
        # Step 2: Check for bundled database
        if self.CheckBundledDatabase():
            return True
        
        # Step 3: Create minimal database
        if self.CreateMinimalDatabase():
            return True
        
        print("❌ All database initialization methods failed")
        return False
    
    def TryGoogleDriveSync(self) -> bool:
        """Attempt to sync database from Google Drive"""
        try:
            sys.path.insert(0, str(self.app_dir / "Source"))
            from Core.DriveManager import DriveManager
            
            config_path = self.config_dir / "andygoogle_config.json"
            if not config_path.exists():
                print("⚠️ Configuration file not found - skipping Google Drive sync")
                return False
            
            drive_manager = DriveManager(str(config_path))
            
            if drive_manager.InitializeDatabase():
                print("✅ Database synced from Google Drive")
                return True
            else:
                print("⚠️ Google Drive sync failed")
                return False
                
        except Exception as e:
            print(f"⚠️ Google Drive sync error: {e}")
            return False
    
    def CheckBundledDatabase(self) -> bool:
        """Check for bundled database files"""
        possible_paths = [
            self.data_dir / "Databases" / "MyLibrary.db",
            self.data_dir / "Local" / "cached_library.db",
            self.app_dir / "MyLibrary.db"
        ]
        
        for db_path in possible_paths:
            if db_path.exists() and self.ValidateDatabase(db_path):
                print(f"✅ Using bundled database: {db_path}")
                return True
        
        print("⚠️ No valid bundled database found")
        return False
    
    def CreateMinimalDatabase(self) -> bool:
        """Create minimal functional database"""
        try:
            db_path = self.data_dir / "Databases" / "MyLibrary.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create basic tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    category_id INTEGER,
                    subject_id INTEGER,
                    FilePath TEXT,
                    ThumbnailImage BLOB,
                    last_opened TEXT,
                    LastOpened TEXT,
                    Rating INTEGER,
                    Notes TEXT,
                    Keywords TEXT,
                    FileSize INTEGER,
                    FileHash TEXT,
                    AddedDate TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
            # Insert sample data
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES ('General')")
            cursor.execute("INSERT OR IGNORE INTO subjects (name) VALUES ('Uncategorized')")
            
            cursor.execute("""
                INSERT OR IGNORE INTO books (title, author, category_id, subject_id) 
                VALUES ('Welcome to AndyLibrary', 'System', 1, 1)
            """)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Created minimal database: {db_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create minimal database: {e}")
            return False
    
    def ValidateDatabase(self, db_path: Path) -> bool:
        """Validate database integrity and structure"""
        try:
            if db_path.stat().st_size < 8192:  # Less than 8KB is suspicious
                return False
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result[0] != 'ok':
                conn.close()
                return False
            
            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            required_tables = ['books', 'categories', 'subjects']
            
            conn.close()
            
            return all(table in tables for table in required_tables)
            
        except Exception:
            return False

def InitializeWindowsDatabase(app_directory: Optional[Path] = None) -> bool:
    """Main function to initialize Windows database"""
    initializer = WindowsDatabaseInitializer(app_directory)
    return initializer.InitializeDatabase()
'''
        
        # Ensure directory exists
        init_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(init_file, 'w') as f:
            f.write(init_content)
        
        print("✅ Created Windows database initialization helper")
        self.fixes_applied.append("Windows database initialization helper created")
    
    def FixMainStartupLogic(self):
        """Fix main startup logic to include database checks"""
        print("🔧 Fixing main startup logic...")
        
        startup_file = self.project_root / "StartAndyGoogle.py"
        if not startup_file.exists():
            print("❌ Main startup file not found")
            return
        
        # Create backup
        backup_file = startup_file.with_suffix('.py.backup')
        shutil.copy2(startup_file, backup_file)
        self.backup_files.append(backup_file)
        
        # Read content
        with open(startup_file, 'r') as f:
            content = f.read()
        
        # Add database validation to environment check
        if "def check_environment(self):" in content:
            # Find the method and add database check
            lines = content.split('\n')
            new_lines = []
            in_check_env = False
            
            for line in lines:
                new_lines.append(line)
                
                if "def check_environment(self):" in line:
                    in_check_env = True
                elif in_check_env and line.strip().startswith("def ") and "check_environment" not in line:
                    # End of method, insert database check before this
                    in_check_env = False
                    
                    # Add database validation
                    new_lines.insert(-1, "")
                    new_lines.insert(-1, "        # Check database availability")
                    new_lines.insert(-1, "        if not self.validate_database():")
                    new_lines.insert(-1, "            issues.append('Database not available - will attempt initialization')")
                    new_lines.insert(-1, "")
            
            content = '\n'.join(new_lines)
        
        # Add database validation method
        if "def validate_database(self):" not in content:
            validation_method = '''
    def validate_database(self):
        """Validate database availability and integrity"""
        from pathlib import Path
        import sqlite3
        
        # Check common database locations
        db_paths = [
            Path(self.script_dir) / "Data" / "Databases" / "MyLibrary.db",
            Path(self.script_dir) / "Data" / "Local" / "cached_library.db"
        ]
        
        for db_path in db_paths:
            if db_path.exists():
                try:
                    # Quick validation
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM books")
                    count = cursor.fetchone()[0]
                    conn.close()
                    
                    if count > 0:
                        return True
                except:
                    continue
        
        return False
'''
            
            # Insert before main function or at end of class
            if "def main():" in content and "class AndyGoogleStarter:" in content:
                content = content.replace("def main():", validation_method + "\ndef main():")
            
        # Write updated content
        with open(startup_file, 'w') as f:
            f.write(content)
        
        print("✅ Updated main startup logic with database validation")
        self.fixes_applied.append("Main startup logic updated with database validation")
    
    def CreateDatabaseValidator(self):
        """Create comprehensive database validation utility"""
        print("🔧 Creating database validation utility...")
        
        validator_file = self.project_root / "Source" / "Utils" / "DatabaseValidator.py"
        validator_content = '''# File: DatabaseValidator.py
# Path: Source/Utils/DatabaseValidator.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 21:45PM
"""
Comprehensive database validation and repair utilities.
Ensures database integrity across different deployment environments.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DatabaseValidator:
    """Validate and repair database files"""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.issues = []
        self.repair_log = []
    
    def ValidateComplete(self) -> Dict[str, any]:
        """Run complete database validation"""
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'stats': {},
            'repair_suggestions': []
        }
        
        try:
            # Basic existence check
            if not self.db_path.exists():
                validation_result['valid'] = False
                validation_result['issues'].append('Database file does not exist')
                return validation_result
            
            # Size check
            size_mb = self.db_path.stat().st_size / 1024 / 1024
            if size_mb < 0.01:  # Less than 10KB
                validation_result['valid'] = False
                validation_result['issues'].append(f'Database too small: {size_mb:.2f} MB')
            
            # SQLite integrity
            integrity_ok, integrity_msg = self.CheckIntegrity()
            if not integrity_ok:
                validation_result['valid'] = False
                validation_result['issues'].append(f'Integrity check failed: {integrity_msg}')
            
            # Schema validation
            schema_ok, schema_issues = self.ValidateSchema()
            if not schema_ok:
                validation_result['valid'] = False
                validation_result['issues'].extend(schema_issues)
            
            # Data validation
            data_stats = self.ValidateData()
            validation_result['stats'] = data_stats
            
            if data_stats['total_records'] == 0:
                validation_result['warnings'].append('Database contains no records')
            elif data_stats['total_records'] < 10:
                validation_result['warnings'].append(f'Database has very few records: {data_stats["total_records"]}')
            
            # Repair suggestions
            if not validation_result['valid']:
                validation_result['repair_suggestions'] = self.GenerateRepairSuggestions(validation_result)
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['issues'].append(f'Validation error: {str(e)}')
        
        return validation_result
    
    def CheckIntegrity(self) -> Tuple[bool, str]:
        """Check SQLite database integrity"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 'ok':
                return True, 'OK'
            else:
                return False, result[0] if result else 'Unknown error'
                
        except Exception as e:
            return False, str(e)
    
    def ValidateSchema(self) -> Tuple[bool, List[str]]:
        """Validate database schema"""
        issues = []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Required tables
            required_tables = ['books', 'categories', 'subjects']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                issues.append(f'Missing required tables: {", ".join(missing_tables)}')
            
            # Validate books table structure
            if 'books' in tables:
                cursor.execute("PRAGMA table_info(books)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                required_columns = ['id', 'title', 'author']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    issues.append(f'Books table missing columns: {", ".join(missing_columns)}')
            
            conn.close()
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f'Schema validation error: {str(e)}']
    
    def ValidateData(self) -> Dict[str, int]:
        """Validate database data and return statistics"""
        stats = {
            'total_records': 0,
            'books_count': 0,
            'categories_count': 0,
            'subjects_count': 0
        }
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Count records in each table
            tables = ['books', 'categories', 'subjects']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[f'{table}_count'] = count
                    stats['total_records'] += count
                except:
                    pass  # Table might not exist
            
            conn.close()
            
        except Exception:
            pass  # Return empty stats
        
        return stats
    
    def GenerateRepairSuggestions(self, validation_result: Dict) -> List[str]:
        """Generate repair suggestions based on validation results"""
        suggestions = []
        
        for issue in validation_result['issues']:
            if 'does not exist' in issue:
                suggestions.append('Initialize database from Google Drive or create minimal database')
            elif 'too small' in issue:
                suggestions.append('Database appears to be placeholder - sync from Google Drive')
            elif 'Integrity check failed' in issue:
                suggestions.append('Database corrupted - restore from backup or re-sync')
            elif 'Missing required tables' in issue:
                suggestions.append('Database schema incomplete - reinitialize database')
        
        return suggestions

def ValidateDatabase(db_path: Path) -> Dict[str, any]:
    """Quick database validation function"""
    validator = DatabaseValidator(db_path)
    return validator.ValidateComplete()
'''
        
        # Ensure directory exists
        validator_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(validator_file, 'w') as f:
            f.write(validator_content)
        
        print("✅ Created database validation utility")
        self.fixes_applied.append("Database validation utility created")
    
    def PrintFixSummary(self):
        """Print summary of all fixes applied"""
        print("\n" + "=" * 50)
        print("🎉 WINDOWS DATABASE SYNC FIXES COMPLETED")
        print("=" * 50)
        
        print(f"\n✅ Applied {len(self.fixes_applied)} fixes:")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"   {i}. {fix}")
        
        if self.backup_files:
            print(f"\n💾 Created {len(self.backup_files)} backup files:")
            for backup in self.backup_files:
                print(f"   • {backup}")
        
        print("\n📋 NEXT STEPS:")
        print("   1. Test the Windows build with: python build_windows_final.py")
        print("   2. Run the executable on Windows to verify database sync")
        print("   3. Check that Google Drive authentication works")
        print("   4. Verify full database is downloaded (not placeholder)")
        
        print("\n🔧 TROUBLESHOOTING:")
        print("   • If Google Drive sync fails, check credentials bundling")
        print("   • If database still small, verify internet connection")
        print("   • Check console output for detailed error messages")
        
        print("\n" + "=" * 50)

def main():
    """Apply all Windows database sync fixes"""
    fixer = WindowsDatabaseSyncFixer()
    fixer.ApplyAllFixes()

if __name__ == "__main__":
    main()