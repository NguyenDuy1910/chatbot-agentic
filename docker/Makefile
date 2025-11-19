# Makefile for Docker Compose Development Environment
# Usage: make <target>

.PHONY: help up down restart logs ps clean health test backup restore

# Default target
help:
	@echo "Available commands:"
	@echo "  make up          - Start core services (Qdrant)"
	@echo "  make up-all      - Start all services including PostgreSQL and Redis"
	@echo "  make up-pg       - Start with PostgreSQL"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make logs-qdrant - View Qdrant logs"
	@echo "  make ps          - Show running services"
	@echo "  make clean       - Stop services and remove volumes"
	@echo "  make health      - Check health of all services"
	@echo "  make test        - Test service connections"
	@echo "  make backup      - Backup Qdrant data"
	@echo "  make restore     - Restore Qdrant data from backup"

# Start core services (Qdrant only)
up:
	@echo "Starting core services..."
	docker-compose -f docker-compose-dev.yaml up -d

# Start all services
up-all:
	@echo "Starting all services..."
	docker-compose -f docker-compose-dev.yaml --profile postgres --profile redis up -d

# Start with PostgreSQL
up-pg:
	@echo "Starting services with PostgreSQL..."
	docker-compose -f docker-compose-dev.yaml --profile postgres up -d

# Start with Redis
up-redis:
	@echo "Starting services with Redis..."
	docker-compose -f docker-compose-dev.yaml --profile redis up -d

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose -f docker-compose-dev.yaml down

# Restart all services
restart:
	@echo "Restarting all services..."
	docker-compose -f docker-compose-dev.yaml restart

# View logs from all services
logs:
	docker-compose -f docker-compose-dev.yaml logs -f

# View Qdrant logs
logs-qdrant:
	docker-compose -f docker-compose-dev.yaml logs -f qdrant

# View PostgreSQL logs
logs-pg:
	docker-compose -f docker-compose-dev.yaml logs -f postgres

# View Redis logs
logs-redis:
	docker-compose -f docker-compose-dev.yaml logs -f redis

# Show running services
ps:
	docker-compose -f docker-compose-dev.yaml ps

# Clean up everything (including volumes)
clean:
	@echo "Cleaning up all services and volumes..."
	docker-compose -f docker-compose-dev.yaml down -v
	@echo "Cleanup complete!"

# Clean with orphans
clean-all:
	@echo "Cleaning up all services, volumes, and orphans..."
	docker-compose -f docker-compose-dev.yaml down -v --remove-orphans
	@echo "Full cleanup complete!"

# Check health of all services
health:
	@echo "Checking service health..."
	@echo "\nQdrant:"
	@curl -s http://localhost:6333/health | jq '.' || echo "Qdrant not responding"
	@echo "\nPostgreSQL:"
	@docker exec finx-postgres pg_isready -U test 2>/dev/null || echo "PostgreSQL not running"
	@echo "\nRedis:"
	@docker exec finx-redis redis-cli ping 2>/dev/null || echo "Redis not running"

# Test service connections
test:
	@echo "Testing service connections..."
	@echo "\nTesting Qdrant..."
	@curl -s http://localhost:6333/collections | jq '.' || echo "Failed to connect to Qdrant"
	@echo "\nTesting PostgreSQL..."
	@docker exec finx-postgres psql -U test -d test -c "SELECT version();" 2>/dev/null || echo "PostgreSQL not available"
	@echo "\nTesting Redis..."
	@docker exec finx-redis redis-cli ping 2>/dev/null || echo "Redis not available"

# Backup Qdrant data
backup:
	@echo "Backing up Qdrant data..."
	@mkdir -p backups
	@docker run --rm -v docker_qdrant_storage:/data -v $(PWD)/backups:/backup alpine tar czf /backup/qdrant-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "Backup complete! Check backups/ directory"

# Restore Qdrant data from latest backup
restore:
	@echo "Restoring Qdrant data..."
	@docker run --rm -v docker_qdrant_storage:/data -v $(PWD)/backups:/backup alpine sh -c "cd /data && tar xzf /backup/$$(ls -t /backup/qdrant-backup-*.tar.gz | head -1)"
	@echo "Restore complete! Restart Qdrant to apply changes"

# Pull latest images
pull:
	@echo "Pulling latest images..."
	docker-compose -f docker-compose-dev.yaml pull

# Show resource usage
stats:
	docker stats --no-stream
