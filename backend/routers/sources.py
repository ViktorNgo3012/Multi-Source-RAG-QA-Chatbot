"""
Sources router — /sources/*

Endpoints:
    POST  /sources/pdf          Upload one or more PDFs (multipart/form-data)
    POST  /sources/website      Add a website URL (JSON body)
    GET   /sources/{session_id} List all sources added to the session
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.dependencies import get_embeddings, get_session
from backend.models.schemas import (
    AddSourceResponse,
    AddWebsiteRequest,
    ListSourcesResponse,
    SourceInfo,
)
from backend.services.document_service import process_pdf, process_website

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.post(
    "/pdf",
    response_model=List[AddSourceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and index one or more PDFs",
)
async def add_pdf(
    session_id: str = Form(..., description="Session ID from POST /session/create"),
    files: List[UploadFile] = File(..., description="One or more PDF files"),
) -> List[AddSourceResponse]:
    """
    Accepts multipart/form-data with:
    - `session_id` (form field)
    - `files`      (one or more PDF files)

    Each PDF is split into chunks and added to the session's vector store.
    """
    session = get_session(session_id)
    embeddings = get_embeddings()

    results: List[AddSourceResponse] = []
    already_added = {s["name"] for s in session.sources if s["type"] == "pdf"}

    for upload in files:
        filename = upload.filename or "uploaded.pdf"

        if filename in already_added:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"'{filename}' has already been added to this session.",
            )

        file_bytes = await upload.read()
        ok, chunks_added, error = process_pdf(file_bytes, filename, session, embeddings)

        if not ok:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process '{filename}': {error}",
            )

        results.append(
            AddSourceResponse(
                session_id=session_id,
                source=SourceInfo(type="pdf", name=filename),
                chunks_added=chunks_added,
                message=f"'{filename}' indexed successfully.",
            )
        )

    return results


@router.post(
    "/website",
    response_model=AddSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add and index a website URL",
)
def add_website(body: AddWebsiteRequest) -> AddSourceResponse:
    """
    Scrapes the given URL, splits the content into chunks,
    and adds them to the session's vector store.
    """
    session = get_session(body.session_id)
    embeddings = get_embeddings()

    already_added = {s["name"] for s in session.sources if s["type"] == "web"}
    if body.url in already_added:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{body.url}' has already been added to this session.",
        )

    ok, chunks_added, error = process_website(body.url, session, embeddings)

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process URL '{body.url}': {error}",
        )

    return AddSourceResponse(
        session_id=body.session_id,
        source=SourceInfo(type="web", name=body.url),
        chunks_added=chunks_added,
        message=f"Website '{body.url}' indexed successfully.",
    )


@router.get(
    "/{session_id}",
    response_model=ListSourcesResponse,
    summary="List all indexed sources for a session",
)
def list_sources(session_id: str) -> ListSourcesResponse:
    """Returns all PDF and website sources that have been indexed."""
    session = get_session(session_id)
    return ListSourcesResponse(
        session_id=session_id,
        sources=[SourceInfo(**s) for s in session.sources],
    )
