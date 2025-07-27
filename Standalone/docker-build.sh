#!/bin/bash
# Simple Docker cross-compilation for Windows

echo "🐳 Building Windows executable with Docker..."

# Create a simple Dockerfile for Windows build
cat > Dockerfile.windows << 'EOF'
FROM python:3.11-windowsservercore-1809

WORKDIR /app
COPY requirements-standalone.txt .
RUN pip install -r requirements-standalone.txt

COPY . .
RUN pyinstaller standalone-library.spec --clean --onefile

CMD ["echo", "Build complete"]
EOF

# Build with Docker
docker build -f Dockerfile.windows -t andylibrary-windows .
docker run --rm -v $(pwd)/dist:/app/dist andylibrary-windows

echo "✅ Check dist/ folder for AndyLibrary-Standalone.exe"