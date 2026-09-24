import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
VECTORSTORE_DIR = APP_DIR / "vectorstore"
UPLOADS_DIR = BASE_DIR.parent / "uploads"
RESUME_UPLOADS_DIR = UPLOADS_DIR / "resumes"
DOCUMENT_UPLOADS_DIR = UPLOADS_DIR / "documents"

for directory in (DATA_DIR, VECTORSTORE_DIR, RESUME_UPLOADS_DIR, DOCUMENT_UPLOADS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

APPLICATIONS_FILE = DATA_DIR / "applications.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))
RETRIEVAL_TOP_K = int(os.getenv("RAG_TOP_K", "4"))

CORS_ORIGINS = ["*"]
