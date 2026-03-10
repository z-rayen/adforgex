# AdForgeX 🚀

An AI-powered ad generation platform that creates high-converting ad copy, hooks, and creative strategies for any product — in seconds.

AdForgeX combines a **6-step LLM pipeline**, **RAG-based knowledge retrieval**, **web scraping for competitor intelligence**, and **vision-based image analysis** into a single full-stack application.

---

## ✨ Features

- **6-Step AI Pipeline** — Product analysis → Competitor intelligence → Image analysis → Audience insights → Strategy → Ad generation
- **RAG Knowledge Base** — ChromaDB-powered retrieval of high-performing ad patterns that grows richer with every run
- **Competitor Scraping** — Automatically scrapes competitor product listings and reviews to inform ad strategy
- **Vision Analysis** — Analyzes uploaded product images using a multimodal LLM (Llama 4 Scout) to extract visual selling points
- **Image Validation** — Detects image/product mismatches before running the full pipeline (with humorous feedback 😄)
- **Auth System** — JWT-based user authentication with SQLite storage
- **Real-Time Progress** — Server-Sent Events (SSE) stream pipeline step updates live to the frontend
- **React Frontend** — Clean dashboard built with React + TypeScript + Vite, served by the FastAPI backend
- **Docker-ready** — Full Docker Compose setup for development and production

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| LLM | Groq API (Llama 3.3 70B + Llama 4 Scout Vision) |
| RAG | ChromaDB, `sentence-transformers` (all-MiniLM-L6-v2) |
| Scraping | Playwright |
| Auth | JWT (python-jose), SQLite |
| Frontend | React 18, TypeScript, Vite, CSS Modules |
| Deployment | Docker, Docker Compose, Nginx |

---

## 📂 Project Structure

```
adforgex/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic settings (env vars)
│   ├── models.py            # Request/response schemas
│   ├── pipeline.py          # 6-step pipeline orchestrator
│   ├── auth.py              # JWT auth logic
│   ├── database.py          # SQLite init & helpers
│   └── routers/
│       ├── auth_router.py   # /auth/* endpoints
│       ├── pipeline_router.py # /pipeline/* endpoints (SSE)
│       └── rag_router.py    # /rag/* endpoints
├── llm/
│   ├── groq_client.py       # Groq API client (text + vision)
│   ├── prompts.py           # All LLM prompt templates
│   └── steps.py             # Individual pipeline step runners
├── rag/
│   ├── rag_engine.py        # ChromaDB interface
│   └── seed_data.py         # Seed the knowledge base
├── frontend-react/          # React + TypeScript frontend (Vite)
│   └── src/
│       ├── pages/           # Dashboard, AuthPage
│       ├── components/      # ProductForm, Results, PipelineTracker, ...
│       └── context/         # AuthContext
├── nginx/
│   └── nginx.conf           # Reverse proxy config
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- [Groq API key](https://console.groq.com/) (free tier available)
- Docker & Docker Compose (optional, for containerized setup)

### 1. Clone & configure

```bash
git clone https://github.com/your-username/adforgex.git
cd adforgex
cp .env.example .env
```

Edit `.env` and fill in your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Install backend dependencies

```bash
pip install -r requirements.txt
playwright install chromium   # for competitor scraping
```

### 3. Seed the RAG knowledge base

```bash
python rag/seed_data.py
```

### 4. Build the React frontend

```bash
cd frontend-react
npm install
npm run build
cd ..
```

### 5. Start the server

```bash
uvicorn backend.main:app --reload --port 8000
```

Visit [http://localhost:8000](http://localhost:8000) — the FastAPI backend serves the React frontend automatically.

API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🐳 Docker Setup

### Development (with hot-reload frontend)

```bash
docker compose --profile dev up --build
```

- Backend: [http://localhost:8000](http://localhost:8000)
- React dev server: [http://localhost:3000](http://localhost:3000)

### Production

```bash
docker compose --profile production up --build -d
```

This starts the AdForge API + Nginx reverse proxy. SSL certificates can be placed in `nginx/ssl/`.

---

## ⚙️ Configuration

All settings are loaded from environment variables (or `.env`):

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Your Groq API key |
| `TEXT_MODEL` | `llama-3.3-70b-versatile` | LLM for text generation |
| `VISION_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` | LLM for image analysis |
| `CHROMA_DB_PATH` | `./chroma_db` | Path to ChromaDB storage |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence embedding model |
| `RAG_TOP_K` | `5` | Number of RAG results to retrieve |
| `SCRAPE_TIMEOUT` | `15` | Competitor scraping timeout (seconds) |
| `JWT_SECRET` | `changeme_in_production` | Secret key for JWT tokens |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

---

## 🔌 API Overview

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT token |

### Pipeline

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/pipeline/generate` | Run the full ad generation pipeline (returns SSE stream) |

The pipeline streams real-time step updates via Server-Sent Events, then delivers the final ad result.

### RAG

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/rag/ingest` | Add a new ad pattern to the knowledge base |
| `GET` | `/rag/search?q=...` | Search the knowledge base |

### System

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check (RAG status, API key set) |
| `GET` | `/docs` | Interactive Swagger UI |

---

## 🧠 The 6-Step Pipeline

1. **Product Analysis** — Extracts USPs, pain points, and key selling points using RAG-retrieved patterns
2. **Competitor Intelligence** — Scrapes competitor listings and analyzes market positioning gaps
3. **Image Analysis** — Validates uploaded images match the product, then extracts visual selling cues
4. **Audience Insights** — Synthesizes user pain points, questions, and use cases
5. **Ad Strategy** — Selects the optimal messaging angle (problem-solution, UGC, luxury, fear, etc.)
6. **Ad Generation** — Produces a final hook, caption, CTA, and visual recommendations

Each completed run automatically saves scraped ads and image descriptions back into the RAG knowledge base, improving future outputs over time.
