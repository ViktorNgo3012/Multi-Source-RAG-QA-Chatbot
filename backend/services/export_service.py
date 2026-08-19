"""
Export service.

Converts session chat history to a downloadable plain-text format.
"""

from __future__ import annotations

from typing import Any, Dict, List


def export_chat_as_text(messages: List[Dict[str, Any]]) -> str:
    """
    Format chat messages as a human-readable plain-text transcript.

    Args:
        messages: list of {"role": "user"|"assistant", "content": str, ...}

    Returns:
        Formatted string ready for download.
    """
    lines: List[str] = []
    for msg in messages:
        role = "You" if msg.get("role") == "user" else "Assistant"
        lines.append(f"{role}: {msg.get('content', '')}\n")
    return "\n".join(lines)
