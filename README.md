# Video2Content (VideoScribe)

> **Paste a video link → Get the complete spoken content.**

Video2Content is a modern web application that converts online videos or uploaded video files into clean, readable text content. It abstracts away caption scraping, audio extraction, and speech-to-text processing to deliver clean paragraphs, timestamp navigation, in-transcript keyword search, and multi-format exports.

---

## 🏗️ Architecture Overview

```
                      +-------------------+
                      |   Next.js (App)   |
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |  FastAPI Backend  |
                      +----+---------+----+
                           |         |
                  +--------+         +--------+
                  v                           v
        +-------------------+       +-------------------+
        | PostgreSQL 16 DB  |       | Redis (Broker)    |
        +-------------------+       +---------+---------+
                                              |
                                              v
                                    +-------------------+
                                    |   Celery Worker   |
                                    | (yt-dlp + ffmpeg) |
                                    +---------+---------+
                                              |
                                              v
                                    +-------------------+
                                    |   MinIO / S3      |
                                    +-------------------+
```

---

## 🚀 Quick Start (Docker Compose)

The easiest way to run the entire stack locally:

```bash
# 1. Clone the repository & enter directory
cd VideoScribe

# 2. Copy environment configuration
cp .env.example .env

# 3. Start all services in the background
docker compose up -d

# 4. Open in browser:
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
# MinIO Storage Console: http://localhost:9001 (minioadmin / minioadmin)
```

---

## 🛠️ Local Development (Standalone)

### Backend

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Start FastAPI dev server
cd backend
uvicorn app.main:app --reload --port 8000
```

### Worker

```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Repository Structure

```
video2content/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI REST endpoints
│   │   ├── core/         # Config, security, exceptions
│   │   ├── db/           # SQLAlchemy models and session
│   │   ├── providers/    # Platform adapters & STT engines
│   │   ├── schemas/      # Pydantic request/response models
│   │   ├── services/     # URL validation, audio extraction, cleaning
│   │   └── workers/      # Celery task definitions
│   └── tests/            # Pytest test suite
│
├── frontend/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Reusable UI & viewer components
│   ├── hooks/            # Custom React hooks (polling, search)
│   ├── services/         # Type-safe API client
│   └── types/            # TypeScript interfaces
│
├── infrastructure/
│   └── docker/           # Dockerfiles for backend, worker, frontend
│
├── tests/                # End-to-end integration tests
├── .env.example          # Environment variables template
├── docker-compose.yml    # Multi-container orchestration
└── Prd.md                # Product Requirements Document
```

---

## 📜 License

MIT License.
