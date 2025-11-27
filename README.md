# Project Setup and Run Instructions

This project is a Django-based RAG (Retrieval-Augmented Generation) application that uses a local LLM and FAISS for vector storage.

## Prerequisites

- Python 3.8+ installed.
- Virtual environment (recommended).

## Setup

1.  **Create and Activate Virtual Environment**:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Apply Migrations**:
    ```bash
    python manage.py migrate
    ```

## Data Ingestion

To ingest PDF documents into the vector store:

1.  Place your PDF files in the `docs` directory.
2.  Run the ingestion script:
    ```bash
    python -m backend.knowledge_base.ingestion
    ```
    This will process the PDFs and save the vector index to `backend/knowledge_base/faiss_index`.

## Running the Server

Start the Django development server:

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.

## Usage

You can ask questions via the API endpoint:

**Endpoint**: `POST http://127.0.0.1:8000/ask/`

**Body**:
```json
{
    "question": "Your question here"
}
```

**Example (PowerShell)**:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask/" -Method Post -ContentType "application/json" -Body '{"question": "What is IESC?"}'
```

**Example (cURL)**:
```bash
curl -X POST http://127.0.0.1:8000/ask/ -H "Content-Type: application/json" -d '{"question": "What is IESC?"}'
```
