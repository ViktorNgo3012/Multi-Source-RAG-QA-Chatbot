"""
Session router — /session/*

Endpoints:
    POST   /session/create            Create a new session
    GET    /session/{session_id}/status   Session info (doc count, sources)
    DELETE /session/{session_id}/reset    Wipe session state
    GET    /session/{session_id}/export   Export chat as plain text
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import get_session
from backend.models.schemas import (
    CreateSessionResponse,
    ExportResponse,
    ResetResponse,
    SessionStatusResponse,
    SourceInfo,
)
from backend.services.export_service import export_chat_as_text
from backend.session_store import get_store

router = APIRouter(prefix="/session", tags=["Session"])


@router.post(
    "/create",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new RAG session",
)
def create_session() -> CreateSessionResponse:
    """
    Creates a fresh isolated session and returns its `session_id`.
    Pass this ID in all subsequent requests.
    """
    store = get_store()
    session = store.create()
    return CreateSessionResponse(session_id=session.session_id)


@router.get(
    "/{session_id}/status",
    response_model=SessionStatusResponse,
    summary="Get session status",
)
def session_status(session_id: str) -> SessionStatusResponse:
    """Returns the current number of indexed chunks and all added sources."""
    session = get_session(session_id)
    return SessionStatusResponse(
        session_id=session_id,
        doc_count=session.doc_count,
        sources=[SourceInfo(**s) for s in session.sources],
    )


@router.delete(
    "/{session_id}/reset",
    response_model=ResetResponse,
    summary="Reset session state",
)
def reset_session(session_id: str) -> ResetResponse:
    """
    Clears the vector store, messages, and sources for the session.
    The session itself remains active.
    """
    store = get_store()
    result = store.reset(session_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return ResetResponse(session_id=session_id)


@router.get(
    "/{session_id}/export",
    response_model=ExportResponse,
    summary="Export chat history as plain text",
)
def export_chat(session_id: str) -> ExportResponse:
    """Returns the full chat transcript as a plain-text string."""
    session = get_session(session_id)
    text = export_chat_as_text(session.messages)
    return ExportResponse(session_id=session_id, content=text)
