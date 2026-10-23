# RAG AMIT GRADUATION PROJECT

## Project Overview

**RAG AMIT Graduation Project** is a Retrieval‑Augmented Generation (RAG) system developed as the capstone project for the AMIT Learning program. The system enables users to query a knowledge base of documents (PDFs, text files, etc.) and receive answers grounded in the retrieved content, leveraging large language models (LLMs) and vector search.

The project demonstrates end‑to‑end pipeline design: document ingestion, chunking, embedding, vector storage, retrieval, and LLM‑based answer generation. It is intended to showcase skills in Python development, LangChain/LlamaIndex integration, vector database management, and production‑ready API design.

## Architecture & Tech Stack

- **Language:** Python 3.11+
- **Framework / Libraries:**
  - `langchain` / `llama-index` – modular LLM interface and retrieval strategies
  - `fastapi` – asynchronous API layer
  - `pydantic` – data validation
  - `openai` / `google-generativeai` – LLM providers (Gemini / OpenAI)
  - `chromadb` / `faiss` – vector database for semantic search
  - `python-dotenv` – environment variable management
- **Vector Store:** Chroma (local development) / Faiss (scalable deployment)
- **Database (metadata/sqlite):** `supportmind.db`, `chroma.sqlite3`
- **Backend:** Modular Python package under `backend/app/` (routers, services, repositories)
- **Frontend:** Static HTML / React‑style JSX (Vite, TailwindCSS) in `frontend/`
- **Tracking / MLOps:** Optional MLflow / Azure monitoring (configure via `.env`)
- **Utilities:** `test_gemini_api.py`, `test_gemini_rest.py` – test scripts for LLM connectivity

## Project Structure

```
RAG-AMIT-GRADUATION-PROJECT/
├── .gitignore                     # excludes .env, __pycache__, vector data, node_modules, etc.
├── README.md                      # this file
├── ACCESS_NOW.txt
├── backend/
│   ├── .env.example               # template for environment variables
│   ├── requirements.txt           # pip dependencies
│   ├── setup_admin_and_upload.py
│   ├── setup_kaggle_dataset.py
│   ├── chroma_data/               # persisted Chroma vector store files
│   ├── downloads/                 # source PDFs / text docs
│   ├── uploads/                   # user‑uploaded PDFs
│   └── app/
│       ├── __init__.py
│       ├── main.py                # entry point ( FastAPI )
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   └── security.py
│       ├── api/
│       │   ├── auth.py
│       │   ├── chat.py
│       │   ├── knowledge_base.py
│       │   └── tickets.py
│       ├── models/
│       │   └── models.py          # SQLAlchemy / pydantic models
│       ├── schemas/
│       │   └── schemas.py         # request/response schemas
│       ├── services/
│       │   ├── rag_service.py
│       │   ├── auth_service.py
│       │   ├── analytics_service.py
│       │   ├── chat_service.py
│       │   ├── ticket_service.py
│       │   └── lazy_services.py
│       ├── repositories/
│       │   ├── document_repository.py
│       │   ├── chat_repository.py
│       │   └── user_repository.py
│       └── routers/
│           ├── auth.py
│           ├── chat.py
│           ├── knowledge_base.py
│           └── tickets.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package-lock.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       └── pages/
│           ├── Landing.jsx
│           ├── Login.jsx
│           ├── Register.jsx
│           ├── Dashboard.jsx
│           ├── KnowledgeBase.jsx
│           ├── Chat.jsx
│           ├── Tickets.jsx
│           └── TicketDetail.jsx
│       └── services/
│           └── api.js
├── .git/
└── README.md (root)
```

## Getting Started & Environment Setup

### 1. Prerequisites

- Python 3.11+ installed
- (Optional) Node.js & npm for the frontend Vite dev server
- Git (already initialized)

### 2. Clone / Open the Repository

```bash
git clone https://github.com/hazem76/RAG-AMIT-GRADUATION-PROJECT.git
cd RAG-AMIT-GRADUATION-PROJECT
```

### 3. Backend Setup

```bash
# Create a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r backend/requirements.txt

# Copy the environment variable template and fill in your keys
cp backend/.env.example backend/.env
# Edit backend/.env with your values:
#   - LLM_PROVIDER=gemini   # or openai
#   - GEMINI_API_KEY=your_key_here
#   - CHROMA_PERSIST_DIRECTORY=./backend/chroma_data
#   - etc.

# (Optional) Initialize the vector store with sample documents
python backend/setup_kaggle_dataset.py   # or run the ingestion script
```

### 4. Run the Backend API

```bash
# From the project root
uvicorn backend.app.main:app --reload
# or directly:
python -m backend.app.main
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs at `/docs`.

### 5. Frontend Setup (optional)

```bash
cd frontend
npm install   # or yarn
npm run dev   # Vite dev server, usually at http://localhost:5173
```

### 6. Running Tests (optional)

```bash
python -m pytest backend/   # if pytest is installed
python backend/test_gemini_api.py
python backend/test_gemini_rest.py
```

### 7. Docker / Production (optional)

A Dockerfile may be added later; currently the project is intended to be run locally via the steps above.

## API Highlights (selected endpoints)

| Endpoint | Description |
|---|---|
| `POST /auth/register` | Register a new user |
| `POST /auth/login` | Login and receive JWT |
| `POST /knowledge-base/upload` | Upload a PDF / text file to the knowledge base |
| `GET /knowledge-base/documents` | List indexed documents |
| `POST /chat/send` | Send a user message; retrieves relevant chunks and returns an LLM‑generated answer |
| `GET /chat/history/{session_id}` | Retrieve chat history |

*(Full list available at `http://127.0.0.1:8000/docs` once the server is running.)*

## License

This project is private and intended for AMIT Learning graduation evaluation. Please respect the `.env` file and do not commit real API keys.

---

**Happy coding!** If you encounter any issues, refer to the inline comments, the `.env.example`, or open an issue on the GitHub repository.