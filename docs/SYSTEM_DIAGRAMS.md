# FinX System Diagrams - Quick Reference

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FINX AI CHATBOT SYSTEM                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND LAYER (React + TypeScript + Vite)                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │   Chat   │ │  Prompt  │ │Connection│ │  Admin   │ │  Files   │    │
│  │   UI     │ │  Manager │ │  Manager │ │  Panel   │ │  Upload  │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ REST API (HTTPS)
┌───────────────────────────────▼─────────────────────────────────────────┐
│  BACKEND LAYER (FastAPI + Python 3.12)                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  API ROUTERS                                                      │  │
│  │  /auth  /chats  /messages  /connections  /prompts  /files       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  AI AGENT ENGINE                                                  │  │
│  │  • Schema Analyzer  • Migration Planner  • Data Transformer      │  │
│  │  • Migration Executor  • Validator                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│  DATA LAYER                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │
│  │   Supabase     │  │   PostgreSQL   │  │  External DBs  │           │
│  │   (Primary)    │  │   (Optional)   │  │  (Connections) │           │
│  └────────────────┘  └────────────────┘  └────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```



## 🔄 Data Migration Flow

```
USER REQUEST
     │
     ▼
┌─────────────────────┐
│  1. SCHEMA ANALYSIS │
│  • Introspect DBs   │
│  • Compare schemas  │
│  • Calculate score  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. PLAN CREATION   │
│  • Select strategy  │
│  • Map columns      │
│  • Assess risks     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. TRANSFORMATION  │
│  • Type conversion  │
│  • Data cleaning    │
│  • Enrichment       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. EXECUTION       │
│  • Batch processing │
│  • Parallel workers │
│  • Progress track   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. VALIDATION      │
│  • Row count check  │
│  • Data integrity   │
│  • Schema verify    │
└──────────┬──────────┘
           │
           ▼
    ┌──────────┐
    │ SUCCESS  │
    └──────────┘
```

## 🗄️ Database Models

```
users ──┬── chats ──── messages ──── message_reactions
        │
        ├── prompts
        │
        ├── connections ──── connection_logs
        │
        ├── files
        │
        ├── knowledge
        │
        └── memories

auths ──── users

folders ──── chats

groups ──── users

channels ──── messages
```

## 🔐 Security Layers

```
Layer 1: Network Security
  ├── HTTPS/TLS
  ├── CORS Policy
  └── Rate Limiting

Layer 2: Authentication
  ├── JWT Tokens
  ├── Password Hashing
  └── Session Management

Layer 3: Authorization
  ├── RBAC
  ├── Permission Checks
  └── Resource Access

Layer 4: Data Security
  ├── Credential Encryption
  ├── Data Masking
  └── SQL Injection Prevention

Layer 5: Audit & Monitoring
  ├── Security Logging
  ├── Access Tracking
  └── Anomaly Detection
```

## 📊 Technology Stack

```
FRONTEND
├── React 18
├── TypeScript
├── Vite
├── Tailwind CSS
├── HeroUI
└── React Router

BACKEND
├── FastAPI
├── Python 3.12
├── SQLAlchemy
├── Pydantic
├── JWT Auth
└── bcrypt

AI/ML
├── OpenAI API
├── Anthropic API
├── sqlparse
├── sqlglot
└── aiohttp

DATABASE
├── PostgreSQL
├── Supabase
└── Redis (optional)

DEVOPS
├── Docker
├── Docker Compose
├── uv (Python)
└── GitHub Actions
```

---

**Quick Reference Guide**  
**Version**: 1.0.0  
**Date**: 2025-01-18
