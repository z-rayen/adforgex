# AdForge — Full-Stack AI Ad Generation System

## Architecture Overview

```
adforge/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── pipeline.py          # Orchestrates all 6 pipeline steps
│   ├── config.py            # Settings & env vars
│   ├── models.py            # Pydantic request/response models
│   └── routers/
│       ├── pipeline_router.py
│       └── rag_router.py
├── rag/
│   ├── rag_engine.py        # ChromaDB vector store + retrieval
│   ├── embeddings.py        # Sentence transformer embeddings
│   └── seed_data.py         # Seed knowledge base with ad patterns
├── scraper/
│   ├── scraper.py           # Playwright + BS4 web scraper
│   ├── ad_parser.py         # Extract ad elements from scraped HTML
│   └── image_downloader.py  # Download & encode competitor images
├── llm/
│   ├── groq_client.py       # Groq API (text + vision)
│   ├── steps.py             # Each pipeline step as a function
│   └── prompts.py           # All LLM prompts
├── frontend/
│   └── index.html           # Full UI (served by FastAPI)
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Copy and fill env vars
cp .env.example .env

# 4. Seed the RAG knowledge base
python rag/seed_data.py

# 5. Run the server
uvicorn backend.main:app --reload --port 8000
```

## Environment Variables

```env
GROQ_API_KEY=gsk_...
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
SCRAPE_TIMEOUT=15
MAX_IMAGES_PER_PRODUCT=5
```
