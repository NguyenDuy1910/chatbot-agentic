# ChatBot - AI Agentic Chatbot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/your-repo/chatbot.svg?branch=master)](https://travis-ci.org/your-repo/chatbot)

A modern chatbot application built with React, TypeScript, and Tailwind CSS, featuring integrated prompt management and database connections.

**[Live Demo](https://your-demo-link.com)**

## Table of Contents

- [Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Key Features

- 🤖 **Modern Chat Interface**: Clean, intuitive, and responsive design.
- 📝 **Prompt Management**: Easily create, manage, and use prompt templates.
- 🔗 **Database Connections**: Manage multiple database connections securely.
- 👤 **User Authentication**: Standard login/registration system.
- ⚙️ **System Administration**: An admin panel for user and system management.
- 🔄 **AI Migration Agent**: Intelligent data migration system with AI-powered agents ⭐ NEW
- 📊 **Schema Analysis**: Automatic schema comparison and compatibility scoring ⭐ NEW
- 🚀 **Parallel Processing**: Multi-worker migration for large datasets ⭐ NEW
- ✅ **Auto Validation**: Comprehensive validation and rollback capabilities ⭐ NEW

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
.
├── finx-ai-service/         # Backend (FastAPI)
│   ├── src/
│   │   ├── core/
│   │   │   ├── engine.py           # SQL engine utilities
│   │   │   ├── migration_agent.py  # AI migration system ⭐ NEW
│   │   │   ├── pipeline.py         # Pipeline framework
│   │   │   └── provider.py         # Provider interface
│   │   └── web/                    # Web API
│   └── demos/
│       └── demo_migration_agent.py # Migration demos ⭐ NEW
├── finx-ui/                 # Frontend (React)
├── deployment/              # Deployment scripts
└── docs/                    # Documentation
    ├── INDEX.md                    # Documentation index ⭐ NEW
    ├── ARCHITECTURE.md             # System architecture ⭐ NEW
    ├── MIGRATION_GUIDE.md          # Migration guide ⭐ NEW
    ├── MIGRATION_DIAGRAMS.md       # Visual diagrams ⭐ NEW
    ├── SYSTEM_DIAGRAMS.md          # Quick reference ⭐ NEW
    ├── AI_MIGRATION_README.md      # Migration overview ⭐ NEW
    └── QUICK_START.md              # Quick start guide
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- Docker and Docker Compose
- `uv` (Python package manager)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/chatbot.git
    cd chatbot
    ```

2.  **Setup the Backend:**

    ```bash
    cd finx-ai-service
    uv pip sync requirements.txt
    cp .env.example .env # and update with your database credentials
    uv run migrate.py # to run database migrations
    uv run run.py # to start the server
    ```

3.  **Setup the Frontend:**

    ```bash
    cd finx-ui
    npm install
    cp .env.example .env # and update with your backend API URL
    npm run dev
    ```

## 📖 Usage

- Access the application at `http://localhost:5173`
- Register a new account or log in with existing credentials.
- Start chatting with the AI, manage prompts, and configure database connections through the UI.

### 🤖 AI Migration System

Run intelligent data migrations with AI agents:

```bash
cd finx-ai-service/demos
python demo_migration_agent.py
```

**Features**:
- Automatic schema analysis and compatibility scoring
- AI-powered column mapping and transformation suggestions
- Multiple migration strategies (Full Copy, Incremental, Batch, Streaming)
- Parallel processing with configurable workers
- Real-time progress tracking and validation
- Automatic rollback on failures

**Documentation**:
- 📚 [Complete Documentation Index](docs/INDEX.md)
- 🏗️ [System Architecture](docs/ARCHITECTURE.md)
- 🚀 [Migration Guide](docs/MIGRATION_GUIDE.md)
- 📊 [Visual Diagrams](docs/MIGRATION_DIAGRAMS.md)
- ⚡ [Quick Start](docs/AI_MIGRATION_README.md)

## 🚀 Deployment

For a production deployment, it is recommended to use the provided Docker setup.

```bash
# Build and deploy the services
./deployment/deploy.sh production

# Check the health of the backend
cURL http://localhost:8000/health
```

For more detailed deployment instructions, see the [Deployment Guide](docs/DEPLOYMENT_GUIDE.md).

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started. Also, please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand our community standards.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.