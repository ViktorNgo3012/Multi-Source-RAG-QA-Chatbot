from dotenv import load_dotenv
 
load_dotenv()
 
import os
import json
from time import sleep
from datetime import datetime
 
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.vectorstores import InMemoryVectorStore
 
# =============================================================
# PAGE CONFIG
# =============================================================
st.set_page_config(
    page_title="Multi-Source Q&A ChatBot",
    page_icon="🤖",
    layout="wide"
)
 
# =============================================================
# CONSTANTS
# =============================================================
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]
 
# =============================================================
# CACHED RESOURCES (loaded only once per server, not per rerun)
# =============================================================
@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
 
 
def get_llm(model_name: str, temperature: float):
    return ChatGroq(
        model=model_name,
        temperature=temperature
    )
 
 
# =============================================================
# SESSION STATE INITIALIZATION
# =============================================================
defaults = {
    "vector_db": None,
    "messages": [],
    "sources": [],          # list of dicts: {"type": "pdf"/"web", "name": str}
    "doc_count": 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value
 
 
# =============================================================
# CORE FUNCTIONS
# =============================================================
def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_documents(docs)
 
 
def add_documents_to_store(docs, source_label):
    """Add split docs to the (possibly empty) vector store."""
    if not docs:
        return
 
    embeddings = get_embeddings()
 
    if st.session_state.vector_db is None:
        st.session_state.vector_db = InMemoryVectorStore.from_documents(
            documents=docs,
            embedding=embeddings
        )
    else:
        st.session_state.vector_db.add_documents(docs)
 
    st.session_state.doc_count += len(docs)
    st.session_state.sources.append(source_label)
 
 
def process_pdf(uploaded_file):
    temp_path = f"./_temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
 
    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        chunks = split_documents(docs)
        add_documents_to_store(
            chunks,
            {"type": "pdf", "name": uploaded_file.name}
        )
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
 
 
def process_website(url):
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        chunks = split_documents(docs)
        add_documents_to_store(
            chunks,
            {"type": "web", "name": url}
        )
        return True, None
    except Exception as e:
        return False, str(e)
 
 
def reset_everything():
    st.session_state.vector_db = None
    st.session_state.messages = []
    st.session_state.sources = []
    st.session_state.doc_count = 0
 
 
def build_prompt(query, context):
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
 
 
def export_chat_as_text():
    lines = []
    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}\n")
    return "\n".join(lines)
 
 
# =============================================================
# SIDEBAR — SOURCE MANAGEMENT & SETTINGS
# =============================================================
with st.sidebar:
    st.header("📚 Knowledge Sources")
 
    tab_pdf, tab_web = st.tabs(["📄 PDF", "🌐 Website"])
 
    with tab_pdf:
        pdf_files = st.file_uploader(
            label="Upload one or more PDFs",
            type="pdf",
            accept_multiple_files=True,
            key="pdf_uploader"
        )
        if st.button("➕ Add PDF(s)", use_container_width=True):
            if not pdf_files:
                st.warning("Pehle koi PDF select karo.")
            else:
                already_added = {s["name"] for s in st.session_state.sources if s["type"] == "pdf"}
                new_files = [f for f in pdf_files if f.name not in already_added]
 
                if not new_files:
                    st.info("Ye PDFs already add ho chuki hain.")
                else:
                    with st.spinner(f"Processing {len(new_files)} PDF(s)..."):
                        for f in new_files:
                            ok, err = process_pdf(f)
                            if not ok:
                                st.error(f"{f.name} process nahi hui: {err}")
                    st.success("PDF(s) added successfully!")
                    sleep(1)
                    st.rerun()
 
    with tab_web:
        url_input = st.text_input("Website URL daalo", placeholder="https://example.com/article")
        if st.button("➕ Add Website", use_container_width=True):
            if not url_input.strip():
                st.warning("Pehle koi URL daalo.")
            else:
                already_added = {s["name"] for s in st.session_state.sources if s["type"] == "web"}
                if url_input in already_added:
                    st.info("Ye website already add ho chuki hai.")
                else:
                    with st.spinner("Website fetch aur process ho rahi hai..."):
                        ok, err = process_website(url_input)
                    if ok:
                        st.success("Website added successfully!")
                        sleep(1)
                        st.rerun()
                    else:
                        st.error(f"URL process nahi hui: {err}")
 
    st.divider()
 
    # ---- Added sources list ----
    st.subheader("✅ Added Sources")
    if st.session_state.sources:
        for i, s in enumerate(st.session_state.sources, start=1):
            icon = "📄" if s["type"] == "pdf" else "🌐"
            st.caption(f"{i}. {icon} {s['name']}")
    else:
        st.caption("Abhi tak koi source add nahi hua.")
 
    st.divider()
 
    # ---- Model & retrieval settings ----
    st.subheader("⚙️ Settings")
    selected_model = st.selectbox("Groq Model", AVAILABLE_MODELS, index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    k_chunks = st.slider("Kitne relevant chunks fetch karein (k)", 1, 8, 3)
    show_sources = st.checkbox("Answer ke saath source chunks dikhao", value=True)
 
    st.divider()
 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Reset All", use_container_width=True):
            reset_everything()
            st.rerun()
    with col2:
        if st.session_state.messages:
            st.download_button(
                label="⬇️ Export Chat",
                data=export_chat_as_text(),
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
 
 
# =============================================================
# MAIN AREA — HEADER
# =============================================================
st.title("🤖 Multi-Source Q&A ChatBot")
st.caption("PDFs aur Websites dono upload karo — phir unse jo chaho poocho.")
 
if st.session_state.doc_count:
    st.info(f"📊 Total {st.session_state.doc_count} chunks indexed from {len(st.session_state.sources)} source(s).")
 
st.divider()
 
# =============================================================
# MAIN AREA — CHAT
# =============================================================
if st.session_state.vector_db is None:
    st.warning("👈 Sidebar se pehle ek PDF ya Website add karo, tab chat shuru hogi.")
else:
    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("🔎 Sources used"):
                    for src in msg["sources"]:
                        st.markdown(f"**{src['label']}**")
                        st.text(src["snippet"])
                        st.markdown("---")
 
    query = st.chat_input("Apna sawaal poochho...")
 
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
 
        with st.chat_message("assistant"):
            with st.spinner("Soch raha hoon..."):
                retrieved_docs = st.session_state.vector_db.similarity_search(
                    query=query,
                    k=k_chunks
                )
 
                context = ""
                source_records = []
                for doc in retrieved_docs:
                    context += doc.page_content + "\n\n"
                    meta = doc.metadata or {}
                    label = meta.get("source", "Unknown source")
                    if "page" in meta:
                        label += f" (page {meta['page']})"
                    source_records.append({
                        "label": label,
                        "snippet": doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else "")
                    })
 
                prompt = build_prompt(query, context)
                llm = get_llm(selected_model, temperature)
                result = llm.invoke(prompt)
                answer = result.content
 
            st.markdown(answer)
 
            if show_sources and source_records:
                with st.expander("🔎 Sources used"):
                    for src in source_records:
                        st.markdown(f"**{src['label']}**")
                        st.text(src["snippet"])
                        st.markdown("---")
 
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": source_records if show_sources else []
        })