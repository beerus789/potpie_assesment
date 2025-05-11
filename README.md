# FastAPI RAG Chatbot Backend

**Author:** Your Name Here

---

## Project Role
A robust, scalable backend for document-based Retrieval-Augmented Generation (RAG) chatbots. Supports PDF, DOCX, and TXT ingestion, real-time chat with document context, and multi-user, multi-threaded chat history. Embeddings are stored in ChromaDB for fast retrieval. Heavy processing is offloaded to Celery for scalability.

---

## Features Implemented
- **Document Ingestion:** PDF, DOCX, and TXT files supported
- **Duplicate File Handling:** Prevents duplicate file names in ChromaDB
- **Chunking & Embedding:** Efficient chunking (configurable size) and GPU/CPU auto-detection
- **ChromaDB Integration:** Vector storage and retrieval for RAG
- **Celery Integration:** Async document processing for large files and folders
- **Streaming Chat:** Real-time, token-by-token chat responses
- **Thread & History Management:** Multi-threaded chat, persistent chat history, thread listing
- **Rate Limiting:** Per-endpoint rate limiting with SlowAPI
- **Logging:** Detailed logging for backend and Celery tasks
- **Environment Config:** OpenAI API key and other secrets in `.env`
- **Modern UI:** Simple, modern HTML/JS frontend for chat (see `app/static/rag_chat_test.html`)

---

## Feature Comparison Table

| Feature                        | Status         | Notes                                                      |
|-------------------------------|----------------|------------------------------------------------------------|
| PDF/DOCX/TXT Ingestion        | ✅ Implemented | Upload and process via API or folder                        |
| Duplicate File Handling       | ✅ Implemented | Prevents duplicate file names in ChromaDB                   |
| Chunking & Embedding          | ✅ Implemented | Configurable chunk size, GPU/CPU auto-detect                |
| ChromaDB Integration          | ✅ Implemented | Vector storage and retrieval for RAG                        |
| Celery Async Processing       | ✅ Implemented | Background task queue for heavy document processing         |
| Streaming Chat                | ✅ Implemented | Real-time, token-by-token chat responses                    |
| Thread & History Management   | ✅ Implemented | Multi-threaded chat, persistent chat history                |
| Rate Limiting (SlowAPI)       | ✅ Implemented | Per-endpoint rate limiting                                  |
| Logging                       | ✅ Implemented | Backend and Celery logs for debugging and monitoring        |
| .env Config                   | ✅ Implemented | OpenAI API key and secrets in .env                          |
| Modern UI                     | ✅ Implemented | Simple, clean HTML/JS frontend (rag_chat_test.html)         |
| Multi-User/Thread Support     | ✅ Implemented | Multiple users and chat threads supported                   |
| Error Handling                | ⚠️ Basic      | Can be improved for user feedback and frontend robustness   |
| Database for State            | ❌ Planned     | Move from JSON to DB for chat history, threads, etc.        |
| Authentication                | ❌ Planned     | Add user auth for secure multi-user deployments             |
| Monitoring/Observability      | ❌ Planned     | Add metrics, dashboards, and error tracking                 |
| File Upload in UI             | ❌ Planned     | Add drag-and-drop or file picker to frontend                |
| Admin Dashboard               | ❌ Planned     | For monitoring tasks, usage, and system health              |

---

## Project Structure
```
fastapi-project/
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── limiter.py             # SlowAPI limiter instance
│   ├── celery_app.py          # Celery app config
│   ├── document_tasks.py      # Celery document processing tasks
│   ├── api/endpoints/         # API endpoints (document, chat)
│   ├── core/                  # Core logic (embedding, file parsing, chroma, etc.)
│   ├── models/, schemas/, services/
│   └── static/                # Frontend UI (rag_chat_test.html)
├── chroma_migrated/           # ChromaDB persistent storage
├── chat_histories/            # Chat history files (if not DB)
├── requirements.txt           # Dependencies
├── .env                       # Environment variables
└── README.md
```

