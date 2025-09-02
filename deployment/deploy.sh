#!/bin/bash

# FinX Backend Deployment Script
# Usage: ./deploy.sh [environment] [database_provider]

set -e

ENVIRONMENT=${1:-production}
DATABASE_PROVIDER=${2:-supabase}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/finx-ai-service"

echo " Deploying FinX Backend - Environment: $ENVIRONMENT, Database: $DATABASE_PROVIDER"

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

print_success "Prerequisites check passed"

# Navigate to deployment directory
cd "$SCRIPT_DIR"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs

# Copy backend files to deployment context
print_status "Preparing deployment context..."
if [ -d "src" ]; then
    rm -rf src
fi
if [ -f "requirements.txt" ]; then
    rm -f requirements.txt
fi
if [ -f "main.py" ]; then
    rm -f main.py
fi
if [ -f "run.py" ]; then
    rm -f run.py
fi

# Copy backend files
cp -r "$BACKEND_DIR"/* .

# Handle environment file
if [ "$ENVIRONMENT" = "production" ]; then
    if [ -f ".env.production" ]; then
        cp .env.production .env
        print_success "Production environment file copied"
    elif [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Using example environment file - please update with production values"
    else
        print_warning "No environment file found - using defaults"
    fi
else
    print_status "Using existing .env file or defaults"
fi

# Choose docker-compose file based on database provider
COMPOSE_FILE="docker-compose.yml"
if [ "$DATABASE_PROVIDER" = "postgresql" ]; then
    COMPOSE_FILE="docker-compose.postgres.yml"
    print_status "Using PostgreSQL database configuration"
elif [ "$DATABASE_PROVIDER" = "supabase" ]; then
    print_status "Using Supabase database configuration"
else
    print_warning "Unknown database provider: $DATABASE_PROVIDER, using default configuration"
fi

# Stop existing services
print_status "Stopping existing services..."
docker-compose -f "$COMPOSE_FILE" down || true
docker-compose -f "$COMPOSE_FILE" rm -f || true

# Cleanup old images
print_status "Cleaning up old images..."
docker image prune -f || true

# Build backend image
print_status "Building backend Docker image..."
docker-compose -f "$COMPOSE_FILE" build --no-cache backend

# Start backend service
print_status "Starting backend service..."
docker-compose -f "$COMPOSE_FILE" up -d backend

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
sleep 20

# Health check with retry logic
max_attempts=20
attempt=1

print_status "Performing health check..."
while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is healthy!"
        break
    else
        print_status "Attempt $attempt/$max_attempts: Backend not ready yet..."
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    print_error "Backend failed to start properly"
    print_status "Checking logs..."
    docker-compose logs backend
    exit 1
fi

# Additional health checks
print_status "Running additional health checks..."

# Test API documentation endpoint
if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    print_success "API documentation endpoint is accessible"
else
    print_warning "API documentation endpoint is not accessible"
fi

# Show container status
print_status "Container status:"
docker-compose -f "$COMPOSE_FILE" ps

# Show container logs (last 20 lines)
print_status "Recent container logs:"
docker-compose -f "$COMPOSE_FILE" logs --tail=20 backend

# Show resource usage
print_status "Resource usage:"
docker stats --no-stream finx-backend

print_success " Backend deployment completed successfully!"
echo ""
echo " Backend is running at: http://localhost:8000"
echo ""
echo " Useful commands:"
echo "  View logs:           docker-compose -f $COMPOSE_FILE logs -f backend"
echo "  Stop backend:        docker-compose -f $COMPOSE_FILE stop backend"
echo "  Restart backend:     docker-compose -f $COMPOSE_FILE restart backend"
echo "  Shell access:        docker-compose -f $COMPOSE_FILE exec backend bash"
echo "  Update deployment:   ./deploy.sh $ENVIRONMENT $DATABASE_PROVIDER"
echo ""
echo " Deployment files are in: $SCRIPT_DIR"

# Cleanup deployment context (keep essential files)
print_status "Cleaning up deployment context..."
rm -rf src/ __pycache__/ .pytest_cache/ *.pyc
rm -f requirements.txt main.py run.py test*.py migrate.py
print_success "Cleanup completed"
