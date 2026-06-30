"""Central configuration, loaded from the project .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load the .env that already lives at the project root (one level above backend/).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# --- Qdrant ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "mcp_notes")

# --- Embeddings (local, free) ---
EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
EMBED_DIM = 384  # BAAI/bge-small-en-v1.5 output dimension

# --- Agent LLM (OpenRouter, free tier) ---
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get(
    "OPENROUTER_MODEL", "openai/gpt-oss-120b:free"
)

# --- Web search (optional) ---
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# --- Single-user demo: every record is scoped to this id so multi-user is a
#     small change later, not a rewrite. ---
DEFAULT_USER = os.environ.get("DEFAULT_USER", "local")

# --- Paths ---
DATA_DIR = PROJECT_ROOT / "backend" / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "app.db"

# --- CORS (Next.js dev server) ---
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000"
).split(",")
