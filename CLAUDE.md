# File: CLAUDE.md

# Path: /home/herb/Desktop/AndyLibrary/CLAUDE.md

# Standard: AIDEV-PascalCase-2.1

# Created: 2025-07-23

# Last Modified: 2025-07-26 06:00AM

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AndyLibrary** (AndyGoogle) is an **educational mission-focused** digital library management system designed to provide equitable access to educational content for students in developing regions. Built with FastAPI and optimized for cost-conscious deployment.

### Educational Mission

**Primary Goal**: Get education into the hands of people who can least afford it

**Core Values**:

- **Cost Protection**: Students protected from surprise data charges via version control
- **Offline First**: Works without internet after initial download
- **Budget Device Friendly**: Optimized for $50 tablets with limited resources
- **Simple Technology**: Avoid over-engineering that doesn't serve students

### Architecture (Simplified for Educational Mission)

- **FastAPI Local Server**: Native app with web UI (`StartAndyGoogle.py`)
- **Direct SQLite Database**: Single 10.2MB file with embedded thumbnails (`MyLibrary.db`)
- **User Authentication System**: Email verification, session management, OAuth social login
- **Multi-User Isolation**: OS-specific user directories with complete environment separation
- **BowersWorld Integration**: Web registration gateway leading to native app installation
- **Native SQLite Caching**: Leverage built-in memory management (no custom cache layer)
- **Version Control System**: 127-byte checks protect students from unnecessary downloads
- **Offline Operation**: Complete functionality without internet dependency

### CRITICAL ARCHITECTURAL DECISIONS

#### ✅ DO (Proven Effective)

- **Use main database directly** - SQLite handles caching automatically
- **Embed thumbnails as BLOBs** - No separate image files needed
- **Native app deployment** - Better performance than browser-based solutions
- **Full database redownload** - Simple version control protects students
- **Student choice** - Never force expensive updates

#### ❌ DON'T (Over-Engineering Traps)

- **Create "cache" databases** - SQLite already caches in memory efficiently
- **Browser-based deployment** - Memory limits harm educational access
- **Complex packet update systems** - Adds cost without student benefit
- **Separate thumbnail files** - Increases complexity and failure points
- **Real-time Google Drive dependency** - Students need offline access

### Development Philosophy

#### Technical Reality Checks

- **Challenge assumptions** - Question "modern" solutions that don't serve the educational mission
- **Unix wisdom applies** - Simple tools, well combined, often outperform complex frameworks
- **Current tech validation** - Verify recommendations match 2025 reality, not outdated blog posts
- **Performance over abstraction** - Choose solutions that work efficiently on student hardware
- **Mission-driven decisions** - Every technical choice must serve educational access

#### Learning Partnership

- **Stay curious** - Question complexity when simpler solutions exist
- **Keep it honest** - Call out over-engineering before it becomes technical debt
- **Prevent foot-shooting** - Stop reinventing solved problems or ignoring efficient solutions
- **Current relevance** - Ensure architecture matches modern capabilities (e.g., SQLite auto-caching)

## Development Commands

### Starting the Application

```bash
# Primary method - with smart port detection
python StartAndyGoogle.py

# Force specific port (useful if 8000 is busy)
python StartAndyGoogle.py --port 8080

# Allow external connections (network access)
python StartAndyGoogle.py --host 0.0.0.0

# Environment check only
python StartAndyGoogle.py --check
```

### Testing

```bash
# Run all automated tests (recommended)
cd Tests && python run_automated_tests.py

# Run specific test categories
cd Tests && python run_automated_tests.py isolation  # user environment tests
cd Tests && python run_automated_tests.py auth      # authentication tests

# Legacy test runner (basic functionality)
python run_tests.py

# Direct pytest usage (manual test selection)
pytest Tests/ -v
pytest Tests/test_user_environment_simple.py -v
pytest Tests/test_database_manager_isolated.py -v
```

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Key Components

### Core Directories

- `Source/API/` - FastAPI endpoints with authentication and user setup
- `Source/Core/` - DatabaseManager (auth + library), UserSetupManager, SocialAuthManager
- `Source/Utils/` - Utility functions and helpers
- `Config/` - Configuration files (andygoogle_config.json, OAuth settings)
- `Data/Local/` - SQLite database and local file cache
- `WebPages/` - Frontend HTML/CSS/JavaScript (bowersworld.html, auth.html, setup.html)
- `Scripts/` - Development and utility scripts
- `Tests/` - Comprehensive test suite with automated runner

### Configuration

- **Main Config**: `Config/andygoogle_config.json`
- **Google Credentials**: `Config/google_credentials.json` (required for Drive sync)
- **OAuth Config**: `Config/social_auth_config.json` (Google/GitHub/Facebook login)
- **OAuth Test Setup**: `Config/oauth_test_accounts.json` (development testing guide)
- **Port Range**: Development [8000, 8010, 8080, 8090], User Environment [8100, 8110, 8120, 8130]

### Smart Port Detection

The application automatically detects and resolves port conflicts:

