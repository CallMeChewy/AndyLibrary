# File: DiagnoseWindowsDatabaseIssue.py
# Path: /home/herb/Desktop/AndyLibrary/Scripts/DiagnoseWindowsDatabaseIssue.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 21:32PM
"""
Comprehensive diagnostic script for Windows executable database sync issues.
Analyzes all potential failure points and provides complete traces for resolution.
"""

import os
import sys
import json
import sqlite3
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class WindowsDatabaseDiagnostics:
    """Complete diagnostics for Windows executable database sync issues"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = None
        self.diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'database_analysis': {},
            'config_analysis': {},
            'build_analysis': {},
            'auth_analysis': {},
            'path_analysis': {},
            'recommendations': []
        }
        
        # Find temp directory
        self.FindTempDirectory()
    
    def FindTempDirectory(self):
        """Find the MEI temp directory"""
        desktop_path = Path.home() / "Desktop"
        for item in desktop_path.glob("_MEI*"):
            if item.is_dir():
                self.temp_dir = item
                break
        
        if not self.temp_dir:
            print("❌ No MEI temp directory found")
    
    def RunCompleteDiagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic checks"""
        print("🔍 Running Comprehensive Windows Database Diagnostics")
        print("=" * 60)
        
        # System Information
        self.AnalyzeSystemInfo()
        
        # Database Analysis
        self.AnalyzeDatabases()
        
        # Configuration Analysis
        self.AnalyzeConfigurations()
        
        # Build Process Analysis
        self.AnalyzeBuildProcess()
        
        # Authentication Analysis  
        self.AnalyzeAuthentication()
        
        # Path Analysis
        self.AnalyzePaths()
        
        # Generate Recommendations
        self.GenerateRecommendations()
        
        # Save diagnostics
        self.SaveDiagnostics()
        
        return self.diagnostics
    
    def AnalyzeSystemInfo(self):
        """Analyze system and environment information"""
        print("📊 Analyzing System Information...")
        
        system_info = {
            'platform': sys.platform,
            'python_version': sys.version,
            'current_directory': str(Path.cwd()),
            'project_root': str(self.project_root),
            'temp_directory': str(self.temp_dir) if self.temp_dir else None,
            'environment_variables': {},
            'path_variables': os.environ.get('PATH', '').split(os.pathsep)[:5]  # First 5 paths
        }
        
        # Key environment variables
        env_vars = ['PYTHONPATH', 'GOOGLE_APPLICATION_CREDENTIALS', 'HOME', 'USERPROFILE']
        for var in env_vars:
            system_info['environment_variables'][var] = os.environ.get(var)
        
        self.diagnostics['system_info'] = system_info
        print(f"✅ System: {sys.platform}, Python: {sys.version.split()[0]}")
    
    def AnalyzeDatabases(self):
        """Comprehensive database analysis"""
        print("📊 Analyzing Database Files...")
        
        databases = {
            'main_database': self.project_root / "Data" / "Databases" / "MyLibrary.db",
            'web_database': self.project_root / "Data" / "Databases" / "MyLibraryWeb.db",
            'temp_database': None
        }
        
        if self.temp_dir:
            databases['temp_database'] = self.temp_dir / "_MEI68922" / "Data" / "MyLibrary.db"
        
        db_analysis = {}
        
        for db_name, db_path in databases.items():
            if db_path and db_path.exists():
                analysis = self.AnalyzeSingleDatabase(db_path)
                db_analysis[db_name] = analysis
                print(f"✅ {db_name}: {analysis['record_count']} records, {analysis['size_mb']} MB")
            else:
                db_analysis[db_name] = {'exists': False, 'path': str(db_path) if db_path else None}
                print(f"❌ {db_name}: Not found at {db_path}")
        
        self.diagnostics['database_analysis'] = db_analysis
    
    def AnalyzeSingleDatabase(self, db_path: Path) -> Dict[str, Any]:
        """Analyze a single database file"""
        analysis = {
            'exists': True,
            'path': str(db_path),
            'size_bytes': db_path.stat().st_size,
            'size_mb': round(db_path.stat().st_size / 1024 / 1024, 2),
            'modified_time': datetime.fromtimestamp(db_path.stat().st_mtime).isoformat(),
            'hash': self.CalculateFileHash(db_path),
            'tables': [],
            'record_count': 0,
            'integrity_check': False,
            'schema_info': {}
        }
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            analysis['tables'] = tables
            
            # Get record counts
            table_counts = {}
            total_records = 0
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                    total_records += count
                except Exception as e:
                    table_counts[table] = f"Error: {e}"
            
            analysis['record_count'] = total_records
            analysis['table_counts'] = table_counts
            
            # Integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            analysis['integrity_check'] = result[0] == 'ok'
            
            # Schema info for books table (if exists)
            if 'books' in tables:
                cursor.execute("PRAGMA table_info(books)")
                columns = cursor.fetchall()
                analysis['schema_info']['books_columns'] = len(columns)
                analysis['schema_info']['books_schema'] = [
                    {'name': col[1], 'type': col[2], 'not_null': bool(col[3])} 
                    for col in columns
                ]
            
            conn.close()
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def AnalyzeConfigurations(self):
        """Analyze all configuration files"""
        print("📊 Analyzing Configuration Files...")
        
        config_files = {
            'andygoogle_config': self.project_root / "Config" / "andygoogle_config.json",
            'oauth_security_config': self.project_root / "Config" / "oauth_security_config.json",
            'google_credentials': self.project_root / "Config" / "google_credentials.json",
            'google_token': self.project_root / "Config" / "google_token.json"
        }
        
        config_analysis = {}
        
        for config_name, config_path in config_files.items():
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    
                    analysis = {
                        'exists': True,
                        'path': str(config_path),
                        'size_bytes': config_path.stat().st_size,
                        'modified_time': datetime.fromtimestamp(config_path.stat().st_mtime).isoformat(),
                        'keys': list(config_data.keys()) if isinstance(config_data, dict) else 'Not a dict',
                        'sensitive_data_present': False
                    }
                    
                    # Check for sensitive data indicators
                    if isinstance(config_data, dict):
                        sensitive_keys = ['client_secret', 'private_key', 'refresh_token', 'access_token']
                        analysis['sensitive_data_present'] = any(key in config_data for key in sensitive_keys)
                    
                    config_analysis[config_name] = analysis
                    print(f"✅ {config_name}: {len(analysis['keys'])} keys" if isinstance(analysis['keys'], list) else f"✅ {config_name}: Found")
                    
                except Exception as e:
                    config_analysis[config_name] = {'exists': True, 'error': str(e)}
                    print(f"❌ {config_name}: Error reading - {e}")
            else:
                config_analysis[config_name] = {'exists': False, 'path': str(config_path)}
                print(f"❌ {config_name}: Not found")
        
        self.diagnostics['config_analysis'] = config_analysis
    
    def AnalyzeBuildProcess(self):
        """Analyze build process and specifications"""
        print("📊 Analyzing Build Process...")
        
        build_files = {
            'pyinstaller_spec': list(self.project_root.glob("*.spec")),
            'build_scripts': list(self.project_root.glob("build*.py")) + list(self.project_root.glob("build*.sh")),
            'dockerfile': self.project_root / "Dockerfile.windows",
            'requirements': self.project_root / "requirements.txt",
            'standalone_requirements': self.project_root / "Standalone" / "requirements-standalone.txt"
        }
        
        build_analysis = {}
        
        for build_type, files in build_files.items():
            if isinstance(files, list):
                build_analysis[build_type] = []
                for file_path in files:
                    if file_path.exists():
                        content = self.ReadFileContent(file_path)
                        build_analysis[build_type].append({
                            'path': str(file_path),
                            'size': file_path.stat().st_size,
                            'content_preview': content[:500] + "..." if len(content) > 500 else content
                        })
                        print(f"✅ Found {build_type}: {file_path.name}")
            else:
                if files.exists():
                    content = self.ReadFileContent(files)
                    build_analysis[build_type] = {
                        'exists': True,
                        'path': str(files),
                        'size': files.stat().st_size,
                        'content_preview': content[:500] + "..." if len(content) > 500 else content
                    }
                    print(f"✅ Found {build_type}: {files.name}")
                else:
                    build_analysis[build_type] = {'exists': False}
                    print(f"❌ {build_type}: Not found")
        
        # Check for database inclusion in build specs
        database_inclusion_analysis = self.AnalyzeDatabaseInclusion(build_analysis)
        build_analysis['database_inclusion'] = database_inclusion_analysis
        
        self.diagnostics['build_analysis'] = build_analysis
    
    def AnalyzeDatabaseInclusion(self, build_analysis: Dict) -> Dict[str, Any]:
        """Analyze how databases are included in build process"""
        inclusion_analysis = {
            'placeholder_db_found': False,
            'full_db_inclusion': False,
            'google_drive_sync_logic': False,
            'startup_database_check': False
        }
        
        # Check PyInstaller specs
        for spec_info in build_analysis.get('pyinstaller_spec', []):
            content = spec_info.get('content_preview', '')
            if 'MyLibrary.db' in content:
                inclusion_analysis['placeholder_db_found'] = True
            if 'DriveManager' in content or 'GoogleDriveAPI' in content:
                inclusion_analysis['google_drive_sync_logic'] = True
        
        # Check build scripts
        for script_info in build_analysis.get('build_scripts', []):
            content = script_info.get('content_preview', '')
            if 'database' in content.lower():
                inclusion_analysis['full_db_inclusion'] = True
        
        return inclusion_analysis
    
    def AnalyzeAuthentication(self):
        """Analyze Google Drive authentication setup"""
        print("📊 Analyzing Authentication Setup...")
        
        auth_analysis = {
            'credentials_file_exists': False,
            'token_file_exists': False,
            'oauth_config_exists': False,
            'drive_api_accessible': False,
            'authentication_test': None
        }
        
        # Check credential files
        creds_path = self.project_root / "Config" / "google_credentials.json"
        token_path = self.project_root / "Config" / "google_token.json"
        oauth_path = self.project_root / "Config" / "oauth_security_config.json"
        
        auth_analysis['credentials_file_exists'] = creds_path.exists()
        auth_analysis['token_file_exists'] = token_path.exists()
        auth_analysis['oauth_config_exists'] = oauth_path.exists()
        
        # Test authentication (safely)
        try:
            sys.path.insert(0, str(self.project_root / "Source"))
            from API.GoogleDriveAPI import GoogleDriveAPI
            
            if creds_path.exists():
                api = GoogleDriveAPI(str(creds_path))
                # Don't actually authenticate, just check if class can be instantiated
                auth_analysis['drive_api_accessible'] = True
                auth_analysis['authentication_test'] = "API class accessible"
            
        except Exception as e:
            auth_analysis['authentication_test'] = f"Error: {e}"
        
        print(f"✅ Credentials: {'Found' if auth_analysis['credentials_file_exists'] else 'Missing'}")
        print(f"✅ Token: {'Found' if auth_analysis['token_file_exists'] else 'Missing'}")
        print(f"✅ OAuth Config: {'Found' if auth_analysis['oauth_config_exists'] else 'Missing'}")
        
        self.diagnostics['auth_analysis'] = auth_analysis
    
    def AnalyzePaths(self):
        """Analyze path configurations and mappings"""
        print("📊 Analyzing Path Configurations...")
        
        path_analysis = {
            'config_paths': {},
            'actual_paths': {},
            'path_mismatches': [],
            'temp_vs_main_paths': {}
        }
        
        # Expected paths from config
        config_path = self.project_root / "Config" / "andygoogle_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            path_analysis['config_paths'] = {
                'google_credentials_path': config.get('google_credentials_path'),
                'local_database_path': config.get('local_database_path'),
                'backup_database_path': config.get('backup_database_path')
            }
        
        # Actual paths found
        path_analysis['actual_paths'] = {
            'main_database': str(self.project_root / "Data" / "Databases" / "MyLibrary.db"),
            'temp_database': str(self.temp_dir / "_MEI68922" / "Data" / "MyLibrary.db") if self.temp_dir else None,
            'credentials': str(self.project_root / "Config" / "google_credentials.json"),
            'token': str(self.project_root / "Config" / "google_token.json")
        }
        
        # Path mismatches
        if self.temp_dir:
            main_db_size = (self.project_root / "Data" / "Databases" / "MyLibrary.db").stat().st_size
            temp_db_path = self.temp_dir / "_MEI68922" / "Data" / "MyLibrary.db"
            temp_db_size = temp_db_path.stat().st_size if temp_db_path.exists() else 0
            
            path_analysis['temp_vs_main_paths'] = {
                'main_db_size': main_db_size,
                'temp_db_size': temp_db_size,
                'size_ratio': temp_db_size / main_db_size if main_db_size > 0 else 0
            }
            
            if temp_db_size < main_db_size * 0.1:  # Less than 10% of main size
                path_analysis['path_mismatches'].append("Temp database significantly smaller than main database")
        
        self.diagnostics['path_analysis'] = path_analysis
        print(f"✅ Path analysis completed, {len(path_analysis['path_mismatches'])} mismatches found")
    
    def GenerateRecommendations(self):
        """Generate specific recommendations based on analysis"""
        print("💡 Generating Recommendations...")
        
        recommendations = []
        
        # Database size mismatch
        db_analysis = self.diagnostics['database_analysis']
        main_db = db_analysis.get('main_database', {})
        temp_db = db_analysis.get('temp_database', {})
        
        if main_db.get('record_count', 0) > temp_db.get('record_count', 0) * 10:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Database Sync',
                'issue': 'Windows executable using placeholder database',
                'recommendation': 'Modify Windows build to call DriveManager.InitializeDatabase() on startup',
                'code_location': 'StartAndyGoogle.py or main startup file',
                'specific_action': 'Add database sync check before server startup'
            })
        
        # Missing authentication
        auth_analysis = self.diagnostics['auth_analysis']
        if not auth_analysis['credentials_file_exists']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Authentication',
                'issue': 'Google credentials file missing',
                'recommendation': 'Ensure google_credentials.json is bundled with Windows executable',
                'code_location': 'PyInstaller spec file',
                'specific_action': 'Add credentials file to --add-data parameter'
            })
        
        # Build process issues
        build_analysis = self.diagnostics['build_analysis']
        db_inclusion = build_analysis.get('database_inclusion', {})
        
        if db_inclusion.get('placeholder_db_found') and not db_inclusion.get('google_drive_sync_logic'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Build Process',
                'issue': 'Placeholder database bundled without sync logic',
                'recommendation': 'Remove placeholder database from build, add startup sync check',
                'code_location': 'PyInstaller spec and startup logic',
                'specific_action': 'Remove DB from spec, add InitializeDatabase() call'
            })
        
        # Path configuration issues
        path_analysis = self.diagnostics['path_analysis']
        if path_analysis['path_mismatches']:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Configuration',
                'issue': 'Path configuration mismatches detected',
                'recommendation': 'Review and align path configurations between environments',
                'code_location': 'Config/andygoogle_config.json',
                'specific_action': 'Update paths to work in both development and Windows executable'
            })
        
        # General startup sequence
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Startup Sequence',
            'issue': 'Missing database initialization check',
            'recommendation': 'Add comprehensive database check on application startup',
            'code_location': 'StartAndyGoogle.py',
            'specific_action': 'Implement startup database validation and sync logic'
        })
        
        self.diagnostics['recommendations'] = recommendations
        print(f"✅ Generated {len(recommendations)} recommendations")
    
    def CalculateFileHash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "Error calculating hash"
    
    def ReadFileContent(self, file_path: Path) -> str:
        """Safely read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return "Binary file or encoding error"
        except Exception as e:
            return f"Error reading file: {e}"
    
    def SaveDiagnostics(self):
        """Save complete diagnostics to file"""
        output_file = self.project_root / "Scripts" / f"WindowsDatabaseDiagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.diagnostics, f, indent=2, default=str)
            print(f"✅ Diagnostics saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving diagnostics: {e}")
    
    def PrintSummaryReport(self):
        """Print a concise summary report"""
        print("\n" + "=" * 60)
        print("📋 WINDOWS DATABASE SYNC DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        # Critical Issues
        print("\n🚨 CRITICAL ISSUES:")
        db_analysis = self.diagnostics['database_analysis']
        main_records = db_analysis.get('main_database', {}).get('record_count', 0)
        temp_records = db_analysis.get('temp_database', {}).get('record_count', 0)
        
        if main_records > temp_records * 10:
            print(f"   • Database sync failure: Main DB has {main_records} records, Windows has {temp_records}")
        
        auth_analysis = self.diagnostics['auth_analysis']
        if not auth_analysis['credentials_file_exists']:
            print("   • Missing Google credentials file")
        
        # High Priority Recommendations
        print("\n💡 HIGH PRIORITY FIXES:")
        for rec in self.diagnostics['recommendations']:
            if rec['priority'] == 'HIGH':
                print(f"   • {rec['category']}: {rec['recommendation']}")
        
        # System Status
        print(f"\n📊 SYSTEM STATUS:")
        print(f"   • Platform: {self.diagnostics['system_info']['platform']}")
        print(f"   • Temp Directory: {'Found' if self.temp_dir else 'Not Found'}")
        print(f"   • Main Database: {main_records} records")
        print(f"   • Windows Database: {temp_records} records")
        print(f"   • Google Credentials: {'Present' if auth_analysis['credentials_file_exists'] else 'Missing'}")
        
        print("\n" + "=" * 60)

def main():
    """Run complete Windows database diagnostics"""
    diagnostics = WindowsDatabaseDiagnostics()
    result = diagnostics.RunCompleteDiagnostics()
    diagnostics.PrintSummaryReport()
    
    return result

if __name__ == "__main__":
    main()