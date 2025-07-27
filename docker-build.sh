#!/bin/bash
# Build Windows EXE using Docker

echo "🐋 Building Windows EXE with Docker..."

# Build the Docker image
docker build -f Dockerfile.windows -t my-app-builder .

# Run the container and extract the executable
docker run --rm -v $(pwd)/dist-docker:/output my-app-builder \
    cmd /c "copy dist\\*.exe C:\\output\\"

echo "✅ Build complete!"
echo "Windows executable: ./dist-docker/"