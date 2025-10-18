# FinX AI Chatbot - System Architecture

## 📐 Architecture Overview

This document provides comprehensive architecture diagrams and technical specifications for the FinX AI Agentic Chatbot system.

---

## 🏗️ High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    React Frontend (FinX UI)                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│  │  │   Chat     │  │ Connection │  │   Prompt   │  │   Admin    │ │  │
│  │  │ Interface  │  │ Management │  │ Management │  │   Panel    │ │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │         Context Providers (Auth, Theme, Navigation)        │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                           │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │ HTTPS/REST API
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                        APPLICATION LAYER                                  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (FinX AI Service)                    │   │
│  │                                                                    │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │                    API Routers                            │   │   │
│  │  │  • Auth Router      • Chat Router    • Connection Router │   │   │
│  │  │  • User Router      • Message Router • Prompt Router     │   │   │
│  │  │  • File Router      • Knowledge Router                   │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                    │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │                  AI Agent Engine                          │   │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │   │   │
│  │  │  │ Generation │  │ Retrieval  │  │ Migration  │         │   │   │
│  │  │  │  Pipeline  │  │  Pipeline  │  │   Agent    │         │   │   │
│  │  │  └────────────┘  └────────────┘  └────────────┘         │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                    │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │              Business Logic Layer                         │   │   │
│  │  │  • Authentication & Authorization                         │   │   │
│  │  │  • Connection Management                                  │   │   │
│  │  │  • Security & Encryption                                  │   │   │
│  │  │  • Health Monitoring                                      │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────────┐
│                          DATA LAYER                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │              Database Provider Factory                            │    │
│  │  ┌────────────────┐              ┌────────────────┐             │    │
│  │  │    Supabase    │              │   PostgreSQL   │             │    │
│  │  │    Provider    │              │    Provider    │             │    │
│  │  └────────────────┘              └────────────────┘             │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │              External Data Sources (via Connections)              │    │
│  │  • PostgreSQL  • MySQL      • MongoDB    • Snowflake             │    │
│  │  • AWS Athena  • BigQuery   • Redis      • Elasticsearch         │    │
│  │  • S3 Storage  • Azure Blob • GCS        • HDFS                  │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 AI Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI AGENT SYSTEM                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         Agent Orchestrator                               │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  • Task Planning & Decomposition                                │    │
│  │  • Agent Selection & Routing                                    │    │
│  │  • Execution Monitoring                                         │    │
│  │  • Result Aggregation                                           │    │
│  └────────────────────────────────────────────────────────────────┘    │
└───────────────┬─────────────────────────────────────────────────────────┘
                │
    ┌───────────┼───────────┬───────────────┬──────────────┐
    │           │           │               │              │
    ▼           ▼           ▼               ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐
│  SQL   │ │ Data   │ │ Schema   │ │  Migration   │ │ Prompt   │
│ Agent  │ │ Agent  │ │  Agent   │ │    Agent     │ │  Agent   │
└────────┘ └────────┘ └──────────┘ └──────────────┘ └──────────┘
    │           │           │               │              │
    └───────────┴───────────┴───────────────┴──────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Shared Resources    │
                │  • LLM Provider       │
                │  • Vector Store       │
                │  • Memory System      │
                │  • Tool Registry      │
                └───────────────────────┘
