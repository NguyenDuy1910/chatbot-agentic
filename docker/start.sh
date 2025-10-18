#!/bin/bash
# Quick start script for FinX development environment

set -e

echo "=========================================="
echo "FinX Development Environment Setup"
echo "=========================================="
echo ""

# Parse command line arguments
PROFILE=""
if [ "$1" = "--with-postgres" ] || [ "$1" = "-pg" ]; then
    PROFILE="--profile postgres"
    echo "Starting with PostgreSQL..."
elif [ "$1" = "--with-all" ] || [ "$1" = "-all" ]; then
    PROFILE="--profile postgres --profile redis"
    echo "Starting with all services..."
else
    echo "Starting core services (Qdrant only)..."
    echo "Tip: Use '--with-postgres' or '-pg' to include PostgreSQL"
    echo "     Use '--with-all' or '-all' to include all services"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Docker is running..."

# Start services
echo ""
echo "Starting services..."
docker-compose -f docker-compose-dev.yaml $PROFILE up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check Qdrant
echo ""
echo "Checking Qdrant..."
if curl -s http://localhost:6333/health > /dev/null; then
    echo "  ✓ Qdrant is healthy"
else
    echo "  ✗ Qdrant is not responding yet"
fi

# Check PostgreSQL if profile is enabled
if [[ "$PROFILE" == *"postgres"* ]]; then
    echo ""
    echo "Checking PostgreSQL..."
    if docker exec finx-postgres pg_isready -U admin > /dev/null 2>&1; then
        echo "  ✓ PostgreSQL is healthy"
    else
        echo "  ✗ PostgreSQL is not responding yet (may still be starting)"
    fi
fi

# Check Redis if profile is enabled
if [[ "$PROFILE" == *"redis"* ]]; then
    echo ""
    echo "Checking Redis..."
    if docker exec finx-redis redis-cli ping > /dev/null 2>&1; then
        echo "  ✓ Redis is healthy"
    else
        echo "  ✗ Redis is not responding yet"
    fi
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
echo "Qdrant API:       http://localhost:6333"

if [[ "$PROFILE" == *"postgres"* ]]; then
    echo ""
    echo "PostgreSQL:"
    echo "  Host:     localhost"
    echo "  Port:     9432"
    echo "  Database: vikki"
    echo "  User:     admin"
    echo "  Password: admin"
    echo "  Connection: postgresql://admin:admin@localhost:9432/vikki"
fi

if [[ "$PROFILE" == *"redis"* ]]; then
    echo ""
    echo "Redis:            redis://localhost:6379"
fi

echo ""
echo "Useful commands:"
echo "  make logs        - View all logs"
echo "  make logs-qdrant - View Qdrant logs"
if [[ "$PROFILE" == *"postgres"* ]]; then
    echo "  make logs-pg     - View PostgreSQL logs"
fi
echo "  make down        - Stop all services"
echo "  make help        - See all available commands"
echo ""