---

## Setup Instructions

### 1. Clone and Install
```sh
# Clone the repo
$ git clone <repository-url>
$ cd fastapi-project

# Create and activate virtual environment (Windows)
$ python -m venv venv1
$ .\venv1\Scripts\activate

# Install dependencies
$ pip install -r requirements.txt
```

### 2. Configure Environment
- Copy `.env.example` to `.env` and set your `OPENAI_API_KEY` and any other secrets.

### 3. Start ChromaDB (if needed)
- ChromaDB is used as a vector store and will persist data in `chroma_migrated/`.

### 4. Run FastAPI Backend
```sh
$ uvicorn app.main:app --reload
```

### 5. Run Celery Worker (Windows)
```sh
celery -A app.celery_app.celery_app worker --loglevel=info -Q docs --pool=threads --concurrency=4
```
- This will process document ingestion tasks in the background.

### 6. Access the UI
- Open `http://localhost:8000/static/rag_chat_test.html` in your browser for a simple chat interface.

---

## UI/Frontend
- The frontend (`rag_chat_test.html`) provides a modern, minimal chat interface.
- Supports real-time streaming of chat responses.
- Shows chat history and allows multi-turn conversations.

---

## Pros of This Project
- **Scalable:** Async processing and background workers for heavy tasks
- **Extensible:** Add new file types, models, or vector DBs easily
- **Production-Ready Patterns:** Rate limiting, logging, .env config, modular code
- **Modern UI:** Simple, clean, and easy to extend
- **Multi-User/Thread:** Supports multiple users and chat threads
- **Streaming:** Real-time chat experience

---

## Future Development Ideas
- **Move chat history and thread maps to a real database (PostgreSQL, MongoDB, etc.)**
- **Add authentication and user management**
- **Support for more file types (HTML, Markdown, etc.)**
- **Admin dashboard for monitoring tasks and usage**
- **Advanced error handling and user feedback in UI**
- **Horizontal scaling for Celery and FastAPI (Docker, Kubernetes)**
- **Monitoring/metrics integration (Prometheus, Grafana, Sentry)**
- **Better duplicate document detection (hashing, user namespace)**
- **File upload support in UI**
- **Malware/Corruption Detection:** Integrate file scanning to detect malware or corrupted documents before processing.
- **File Preview & Metadata Extraction:** Allow users to preview documents and extract metadata (author, title, etc.) before ingestion.
- **Advanced Search:** Implement semantic and keyword search across all ingested documents and chat histories.
- **Analytics Dashboard:** Provide usage analytics, document statistics, and system health monitoring for admins.
- **Multi-language Support:** Add support for document ingestion and chat in multiple languages, including translation features.
- **Multi-Agent Support:** Enable multiple specialized agents (e.g., code expert, legal expert) that users can select or route queries to.
- **Agent Collaboration:** Allow agents to collaborate or debate on complex queries, providing richer answers.
- **Agent Assignment/Personalization:** Assign agents to users or threads for personalized assistance and context retention.

---

## Major Update Suggestions
- **Security:** Add authentication, file size/type validation, and malware scanning for uploads.
- **Observability:** Add structured logging, error tracking, and metrics.
- **Deployment:** Add Dockerfiles and deployment scripts for cloud or on-premise.

---

## Author
Satyam Prakash Srivastava

---

## Quick Start (Summary)
1. Clone, create venv, install requirements
2. Set up `.env` with your OpenAI API key.
3. Open Two terminal and run 4t and 5th cmd seperately with sequencial.
4. Start Celery: `celery -A app.celery_app.celery_app worker --loglevel=info -Q docs --pool=threads --concurrency=4`
5. Start FastAPI: `uvicorn app.main:app --reload`
6. Open the UI at `http://localhost:8000/static/rag_chat_test.html` (for chatbot).
7. You can create your own UI.

---

For any questions or contributions, please open an issue or pull request!