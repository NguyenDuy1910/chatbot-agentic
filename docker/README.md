# Docker Compose Development Environment

This directory contains Docker Compose configurations for the FinX AI Service development environment.

## Services

### Core Services (Always Running)

#### Qdrant Vector Database
- **Container:** finx-qdrant
- **Image:** qdrant/qdrant:v1.11.0
- **Ports:** 
  - 6333 - HTTP API
  - 6334 - gRPC API
- **Storage:** Persistent volume for vector data
- **Health Check:** HTTP endpoint monitoring

### Optional Services (Profile-based)

#### PostgreSQL Database
- **Container:** finx-postgres
- **Image:** postgres:14-alpine
- **Port:** 9432 (mapped from 5432)
- **Credentials:**
  - User: test
  - Password: secret
  - Database: test
- **Usage:** Uncomment or use `--profile postgres` to enable

#### Redis Cache
- **Container:** finx-redis
- **Image:** redis:7-alpine
- **Port:** 6379
- **Usage:** Use `--profile redis` to enable

## Quick Start

### Start Core Services (Qdrant only)
```bash
cd docker
docker-compose -f docker-compose-dev.yaml up -d
```

### Start with PostgreSQL
```bash
docker-compose -f docker-compose-dev.yaml --profile postgres up -d
```

### Start with Redis
```bash
docker-compose -f docker-compose-dev.yaml --profile redis up -d
```

### Start All Services
```bash
docker-compose -f docker-compose-dev.yaml --profile postgres --profile redis up -d
```

## Managing Services

### Check Service Status
```bash
docker-compose -f docker-compose-dev.yaml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose-dev.yaml logs -f

# Specific service
docker-compose -f docker-compose-dev.yaml logs -f qdrant
```

### Stop Services
```bash
docker-compose -f docker-compose-dev.yaml down
```

### Stop and Remove Volumes
```bash
docker-compose -f docker-compose-dev.yaml down -v
```

### Restart Services
```bash
docker-compose -f docker-compose-dev.yaml restart
```

## Service Endpoints

### Qdrant
- **REST API:** http://localhost:6333
- **Dashboard:** http://localhost:6333/dashboard
- **Health Check:** http://localhost:6333/health
- **gRPC:** localhost:6334

### PostgreSQL (if enabled)
- **Host:** localhost
- **Port:** 9432
- **Connection String:** `postgresql://test:secret@localhost:9432/test`

### Redis (if enabled)
- **Host:** localhost
- **Port:** 6379
- **Connection String:** `redis://localhost:6379`

## Health Checks

All services include health checks that can be monitored:

```bash
# Check Qdrant health
curl http://localhost:6333/health

# Check PostgreSQL health
docker exec finx-postgres pg_isready -U test

# Check Redis health
docker exec finx-redis redis-cli ping
```

## Volume Management

### Persistent Volumes
- `qdrant_storage` - Qdrant vector data
- `data` - PostgreSQL data
- `redis-data` - Redis persistence (local directory)

### Backup Qdrant Data
```bash
docker run --rm -v finx_qdrant_storage:/data -v $(pwd):/backup alpine tar czf /backup/qdrant-backup.tar.gz -C /data .
```

### Restore Qdrant Data
```bash
docker run --rm -v finx_qdrant_storage:/data -v $(pwd):/backup alpine tar xzf /backup/qdrant-backup.tar.gz -C /data
```

## Troubleshooting

### Qdrant Connection Issues
```bash
# Check if Qdrant is running
docker-compose -f docker-compose-dev.yaml ps qdrant

# Check Qdrant logs
docker-compose -f docker-compose-dev.yaml logs qdrant

# Test connection
curl http://localhost:6333/collections
```

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose-dev.yaml ps postgres

# Test connection
docker exec finx-postgres psql -U test -d test -c "SELECT version();"
```

### Port Conflicts
If you see port conflict errors:

```bash
# Check what's using the port
lsof -i :6333  # For Qdrant
lsof -i :9432  # For PostgreSQL
lsof -i :6379  # For Redis

# Stop the conflicting service or change ports in docker-compose-dev.yaml
```

### Reset Everything
```bash
# Stop all services and remove volumes
docker-compose -f docker-compose-dev.yaml down -v

# Remove orphaned containers
docker-compose -f docker-compose-dev.yaml down --remove-orphans

# Start fresh
docker-compose -f docker-compose-dev.yaml up -d
```

## Network Configuration

All services are connected to the `finx` bridge network, allowing them to communicate with each other using container names.

### Accessing from Host
- Use `localhost` and the exposed ports

### Accessing Between Containers
- Use container names (e.g., `qdrant`, `postgres`, `redis`)
- Use internal ports (e.g., 6333, 5432, 6379)

Example from Python application:
```python
# From host machine
QDRANT_URL = "http://localhost:6333"

# From another container in the same network
QDRANT_URL = "http://qdrant:6333"
```

## Development Workflow

### 1. Start Services
```bash
docker-compose -f docker-compose-dev.yaml up -d
```

### 2. Run Tests
```bash
cd ../finx-ai-service
source venv/bin/activate
python -m pytest tests/
```

### 3. Run Application
```bash
python main.py
```

### 4. Stop Services When Done
```bash
docker-compose -f docker-compose-dev.yaml down
```

## Configuration Files

### Environment Variables
Create a `.env` file in the docker directory:

```env
# Qdrant
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334

# PostgreSQL
POSTGRES_PORT=9432
POSTGRES_USER=test
POSTGRES_PASSWORD=secret
POSTGRES_DB=test

# Redis
REDIS_PORT=6379
```

Then reference in docker-compose:
```yaml
ports:
  - "${QDRANT_PORT}:6333"
```

## Performance Tuning

### Qdrant
For better performance, you can add configuration:
```yaml
qdrant:
  environment:
    - QDRANT__SERVICE__MAX_REQUEST_SIZE_MB=32
    - QDRANT__STORAGE__OPTIMIZERS__INDEXING_THRESHOLD_KB=20000
```

### PostgreSQL
For better performance:
```yaml
postgres:
  environment:
    - POSTGRES_MAX_CONNECTIONS=200
    - POSTGRES_SHARED_BUFFERS=256MB
```

## CI/CD Integration

### GitHub Actions Example
```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.11.0
    ports:
      - 6333:6333
      
  postgres:
    image: postgres:14-alpine
    ports:
      - 5432:5432
    env:
      POSTGRES_PASSWORD: secret
      POSTGRES_USER: test
      POSTGRES_DB: test
```

## Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
