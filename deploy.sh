#!/bin/bash

# FinX Backend Deployment Script
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}

echo "🚀 Deploying FinX Backend - Environment: $ENVIRONMENT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p backend/logs

# Copy environment file for production
if [ "$ENVIRONMENT" = "production" ]; then
    if [ -f "backend/.env.production" ]; then
        cp backend/.env.production backend/.env
        print_success "Production environment file copied"
    else
        print_status "Using existing .env file"
    fi
fi

# Stop existing backend if running
print_status "Stopping existing backend..."
docker-compose stop backend 2>/dev/null || true
docker-compose rm -f backend 2>/dev/null || true

# Build backend image
print_status "Building backend Docker image..."
docker-compose build --no-cache backend

# Start backend
print_status "Starting backend service..."
docker-compose up -d backend

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
sleep 15

# Health check
max_attempts=20
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is healthy!"
        break
    else
        print_status "Attempt $attempt/$max_attempts: Backend not ready yet..."
        sleep 3
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    print_error "Backend failed to start properly"
    print_status "Checking logs..."
    docker-compose logs backend
    exit 1
fi

# Show status
print_status "Backend container status:"
docker-compose ps backend

print_success "✅ Backend deployment completed successfully!"
echo ""
echo "🌐 Backend is running at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Useful commands:"
echo "  View logs:        docker-compose logs -f backend"
echo "  Stop backend:     docker-compose stop backend"
echo "  Restart backend:  docker-compose restart backend"
echo "  Shell access:     docker-compose exec backend bash"
