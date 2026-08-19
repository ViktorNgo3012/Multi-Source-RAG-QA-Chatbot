"""
All Pydantic request and response schemas for the API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


# ===========================================================
# SHARED
# ===========================================================

class SourceInfo(BaseModel):
    type: Literal["pdf", "web"]
    name: str


class SourceChunk(BaseModel):
    label: str
    snippet: str


# ===========================================================
# SESSION
# ===========================================================

class CreateSessionResponse(BaseModel):
    session_id: str
    message: str = "Session created successfully."


class SessionStatusResponse(BaseModel):
    session_id: str
    doc_count: int
    sources: List[SourceInfo]


class ResetResponse(BaseModel):
    session_id: str
    message: str = "Session reset successfully."


class ExportResponse(BaseModel):
    session_id: str
    content: str


# ===========================================================
# SOURCES
# ===========================================================

class AddWebsiteRequest(BaseModel):
    session_id: str
    url: str = Field(..., description="Full URL of the website to scrape and index.")


class AddSourceResponse(BaseModel):
    session_id: str
    source: SourceInfo
    chunks_added: int
    message: str


class ListSourcesResponse(BaseModel):
    session_id: str
    sources: List[SourceInfo]


# ===========================================================
# CHAT
# ===========================================================

class ChatRequest(BaseModel):
    session_id: str
    query: str = Field(..., min_length=1, description="User's question.")
    model: str = "llama-3.3-70b-versatile"
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    k_chunks: int = Field(default=3, ge=1, le=8)
    show_sources: bool = True


class ChatResponse(BaseModel):
    session_id: str
    query: str
    answer: str
    sources: List[SourceChunk]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    sources: List[SourceChunk] = []


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
