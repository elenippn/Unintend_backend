#!/bin/bash
# Build script for Docker deployment

echo "🔨 Building Docker image..."
docker build -t unintend-backend:latest .

echo "✅ Build complete!"
echo ""
echo "To run locally:"
echo "  docker run -p 8000:8000 unintend-backend:latest"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up"
