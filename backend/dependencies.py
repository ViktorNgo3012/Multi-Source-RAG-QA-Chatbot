"""
FastAPI dependency-injection helpers.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import HTTPException, status

from backend.config import get_settings
from backend.session_store import SessionData, SessionStore, get_store


# ------------------------------------------------------------------
# Embeddings — created once, reused across all requests
# ------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_embeddings():
    """Return a cached HuggingFaceEmbeddings instance."""
    from langchain_huggingface import HuggingFaceEmbeddings

    settings = get_settings()
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


# ------------------------------------------------------------------
# Session lookup
# ------------------------------------------------------------------

def get_session(session_id: str, store: SessionStore = None) -> SessionData:
    """
    Resolve a session_id to its SessionData.
    Raises 404 if the session does not exist.
    Used as a FastAPI dependency via Depends().
    """
    if store is None:
        store = get_store()
    session = store.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found. Create one via POST /session/create.",
        )
    return session
