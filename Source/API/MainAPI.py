# File: MainAPI.py
# Path: AndyGoogle/Source/API/MainAPI.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-12
# Last Modified: 2025-07-24 07:15AM
"""
Description: FastAPI main server for AndyGoogle with Google Drive integration
Provides RESTful API endpoints for library management with cloud synchronization
"""

import os
import sys
import sqlite3
import time
import platform
import requests
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Core.DriveManager import DriveManager
except ImportError:
    DriveManager = None
    print("⚠️ DriveManager not available - Google Drive functionality disabled")

try:
    from Utils.SheetsLogger import SheetsLogger  
except ImportError:
    SheetsLogger = None
    print("⚠️ SheetsLogger not available - logging to sheets disabled")

try:
    from Core.StudentBookDownloader import StudentBookDownloader, StudentRegion
except ImportError:
    StudentBookDownloader = None
    print("⚠️ StudentBookDownloader not available - book download functionality disabled")

# FastAPI app instance
app = FastAPI(
    title="AndyGoogle Library API",
    description="""
    **Cloud-synchronized digital library management system**
    
    ## Features
    - 📚 **Book Management**: Search, filter, and browse your digital library
    - 🌐 **Google Drive Sync**: Seamless cloud synchronization 
    - 🔍 **Smart Search**: Full-text search across titles and metadata
    - 📱 **Multi-mode**: LOCAL (offline) or GDRIVE (cloud sync)
    - 🚀 **High Performance**: Optimized database queries with indexing
    - 🛡️ **Robust**: Auto-recovery and graceful error handling
    
    ## Quick Start
    1. **Local Mode**: `python StartAndyGoogle.py --mode local`
    2. **Google Drive**: `python StartAndyGoogle.py --mode gdrive`
    3. **Stable Mode**: `python RunStableMode.py --mode gdrive`
    
    ## API Status
    - Health check: `/api/health`
    - Current mode: `/api/mode`  
    - Library stats: `/api/stats`
    """,
    version="1.0.0",
    contact={
        "name": "AndyLibrary Support",
        "url": "https://github.com/your-repo/andylibrary"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Global managers (initialized on startup)
drive_manager = None
sheets_logger = None


# Pydantic models for API requests/responses
class BookResponse(BaseModel):
    id: int
    title: str
    author: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    rating: Optional[int] = None
    last_opened: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    category: str

class SubjectResponse(BaseModel):
    id: int
    subject: str
    category_id: Optional[int] = None

class StatsResponse(BaseModel):
    total_books: int
    total_categories: int
    total_subjects: int
    database_version: str
    last_sync: Optional[str] = None
    offline_mode: bool

class SyncStatusResponse(BaseModel):
    local_database_exists: bool
    local_version: str
    last_sync: Optional[str] = None
    record_count: int
    sync_status: str
    offline_mode: bool

# Student book download models
class BookCostResponse(BaseModel):
    book_id: int
    title: str
    file_size_mb: float
    estimated_cost_usd: float
    warning_level: str
    budget_percentage: float

class DownloadOptionsResponse(BaseModel):
    book_info: dict
    download_options: list
    cost_warnings: list
    student_guidance: dict

class BudgetSummaryResponse(BaseModel):
    month: str
    total_spent: float
    remaining_budget: float
    budget_used_percentage: float
    downloads_count: int
    budget_status: str

# Dependency to get database connection
def get_database():
    """Get SQLite database connection with enhanced error handling"""
    try:
        # Use direct path when drive_manager is not available
        if drive_manager:
            print("🔍 Using DriveManager database path")
            db_path = drive_manager.local_db_path
        else:
            # Check for temp database path from environment (for testing)
            temp_db_path = os.environ.get('ANDYGOOGLE_TEMP_DB')
            if temp_db_path and os.path.exists(temp_db_path):
                print(f"🔍 Using temp database from environment: {temp_db_path}")
                db_path = temp_db_path
            else:
                print("🔍 Using fallback local database path")
                # Use absolute path to ensure it works regardless of working directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        print(f"🔍 Database path resolved to: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {db_path}")
            raise HTTPException(status_code=503, detail="Database not available - sync required")
        
        print(f"🔗 Connecting to database at: {db_path}")
        # Use check_same_thread=False to allow SQLite to work with FastAPI's threading
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        print("✅ Database connection established")
        yield conn
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
    finally:
        try:
            if 'conn' in locals():
                conn.close()
                print("🔒 Database connection closed")
        except Exception as e:
            print(f"⚠️ Error closing database connection: {e}")

async def optimize_database_indexes():
    """Optimize database indexes for better query performance"""
    try:
        # Get database connection
        db_gen = get_database()
        conn = next(db_gen)
        
        try:
            # Create performance indexes if they don't exist
            optimization_queries = [
                # Books table optimizations
                "CREATE INDEX IF NOT EXISTS idx_books_title_search ON books (title COLLATE NOCASE)",
                "CREATE INDEX IF NOT EXISTS idx_books_category_subject ON books (category_id, subject_id)",
                "CREATE INDEX IF NOT EXISTS idx_books_title_category ON books (title, category_id)",
                
                # Categories table optimization
                "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (category COLLATE NOCASE)",
                
                # Subjects table optimization  
                "CREATE INDEX IF NOT EXISTS idx_subjects_name_category ON subjects (subject COLLATE NOCASE, category_id)",
                "CREATE INDEX IF NOT EXISTS idx_subjects_category ON subjects (category_id)",
                
                # Analyze tables for query planner optimization
                "ANALYZE books",
                "ANALYZE categories", 
                "ANALYZE subjects"
            ]
            
            for query in optimization_queries:
                try:
                    conn.execute(query)
                except Exception as e:
                    print(f"⚠️ Index optimization warning: {e}")
            
            conn.commit()
            print("✅ Database indexes optimized for performance")
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ Database optimization failed: {e}")

# Dependency to log API usage
def log_api_usage(request: Request, action: str, details: str = None):
    """Log API usage to Google Sheets"""
    if sheets_logger:
        try:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            sheets_logger.LogUsage(
                action=action,
                action_details=details or "",
                client_ip=client_ip,
                user_agent=user_agent,
                session_id=f"api_{int(datetime.now().timestamp())}"
            )
        except Exception as e:
            print(f"Warning: Failed to log API usage: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize AndyGoogle components on startup"""
    global drive_manager, sheets_logger
    
    print("🚀 Starting AndyGoogle API server...")
    
    # Check operating mode from environment
    mode = os.environ.get('ANDYGOOGLE_MODE', 'local')
    
    if mode == 'gdrive':
        print("🌐 GOOGLE DRIVE MODE - Initializing Drive integration...")
        try:
            from Core.DriveManager import DriveManager
            from Utils.SheetsLogger import SheetsLogger
            
            # Use proper config paths
            config_path = "Config/andygoogle_config.json"
            creds_path = "Config/google_credentials.json"
            
            print(f"🔍 Initializing DriveManager with config: {config_path}")
            
            # Initialize DriveManager with enhanced error handling
            drive_manager = DriveManager(config_path)
            
            # Validate DriveManager functionality
            if hasattr(drive_manager, 'local_db_path'):
                print(f"🔍 DriveManager local_db_path: {drive_manager.local_db_path}")
                db_path_valid = True
            else:
                print("⚠️ DriveManager missing local_db_path attribute")
                db_path_valid = False
            
            # Test Google Drive connectivity (non-blocking)
            try:
                if hasattr(drive_manager, 'TestConnection'):
                    connection_status = drive_manager.TestConnection()
                    if connection_status:
                        print("✅ Google Drive connection test successful")
                    else:
                        print("⚠️ Google Drive connection test failed - will work offline")
                else:
                    print("ℹ️ Connection test not available - assuming connected")
            except Exception as conn_error:
                print(f"⚠️ Google Drive connection test error: {conn_error}")
                print("ℹ️ Will continue in offline mode")
            
            # Initialize SheetsLogger with error handling
            try:
                print(f"🔍 Initializing SheetsLogger with creds: {creds_path}")
                sheets_logger = SheetsLogger(creds_path)
                print("✅ SheetsLogger initialized successfully")
            except Exception as sheets_error:
                print(f"⚠️ SheetsLogger initialization failed: {sheets_error}")
                print("ℹ️ Continuing without sheets logging")
                sheets_logger = None
            
            # Validate database access through DriveManager
            if drive_manager and db_path_valid:
                test_db_path = drive_manager.local_db_path
                if os.path.exists(test_db_path):
                    print(f"✅ Database accessible at: {test_db_path}")
                    
                    # Test database connectivity
                    try:
                        conn = sqlite3.connect(test_db_path, check_same_thread=False)
                        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
                        conn.close()
                        print(f"✅ Database validation successful - {count} books found")
                    except Exception as db_error:
                        print(f"⚠️ Database validation warning: {db_error}")
                        
                else:
                    print(f"⚠️ Database not found at DriveManager path: {test_db_path}")
                    print("📊 Will attempt to sync from Google Drive or fallback to local")
            
            print("✅ Google Drive integration enabled successfully")
            print("📊 Database ready with Google Drive sync capabilities")
        except Exception as e:
            print(f"⚠️ Google Drive initialization failed: {e}")
            print("📊 Falling back to local SQLite mode")
            drive_manager = None
            sheets_logger = None
            
            # Force environment to local mode to prevent further issues
            os.environ['ANDYGOOGLE_MODE'] = 'local'
            print("🔄 Environment mode switched to LOCAL for stability")
    else:
        print("💾 LOCAL MODE - Using local SQLite database only")
        print("📊 Database ready with local SQLite file")
    
    # Optimize database indexes for better performance
    await optimize_database_indexes()
    
    print("✅ AndyGoogle API server started successfully")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/mode")
async def get_mode():
    """Get current operating mode with enhanced sync status"""
    mode = os.environ.get('ANDYGOOGLE_MODE', 'local')
    
    # Base mode info
    mode_info = {
        "mode": mode,
        "display_name": "LOCAL (Memorex)" if mode == 'local' else "GOOGLE DRIVE",
        "icon": "💾" if mode == 'local' else "🌐",
        "description": "Local SQLite database only" if mode == 'local' else "Google Drive synchronized"
    }
    
    # Enhanced sync status for Google Drive mode
    if mode == 'gdrive' and drive_manager:
        try:
            # Get detailed sync status
            sync_status = drive_manager.GetSyncStatus() if hasattr(drive_manager, 'GetSyncStatus') else {}
            
            mode_info.update({
                "sync_enabled": True,
                "last_sync": sync_status.get('last_sync', 'Never'),
                "sync_status": sync_status.get('sync_status', 'Unknown'),
                "local_version": sync_status.get('local_version', '1.0.0'),
                "remote_version": sync_status.get('remote_version', '1.0.0'),
                "offline_mode": sync_status.get('offline_mode', False),
                "connection_status": "Connected" if not sync_status.get('offline_mode', True) else "Offline"
            })
            
            # Update icon based on sync status
            if sync_status.get('offline_mode', True):
                mode_info["icon"] = "🔄"  # Syncing/offline
                mode_info["display_name"] = "GOOGLE DRIVE (Offline)"
            elif sync_status.get('sync_status') == 'up_to_date':
                mode_info["icon"] = "✅"  # Up to date
                mode_info["display_name"] = "GOOGLE DRIVE (Synced)"
            else:
                mode_info["icon"] = "🌐"  # Connected but not synced
                
        except Exception as e:
            print(f"⚠️ Error getting sync status: {e}")
            mode_info.update({
                "sync_enabled": False,
                "sync_error": str(e),
                "connection_status": "Error"
            })
    else:
        mode_info.update({
            "sync_enabled": False,
            "connection_status": "Local Only"
        })
    
    return mode_info

# Database download endpoint for users
@app.get("/api/database/download")
async def download_database(request: Request):
    """Download the current database file for users"""
    log_api_usage(request, "database_download")
    
    try:
        # Determine database path based on mode
        if drive_manager and hasattr(drive_manager, 'local_db_path'):
            db_path = drive_manager.local_db_path
        else:
            # Fallback to local database
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail="Database file not found")
        
        # Get file info
        file_size = os.path.getsize(db_path)
        file_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        # Create download filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_filename = f"andylibrary_{timestamp}.db"
        
        # Log download start for analytics
        start_time = time.time()
        size_mb = file_size / 1024 / 1024
        
        if sheets_logger:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            version = f"{int(os.path.getmtime(db_path))}.{file_size}"
            
            sheets_logger.LogDatabaseDownload(
                client_ip=client_ip,
                user_agent=user_agent,
                version=version,
                size_mb=size_mb,
                duration_seconds=0,  # Will be updated later if needed
                success=True
            )
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=db_path,
            filename=download_filename,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}",
                "X-File-Size": str(file_size),
                "X-Last-Modified": file_modified.isoformat(),
                "X-Database-Version": "1.0.0",
                "X-Estimated-Cost": f"${size_mb * 0.10:.2f}"
            }
        )
        
    except Exception as e:
        print(f"❌ Database download error: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Lightweight database version check endpoint  
@app.get("/api/database/version")
async def get_database_version(request: Request):
    """Get lightweight database version info for smart updates (< 1KB response)"""
    log_api_usage(request, "version_check")
    
    try:
        # Get database path
        if drive_manager and hasattr(drive_manager, 'local_db_path'):
            db_path = drive_manager.local_db_path
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        if not os.path.exists(db_path):
            return {
                "version": "0.0",
                "size_mb": 0,
                "book_count": 0,
                "available": False,
                "message": "Database not available"
            }
        
        # Get file stats (lightweight)
        file_size = os.path.getsize(db_path)
        file_mtime = int(os.path.getmtime(db_path))
        
        # Quick book count (minimal DB access)
        conn = sqlite3.connect(db_path)
        book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        conn.close()
        
        # Create version string: timestamp.bookcount
        version = f"{file_mtime}.{book_count}"
        
        result = {
            "version": version,
            "size_mb": round(file_size / 1024 / 1024, 1),
            "book_count": book_count,
            "available": True,
            "download_url": "/api/database/download"
        }
        
        # Log version check for analytics
        if sheets_logger:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            sheets_logger.LogVersionCheck(
                client_ip=client_ip,
                user_agent=user_agent,
                current_version="unknown",  # Client would send this
                server_version=version,
                update_available=True  # Assume update available for version checks
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Version check failed: {e}")

# Database info endpoint
@app.get("/api/database/info")
async def get_database_info(request: Request):
    """Get database information without downloading"""
    log_api_usage(request, "database_info")
    
    try:
        # Get database path
        if drive_manager and hasattr(drive_manager, 'local_db_path'):
            db_path = drive_manager.local_db_path
            db_source = "Google Drive (cached locally)"
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
            db_source = "Local SQLite file"
        
        if not os.path.exists(db_path):
            return {"available": False, "error": "Database file not found"}
        
        # Get file statistics
        file_size = os.path.getsize(db_path)
        file_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        # Get database content statistics
        conn = sqlite3.connect(db_path, check_same_thread=False)
        try:
            book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] 
            subject_count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        finally:
            conn.close()
        
        return {
            "available": True,
            "source": db_source,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "last_modified": file_modified.isoformat(),
            "total_books": book_count,
            "total_categories": category_count,
            "total_subjects": subject_count,
            "database_version": "1.0.0",
            "download_url": "/api/database/download"
        }
        
    except Exception as e:
        print(f"❌ Database info error: {e}")
        return {"available": False, "error": str(e)}

# Google Drive sync trigger endpoint  
@app.post("/api/database/sync")
async def trigger_database_sync(request: Request, background_tasks: BackgroundTasks):
    """Manually trigger database sync from Google Drive"""
    log_api_usage(request, "manual_database_sync")
    
    if not drive_manager:
        raise HTTPException(status_code=400, detail="Google Drive mode not available")
    
    try:
        # Add sync task to background
        background_tasks.add_task(sync_database_task)
        
        return {
            "message": "Database sync initiated",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Sync trigger error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

async def sync_database_task():
    """Background task for database synchronization"""
    try:
        if drive_manager and hasattr(drive_manager, 'SyncDatabaseFromDrive'):
            print("🔄 Starting background database sync...")
            result = drive_manager.SyncDatabaseFromDrive(force_update=True)
            
            if result:
                print("✅ Database sync completed successfully")
            else:
                print("⚠️ Database sync completed with warnings")
        else:
            print("❌ DriveManager not available for sync")
            
    except Exception as e:
        print(f"❌ Background sync error: {e}")

# Debug database endpoint
@app.get("/api/debug/db")
async def debug_database():
    """Debug database connection"""
    try:
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        if not os.path.exists(db_path):
            return {"error": f"Database not found at: {db_path}"}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT COUNT(*) as count FROM categories")
        result = cursor.fetchone()
        conn.close()
        
        return {
            "status": "success",
            "db_path": db_path,
            "categories_count": result[0] if result else 0
        }
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

# Sync status endpoint
@app.get("/api/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(request: Request):
    """Get database synchronization status"""
    log_api_usage(request, "sync_status_check")
    
    if not drive_manager:
        raise HTTPException(status_code=500, detail="Drive manager not available")
    
    status = drive_manager.GetSyncStatus()
    return SyncStatusResponse(**status)

# Manual sync endpoint
@app.post("/api/sync/database")
async def sync_database(request: Request, background_tasks: BackgroundTasks):
    """Manually trigger database sync from Google Drive"""
    log_api_usage(request, "manual_sync_requested")
    
    if not drive_manager:
        raise HTTPException(status_code=500, detail="Drive manager not available")
    
    # Run sync in background
    background_tasks.add_task(drive_manager.SyncDatabaseFromDrive, True)
    
    return {
        "status": "sync_started",
        "message": "Database sync initiated in background",
        "timestamp": datetime.now().isoformat()
    }

# Check for updates endpoint
@app.get("/api/sync/updates")
async def check_for_updates(request: Request):
    """Check if database updates are available"""
    log_api_usage(request, "update_check")
    
    if not drive_manager:
        raise HTTPException(status_code=500, detail="Drive manager not available")
    
    update_info = drive_manager.CheckForUpdates()
    return update_info

# Books endpoints
@app.get("/api/books")
async def get_books(
    request: Request,
    limit: int = 50, 
    offset: int = 0, 
    search: Optional[str] = None,
    category: Optional[str] = None,
    subject: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_database)
):
    """Get paginated list of books with optional filtering"""
    print(f"🔍 API CALL: /api/books - limit={limit}, offset={offset}, search='{search}', category='{category}', subject='{subject}'")
    log_api_usage(request, "books_list", f"limit={limit}, offset={offset}, search={search}")
    
    # Build optimized query with proper JOINs and indexing
    query = """
        SELECT b.id, b.title, 
               NULL as author, c.category, s.subject, 
               NULL as file_path, NULL as file_size, 
               NULL as page_count, NULL as rating,
               NULL as last_opened
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN subjects s ON b.subject_id = s.id
        WHERE 1=1
    """
    
    params = []
    
    # Add search filter with index optimization
    if search:
        # Use proper indexing for LIKE queries
        query += " AND (b.title LIKE ? OR b.title LIKE ?)"
        search_param = f"%{search}%"
        search_param_start = f"{search}%"  # More index-friendly
        params.extend([search_param, search_param_start])
    
    # Add category filter using efficient foreign key join
    if category:
        query += " AND c.category = ?"
        params.append(category)
    
    # Add subject filter using efficient foreign key join
    if subject:
        query += " AND s.subject = ?"
        params.append(subject)
    
    # Add optimized pagination with covering index
    query += " ORDER BY b.title LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    
    books = []
    for row in rows:
        books.append(BookResponse(
            id=row['id'],
            title=row['title'],
            author=row['author'],
            category=row['category'],
            subject=row['subject'],
            file_path=row['file_path'],
            file_size=row['file_size'],
            page_count=row['page_count'],
            rating=row['rating'],
            last_opened=row['last_opened']
        ))
    
    # Return format expected by frontend
    return {
        "books": books,
        "total": len(books),
        "page": (offset // limit) + 1,
        "limit": limit
    }

# Books filter endpoint (alias for compatibility)
@app.get("/api/books/filter")
async def filter_books(
    request: Request,
    category: Optional[str] = None,
    subject: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: sqlite3.Connection = Depends(get_database)
):
    """Filter books by category, subject, or search term"""
    print(f"🔍 API CALL: /api/books/filter - category='{category}', subject='{subject}', search='{search}', page={page}, limit={limit}")
    offset = (page - 1) * limit
    return await get_books(request, limit, offset, search, category, subject, db)

# Books search endpoint (POST for compatibility)
@app.post("/api/books/search")
async def search_books(
    request: Request,
    search_data: dict,
    db: sqlite3.Connection = Depends(get_database)
):
    """Search books via POST request"""
    print(f"🔍 API CALL: /api/books/search - POST data: {search_data}")
    # Frontend sends 'query' not 'search'
    search_term = search_data.get('query', search_data.get('search', ''))
    filters = search_data.get('filters', {})
    category = filters.get('category')
    subject = filters.get('subject')
    page = search_data.get('page', 1)
    limit = search_data.get('limit', 50)
    
    print(f"🔍 PARSED: search_term='{search_term}', category='{category}', subject='{subject}', page={page}, limit={limit}")
    offset = (page - 1) * limit
    return await get_books(request, limit, offset, search_term, category, subject, db)

@app.get("/api/books/{book_id}", response_model=BookResponse)
async def get_book(request: Request, book_id: int, db: sqlite3.Connection = Depends(get_database)):
    """Get detailed information about a specific book"""
    log_api_usage(request, "book_detail", f"book_id={book_id}")
    
    query = """
        SELECT b.id, b.title, b.author, c.category, s.subject, 
               b.FilePath as file_path, b.FileSize as file_size, 
               b.PageCount as page_count, b.Rating as rating,
               b.LastOpened as last_opened
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN subjects s ON b.subject_id = s.id
        WHERE b.id = ?
    """
    
    cursor = db.execute(query, (book_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return BookResponse(
        id=row['id'],
        title=row['title'],
        author=row['author'],
        category=row['category'],
        subject=row['subject'],
        file_path=row['file_path'],
        file_size=row['file_size'],
        page_count=row['page_count'],
        rating=row['rating'],
        last_opened=row['last_opened']
    )

@app.get("/api/books/{book_id}/thumbnail")
async def get_book_thumbnail(request: Request, book_id: int, db: sqlite3.Connection = Depends(get_database)):
    """Get book thumbnail image"""
    log_api_usage(request, "thumbnail_view", f"book_id={book_id}")
    
    try:
        # First check if book exists
        cursor = db.execute("SELECT id FROM books WHERE id = ?", (book_id,))
        book_exists = cursor.fetchone()
        
        if not book_exists:
            from fastapi import Response
            return Response(status_code=404, content="Book not found")
        
        # Check if ThumbnailImage column exists in schema
        cursor = db.execute("PRAGMA table_info(books)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'ThumbnailImage' not in columns:
            # Column doesn't exist - return 204 No Content
            from fastapi import Response
            return Response(status_code=204)
        
        # Try to get thumbnail
        cursor = db.execute("SELECT ThumbnailImage FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            # No thumbnail available - return 204 No Content  
            from fastapi import Response
            return Response(status_code=204)
        
        # Return the image blob with proper content type
        from fastapi import Response
        return Response(
            content=row[0],
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except Exception as e:
        print(f"Thumbnail error for book {book_id}: {e}")
        # Return 204 instead of 500 for graceful degradation
        from fastapi import Response
        return Response(status_code=204)

# Categories endpoint
@app.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories(request: Request, db: sqlite3.Connection = Depends(get_database)):
    """Get all categories"""
    log_api_usage(request, "categories_list")
    
    cursor = db.execute("SELECT id, category FROM categories ORDER BY category")
    rows = cursor.fetchall()
    
    return [CategoryResponse(id=row['id'], category=row['category']) for row in rows]

# Subjects endpoint
@app.get("/api/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    request: Request, 
    category_id: Optional[int] = None,
    category: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_database)
):
    """Get subjects, optionally filtered by category ID or category name"""
    log_api_usage(request, "subjects_list", f"category_id={category_id}, category={category}")
    
    if category:
        # Filter by category name (what frontend sends)
        query = """
            SELECT s.id, s.subject, s.category_id 
            FROM subjects s 
            JOIN categories c ON s.category_id = c.id 
            WHERE c.category = ? 
            ORDER BY s.subject
        """
        params = (category,)
    elif category_id:
        # Filter by category ID (legacy support)
        query = "SELECT id, subject, category_id FROM subjects WHERE category_id = ? ORDER BY subject"
        params = (category_id,)
    else:
        # Get all subjects
        query = "SELECT id, subject, category_id FROM subjects ORDER BY subject"
        params = ()
    
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    
    return [
        SubjectResponse(id=row['id'], subject=row['subject'], category_id=row['category_id']) 
        for row in rows
    ]

# Statistics endpoint
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(request: Request, db: sqlite3.Connection = Depends(get_database)):
    """Get library statistics"""
    log_api_usage(request, "stats_view")
    
    # Get counts
    book_count = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    category_count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    subject_count = db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    
    # Get sync info
    sync_status = drive_manager.GetSyncStatus() if drive_manager else {}
    
    return StatsResponse(
        total_books=book_count,
        total_categories=category_count,
        total_subjects=subject_count,
        database_version=sync_status.get('local_version', '0.0.0'),
        last_sync=sync_status.get('last_sync'),
        offline_mode=sync_status.get('offline_mode', False)
    )

@app.get("/api/performance/assessment")
async def get_performance_assessment():
    """Get user's system performance assessment and recommendations"""
    try:
        # Quick network test
        start_time = time.time()
        try:
            response = requests.get("https://www.google.com/favicon.ico", timeout=5)
            network_time = time.time() - start_time
            network_speed = (len(response.content) * 8) / (network_time * 1000000) if network_time > 0 else 1
        except:
            network_speed = 1  # Conservative estimate
        
        # Hardware detection
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        
        # Classification
        if network_speed >= 20:
            network_class = "fast"
        elif network_speed >= 10:
            network_class = "medium"
        elif network_speed >= 5:
            network_class = "slow"
        else:
            network_class = "very_slow"
        
        if memory_gb >= 8 and cpu_count >= 4:
            hardware_class = "modern"
        elif memory_gb >= 4 and cpu_count >= 2:
            hardware_class = "budget"
        else:
            hardware_class = "limited"
        
        # Performance prediction (10MB database)
        download_speed_mbps = network_speed * 0.8
        download_time = (10.3 * 8) / download_speed_mbps if download_speed_mbps > 0 else 60
        
        processing_times = {"modern": 0.002, "budget": 0.005, "limited": 0.010}
        processing_time = processing_times.get(hardware_class, 0.005)
        
        total_time = download_time + processing_time
        
        # Generate recommendations
        recommendations = []
        
        if total_time > 30:
            recommendations.append({
                "type": "warning",
                "title": "Slow Connection Detected", 
                "message": f"Download will take ~{total_time:.0f}s. Consider progressive loading.",
                "action": "progressive_loading"
            })
        elif total_time > 15:
            recommendations.append({
                "type": "caution",
                "title": "Moderate Wait Time",
                "message": f"Download will take ~{total_time:.0f}s. Progress indicator recommended.",
                "action": "show_progress"
            })
        else:
            recommendations.append({
                "type": "success",
                "title": "Fast Connection",
                "message": f"Download will complete quickly (~{total_time:.0f}s).",
                "action": "standard_download"
            })
        
        if network_class == "very_slow":
            recommendations.append({
                "type": "error",
                "title": "Very Slow Network",
                "message": "Consider lite mode or off-peak download.",
                "action": "lite_mode"
            })
        
        if memory_available_gb < 1:
            recommendations.append({
                "type": "warning",
                "title": "Low Memory",
                "message": f"Only {memory_available_gb:.1f}GB available. Use disk caching.",
                "action": "disk_cache"
            })
        
        # Optimal strategy
        if memory_available_gb >= 1 and hardware_class in ['modern', 'budget']:
            strategy = "python_cache"
            strategy_reason = "Python dict caching - optimal for your hardware"
        elif memory_available_gb >= 0.5:
            strategy = "memory_db"
            strategy_reason = "In-memory SQLite - good balance"
        else:
            strategy = "disk_optimized"
            strategy_reason = "Optimized disk access - conserves memory"
        
        return {
            "system": {
                "network_speed_mbps": round(network_speed, 1),
                "network_class": network_class,
                "hardware_class": hardware_class,
                "cpu_cores": cpu_count,
                "memory_gb": round(memory_gb, 1),
                "memory_available_gb": round(memory_available_gb, 1),
                "platform": platform.system()
            },
            "performance_prediction": {
                "download_time_seconds": round(download_time, 1),
                "processing_time_seconds": round(processing_time, 3),
                "total_wait_seconds": round(total_time, 1),
                "memory_usage_mb": round(10.3 * 0.15, 1)
            },
            "recommendations": recommendations,
            "optimal_strategy": {
                "strategy": strategy,
                "reason": strategy_reason,
                "estimated_query_time": "0.0001s" if strategy == "python_cache" else "0.001s"
            },
            "user_experience": {
                "rating": "excellent" if total_time <= 10 else "good" if total_time <= 30 else "slow",
                "advice": "Full download recommended" if total_time <= 10 else 
                        "Standard download with progress" if total_time <= 30 else 
                        "Progressive loading recommended"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance assessment failed: {e}")

@app.get("/api/analytics/data-usage")
async def get_data_usage_analytics(request: Request, days: int = 30):
    """Get data usage analytics for educational mission insights"""
    log_api_usage(request, "data_usage_analytics")
    
    try:
        if not sheets_logger:
            return {"error": "Analytics not available - logging disabled"}
        
        # Get data usage analytics
        analytics = sheets_logger.GetDataUsageAnalytics(days)
        
        if not analytics:
            return {
                "period_days": days,
                "message": "No data usage data available",
                "recommendations": [
                    "Enable logging to track data usage patterns",
                    "Monitor user download behavior for cost optimization"
                ]
            }
        
        # Add mission-focused insights
        insights = []
        
        if analytics['data_protection_enabled']:
            insights.append({
                "type": "success",
                "message": f"Version control is protecting users - {analytics['efficiency_ratio']:.1f}x more checks than downloads",
                "impact": "Significant data cost savings for students"
            })
        else:
            insights.append({
                "type": "warning", 
                "message": "Users downloading without version checks",
                "impact": "Potential unnecessary data costs for students"
            })
        
        if analytics['total_estimated_cost_usd'] > 50:
            insights.append({
                "type": "caution",
                "message": f"High estimated user costs: ${analytics['total_estimated_cost_usd']:.2f}",
                "impact": "May be barrier to educational access"
            })
        
        mobile_usage = analytics['connection_patterns'].get('mobile', 0)
        total_usage = sum(analytics['connection_patterns'].values())
        if mobile_usage > 0 and total_usage > 0:
            mobile_percent = (mobile_usage / total_usage) * 100
            if mobile_percent > 50:
                insights.append({
                    "type": "info",
                    "message": f"{mobile_percent:.0f}% of downloads on mobile data",
                    "impact": "Consider mobile-optimized progressive loading"
                })
        
        return {
            **analytics,
            "mission_insights": insights,
            "educational_impact": {
                "data_protected": analytics['data_protection_enabled'],
                "estimated_user_savings": f"${analytics['data_savings_mb'] * 100:.2f}",
                "accessibility_rating": "high" if analytics['total_estimated_cost_usd'] < 10 else "medium" if analytics['total_estimated_cost_usd'] < 25 else "low"
            },
            "recommendations": [
                "Continue promoting version check usage" if analytics['data_protection_enabled'] else "Implement mandatory version checks",
                "Monitor mobile vs WiFi usage patterns",
                "Consider progressive loading for high-cost regions",
                "Track educational content access patterns"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data usage analytics failed: {e}")

# Static file serving
app.mount("/static", StaticFiles(directory="WebPages"), name="static")

# Serve main web interface
@app.get("/")
async def serve_main_page():
    """Serve the main AndyGoogle web interface"""
    return FileResponse("WebPages/desktop-library.html")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and log errors"""
    if sheets_logger:
        sheets_logger.LogError(
            error_type="HTTP_ERROR",
            error_message=f"{exc.status_code}: {exc.detail}",
            context=f"{request.method} {request.url.path}"
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions and log errors"""
    if sheets_logger:
        sheets_logger.LogError(
            error_type="INTERNAL_ERROR",
            error_message=str(exc),
            context=f"{request.method} {request.url.path}",
            severity="CRITICAL"
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# Student Book Download Endpoints
@app.get("/api/books/{book_id}/cost", response_model=BookCostResponse)
async def get_book_cost(book_id: int, region: str = "developing"):
    """Get cost estimate for downloading a book"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    try:
        # Parse region
        student_region = StudentRegion(region.lower())
        
        downloader = StudentBookDownloader()
        cost_info = downloader.GetBookCostEstimate(book_id, student_region)
        
        if not cost_info:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return BookCostResponse(
            book_id=cost_info.book_id,
            title=cost_info.title,
            file_size_mb=cost_info.file_size_mb,
            estimated_cost_usd=cost_info.estimated_cost_usd,
            warning_level=cost_info.warning_level,
            budget_percentage=cost_info.budget_percentage
        )
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid region. Use: developing, emerging, or developed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost calculation error: {str(e)}")

@app.get("/api/books/{book_id}/download-options", response_model=DownloadOptionsResponse)
async def get_download_options(book_id: int, region: str = "developing"):
    """Get download options for a book with student guidance"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    try:
        student_region = StudentRegion(region.lower())
        
        downloader = StudentBookDownloader()
        options = downloader.GetDownloadOptions(book_id, student_region)
        
        if 'error' in options:
            raise HTTPException(status_code=404, detail=options['error'])
        
        return DownloadOptionsResponse(**options)
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid region. Use: developing, emerging, or developed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Options error: {str(e)}")

@app.get("/api/books/{book_id}/pdf")
async def get_book_pdf(request: Request, book_id: int, db: sqlite3.Connection = Depends(get_database)):
    """Get PDF file for a book - integrates with Google Drive or local storage"""
    log_api_usage(request, "pdf_access", f"book_id={book_id}")
    
    # First get book info from database
    cursor = db.execute("SELECT id, title, FilePath FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        # Try Google Drive integration first
        from Core.StudentGoogleDriveAPI import StudentGoogleDriveAPI, GOOGLE_AVAILABLE
        
        if GOOGLE_AVAILABLE:
            print(f"🔍 Attempting Google Drive access for book: {book['title']}")
            
            try:
                # Initialize Google Drive API
                gdrive_api = StudentGoogleDriveAPI()
                
                # Check if we have a valid token (simplified check)
                token_path = "Config/google_token.json"
                if os.path.exists(token_path):
                    print("✅ Google token found, attempting book access")
                    
                    # Get file info from Google Drive
                    file_info = gdrive_api.GetBookFileInfo(book['title'])
                    
                    if file_info:
                        print(f"✅ Found book in Google Drive: {file_info.name}")
                        
                        # For now, redirect to Google Drive download URL
                        # In production, you might want to proxy the download
                        from fastapi.responses import RedirectResponse
                        return RedirectResponse(url=file_info.download_url)
                    else:
                        print(f"⚠️ Book '{book['title']}' not found in Google Drive")
                
                else:
                    print("⚠️ No Google authentication token found")
                    
            except Exception as e:
                print(f"⚠️ Google Drive access failed: {e}")
        
        # Fallback to local file system
        if book['FilePath']:
            local_path = book['FilePath']
            
            # Convert relative path to absolute
            if not os.path.isabs(local_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                local_path = os.path.join(base_dir, local_path)
            
            if os.path.exists(local_path):
                print(f"✅ Serving PDF from local file: {local_path}")
                from fastapi import Response
                
                # Read PDF file and serve with inline viewing headers
                with open(local_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                
                return Response(
                    content=pdf_content,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"inline; filename=\"{book['title']}.pdf\"",
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0"
                    }
                )
        
        # If we get here, no PDF source is available
        raise HTTPException(
            status_code=404, 
            detail="PDF not available. Book may need to be downloaded from Google Drive first."
        )
        
    except Exception as e:
        print(f"❌ PDF access error: {e}")
        raise HTTPException(status_code=500, detail=f"Error accessing PDF: {str(e)}")

@app.get("/api/student/budget-summary", response_model=BudgetSummaryResponse)
async def get_budget_summary():
    """Get student's monthly spending summary"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    try:
        downloader = StudentBookDownloader()
        summary = downloader.GetMonthlySpendingSummary()
        
        return BudgetSummaryResponse(**summary)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Budget summary error: {str(e)}")

@app.post("/api/books/{book_id}/download")
async def initiate_book_download(book_id: int, download_method: str = "download_now"):
    """Initiate book download (placeholder for actual Google Drive integration)"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    # For now, just return download initiation info
    # TODO: Implement actual Google Drive download with chunking
    
    try:
        downloader = StudentBookDownloader()
        cost_info = downloader.GetBookCostEstimate(book_id)
        
        if not cost_info:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Simulate download cost recording
        actual_cost = cost_info.estimated_cost_usd if download_method == "download_now" else 0.0
        downloader.RecordDownload(book_id, actual_cost, download_method)
        
        return {
            "status": "download_initiated",
            "book_id": book_id,
            "method": download_method,
            "estimated_cost": actual_cost,
            "message": f"Download started for: {cost_info.title}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

def main():
    """Run the AndyGoogle API server"""
    print("🚀 Starting AndyGoogle API Server")
    print("=" * 40)
    
    # Configuration
    host = "127.0.0.1"
    port = 8000
    
    # Try to find an available port
    import socket
    for test_port in range(port, port + 10):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind((host, test_port))
            test_socket.close()
            port = test_port
            break
        except OSError:
            continue
    
    print(f"🌐 Server will start at: http://{host}:{port}")
    print(f"📚 AndyGoogle Library: http://{host}:{port}")
    print(f"🔧 API Documentation: http://{host}:{port}/docs")
    print("=" * 40)
    
    # Start server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
