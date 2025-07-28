# File: README.md
# Path: /home/herb/Desktop/AndyLibrary/README.md
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-28
# Last Modified: 2025-07-28 01:47PM

# 🏔️ Project Himalaya - Educational Library Platform

**Getting education into the hands of people who can least afford it**

Project Himalaya is a comprehensive educational library management system designed to provide equitable access to educational content for students in developing regions. This repository contains benchmark implementations for AI-human synergy in educational technology.

## 🎯 Mission Statement

Our primary goal is to deliver cost-effective, offline-capable educational resources optimized for low-cost devices ($50 tablets) while maintaining world-class user experiences through intelligent systems.

## ✨ Key Features

### 🔐 Modern OAuth 2.0 Authentication
- **PKCE Security**: Proof Key for Code Exchange implementation
- **Multi-Provider Support**: Google, GitHub, Facebook integration
- **Token Encryption**: Fernet encryption for all OAuth tokens
- **Security Middleware**: Comprehensive HTTP security headers

### 🧭 Intelligent User Journey Management
- **5-Stage Journey**: Discovery → Trust Building → Welcome → Engagement → Mastery
- **Educational Psychology**: Learning science principles applied to platform design
- **Contextual Intelligence**: Real-time user behavior analysis and adaptation
- **Privacy Analytics**: GDPR/CCPA compliant interaction tracking

### 🔍 Advanced Search Engine
- **Learning Intent Recognition**: 7 types of educational intent classification
- **Academic Level Detection**: Elementary through Graduate level content adaptation
- **Semantic Understanding**: Goes beyond keywords to understand educational meaning
- **Multi-Factor Relevance Scoring**: Educational value + content quality + accessibility

### 🛡️ Security & Privacy
- **Data Protection**: GDPR/CCPA compliance built-in
- **Privacy-First Design**: Anonymized analytics and data protection
- **Secure Credential Management**: Multi-backend secret management system
- **Input Validation**: SQL injection prevention and security testing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SQLite (included with Python)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AndyLibrary.git
   cd AndyLibrary
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure OAuth credentials**
   ```bash
   cp Config/google_credentials.json.template Config/google_credentials.json
   # Edit Config/google_credentials.json with your Google OAuth credentials
   ```

5. **Start the application**
   ```bash
   python StartAndyGoogle.py
   ```

The application will automatically detect available ports and start the server at `http://127.0.0.1:8000` (or next available port).

## 🏗️ Architecture

### Core Components

- **FastAPI Backend**: Modern async web framework with auto-generated API docs
- **SQLite Database**: Single-file database with embedded thumbnails (10.2MB)
- **OAuth 2.0 System**: Modern social authentication with PKCE security
- **Intelligent Search**: Educational content discovery with learning intent recognition
- **User Journey Manager**: UX orchestration system with educational psychology principles

### Directory Structure

```
AndyLibrary/
├── Source/
│   ├── API/           # FastAPI endpoints and route handlers
│   ├── Core/          # Core business logic (Auth, Search, Journey)
│   ├── Utils/         # Utility functions and helpers
│   └── Middleware/    # Security and performance middleware
├── Config/            # Configuration files and templates
├── Data/              # Database and local data storage
├── WebPages/         # Frontend HTML/CSS/JavaScript
├── Tests/            # Comprehensive test suite
├── Docs/             # Documentation and guides
└── Scripts/          # Development and utility scripts
```

## 🧪 Testing

### Run All Tests
```bash
# Comprehensive test suite
python Tests/run_automated_tests.py

# Benchmark validation tests
python Tests/run_benchmark_tests.py

# Specific test categories
cd Tests && python run_automated_tests.py isolation  # User environment tests
cd Tests && python run_automated_tests.py auth      # Authentication tests
```

### Test Categories
- **Unit Tests**: Individual component functionality
- **Integration Tests**: Cross-component workflows
- **Performance Tests**: Speed and efficiency benchmarks
- **Security Tests**: OAuth, privacy, and data protection
- **End-to-End Tests**: Complete user workflows

## 📚 API Documentation

The application provides auto-generated API documentation at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Key Endpoints

#### Authentication
- `GET /api/auth/oauth/providers` - Available OAuth providers
- `GET /api/auth/oauth/{provider}` - Initiate OAuth login
- `GET /api/auth/oauth/callback` - Handle OAuth callback

