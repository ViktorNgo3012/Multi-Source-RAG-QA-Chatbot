"""
Chat router — /chat/*

Endpoints:
    POST  /chat/query                 Send a question, get an AI answer
    GET   /chat/{session_id}/history  Retrieve full chat history
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import get_session
from backend.models.schemas import (
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    SourceChunk,
)
from backend.services.rag_service import run_rag_query

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/query",
    response_model=ChatResponse,
    summary="Ask a question against indexed sources",
)
def query(body: ChatRequest) -> ChatResponse:
    """
    Runs the full RAG pipeline:
    1. Retrieves `k_chunks` most relevant document chunks from the vector store
    2. Injects them into a prompt
    3. Calls the selected Groq LLM
    4. Returns the answer and optionally the source snippets

    The query and answer are appended to the session's chat history.
    """
    session = get_session(body.session_id)

    if session.vector_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No knowledge sources indexed yet. Add a PDF or website first.",
        )

    answer, source_records = run_rag_query(
        query=body.query,
        session=session,
        model=body.model,
        temperature=body.temperature,
        k_chunks=body.k_chunks,
        show_sources=body.show_sources,
    )

    # Persist conversation history in session
    session.messages.append({"role": "user", "content": body.query, "sources": []})
    session.messages.append(
        {"role": "assistant", "content": answer, "sources": source_records}
    )

    return ChatResponse(
        session_id=body.session_id,
        query=body.query,
        answer=answer,
        sources=[SourceChunk(**s) for s in source_records],
    )


@router.get(
    "/{session_id}/history",
    response_model=ChatHistoryResponse,
    summary="Retrieve full chat history for a session",
)
def chat_history(session_id: str) -> ChatHistoryResponse:
    """Returns all messages (user + assistant) stored in the session."""
    session = get_session(session_id)
    messages = [
        ChatMessage(
            role=msg["role"],
            content=msg["content"],
            sources=[SourceChunk(**s) for s in msg.get("sources", [])],
        )
        for msg in session.messages
    ]
    return ChatHistoryResponse(session_id=session_id, messages=messages)
