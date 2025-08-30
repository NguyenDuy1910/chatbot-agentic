# ChatBot - AI Agentic Chatbot

A modern chatbot application built with React, TypeScript, and Tailwind CSS, featuring integrated prompt management and database connections.

## 🚀 Key Features

- 🤖 **Modern Chat Interface** - Clean, intuitive design
- 💬 **Real-time Messaging** - Smooth chat experience
- 📱 **Responsive Design** - Works great on all devices
- 🧠 **Prompt Management** - Create and manage prompt templates
- 🔗 **Database Connections** - Manage multiple database connections
- 👤 **User Authentication** - Login/registration system
- ⚙️ **System Administration** - Admin panel for management

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: PostgreSQL/MySQL/Supabase

## 🚀 Backend Deployment

### Quick Deploy
```bash
# Deploy backend with Docker
./deploy.sh production

# Check health
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

### Commands
```bash
# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Update deployment
git pull && ./deploy.sh production
```

### Endpoints
- **API**: `http://localhost:8000/api/v1`
- **Health**: `http://localhost:8000/health`
- **Docs**: `http://localhost:8000/docs`

📚 **Deployment details**: See `README-DEPLOYMENT.md`
- **Authentication**: JWT

## 📁 Project Structure

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

## 🚀 Installation and Setup

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- uv (Python package manager)
- PostgreSQL/MySQL

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd backend
uv pip sync requirements.txt
uv run run.py
```

## 🔧 Configuration

### Environment Variables
```env
# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000
VITE_JWT_SECRET=your-secret-key

# Backend
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=your-secret-key
```

## 📖 Usage Guide

### 1. Login/Registration
- Access `/auth/login` to log in
- Create a new account at `/auth/register`

### 2. Chat with AI
- Use the main chat interface
- Select existing prompts or create new ones
- Send messages and receive AI responses

### 3. Prompt Management
- Access the "Prompts" tab in the sidebar
- Create, edit, and organize prompt templates
- Use dynamic variables `{variable_name}` in prompts

### 4. Database Connections
- Configure database connections in settings
- Manage multiple connections simultaneously
- Test connections before use

## 🔗 API Endpoints

### Authentication
- `POST /auth/login` - Login
- `POST /auth/register` - Registration
- `POST /auth/logout` - Logout

### Chat
- `POST /chat` - Send message
- `GET /sessions` - Get chat session list

### Prompts
- `GET /prompts` - Get prompt list
- `POST /prompts` - Create new prompt
- `PUT /prompts/:id` - Update prompt

### Connections
- `GET /connections` - Get connection list
- `POST /connections` - Create new connection
- `POST /connections/:id/test` - Test connection

## 🎨 Customization

### Themes
- Light/Dark mode support
- Customize colors in `tailwind.config.js`
- CSS variables in `src/styles/`

### Components
- All components are modular
- Easy to customize and extend
- Full TypeScript support

## 📝 License

MIT License - see [LICENSE](LICENSE) file for more details.