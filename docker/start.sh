#!/bin/bash
# Quick start script for FinX development environment

set -e

echo "=========================================="
echo "FinX Development Environment Setup"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Docker is running..."

# Start services
echo ""
echo "Starting services..."
docker-compose -f docker-compose-dev.yaml up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check Qdrant
echo ""
echo "Checking Qdrant..."
if curl -s http://localhost:6333/health > /dev/null; then
    echo "  [OK] Qdrant is healthy"
else
    echo "  [WARN] Qdrant is not responding yet"
fi

# Show status
echo ""
echo "Service status:"
docker-compose -f docker-compose-dev.yaml ps

echo ""
echo "=========================================="
echo "Services are ready!"
echo "=========================================="
echo ""
echo "Qdrant Dashboard: http://localhost:6333/dashboard"
echo "Qdrant API: http://localhost:6333"
echo ""
echo "To view logs: make logs"
echo "To stop services: make down"
echo "To see all commands: make help"
echo ""
