# Multi-Source RAG Q&A Chatbot

A full-stack **Retrieval-Augmented Generation (RAG)** application for question answering across PDF documents and website content.

The system ingests heterogeneous text sources, splits them into overlapping chunks, generates semantic embeddings, stores them in a session-specific vector store, retrieves relevant context for each query, and uses a Groq-hosted large language model to generate answers grounded in the retrieved information.

The application also returns source snippets alongside generated answers, allowing users to inspect the context retrieved by the RAG pipeline.

---

## Project Overview

Large language models can generate fluent responses but do not inherently have access to private or user-provided knowledge.

This project explores a practical RAG architecture that connects an LLM with external information supplied at runtime.

The pipeline follows:

**Source ingestion → Text processing → Chunking → Embedding → Vector retrieval → Context construction → LLM generation → Source attribution**

Users can create an isolated session, index multiple PDFs and website URLs, and query the resulting knowledge base through a React interface.

---

## Key Features

- Multi-source knowledge ingestion from PDFs and website URLs
- Semantic text embeddings using Hugging Face sentence-transformers
- Vector similarity retrieval using LangChain `InMemoryVectorStore`
- Retrieval-Augmented Generation using Groq-hosted LLMs
- Configurable retrieval depth (`k`)
- Configurable model temperature
- Source snippets returned with generated answers
- Session-specific vector stores and conversation histories
- Duplicate source detection within a session
- PDF and website source management
- Chat history tracking
- Plain-text conversation export
- Session reset functionality
- REST API implemented with FastAPI
- Interactive frontend built with React and Vite

---

## RAG Pipeline

The core question-answering workflow is:

```text
PDF / Website
      │
      ▼
Document Loading
      │
      ▼
Text Extraction
      │
      ▼
RecursiveCharacterTextSplitter
      │
      ▼
Overlapping Text Chunks
      │
      ▼
Hugging Face Embeddings
all-MiniLM-L6-v2
      │
      ▼
LangChain InMemoryVectorStore
      │
      ▼
Similarity Retrieval
Top-k Chunks
      │
      ▼
Retrieved Context
      │
      ▼
Groq LLM
      │
      ▼
Grounded Answer + Source Snippets
```

### 1. Source ingestion

The application accepts two source types:

- PDF documents
- Website URLs

PDF content is loaded using `PyPDFLoader`, while web content is loaded using `WebBaseLoader`.

### 2. Text chunking

Loaded documents are divided into smaller overlapping segments using LangChain's `RecursiveCharacterTextSplitter`.

Current defaults:

```text
Chunk size:     1000
Chunk overlap:   200
```

The overlap helps preserve contextual information across adjacent chunks.

### 3. Embedding

Each text chunk is transformed into a dense vector representation using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

These embeddings enable semantic retrieval based on meaning rather than exact keyword matching.

### 4. Vector storage

Embedded chunks are stored using:

```text
LangChain InMemoryVectorStore
```

Each application session maintains its own vector store, keeping indexed sources and retrieval state isolated between sessions.

### 5. Retrieval

When a question is submitted, the system performs similarity-based retrieval against the session's vector store.

The most relevant `k` chunks are selected as context for generation.

Default:

```text
k = 3
```

### 6. Generation

The retrieved chunks are incorporated into the prompt supplied to a Groq-hosted chat model.

The application instructs the model to answer using the retrieved context rather than relying solely on its general model knowledge.

### 7. Source traceability

The API returns relevant source snippets together with the generated response.

This allows users to inspect the retrieved evidence that contributed to the answer.

---

## System Architecture

```text
┌───────────────────────────────┐
│        React Frontend         │
│                               │
│ PDF Upload │ Website │ Chat   │
└───────────────┬───────────────┘
                │
                │ HTTP / REST
                ▼
┌───────────────────────────────┐
│         FastAPI Backend       │
│                               │
│ Routers                       │
│ ├── Chat                      │
│ ├── Sources                   │
│ └── Session                   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│         Service Layer         │
│                               │
│ document_service              │
│ rag_service                   │
│ export_service                │
└───────────────┬───────────────┘
                │
       ┌────────┴─────────┐
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│ Hugging Face │   │     Groq     │
│  Embeddings  │   │     LLM      │
└──────┬───────┘   └──────────────┘
       │
       ▼
┌───────────────────────────────┐
│ LangChain InMemoryVectorStore │
│     Session-specific data     │
└───────────────────────────────┘
```

---

## Backend Architecture

The backend follows a modular structure separating API routing, data models, application services, configuration, and session state.

```text
backend/
│
├── models/
│   ├── __init__.py
│   └── schemas.py
│
├── routers/
│   ├── __init__.py
│   ├── chat.py
│   ├── session.py
│   └── sources.py
│
├── services/
│   ├── __init__.py
│   ├── document_service.py
│   ├── export_service.py
│   └── rag_service.py
│
├── __init__.py
├── config.py
├── dependencies.py
├── main.py
└── session_store.py
```

### Session management

`SessionStore` creates and manages isolated application sessions.

Each session maintains:

- its own vector store
- indexed source metadata
- chat messages
- indexed chunk count

This prevents one user's indexed documents from being mixed with another session's retrieval context.

The current implementation deliberately uses **in-memory state**, making it appropriate for local development and experimentation rather than persistent production storage.

---

## Frontend Architecture

The frontend is implemented using **React and Vite**.

