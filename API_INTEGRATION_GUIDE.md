# 🚀 API Integration Guide

## Tổng quan

Dự án đã được tích hợp hoàn chỉnh giữa frontend (React/TypeScript) và backend (FastAPI/Python). Tất cả API endpoints đã được validate và sẵn sàng sử dụng.

## 🔧 Setup và Chạy

### 1. Backend Setup

```bash
cd backend

# Cài đặt dependencies
pip install -r requirement.txt

# Cấu hình environment
cp .env.example .env
# Edit .env file với database credentials

# Chạy server
python main.py
# hoặc
python run.py
```

Backend sẽ chạy trên: `http://localhost:8000`

### 2. Frontend Setup

```bash
# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

Frontend sẽ chạy trên: `http://localhost:5173`

## 📡 API Endpoints Đã Tích Hợp

### Authentication (`/api/v1/auth`)
- ✅ `POST /signup` - User registration
- ✅ `POST /signin` - User login
- ✅ `POST /signout` - User logout
- ✅ `GET /user` - Get current user
- ✅ `PUT /update/profile` - Update user profile
- ✅ `PUT /update/password` - Update password

### Chats (`/api/v1/chats`)
- ✅ `GET /` - Get user chats
- ✅ `POST /` - Create new chat
- ✅ `GET /{chat_id}` - Get specific chat
- ✅ `PUT /{chat_id}` - Update chat
- ✅ `DELETE /{chat_id}` - Delete chat
- ✅ `POST /{chat_id}/archive` - Archive chat
- ✅ `POST /{chat_id}/pin` - Pin chat

### Messages (`/api/v1/messages`)
- ✅ `GET /` - Get messages
- ✅ `POST /` - Create message
- ✅ `GET /{message_id}` - Get specific message
- ✅ `PUT /{message_id}` - Update message
- ✅ `DELETE /{message_id}` - Delete message

### Connections (`/api/v1/connections`)
- ✅ `GET /` - Get connections
- ✅ `POST /` - Create connection
- ✅ `GET /{connection_id}` - Get specific connection
- ✅ `PUT /{connection_id}` - Update connection
- ✅ `DELETE /{connection_id}` - Delete connection
- ✅ `POST /test` - Test connection

### Prompts (`/api/v1/prompts`)
- ✅ `GET /` - Get prompts
- ✅ `POST /` - Create prompt
- ✅ `GET /{prompt_id}` - Get specific prompt
- ✅ `PUT /{prompt_id}` - Update prompt
- ✅ `DELETE /{prompt_id}` - Delete prompt

### Other Endpoints
- ✅ `GET /health` - Health check
- ✅ `GET /config` - App configuration

## 🧪 Testing API Integration

### 1. Sử dụng Demo Page

Truy cập: `http://localhost:5173/demo`

Demo page có 3 tabs:
- **🔐 Authentication**: Test login/logout flow
- **🔌 API Integration**: Test tất cả API endpoints
- **🎨 UI Components**: Test UI components

### 2. Demo Credentials

```
Email: demo@vikki.com
Password: demo123
```

### 3. Manual Testing

```typescript
// Import API functions
import { authAPI } from '@/lib/authAPI';
import { chatAPI } from '@/lib/chatAPI';
import { connectionAPI } from '@/lib/connectionAPI';

// Test authentication
const response = await authAPI.login({
  email: 'demo@vikki.com',
  password: 'demo123'
});

// Test chat creation
const chat = await chatAPI.createChat({
  title: 'Test Chat'
});

// Test connections
const connections = await connectionAPI.getConnections();
```

## 📁 File Structure

### Frontend API Files
```
src/lib/
├── api.ts              # Core API utilities
├── authAPI.ts          # Authentication API
├── chatAPI.ts          # Chat & Messages API
├── connectionAPI.ts    # Connections API
├── promptAPI.ts        # Prompts API
├── databaseAPI.ts      # Database API
└── testAPI.ts          # API testing utilities
```

### Backend API Files
```
backend/finx/routers/
├── auth.py             # Authentication endpoints
├── chats.py            # Chat endpoints
├── messages.py         # Message endpoints
├── connections.py      # Connection endpoints
├── prompts.py          # Prompt endpoints
├── users.py            # User endpoints
├── knowledge.py        # Knowledge endpoints
└── files.py            # File endpoints
```

## 🔑 Key Features

### 1. Automatic Authentication
- Token được tự động attach vào requests
- Support cả localStorage và cookie storage
- Automatic error handling cho unauthorized requests

### 2. Type Safety
- Full TypeScript support
- Backend models mapped to frontend types
- Compile-time error checking

### 3. Error Handling
- Consistent error format
- User-friendly error messages
- Automatic retry logic (configurable)

### 4. Development Tools
- API testing interface
- Real-time endpoint testing
- Response inspection
- Error debugging

## 🚨 Troubleshooting

### Backend không chạy
```bash
# Kiểm tra port
lsof -i :8000

# Kiểm tra database connection
cd backend && python -c "from finx.internal.database_factory import test_current_provider; print(test_current_provider())"
```

### Frontend không connect được backend
1. Kiểm tra `.env` file có `VITE_API_BASE_URL=http://localhost:8000`
2. Kiểm tra CORS settings trong backend
3. Kiểm tra network tab trong browser DevTools

### Authentication issues
1. Kiểm tra demo credentials
2. Clear localStorage và cookies
3. Kiểm tra backend auth endpoints

## 📈 Next Steps

1. **Real-time Features**: Implement WebSocket cho chat real-time
2. **File Upload**: Implement file upload endpoints
3. **Advanced Features**: Search, filtering, pagination
4. **Performance**: Caching, optimization
5. **Security**: Rate limiting, input validation

## 🎯 Production Checklist

- [ ] Environment variables properly configured
- [ ] Database migrations run
- [ ] CORS origins restricted
- [ ] Authentication secrets changed
- [ ] Error logging setup
- [ ] Performance monitoring
- [ ] Security headers configured
- [ ] API rate limiting enabled

---

**🎉 API Integration hoàn thành! Tất cả endpoints đã được validate và sẵn sàng sử dụng.**
