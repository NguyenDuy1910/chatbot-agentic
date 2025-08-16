# Vikki ChatBot - AI Agentic Chatbot

Một ứng dụng chatbot hiện đại được xây dựng với React, TypeScript, và Tailwind CSS, tích hợp quản lý prompt và kết nối database.

## 🚀 Tính năng chính

- 🤖 **Giao diện chat hiện đại** - Thiết kế sạch sẽ, trực quan
- 💬 **Tin nhắn thời gian thực** - Trải nghiệm chat mượt mà
- 📱 **Responsive Design** - Hoạt động tốt trên mọi thiết bị
- 🧠 **Quản lý Prompt** - Tạo và quản lý prompt templates
- 🔗 **Kết nối Database** - Quản lý nhiều kết nối database
- 👤 **Xác thực người dùng** - Hệ thống đăng nhập/đăng ký
- ⚙️ **Quản trị hệ thống** - Panel admin cho quản lý

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: PostgreSQL/MySQL
- **Authentication**: JWT

## 📁 Cấu trúc Project

```
├── src/
│   ├── components/          # React components
│   │   ├── shared/         # Shared components
│   │   │   ├── ui/        # UI components (Button, Input, etc.)
│   │   │   └── AppWithAuth.tsx
│   │   └── features/      # Feature-specific components
│   │       ├── admin/     # Admin components
│   │       ├── auth/      # Authentication
│   │       ├── chat/      # Chat interface
│   │       ├── connections/ # Database connections
│   │       └── prompts/   # Prompt management
│   ├── pages/              # Page components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities & API
│   ├── types/              # TypeScript definitions
│   ├── contexts/           # React contexts
│   └── styles/             # Styling files
├── backend/                # Python backend
│   └── finx/              # FastAPI application
└── package.json           # Dependencies
```

## 🚀 Cài đặt và Chạy

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- PostgreSQL/MySQL

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn finx.main:app --reload
```

## 🔧 Cấu hình

### Environment Variables
```env
# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000
VITE_JWT_SECRET=your-secret-key

# Backend
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=your-secret-key
```

## 📖 Hướng dẫn sử dụng

### 1. Đăng nhập/Đăng ký
- Truy cập `/auth/login` để đăng nhập
- Tạo tài khoản mới tại `/auth/register`

### 2. Chat với AI
- Sử dụng giao diện chat chính
- Chọn prompt có sẵn hoặc tạo prompt mới
- Gửi tin nhắn và nhận phản hồi từ AI

### 3. Quản lý Prompt
- Truy cập tab "Prompts" trong sidebar
- Tạo, chỉnh sửa, và tổ chức prompt templates
- Sử dụng biến động `{variable_name}` trong prompt

### 4. Kết nối Database
- Cấu hình kết nối database trong settings
- Quản lý nhiều kết nối cùng lúc
- Test kết nối trước khi sử dụng

## 🔗 API Endpoints

### Authentication
- `POST /auth/login` - Đăng nhập
- `POST /auth/register` - Đăng ký
- `POST /auth/logout` - Đăng xuất

### Chat
- `POST /chat` - Gửi tin nhắn
- `GET /sessions` - Lấy danh sách phiên chat

### Prompts
- `GET /prompts` - Lấy danh sách prompt
- `POST /prompts` - Tạo prompt mới
- `PUT /prompts/:id` - Cập nhật prompt

### Connections
- `GET /connections` - Lấy danh sách kết nối
- `POST /connections` - Tạo kết nối mới
- `POST /connections/:id/test` - Test kết nối

## 🎨 Customization

### Themes
- Light/Dark mode support
- Tùy chỉnh màu sắc trong `tailwind.config.js`
- CSS variables trong `src/styles/`

### Components
- Tất cả components đều modular
- Dễ dàng tùy chỉnh và mở rộng
- TypeScript support đầy đủ

## 📝 License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.