#!/bin/bash
# File: setup-github.sh
# Setup script for GitHub repository

echo "🚀 SETTING UP ANDYLIBRARY STANDALONE FOR GITHUB"
echo "=============================================="

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "📁 Git repository already exists"
fi

# Copy README for GitHub
echo "📝 Setting up GitHub README..."
cp README-GitHub.md README.md

# Create .gitignore
echo "🚫 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local data
Data/
*.db
*.db-shm
*.db-wal

# Logs
*.log
EOF

# Add files to git
echo "➕ Adding files to Git..."
git add .
git add .github/

# Commit
echo "💾 Creating initial commit..."
git commit -m "🚀 Initial commit: AndyLibrary Standalone with GitHub Actions

✨ Features:
- Standalone educational library (1,219+ books)
- Windows executable via GitHub Actions
- Zero-installation educational access
- Part of Project Himalaya educational mission"

echo ""
echo "✅ Git repository ready for GitHub!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Copy the remote URL from GitHub"
echo "3. Run: git remote add origin YOUR_GITHUB_URL"
echo "4. Run: git push -u origin main"
echo "5. GitHub Actions will automatically build Windows .exe!"
echo ""
echo "🎯 The executable will be available in:"
echo "   - GitHub Actions → Artifacts (immediate)"
echo "   - Releases (if you create a tag)"