- Starts with port 8000 (or user-specified)
- Identifies common conflicts (HP printer service on 8000, Tomcat on 8080)
- Falls back to configured port range
- Reports which service is using busy ports

### Dependencies

Key Python packages:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` - Google Drive integration
- `pydantic` - Data validation
- `sqlite3` - Database (built-in)
- `aiofiles` - Async file operations

## Development Patterns

### File Headers

All files follow AIDEV-PascalCase-2.1 standard with proper headers including file path, creation date, and modification timestamps.

### Error Handling

- Environment validation before startup
- Graceful port conflict resolution
- Database connection fallbacks
- Google API error handling

### Testing Strategy

- **Automated Test Suite**: `Tests/run_automated_tests.py` (100% pass rate validation)
- **User Environment Isolation**: Multi-user path generation and OS-specific conventions
- **Database Operations**: User authentication, email verification, session management
- **Security Testing**: Password hashing, token validation, duplicate prevention
- **Development vs User Separation**: Environment isolation testing

## Common Issues & Solutions

### Port 8000 Busy

Usually caused by HP printer services. The application automatically finds alternative ports and reports the conflict source.

### Missing Google Credentials

Place `google_credentials.json` in `Config/` directory. The startup script validates this requirement.

### Database Issues

Local SQLite database in `Data/Local/cached_library.db`. Check database connectivity with test endpoint `/test`.

### Dependencies

Install all requirements from `requirements.txt`. The startup script validates critical packages are available.

## API Endpoints

### Core Application

- `/` - BowersWorld promotional page (entry point)
- `/docs` - FastAPI auto-generated API documentation with 40+ endpoints
- `/api/health` - System health check
- `/api/mode` - Current operating mode (local/gdrive)

### Authentication System

- `/api/auth/register` - User registration with email verification
- `/api/auth/login` - User authentication
- `/api/auth/oauth/{provider}` - Social login (Google/GitHub/Facebook)
- `/api/auth/verify-email` - Email verification endpoint

### User Setup System

- `/api/setup/status` - Check user installation status
- `/api/setup/install` - Complete user installation process
- `/api/setup/launch` - Launch native app from user environment

### Advanced Search System (Phase 2A)

- `POST /api/search/advanced` - Multi-mode search with relevance scoring
- `GET /api/search/suggestions` - Contextual search suggestions
- `GET /api/search/categories` - Educational categories for filtering

### User Progress Tracking (Phase 2A)

- `POST /api/progress/session/start` - Start reading session tracking
- `POST /api/progress/session/end` - End session with analytics
- `GET /api/progress/user` - Comprehensive user progress and statistics
- `POST /api/progress/bookmark` - Toggle bookmark status for books

### Library Core

- `/api/categories` - All educational categories (26 subjects)
- `/api/books/search` - Traditional book search
- `/api/books/{book_id}` - Individual book details

### Web Pages

- `/bowersworld.html` - Project Himalaya promotional landing
- `/auth.html` - Registration and login interface
- `/setup.html` - Installation progress and app launch

Access at: `http://127.0.0.1:{port}` where port is auto-detected (usually 8000).

## Version Control Strategy

### Student-Centric Update Philosophy

- **Student choice over forced updates** - App must work gracefully with outdated databases
- **Cost transparency** - Clear pricing for all update options ($1.02 for full 10.2MB download)
- **Graceful degradation** - Handle missing/deprecated books without crashes
- **Update frequency options** - Monthly ($12.24/year), Quarterly ($4.08/year), Yearly ($1.02/year), or Manual

### Implementation Approach

1. **Phase 1**: Simple full database redownload with student choice
2. **Phase 2**: Enhanced user control and update scheduling
3. **Phase 3**: Advanced packet system only if students demand it

### Key Principle

**Technical complexity should serve educational mission, not the reverse.**

## User Journey Architecture

### Complete User Workflow

1. **BowersWorld Discovery**: User visits promotional page showcasing Project Himalaya
2. **Registration Gateway**: Email/social login with mission acknowledgment and data consent
3. **Email Verification**: Secure token-based verification with 24-hour expiry
4. **User Environment Setup**: OS-specific installation with isolated directories
5. **Database Download**: 10.2MB library database copied to user's system
6. **Native App Launch**: Desktop application starts from user's isolated environment
7. **Future Access**: Simple login launches existing installation

### Multi-User Support

- **OS-Specific Paths**: Windows (LocalAppData), macOS (Application Support), Linux (.local/share)
- **User Isolation**: Each user gets separate installation directory with no conflicts
- **Development Separation**: User environments completely isolated from development resources
- **Cross-Platform**: Consistent behavior across Windows, macOS, and Linux

### Authentication & Security

- **Email Verification**: Required for account activation with secure token system
- **OAuth Integration**: Optional Google/GitHub/Facebook login for convenience
- **Session Management**: JWT-style tokens with expiration and validation
- **Password Security**: bcrypt hashing with rate limiting for brute force protection
- **Access Levels**: Tiered system (pending → basic → verified → elevated → admin)