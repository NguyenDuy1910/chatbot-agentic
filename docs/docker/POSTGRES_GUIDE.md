# PostgreSQL Quick Guide

## 🚀 Starting PostgreSQL

### Option 1: Using start.sh (Easiest)
```bash
cd docker
./start.sh --with-postgres
```

### Option 2: Using Makefile
```bash
cd docker
make up-pg
```

### Option 3: Using Docker Compose
```bash
cd docker
docker-compose -f docker-compose-dev.yaml --profile postgres up -d
```

## 📋 Connection Details

```yaml
Host:     localhost
Port:     9432
Database: vikki
User:     admin
Password: admin
```

**Connection String:**
```
postgresql://admin:admin@localhost:9432/vikki
```

**Why port 9432?** To avoid conflicts with local PostgreSQL installations (default port 5432).

## 🔧 Usage Examples

### psql (PostgreSQL CLI)

**Connect from host machine:**
```bash
psql -h localhost -p 9432 -U admin -d vikki
# Password: admin
```

**Connect from Docker:**
```bash
docker exec -it finx-postgres psql -U admin -d vikki
```

### Python (psycopg2)

```python
import psycopg2

# Connection
conn = psycopg2.connect(
    host="localhost",
    port=9432,
    database="vikki",
    user="admin",
    password="admin"
)

# Or using connection string
conn = psycopg2.connect(
    "postgresql://admin:admin@localhost:9432/vikki"
)

# Create cursor
cur = conn.cursor()

# Execute query
cur.execute("SELECT version();")
version = cur.fetchone()
print(version)

# Close
cur.close()
conn.close()
```

### Python (SQLAlchemy)

```python
from sqlalchemy import create_engine

# Create engine
engine = create_engine(
    "postgresql://admin:admin@localhost:9432/vikki"
)

# Test connection
with engine.connect() as conn:
    result = conn.execute("SELECT version();")
    print(result.fetchone())
```

### Node.js (pg)

```javascript
const { Client } = require('pg');

const client = new Client({
  host: 'localhost',
  port: 9432,
  database: 'vikki',
  user: 'admin',
  password: 'admin',
});

await client.connect();
const res = await client.query('SELECT version()');
console.log(res.rows[0]);
await client.end();
```

## 🔍 Common Operations

### Check if PostgreSQL is Running

```bash
# Using Docker
docker ps | grep finx-postgres

# Check health
docker exec finx-postgres pg_isready -U admin

# Using make
make ps
```

### Create a Table

```bash
docker exec -it finx-postgres psql -U admin -d vikki
```

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert data
INSERT INTO users (name, email) VALUES 
    ('John Doe', 'john@example.com'),
    ('Jane Smith', 'jane@example.com');

-- Query
SELECT * FROM users;
```

### View Logs

```bash
# All PostgreSQL logs
make logs-pg

# Or using Docker Compose
docker-compose -f docker-compose-dev.yaml logs -f postgres

# Last 100 lines
docker logs finx-postgres --tail 100
```

### Execute SQL File

```bash
# From host
psql -h localhost -p 9432 -U admin -d vikki -f schema.sql

# From Docker
docker exec -i finx-postgres psql -U admin -d vikki < schema.sql
```

### Backup Database

```bash
# Dump entire database
docker exec finx-postgres pg_dump -U admin vikki > backup.sql

# Dump with compression
docker exec finx-postgres pg_dump -U admin vikki | gzip > backup.sql.gz

# Dump specific table
docker exec finx-postgres pg_dump -U admin -t users vikki > users_backup.sql
```

### Restore Database

```bash
# Restore from SQL file
docker exec -i finx-postgres psql -U admin vikki < backup.sql

