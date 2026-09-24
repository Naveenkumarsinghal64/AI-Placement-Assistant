# AI Placement Assistant

A full-stack web application that helps students track placement applications and provides AI-powered resume analysis, job description matching, and document-grounded question answering using Retrieval-Augmented Generation (RAG).

## 1. Project Overview

AI Placement Assistant combines a straightforward placement application tracker with three practical AI features:

- **Resume analysis** — extracts skills, gaps, and improvement suggestions from an uploaded resume.
- **Job description matching** — compares a resume against a specific job description and estimates alignment.
- **Document-grounded assistant (RAG)** — answers questions about uploaded placement documents (guidelines, eligibility criteria, policies) using only retrieved content from those documents.

The project is intentionally scoped for clarity: no databases, containers, or microservices are used. Application data is stored in a JSON file, and document embeddings are stored in a local ChromaDB instance.

## 2. Features

**Placement Application Tracker**
- Add, edit, delete, search, and filter applications
- Track company, role, package, application date, and status
- Dashboard with live statistics (total, applied, shortlisted, interview, selected, rejected)

**AI Features**
- Resume analysis: detected skills, missing skills, relevant technologies, strengths, improvement areas, suggestions
- Job description matching: matching/missing skills, relevant technologies, approximate alignment percentage, preparation suggestions
- RAG-based assistant: upload placement documents, ask natural-language questions, get answers grounded in retrieved chunks with source attribution

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5 |
| AI Model | Google Gemini (`google-genai` SDK) |
| Vector Store | ChromaDB (local, persistent) |
| Data Storage | JSON file (applications), local filesystem (uploads) |
| Document Parsing | pdfplumber, python-docx |

## 4. Architecture

```
Browser (HTML/CSS/JS)
      │  fetch() calls to REST API
      ▼
FastAPI application (backend/app)
      │
      ├── api/routes      → HTTP endpoints, request/response handling
      ├── services         → business logic, isolated from route functions
      ├── models/schemas    → Pydantic request/response models
      ├── data/applications.json → application persistence
      └── vectorstore       → ChromaDB persistent collection
```

Routes never touch the filesystem or vector store directly — they call service functions, which own all persistence logic. This keeps route handlers thin and testable, and keeps data-access logic in one place per concern.

## 5. Project Structure

```
ai-placement-assistant/
│
├── frontend/
│   ├── index.html            Dashboard
│   ├── applications.html     Application tracker
│   ├── resume.html           Resume analysis & job match
│   ├── assistant.html        RAG chat interface
│   ├── documents.html        Knowledge base management
│   ├── css/style.css
│   └── js/
│       ├── api.js            Central fetch wrapper for all API calls
│       ├── dashboard.js
│       ├── applications.js
│       ├── resume.js
│       ├── assistant.js
│       └── documents.js
│
├── backend/
│   ├── app/
│   │   ├── main.py           FastAPI app, router registration, CORS
│   │   ├── config.py         Paths, environment variables, constants
│   │   ├── api/routes/       applications.py, resume.py, documents.py, assistant.py
│   │   ├── models/schemas.py Pydantic models
│   │   ├── services/
│   │   │   ├── application_service.py   JSON persistence for applications
│   │   │   ├── resume_service.py        Resume analysis & job matching prompts
│   │   │   ├── document_service.py      Text chunking
│   │   │   ├── rag_service.py           Embedding, ChromaDB storage, retrieval
│   │   │   ├── text_extraction.py       PDF/DOCX/TXT text extraction
│   │   │   └── ai_service.py            Gemini client wrapper
│   │   ├── data/applications.json
│   │   └── vectorstore/                 ChromaDB persistent storage (generated)
│   ├── requirements.txt
│   └── .env.example
│
├── uploads/
│   ├── resumes/       temporary resume uploads (deleted after analysis)
│   └── documents/     stored copies of ingested RAG documents
│
├── .gitignore
├── README.md
└── LICENSE
```

## 6. How RAG Works