#### Intelligent Search
- `POST /api/search/intelligent` - Educational content discovery
- `GET /api/search/suggestions` - Contextual search suggestions
- `GET /api/search/analytics` - Privacy-respecting search analytics

#### User Journey
- `POST /api/journey/initialize` - Start user experience journey
- `POST /api/journey/advance` - Progress through journey stages
- `GET /api/journey/analytics` - Anonymized optimization data

## 🔧 Configuration

### Environment Variables
```bash
# OAuth Configuration
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Security Keys
export SECRET_ENCRYPTION_KEY="your-32-character-encryption-key"
export OAUTH_TOKEN_ENCRYPTION_KEY="your-32-character-oauth-key"

# Environment
export ENVIRONMENT="development"  # or "production"
```

### Configuration Files
- `Config/andygoogle_config.json` - Main application configuration
- `Config/oauth_security_config.json` - OAuth security settings
- `Config/social_auth_config.json` - Social login providers

## 🌟 Project Highlights

### Educational Mission Focus
Every technical decision serves the core mission of making education accessible to underserved populations:

- **Cost Protection**: Students protected from surprise data charges
- **Offline First**: Complete functionality without internet dependency
- **Budget Device Friendly**: Optimized for $50 tablets with limited resources
- **Simple Technology**: Avoiding over-engineering that doesn't serve students

### Benchmark Quality Code
This codebase establishes foundational benchmarks for AI-human synergy that will be studied and replicated:

- **AIDEV-PascalCase-2.1**: Consistent coding standards throughout
- **Comprehensive Documentation**: Every component thoroughly documented
- **Test-Driven Development**: 100% test coverage with automated validation
- **Security Best Practices**: Production-ready security implementation

## 🔒 Security

### OAuth 2.0 Implementation
- PKCE (Proof Key for Code Exchange) for enhanced security
- State parameter CSRF protection
- Secure token storage with encryption
- Minimal scope principle

### Data Protection
- GDPR/CCPA compliance built-in
- Anonymized analytics data
- SQL injection prevention
- Input validation and sanitization

### Privacy Design
- No personal data in logs or analytics
- Privacy-respecting user tracking
- Secure credential management
- Data retention limits

## 🤝 Contributing

We welcome contributions that align with our educational mission! Please ensure:

1. **Follow coding standards**: AIDEV-PascalCase-2.1 compliance
2. **Include comprehensive tests**: All new features must include tests
3. **Update documentation**: Keep docs current with changes
4. **Security focus**: Maintain our privacy and security standards

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run pre-commit hooks
pre-commit install

# Run full test suite
python Tests/run_benchmark_tests.py
```

## 📖 Documentation

Comprehensive documentation is available in the `Docs/` directory:

- **Production Deployment Guide**: `Docs/PRODUCTION_DEPLOYMENT_GUIDE.md`
- **OAuth Setup Guide**: `Docs/OAUTH_PRODUCTION_SETUP.md`
- **Security Configuration**: `Docs/SECURITY_SETUP.md`
- **Testing Guide**: `Docs/MANUAL_TESTING_GUIDE.md`

## 🚀 Deployment

### Local Development
```bash
python StartAndyGoogle.py
```

### Production Deployment
See `Docs/PRODUCTION_DEPLOYMENT_GUIDE.md` for comprehensive deployment instructions including:
- Docker containerization
- Environment configuration
- Security hardening
- Performance optimization

## 📊 Performance

### Benchmarks
- **OAuth Operations**: < 100ms response time
- **Search Queries**: < 1000ms with intelligent caching
- **User Journey Events**: < 50ms processing time
- **Database Operations**: Optimized SQLite with memory caching

### Optimization Features
- **Intelligent Caching**: Multi-layer caching system
- **Database Optimization**: Indexed queries and connection pooling
- **Async Operations**: Non-blocking I/O for better performance
- **Memory Management**: Efficient resource utilization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Project Himalaya represents the collaborative effort to establish benchmarks for AI-human synergy in educational technology. Special recognition to:

- Educational psychology research informing our UX design
- Open-source security libraries enabling robust authentication
- The global community working toward educational equity

---

**🏔️ Project Himalaya**: *Establishing foundational benchmarks for AI-human synergy that will be studied, replicated, and built upon.*

For questions, support, or contributions, please open an issue or contact the development team.