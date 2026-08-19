"""
Multi-Source RAG Q&A ChatBot — FastAPI Backend
===============================================
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routers import chat, session, sources



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load the HuggingFace embedding model at startup so the first
    request is not penalised by model download / initialisation time."""
    from backend.dependencies import get_embeddings
    print("Loading embedding model...")
    get_embeddings()
    print("Embedding model ready.")
    yield
    print("Shutting down backend.")


# ------------------------------------------------------------------
# App factory
# ------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title="Multi-Source RAG Q&A ChatBot API",
    description=(
        "A Retrieval-Augmented Generation API that indexes PDFs and websites "
        "into per-session vector stores and answers questions using Groq LLMs."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

app.include_router(session.router)
app.include_router(sources.router)
app.include_router(chat.router)


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@app.get("/health", tags=["Health"], summary="Health check")
def health() -> dict:
    """Returns 200 OK when the service is running."""
    return {"status": "ok", "service": "Multi-Source RAG Q&A ChatBot API"}
