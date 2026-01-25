# Secure RAG Demo

A demonstration of a **Secure Retrieval-Augmented Generation (RAG)** architecture on Google Cloud Platform. 

This project corresponds to the blog series **"Securing RAG Systems"**.

## Overview

This demo builds a RAG system that ingests PDFs, processes them securely (CDR/Sanitization), and serves them via a secure API.

### Features
- **Frontend**: Angular (Cloud Run)
- **Backend**: FastAPI (Cloud Run)
- **Processor**: Python Worker (Cloud Run / PubSub)
- **Vector DB**: ChromaDB
- **LLM**: Vertex AI (Gemini)

### Security Layers (New!)
1.  **Authentication**: Bearer Token verification (Mock/Dev token for demo).
2.  **Input Validation**: Strict PDF MIME type checking (Magic Bytes) and Size Limits (10MB).
3.  **Content Disarm & Reconstruction (CDR)**: Text sanitization to remove non-printable characters.
4.  **Guardrails**: Input regex filtering to block prompt injection attempts.

## Running Locally

### Prerequisites
- Python 3.10+
- Google Cloud Project with Vertex AI enabled.
- `gcloud` authenticated.

### 1. Backend
```bash
cd secure-rag-app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run server
export DEV_TOKEN="secure-rag-dev-token"
uvicorn main:app --reload --port 8000
```

### 2. Processor
```bash
cd secure-rag-app/processor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run worker
python main.py
```

### 3. Testing
Use the provided `DEV_TOKEN` to authorize requests.

```bash
# Upload (Authorized)
curl -X POST -H "Authorization: Bearer secure-rag-dev-token" -F "file=@your.pdf;type=application/pdf" http://localhost:8000/upload

# Chat (Authorized)
curl -X POST -H "Authorization: Bearer secure-rag-dev-token" -H "Content-Type: application/json" -d '{"message": "Hello"}' http://localhost:8000/chat
```

## Blog Series
- **Part 1**: Building the Foundation
- **Part 2**: Threat Modeling
- **Part 3**: Securing the System (This Repo)
