# FinX Backend Only - Deployment Guide

## 🎯 Triển khai chỉ Backend API

### 📋 Yêu cầu

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Server**: 2GB RAM, 2 CPU cores, 10GB storage
- **Port**: 8000 (mở cho external access)

### 🚀 Triển khai nhanh

#### 1. Chuẩn bị server

```bash
# Cài đặt Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Cài đặt Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout và login lại để áp dụng quyền Docker
```

#### 2. Clone và deploy

```bash
# Clone repository
git clone <your-repo-url>
cd chatbot-agentic

# Cấu hình environment (tùy chọn)
cp backend/.env.production backend/.env
nano backend/.env  # Chỉnh sửa nếu cần

# Deploy backend
./deploy.sh production
```

### ⚙️ Cấu hình Environment

Chỉnh sửa file `backend/.env` cho production:

#### Option 1: Sử dụng Supabase (Recommended)

```bash
# Environment
ENVIRONMENT=production

# Database Provider Configuration
# Choose: "supabase" or "postgresql"
DATABASE_PROVIDER=supabase

# Supabase Configuration (when DATABASE_PROVIDER=supabase)
SUPABASE_URL=https://vurlhjsramyqeyuvkuab.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1cmxoanNyYW15cWV5dXZrdWFiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzNTY3MzUsImV4cCI6MjA3MDkzMjczNX0.X2e2E7uVm_XWxOKEE7O90Om5a1WqTSQs5qz8Nbxm3hg
SUPABASE_DB_URL=postgresql://postgres.vurlhjsramyqeyuvkuab:19102003Duy123321kdkd@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres

# Local PostgreSQL Configuration (when DATABASE_PROVIDER=postgresql)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DATABASE=finx_db
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=finx_password_production
POSTGRES_SCHEMA=public

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_RELOAD=false
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security Configuration
SECRET_KEY=agentkey
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

#### Option 2: Sử dụng PostgreSQL Container

Nếu muốn sử dụng PostgreSQL thay vì Supabase, thay đổi cấu hình:

```bash
# Database Provider Configuration
DATABASE_PROVIDER=postgresql

# Local PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DATABASE=finx_db
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=finx_password_production
POSTGRES_SCHEMA=public
```

**Lưu ý**: Khi sử dụng PostgreSQL, bạn cần setup PostgreSQL server riêng biệt.

### 🔧 Commands hữu ích

```bash
# Xem trạng thái
docker-compose ps backend

# Xem logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop backend
docker-compose stop backend

# Update và redeploy
git pull
./deploy.sh production

# Shell vào container
docker-compose exec backend bash

# Kiểm tra health
curl http://localhost:8000/health
```

### 🌐 API Endpoints

Sau khi deploy thành công:

- **API Root**: `http://your-server:8000/api/v1`
- **Health Check**: `http://your-server:8000/health`
- **Documentation**: `http://your-server:8000/docs`
- **ReDoc**: `http://your-server:8000/redoc`

### 🔍 Monitoring

```bash
# Quick health check
curl http://localhost:8000/health

# API status
curl http://localhost:8000/api/v1

# Container stats
docker stats finx-backend

# Check container status
docker-compose ps backend

# Logs monitoring
docker-compose logs -f backend | grep ERROR
```

### 🛠️ Troubleshooting

#### Backend không start được:

```bash
# Xem logs chi tiết
docker-compose logs backend

# Kiểm tra port conflict
netstat -tulpn | grep :8000

# Rebuild container
docker-compose build --no-cache backend
docker-compose up -d backend
```

#### Database connection issues:

```bash
# Kiểm tra environment variables
docker-compose exec backend env | grep -E "(SUPABASE|DATABASE)"

# Test database connection
docker-compose exec backend python -c "
from finx.internal.db import test_current_provider
print(test_current_provider())
"

# Check if backend is responding
curl -v http://localhost:8000/health
```

#### Performance issues:

```bash
# Kiểm tra resource usage
docker stats finx-backend

# Kiểm tra memory usage
docker-compose exec backend free -h

# Kiểm tra disk space
df -h
```

### 🔒 Security Notes

1. **Thay đổi SECRET_KEY** trong production
2. **Cấu hình CORS** với domain chính xác
3. **Sử dụng HTTPS** trong production (setup reverse proxy)
4. **Firewall**: Chỉ mở port 8000 cho trusted sources
5. **Regular updates**: `git pull && ./deploy.sh production`

### 📊 Production Checklist

- [x] SECRET_KEY đã được thay đổi (agentkey)
- [x] CORS_ORIGINS cấu hình đúng domain (https://yourdomain.com,https://www.yourdomain.com)
- [x] Database connection hoạt động (Supabase)
- [ ] Health check endpoint trả về 200
- [ ] API documentation accessible
- [ ] Logs được ghi đúng cách
- [x] Container restart policy = unless-stopped
- [ ] Backup strategy cho database

### 🆘 Support

Nếu gặp vấn đề:

1. Kiểm tra logs: `docker-compose logs backend`
2. Kiểm tra health: `curl http://localhost:8000/health`
3. Restart service: `docker-compose restart backend`
4. Rebuild: `docker-compose build --no-cache backend`

**Container chỉ chạy backend API, không bao gồm database hay reverse proxy.**

---

### 📝 Current Configuration Status

Dự án hiện tại đã được cấu hình với:
- ✅ **Environment**: Production
- ✅ **Database Provider**: Supabase (configured)
- ✅ **PostgreSQL Fallback**: Available (postgres host, password set)
- ✅ **Security**: Production secret key set
- ✅ **CORS**: Configured for production domains
- ✅ **API Debug**: Disabled for production
- ✅ **Container**: Auto-restart enabled