```

---

## 🗄️ Database Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA OVERVIEW                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│       users          │         │        auths         │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │◄────────┤ id (PK)              │
│ name                 │         │ email                │
│ email                │         │ password_hash        │
│ role                 │         │ active               │
│ profile_image_url    │         │ created_at           │
│ created_at           │         └──────────────────────┘
│ updated_at           │
└──────────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────────┐         ┌──────────────────────┐
│       chats          │         │      folders         │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │         │ id (PK)              │
│ user_id (FK)         │◄────────┤ user_id (FK)         │
│ title                │         │ name                 │
│ folder_id (FK)       │─────────►│ parent_id (FK)       │
│ archived             │         │ created_at           │
│ pinned               │         └──────────────────────┘
│ created_at           │
└──────────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────────┐         ┌──────────────────────┐
│      messages        │         │  message_reactions   │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │◄────────┤ id (PK)              │
│ chat_id (FK)         │         │ message_id (FK)      │
│ user_id (FK)         │         │ user_id (FK)         │
│ content              │         │ reaction             │
│ role                 │         │ created_at           │
│ created_at           │         └──────────────────────┘
└──────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│    connections       │         │ connection_templates │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │         │ id (PK)              │
│ user_id (FK)         │         │ name                 │
│ name                 │         │ type                 │
│ type                 │         │ provider             │
│ provider             │         │ config_schema        │
│ host                 │         │ description          │
│ port                 │         └──────────────────────┘
│ database_name        │
│ credentials (enc)    │                 │
│ status               │                 │ 1:N
│ created_at           │                 ▼
└──────────────────────┘         ┌──────────────────────┐
         │                       │   connection_logs    │
         │ 1:N                   ├──────────────────────┤
         └──────────────────────►│ id (PK)              │
                                 │ connection_id (FK)   │
                                 │ action               │
                                 │ status               │
                                 │ error_message        │
                                 │ created_at           │
                                 └──────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│      prompts         │         │      knowledge       │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │         │ id (PK)              │
│ user_id (FK)         │         │ user_id (FK)         │
│ command              │         │ name                 │
│ title                │         │ description          │
│ content              │         │ data                 │
│ created_at           │         │ created_at           │
└──────────────────────┘         └──────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│       files          │         │      memories        │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │         │ id (PK)              │
│ user_id (FK)         │         │ user_id (FK)         │
│ filename             │         │ content              │
│ path                 │         │ created_at           │
│ hash                 │         └──────────────────────┘
│ created_at           │
└──────────────────────┘
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYERS                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                                               │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  • HTTPS/TLS Encryption                                         │    │
│  │  • CORS Policy Configuration                                    │    │
│  │  • Rate Limiting                                                │    │
│  │  • DDoS Protection                                              │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 2: Authentication & Authorization                                 │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  • JWT Token-Based Authentication                               │    │
│  │  • Role-Based Access Control (RBAC)                            │    │
│  │  • Session Management                                           │    │
│  │  • Password Hashing (bcrypt)                                    │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 3: Data Security                                                  │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  • Credential Encryption (AES-256)                              │    │
│  │  • Sensitive Data Masking                                       │    │
│  │  • SQL Injection Prevention                                     │    │
│  │  • Input Validation (Pydantic)                                  │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 4: Audit & Monitoring                                             │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  • Security Event Logging                                       │    │
│  │  • Access Audit Trail                                           │    │
│  │  • Anomaly Detection                                            │    │
│  │  • Health Monitoring                                            │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    USER CHAT REQUEST FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

User Input
    │
    ▼
┌─────────────────┐
│  React Frontend │
│  • Input Form   │
│  • Validation   │
└────────┬────────┘
         │ POST /api/v1/messages
         ▼
┌─────────────────┐
│  API Gateway    │
│  • Auth Check   │
│  • Rate Limit   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Message Router  │
│  • Route Logic  │
│  • Validation   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Agent       │
│  Orchestrator   │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ▼         ▼            ▼          ▼
┌────────┐ ┌──────┐ ┌──────────┐ ┌────────┐
│  SQL   │ │ Data │ │ Retrieval│ │ Prompt │
│ Agent  │ │Agent │ │  Agent   │ │ Agent  │
└───┬────┘ └──┬───┘ └────┬─────┘ └───┬────┘
    │         │          │           │
    └─────────┴──────────┴───────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  LLM Provider    │
         │  • OpenAI        │
         │  • Anthropic     │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Response        │
         │  Aggregation     │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Database        │
         │  • Save Message  │
         │  • Update Chat   │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  WebSocket/HTTP  │
         │  Response        │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  React Frontend  │
         │  • Display       │
         │  • Update UI     │
         └──────────────────┘
```

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         Load Balancer                                    │
│                    (Nginx / AWS ALB / Cloudflare)                       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│   Frontend Container      │   │   Backend Container       │
│   (React + Nginx)         │   │   (FastAPI + Python)      │
│                           │   │                           │
│  • Static Assets          │   │  • API Endpoints          │
│  • Client-Side Routing    │   │  • AI Agent Engine        │
│  • CDN Integration        │   │  • Business Logic         │
└───────────────────────────┘   └───────────┬───────────────┘
                                            │
                                            ▼
                        ┌───────────────────────────────┐
                        │   Database Layer              │
                        │                               │
                        │  ┌─────────────────────────┐ │
                        │  │  Primary Database       │ │
                        │  │  (Supabase/PostgreSQL)  │ │
                        │  └─────────────────────────┘ │
                        │                               │
                        │  ┌─────────────────────────┐ │
                        │  │  Redis Cache            │ │
                        │  │  (Session/Rate Limit)   │ │
                        │  └─────────────────────────┘ │
                        └───────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    External Services                                     │
