from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from auth import verify_token
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import magic

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
import re

def validate_input(text):
    """
    Basic Input Guardrail.
    Blocks common prompt injection patterns.
    """
    patterns = [
        r"ignore previous instructions",
        r"identify yourself",
        r"system prompt",
        r"you are a hacked",
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(status_code=400, detail="Input Content Violation: Potential prompt injection detected.")
    return True

import shutil
import os

app = FastAPI()

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Secure RAG Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from google.cloud import storage, pubsub_v1
import uuid
import json

# Configuration
BUCKET_NAME = "secure-rag-ingest"
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "secure-rag-demo")
TOPIC_ID = "secure-rag-upload-topic"

@app.post("/upload", dependencies=[Depends(verify_token)])
async def upload_file(file: UploadFile = File(...)):
    try:
        # 1. Initialize Clients
        storage_client = storage.Client(project=PROJECT_ID)
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

        # 2. Check/Create Bucket
        try:
            bucket = storage_client.get_bucket(BUCKET_NAME)
        except Exception:
            try:
                bucket = storage_client.create_bucket(BUCKET_NAME, location="US")
            except Exception as create_err:
                 print(f"Could not create bucket '{BUCKET_NAME}': {create_err}")
                 raise HTTPException(status_code=500, detail=f"Bucket access failed: {create_err}")

        # 3. Validate & Upload File
        file_content = await file.read()

        # Size Check
        if len(file_content) > MAX_FILE_SIZE:
             raise HTTPException(status_code=413, detail="File too large (max 10MB)")

        # Magic Number Check
        mime_type = magic.from_buffer(file_content, mime=True)
        if mime_type != "application/pdf":
             raise HTTPException(status_code=400, detail=f"Invalid file type: {mime_type}. Only PDF is allowed.")
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        blob = bucket.blob(unique_filename)
        
        blob.upload_from_string(
            file_content,
            content_type=mime_type
        )
        
        gcs_uri = f"gs://{BUCKET_NAME}/{unique_filename}"
        print(f"Uploaded {file.filename} to {gcs_uri}")

        # 4. Publish to Pub/Sub
        try:
            # Check/Create Topic (For demo safety)
            try:
                publisher.get_topic(request={"topic": topic_path})
            except Exception:
                publisher.create_topic(request={"name": topic_path})
                print(f"Created topic {topic_path}")

            # Message Data
            message_data = {
                "filename": file.filename,
                "gcs_uri": gcs_uri,
                "content_type": file.content_type,
                "size_bytes": len(file_content)
            }
            data_str = json.dumps(message_data).encode("utf-8")
            
            future = publisher.publish(topic_path, data_str)
            message_id = future.result()
            print(f"Published message {message_id} to {topic_path}")

        except Exception as pub_err:
            print(f"Pub/Sub publish failed: {pub_err}")
            # We don't fail the request if pubsub fails, but we should log it clearly.
            # In a strict system, we might want to rollback the upload or fail the request.
        
        return {
            "filename": file.filename,
            "gcs_uri": gcs_uri,
            "size": len(file_content),
            "message": "File uploaded and processed successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- RAG Setup ---
import chromadb
from sentence_transformers import SentenceTransformer
import vertexai
from vertexai.generative_models import GenerativeModel

# Use relative path for ChromaDB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Assuming processor is sibling to backend
CHROMA_PATH = os.path.join(BASE_DIR, "../processor/chroma_db")

print("Initializing RAG resources...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="rag_collection")

vertexai.init(project=PROJECT_ID, location="us-central1")
gen_model = GenerativeModel("gemini-2.0-flash-exp")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat", dependencies=[Depends(verify_token)])
async def chat(request: ChatRequest):
    try:
        query = request.message
        validate_input(query)
        print(f"Received query: {query}")
        
        # 1. Embed Query
        query_embedding = embedding_model.encode([query]).tolist()
        
        # 2. Retrieve Context
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=5
        )
        
        # 3. Construct Prompt
        context_text = "\n\n".join(results['documents'][0])
        print(f"Retrieved context length: {len(context_text)}")
        
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.
If the answer is not in the context, say you don't know.

Context:
{context_text}

Question:
{query}

Answer:"""

        # 4. Generate Answer
        response = gen_model.generate_content(prompt)
        answer = response.text
        
        return {
            "response": answer,
            "context": results['documents'][0] # Optional: return context for debugging
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Allow running as a script for convenience
    uvicorn.run(app, host="0.0.0.0", port=8000)
