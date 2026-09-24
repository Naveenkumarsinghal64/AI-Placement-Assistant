from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import applications, assistant, documents, resume
from app.config import CORS_ORIGINS

app = FastAPI(
    title="AI Placement Assistant API",
    description="Backend API for tracking placement applications and AI-powered "
    "resume analysis, job matching, and document Q&A.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(resume.router)
app.include_router(documents.router)
app.include_router(assistant.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