```text
frontend/
│
├── src/
│   ├── components/
│   │   ├── ChatInput.jsx
│   │   ├── MessageBubble.jsx
│   │   ├── PDFUploader.jsx
│   │   ├── Settings.jsx
│   │   ├── Sidebar.jsx
│   │   ├── SourcesList.jsx
│   │   ├── Toast.jsx
│   │   └── WebsiteAdder.jsx
│   │
│   ├── api.js
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
│
├── index.html
├── package.json
├── package-lock.json
└── vite.config.js
```

The interface:

- creates a session on startup
- displays source and indexed-chunk information
- accepts PDF uploads
- accepts website URLs
- sends questions to the backend
- displays generated answers
- exposes retrieved source snippets
- allows session reset
- supports chat-history export

During local development, Vite proxies API requests to the FastAPI backend.

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python, FastAPI | REST API and application logic |
| Frontend | React, Vite | Interactive user interface |
| RAG framework | LangChain | Document processing and retrieval workflow |
| Embeddings | Hugging Face Sentence Transformers | Semantic vector representation |
| Embedding model | `all-MiniLM-L6-v2` | Text embeddings |
| Vector store | `InMemoryVectorStore` | Semantic retrieval |
| LLM provider | Groq | LLM inference |
| PDF ingestion | `PyPDFLoader` | PDF text extraction |
| Web ingestion | `WebBaseLoader` | Website content loading |
| Text splitting | `RecursiveCharacterTextSplitter` | Document chunking |
| API architecture | REST | Frontend-backend communication |

---

## API Endpoints

### Session Management

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/session/create` | Create a new isolated session |
| `GET` | `/session/{session_id}/status` | Retrieve source and chunk counts |
| `DELETE` | `/session/{session_id}/reset` | Clear current session state |
| `GET` | `/session/{session_id}/export` | Export chat history |

### Source Management

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/sources/pdf` | Upload and index PDF documents |
| `POST` | `/sources/website` | Index a website URL |
| `GET` | `/sources/{session_id}` | List indexed sources |

### Chat

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/chat/query` | Query indexed knowledge sources |
| `GET` | `/chat/{session_id}/history` | Retrieve conversation history |

### System

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Backend health check |

---

## Repository Structure

```text
Multi-Source-RAG-QA-Chatbot/
│
├── .vscode/
│
├── backend/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── __init__.py
│   ├── config.py
│   ├── dependencies.py
│   ├── main.py
│   └── session_store.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .gitignore
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

---

## Local Setup

### Requirements

- Python 3.10+
- Node.js 18+
- Groq API key

### 1. Create a Python environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure the Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Do not commit your real API key to GitHub.

### 3. Start the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

The FastAPI backend runs locally on port `8000`.

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open the local address shown by Vite in your browser.

---

## Example Workflow

```text
Create Session
      ↓
Upload PDF / Add Website
      ↓
Extract Text
      ↓
Split into Chunks
      ↓
Generate Embeddings
      ↓
Store Vectors
      ↓
Ask Question
      ↓
Similarity Search
      ↓
Retrieve Top-k Chunks
      ↓
Construct RAG Context
      ↓
Generate Answer
      ↓
Return Answer + Sources
```

For example, a user can upload several documents, add a relevant website, and then ask questions across the combined indexed content rather than manually searching each source.

---

## Configuration

Current default retrieval and generation settings include:

```text
Embedding model:     sentence-transformers/all-MiniLM-L6-v2
LLM:                 llama-3.3-70b-versatile
Temperature:         0.3
Retrieved chunks:    3
Chunk size:          1000
Chunk overlap:       200
```

Alternative configured model options include:

```text
llama-3.1-8b-instant
gemma2-9b-it
```

---

## Current Design Limitations

This project is currently designed as a local RAG application and learning prototype.

Important limitations include:

- vector data is stored in memory
- sessions are not persisted across backend restarts
- indexed documents are lost when the backend stops
- no authentication or user account system
- no persistent database
- no persistent vector database
- no automated RAG evaluation framework
- no production cloud deployment

These limitations are intentionally documented rather than presenting the application as a production system.

---

## Potential Next Steps

Future development could include:

- persistent vector storage
- persistent conversation and session storage
- authentication and user-level data isolation
- additional document formats
- metadata filtering during retrieval
- hybrid semantic and keyword retrieval
- reranking retrieved documents
- automated retrieval evaluation
- RAG answer-quality evaluation
- hallucination and faithfulness assessment
- configurable embedding models
- automated testing
- containerisation
- CI/CD
- cloud deployment

A particularly valuable next step would be to introduce a small evaluation dataset and measure retrieval quality using metrics such as **Recall@K** or **MRR**, followed by systematic comparison of chunk size, overlap, retrieval depth, and embedding configurations.

---

## What This Project Demonstrates

From a data and AI engineering perspective, this project demonstrates practical implementation of:

- Retrieval-Augmented Generation
- semantic embeddings
- vector similarity search
- unstructured document processing
- multi-source data ingestion
- text chunking and preprocessing
- LLM integration
- retrieval-context construction
- source traceability
- session-based state management
- REST API development
- modular backend design
- frontend-backend integration

The focus is not on training a foundation model. Instead, the project demonstrates how existing embedding and generative models can be integrated into an end-to-end information retrieval and question-answering system.

---

## Author

**Xuan Nam Ngo (Viktor)**

Master of Data Science student with interests in **data science, machine learning, generative AI, information retrieval, and applied AI systems**.
