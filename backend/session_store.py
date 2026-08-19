"""
Thread-safe in-memory session store.

Each session holds:
    - vector_db   : InMemoryVectorStore or None
    - sources     : list of {"type": "pdf"|"web", "name": str}
    - messages    : list of {"role": str, "content": str, "sources": list}
    - doc_count   : int
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionData:
    session_id: str
    vector_db: Optional[Any] = None
    sources: List[Dict[str, str]] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    doc_count: int = 0


class SessionStore:
    """Singleton in-memory store for all active sessions."""

    def __init__(self) -> None:
        self._store: Dict[str, SessionData] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(self) -> SessionData:
        """Create a new session and return it."""
        session_id = str(uuid.uuid4())
        data = SessionData(session_id=session_id)
        with self._lock:
            self._store[session_id] = data
        return data

    def get(self, session_id: str) -> Optional[SessionData]:
        """Return the SessionData for the given id, or None."""
        with self._lock:
            return self._store.get(session_id)

    def delete(self, session_id: str) -> bool:
        """Delete a session entirely. Returns True if it existed."""
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]
                return True
        return False

    def reset(self, session_id: str) -> Optional[SessionData]:
        """Reset a session's state but keep the session alive."""
        with self._lock:
            session = self._store.get(session_id)
            if session is None:
                return None
            session.vector_db = None
            session.sources = []
            session.messages = []
            session.doc_count = 0
        return session

    def list_ids(self) -> List[str]:
        with self._lock:
            return list(self._store.keys())


# Global singleton — imported by dependencies.py
_store = SessionStore()


def get_store() -> SessionStore:
    return _store