# Restore from compressed file
gunzip -c backup.sql.gz | docker exec -i finx-postgres psql -U admin vikki
```

## 🛠️ Troubleshooting

### PostgreSQL not starting?

**Check if profile is enabled:**
```bash
docker-compose -f docker-compose-dev.yaml ps
```

If you don't see `finx-postgres`, you need to start with the postgres profile:
```bash
./start.sh --with-postgres
```

### Connection refused?

**Check if container is running:**
```bash
docker ps | grep finx-postgres
```

**Check PostgreSQL logs:**
```bash
make logs-pg
```

**Check if PostgreSQL is ready:**
```bash
docker exec finx-postgres pg_isready -U admin
```

### Port 9432 already in use?

**Find what's using the port:**
```bash
lsof -i :9432
```

**Kill the process or change the port in docker-compose-dev.yaml:**
```yaml
ports:
  - "9433:5432"  # Changed to 9433
```

### Permission denied?

**Check volume permissions:**
```bash
docker volume inspect docker_data
```

**Recreate volume:**
```bash
make down
docker volume rm docker_data
make up-pg
```

### Database not found?

**List databases:**
```bash
docker exec finx-postgres psql -U admin -c "\l"
```

**Create database if missing:**
```bash
docker exec finx-postgres psql -U admin -c "CREATE DATABASE vikki;"
```

## 🔐 Security Notes

**⚠️ DEVELOPMENT ONLY**

These credentials are for development purposes only!

- Default user: `admin`
- Default password: `admin`
- No SSL required

**For production:**
- Change username and password
- Use strong passwords
- Enable SSL/TLS
- Restrict network access
- Use environment variables for credentials

## 📊 Performance Tips

### Connection Pooling

**Python (psycopg2):**
```python
from psycopg2 import pool

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="localhost",
    port=9432,
    database="vikki",
    user="admin",
    password="admin"
)

# Get connection from pool
conn = db_pool.getconn()
# ... use connection ...
db_pool.putconn(conn)
```

**Python (SQLAlchemy):**
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://admin:admin@localhost:9432/vikki",
    pool_size=10,
    max_overflow=20
)
```

### Optimize Configuration

Add to `docker-compose-dev.yaml`:
```yaml
postgres:
  environment:
    - POSTGRES_MAX_CONNECTIONS=200
    - POSTGRES_SHARED_BUFFERS=256MB
    - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
  command:
    - postgres
    - -c
    - shared_buffers=256MB
    - -c
    - effective_cache_size=1GB
```

## 🧪 Testing

### Test Connection

```bash
# Using make
make test

# Using psql
psql -h localhost -p 9432 -U admin -d vikki -c "SELECT 1;"

# Using curl (through pg_isready)
docker exec finx-postgres pg_isready -U admin
```

### Sample Test Script

```bash
#!/bin/bash
# test-postgres.sh

echo "Testing PostgreSQL connection..."

# Test connection
docker exec finx-postgres psql -U admin -d vikki -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ PostgreSQL is working!"
else
    echo "✗ PostgreSQL connection failed!"
    exit 1
fi

# Test table creation
docker exec finx-postgres psql -U admin -d vikki -c "
    CREATE TABLE IF NOT EXISTS test (id SERIAL PRIMARY KEY);
    INSERT INTO test VALUES (DEFAULT);
    SELECT COUNT(*) FROM test;
    DROP TABLE test;
" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ PostgreSQL operations working!"
else
    echo "✗ PostgreSQL operations failed!"
    exit 1
fi

echo "All tests passed!"
```

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker PostgreSQL](https://hub.docker.com/_/postgres)

## 💡 Tips

1. **Always use connection pooling** in production
2. **Use environment variables** for credentials
3. **Regularly backup** your data
4. **Monitor connection count** and resource usage
5. **Use indexes** for frequently queried columns
6. **Vacuum regularly** to maintain performance

## 🎯 Quick Commands Reference

```bash
# Start PostgreSQL
./start.sh -pg

# Stop PostgreSQL
make down

# Connect to database
docker exec -it finx-postgres psql -U admin -d vikki

# View logs
make logs-pg

# Check health
docker exec finx-postgres pg_isready -U admin

# Backup
docker exec finx-postgres pg_dump -U admin vikki > backup.sql

# Restore
docker exec -i finx-postgres psql -U admin vikki < backup.sql

# List databases
docker exec finx-postgres psql -U admin -c "\l"

# List tables
docker exec finx-postgres psql -U admin -d vikki -c "\dt"
```

---

**Need help?** Check the main [README.md](./README.md) or run `make help`