│  • OpenAI API          • AWS S3              • Monitoring (DataDog)     │
│  • Anthropic API       • Email Service       • Logging (ELK Stack)      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  COMPONENT INTERACTION FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

Frontend Components          Backend Services           Data Layer
─────────────────────        ────────────────           ──────────

┌──────────────┐
│ Chat Page    │
└──────┬───────┘
       │ useChat()
       ▼
┌──────────────┐            ┌──────────────┐
│ Chat Hook    │───────────►│ Chat API     │
└──────────────┘   HTTP     └──────┬───────┘
                                   │
┌──────────────┐            ┌──────▼───────┐         ┌──────────┐
│ Auth Context │───────────►│ Auth Service │────────►│ Database │
└──────────────┘            └──────────────┘         └──────────┘
       │
       │ JWT Token
       ▼
┌──────────────┐            ┌──────────────┐
│ API Client   │───────────►│ API Gateway  │
└──────────────┘            └──────┬───────┘
                                   │
┌──────────────┐            ┌──────▼───────┐         ┌──────────┐
│ Connection   │───────────►│ Connection   │────────►│ External │
│ Manager      │            │ Service      │         │ Data     │
└──────────────┘            └──────────────┘         └──────────┘
                                   │
                            ┌──────▼───────┐
                            │ AI Agent     │
                            │ Engine       │
                            └──────────────┘
```

---

## 🔧 Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: HeroUI + Tailwind CSS
- **State Management**: React Context API
- **Routing**: React Router v6
- **HTTP Client**: Fetch API

### Backend
- **Framework**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Database**: PostgreSQL / Supabase

### AI/ML
- **LLM Integration**: OpenAI, Anthropic
- **Vector Store**: (Configurable)
- **SQL Parsing**: sqlparse, sqlglot
- **Async HTTP**: aiohttp

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Package Manager**: uv (Python)
- **CI/CD**: GitHub Actions (configurable)

---

## 📈 Scalability Considerations

### Horizontal Scaling
- Stateless API design for easy replication
- Load balancer distribution
- Database connection pooling
- Redis for distributed caching

### Vertical Scaling
- Optimized database queries
- Efficient connection management
- Async/await patterns
- Resource monitoring

### Performance Optimization
- Database indexing strategy
- Query result caching
- CDN for static assets
- Lazy loading components

---

## 🔍 Monitoring & Observability

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Centralized log aggregation
- Security event logging

### Metrics
- API response times
- Database query performance
- Connection health status
- Error rates and types

### Health Checks
- Application health endpoint
- Database connectivity
- External service availability
- Resource utilization

---

**Last Updated**: 2025-01-18
**Version**: 1.0.0
