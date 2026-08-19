"""
Document ingestion service.

Handles:
- Splitting raw LangChain documents into chunks
- Adding chunks to a session's InMemoryVectorStore
- Processing uploaded PDF bytes
- Processing a website URL
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Tuple

from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import get_settings
from backend.session_store import SessionData


def split_documents(docs: List[Any]) -> List[Any]:
    """Split LangChain documents into overlapping chunks."""
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(docs)


def add_to_store(
    chunks: List[Any],
    source_label: Dict[str, str],
    session: SessionData,
    embeddings: Any,
) -> int:
    """
    Embed chunks and add to the session's vector store.
    Creates the store if it doesn't exist yet.
    Returns number of chunks added.
    """
    if not chunks:
        return 0

    if session.vector_db is None:
        session.vector_db = InMemoryVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
        )
    else:
        session.vector_db.add_documents(chunks)

    session.doc_count += len(chunks)
    session.sources.append(source_label)
    return len(chunks)


def process_pdf(
    file_bytes: bytes,
    filename: str,
    session: SessionData,
    embeddings: Any,
) -> Tuple[bool, int, str]:
    """
    Process a PDF from raw bytes.

    Returns (success, chunks_added, error_message).
    """
    # Write to a named temp file so PyPDFLoader can read it
    suffix = os.path.splitext(filename)[-1] or ".pdf"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        chunks = split_documents(docs)
        added = add_to_store(
            chunks,
            {"type": "pdf", "name": filename},
            session,
            embeddings,
        )
        return True, added, ""
    except Exception as exc:
        return False, 0, str(exc)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def process_website(
    url: str,
    session: SessionData,
    embeddings: Any,
) -> Tuple[bool, int, str]:
    """
    Scrape and process a website URL.

    Returns (success, chunks_added, error_message).
    """
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        chunks = split_documents(docs)
        added = add_to_store(
            chunks,
            {"type": "web", "name": url},
            session,
            embeddings,
        )
        return True, added, ""
    except Exception as exc:
        return False, 0, str(exc)
