# Secure RAG (Base Application)

This is the base application for the Secure RAG blog series. It demonstrates a simple RAG (Retrieval-Augmented Generation) system with a FastAPI backend, Angular frontend, and a Pub/Sub file processor.

**Note:** This is the "Before" state. The "After" state will introduce advanced security features like Workload Identity Federation, Document Level Access Control, and Content Disarm & Reconstruction.

## Architecture

- **Frontend**: Angular 18 (Standalone Components)
- **Backend**: FastAPI (Python 3.11+)
- **Processor**: Python worker listening on Pub/Sub
- **Database**: ChromaDB (local instance for demo)
- **LLM**: Google Vertex AI (Gemini 2.0 Flash)
- **Infrastructure**: Google Cloud Storage, Pub/Sub

## Prerequisites

1.  **Google Cloud Platform Project**:
    *   Enable APIs: `storage-component.googleapis.com`, `pubsub.googleapis.com`, `aiplatform.googleapis.com`
    *   Create a generic Service Account or use `gcloud auth application-default login`.
2.  **Tools**:
    *   Python 3.11+
    *   Node.js 20+
    *   gcloud CLI

## Setup Instructions

### 1. Environment Variables

Ensure your environment is set up. You can check your active project with:

```bash
gcloud config get-value project
```

The application uses `os.getenv("GOOGLE_CLOUD_PROJECT")` to determine the project ID.

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run Backend:**

```bash
# From the backend directory
uvicorn main:app --reload --port 8000
```

### 3. Processor Setup

The processor listens for file upload events to embed them into ChromaDB.

```bash
cd processor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run Processor:**

```bash
# From the processor directory
python3 main.py
```

### 4. Frontend Setup

Update `frontend/src/environments/environment.ts` with your Firebase config if you want to use the full feature set (authentication), although this base version mainly focuses on the RAG flow.

```bash
cd frontend
npm install
ng serve
```

Access the app at `http://localhost:4200`.

## Usage

1.  **Upload**: Go to the Upload tab and upload a PDF document.
2.  **Process**: Watch the `processor` terminal logs. It should download, chunk, and embed the file.
3.  **Chat**: Go to the Chat tab and ask questions about the uploaded document.

## License

MIT
