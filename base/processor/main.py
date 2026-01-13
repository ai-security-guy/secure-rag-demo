from google.cloud import pubsub_v1
from google.cloud import storage
import os
import json
import time
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import io

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "secure-rag-demo")
TOPIC_ID = "secure-rag-upload-topic"
SUBSCRIPTION_ID = "secure-rag-processing-sub"
CHROMA_PATH = "./chroma_db"

# Initialize Models & DB
print("Initializing Embedding Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Initializing ChromaDB...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="rag_collection")

def process_message(message):
    try:
        print(f"Received message: {message.data}")
        data = json.loads(message.data.decode("utf-8"))
        filename = data.get('filename')
        gcs_uri = data.get('gcs_uri')
        bucket_name = gcs_uri.split("/")[2]
        blob_name = "/".join(gcs_uri.split("/")[3:])
        
        print(f"Processing file: {filename} from {bucket_name}/{blob_name}")
        
        # 1. Download from GCS
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        file_bytes = blob.download_as_bytes()
        
        # 2. Extract Text (Simulating CDR/Docling with pypdf for now)
        print("Extracting text...")
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        print(f"Extracted {len(text)} characters.")
        
        # 3. Embed & Store
        if text.strip():
            print("Embedding and storing...")
            # Simple chunking with overlap for better context retention
            chunk_size = 1000
            chunk_overlap = 200
            step = chunk_size - chunk_overlap
            
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), step)]
            ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]
            
            embeddings = model.encode(chunks)
            
            collection.upsert(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=metadatas
            )
            print(f"Stored {len(chunks)} chunks in ChromaDB.")
        
        message.ack()
        print("Message acknowledged.")
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()

def main():
    print("Starting Processing Service...")
    
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = subscriber.topic_path(PROJECT_ID, TOPIC_ID)
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
    
    # Create subscription if it doesn't exist
    try:
        subscriber.get_subscription(request={"subscription": subscription_path})
        print(f"Found subscription: {subscription_path}")
    except Exception:
        print(f"Creating subscription: {subscription_path}")
        try:
            subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path}
            )
        except Exception as e:
            print(f"Failed to create subscription: {e}")
            return

    # Start listening
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_message)
    print(f"Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()

if __name__ == "__main__":
    main()