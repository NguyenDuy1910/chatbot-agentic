# Hướng dẫn Setup Database cho Backend

Backend hỗ trợ 2 loại database:
- **Supabase** (PostgreSQL cloud)
- **PostgreSQL Local**

## Chọn Database Provider

Trong file `.env`, set `DATABASE_PROVIDER`:
```env
# Cho Supabase
DATABASE_PROVIDER=supabase

# Cho PostgreSQL local
DATABASE_PROVIDER=postgresql
```

---

# Setup Supabase (DATABASE_PROVIDER=supabase)

## 1. Tạo Supabase Project

1. Truy cập [Supabase Dashboard](https://supabase.com/dashboard)
2. Tạo project mới
3. Chọn region gần nhất (Singapore cho Việt Nam)
4. Đặt tên project và password cho database

## 2. Lấy thông tin kết nối

### Từ Supabase Dashboard:

1. **Project URL và API Keys**:
   - Vào `Settings` > `API`
   - Copy `Project URL` → `SUPABASE_URL`
   - Copy `anon public` key → `SUPABASE_ANON_KEY`
   - Copy `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`

2. **Database Connection String**:
   - Vào `Settings` > `Database`
   - Trong phần `Connection string`, chọn `URI`
   - Copy connection string → `SUPABASE_DB_URL`

3. **JWT Secret**:
   - Vào `Settings` > `API`
   - Copy `JWT Secret` → `SUPABASE_JWT_SECRET`

## 3. Cấu hình Environment

1. Copy file `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```

2. Điền thông tin Supabase vào file `.env`:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_DB_URL=postgresql://postgres:your-password@db.your-project-id.supabase.co:5432/postgres
   SUPABASE_JWT_SECRET=your-jwt-secret
   ```

## 4. Cài đặt Dependencies

```bash
cd backend
pip install -r requirement.txt
```

## 5. Tạo Tables

Sau khi cấu hình xong, chạy script để tạo tables:

```python
from backend.finx.internal.db import create_tables
create_tables()
```

## 6. Test Connection

```python
from backend.finx.internal.db import get_supabase, init_database

# Test Supabase client
supabase = get_supabase()
print("Supabase client initialized successfully")

# Test database connection
init_database()
print("Database connection established successfully")
```

## 7. Cấu hình Row Level Security (RLS)

Trong Supabase Dashboard:

1. Vào `Authentication` > `Settings`
2. Enable Row Level Security cho các tables cần thiết
3. Tạo policies phù hợp với ứng dụng

## 8. Troubleshooting

### Lỗi kết nối database:
- Kiểm tra connection string có đúng không
- Kiểm tra password database
- Kiểm tra firewall/network settings

### Lỗi authentication:
- Kiểm tra API keys có đúng không
- Kiểm tra JWT secret
- Kiểm tra RLS policies

### Lỗi SSL:
Nếu gặp lỗi SSL, thêm `?sslmode=require` vào cuối connection string:
```
postgresql://postgres:password@db.project.supabase.co:5432/postgres?sslmode=require
```

---

# Setup PostgreSQL Local (DATABASE_PROVIDER=postgresql)

## 1. Cài đặt PostgreSQL

### macOS:
```bash
# Sử dụng Homebrew
brew install postgresql
brew services start postgresql

# Hoặc sử dụng Postgres.app
# Download từ https://postgresapp.com/
```

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Windows:
- Download từ https://www.postgresql.org/download/windows/
- Chạy installer và follow hướng dẫn

## 2. Tạo Database và User

```bash
# Kết nối với PostgreSQL
sudo -u postgres psql

# Tạo database
CREATE DATABASE finx_db;

# Tạo user (optional)
CREATE USER finx_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE finx_db TO finx_user;

# Thoát
\q
```

## 3. Cấu hình Environment

Copy file `.env.example` thành `.env` và cấu hình:

```env
DATABASE_PROVIDER=postgresql

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=finx_db
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SCHEMA=public
```

## 4. Test Connection

```bash
cd backend
python test_connection.py
```

## 5. Troubleshooting PostgreSQL

### Lỗi connection refused:
- Kiểm tra PostgreSQL service đang chạy:
  ```bash
  # macOS
  brew services list | grep postgresql

  # Ubuntu
  sudo systemctl status postgresql
  ```

### Lỗi authentication:
- Kiểm tra pg_hba.conf file
- Đảm bảo user/password đúng

### Lỗi database không tồn tại:
```bash
sudo -u postgres createdb finx_db
```

---

# So sánh Supabase vs PostgreSQL Local

| Feature | Supabase | PostgreSQL Local |
|---------|----------|------------------|
| Setup | Dễ, cloud-based | Cần cài đặt local |
| Performance | Phụ thuộc internet | Nhanh, local |
| Scalability | Auto-scale | Manual setup |
| Cost | Có free tier | Miễn phí |
| Real-time | Built-in | Cần setup thêm |
| Auth | Built-in | Cần implement |
| Backup | Tự động | Manual |
| Development | Tốt cho prototype | Tốt cho development |

## Khuyến nghị:
- **Development**: PostgreSQL Local (nhanh, không cần internet)
- **Production**: Supabase (managed, scalable)
- **Testing**: PostgreSQL Local (isolated, reproducible)