1. A user uploads a document (PDF, DOCX, or TXT) through the Documents page.
2. `text_extraction.py` extracts raw text from the file.
3. `document_service.chunk_text` splits the text into overlapping chunks (default: 800 characters, 120 character overlap) to preserve context across chunk boundaries.
4. Each chunk is embedded using Gemini's embedding model (`text-embedding-004`) via `ai_service.embed_text`.
5. Chunks, embeddings, and metadata (filename, document id, upload time) are stored in a persistent ChromaDB collection.
6. When a user asks a question, the question is embedded and ChromaDB returns the most similar chunks (`RAG_TOP_K`, default 4).
7. The retrieved chunks are inserted into a prompt template that instructs the model to answer **only** using the provided context, and to say so explicitly if the answer is not present.
8. The response includes the filenames of the source chunks used, so the user can verify where an answer came from.

This is a standard retrieve-then-generate pipeline: no fine-tuning, no external hosted vector database — everything runs locally in a `chromadb.PersistentClient`.

## 7. How AI Integration Works

All AI calls go through `backend/app/services/ai_service.py`, a thin wrapper around the `google-genai` SDK:

- `generate_text(prompt)` — used for the RAG assistant's free-form answers.
- `generate_json(prompt)` — used for resume analysis and job matching, where the model is instructed to return a strict JSON object matching a defined schema. This keeps AI output structured and directly usable by the frontend without additional parsing logic.
- `embed_text(text)` — used both when ingesting documents and when embedding user questions for retrieval.

The Gemini API key is read from the `GEMINI_API_KEY` environment variable and is never hardcoded. If the key is missing, the affected endpoints return a `503` with a clear error message instead of failing silently.

## 8. API Overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/applications` | List applications (supports `search`, `status` query params) |
| GET | `/api/applications/stats` | Dashboard statistics |
| GET | `/api/applications/{id}` | Get a single application |
| POST | `/api/applications` | Create an application |
| PUT | `/api/applications/{id}` | Update an application |
| DELETE | `/api/applications/{id}` | Delete an application |
| POST | `/api/resume/analyze` | Analyze an uploaded resume |
| POST | `/api/resume/match` | Compare a resume against a job description |
| GET | `/api/documents` | List indexed knowledge base documents |
| POST | `/api/documents` | Upload and index a document for RAG |
| DELETE | `/api/documents/{id}` | Remove a document from the vector store |
| POST | `/api/assistant/ask` | Ask a question answered via RAG |
| GET | `/api/health` | Health check |

Interactive API documentation is available at `http://127.0.0.1:8000/docs` once the backend is running.

## 9. Installation

### Prerequisites
- Python 3.10+
- A Google Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

### Clone the repository

```bash
git clone https://github.com/<your-username>/ai-placement-assistant.git
cd ai-placement-assistant
```

## 10. Environment Variables

Copy the example environment file and fill in your API key:

```bash
cd backend
cp .env.example .env
```

`backend/.env`:

```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=models/text-embedding-004
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=120
RAG_TOP_K=4
```

The `.env` file is excluded from version control via `.gitignore`. Never commit real API keys.

## 11. How to Run Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## 12. How to Run Frontend

The frontend is static HTML/CSS/JS and requires no build step. From the `frontend/` directory, serve it with any static file server, for example:

```bash
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500` in your browser. The frontend calls the backend at `http://127.0.0.1:8000` (configured in `frontend/js/api.js`).

## 13. Example Usage

1. Start the backend and frontend as described above.
2. Open the Dashboard and add a few applications via the **Applications** page.
3. Go to **Resume & Job Match**, upload a resume, and click **Analyze Resume** to see detected skills and suggestions.
4. Paste a job description in the same page's second tab to see a matching report.
5. Go to **Documents**, upload a placement policy PDF (e.g. containing eligibility criteria).
6. Go to **AI Assistant** and ask a question such as *"What is the minimum CGPA required?"* — the answer will be generated from the uploaded document, with the source filename shown.

## 14. Future Improvements

- Pagination for large application lists
- Export applications to CSV
- Multi-user authentication for shared use
- Support for additional document formats (e.g. scanned PDFs via OCR)
- Caching of repeated AI analysis results
