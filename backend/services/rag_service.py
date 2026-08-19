"""
RAG query service.

Handles:
- Building the prompt
- Retrieving relevant chunks from the session's vector store
- Calling the Groq LLM
- Returning the structured answer with source metadata
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from langchain_groq import ChatGroq

from backend.session_store import SessionData


# ------------------------------------------------------------------
# Prompt builder
# ------------------------------------------------------------------

def build_prompt(query: str, context: str) -> str:
    return f"""You are a helpful AI assistant.

Answer the user's question ONLY using the context below.
Be clear and concise. If useful, structure the answer with short bullet points.

If the answer is not found in the context, reply exactly:
"I couldn't find that information in the uploaded sources."

Context:
{context}

Question:
{query}
"""


# ------------------------------------------------------------------
# Core RAG pipeline
# ------------------------------------------------------------------

def run_rag_query(
    query: str,
    session: SessionData,
    model: str,
    temperature: float,
    k_chunks: int,
    show_sources: bool,
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Retrieve relevant chunks, build a prompt, query the LLM.

    Returns:
        answer        : str
        source_records: list of {"label": str, "snippet": str}
    """
    if session.vector_db is None:
        return (
            "No knowledge sources have been added yet. "
            "Please upload a PDF or add a website URL first.",
            [],
        )

    # --- Retrieve ---
    retrieved_docs = session.vector_db.similarity_search(query=query, k=k_chunks)

    context = ""
    source_records: List[Dict[str, str]] = []

    for doc in retrieved_docs:
        context += doc.page_content + "\n\n"
        meta = doc.metadata or {}
        label = meta.get("source", "Unknown source")
        if "page" in meta:
            label += f" (page {meta['page']})"
        source_records.append(
            {
                "label": label,
                "snippet": doc.page_content[:400]
                + ("..." if len(doc.page_content) > 400 else ""),
            }
        )

    # --- Generate ---
    prompt = build_prompt(query, context)
    llm = ChatGroq(model=model, temperature=temperature)
    result = llm.invoke(prompt)
    answer: str = result.content

    return answer, source_records if show_sources else []
