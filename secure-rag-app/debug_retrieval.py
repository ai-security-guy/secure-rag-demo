import chromadb
from sentence_transformers import SentenceTransformer

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "processor/chroma_db")

def debug_retrieval(query):
    print(f"--- Debugging Query: '{query}' ---")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name="rag_collection")
    
    query_embedding = model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )
    
    if not results['documents'][0]:
        print("No results found.")
        return

    for i, (doc, dist, meta) in enumerate(zip(results['documents'][0], results['distances'][0], results['metadatas'][0])):
        print(f"\nResult {i+1} (Distance: {dist:.4f}):")
        print(f"Metadata: {meta}")
        print(f"Content: {doc[:200]}..." if len(doc) > 200 else f"Content: {doc}")

if __name__ == "__main__":
    debug_retrieval("Who is Dima Fomberg?")
    
    def check_file_in_db(filename_substring):
        print(f"\n--- Checking for files containing '{filename_substring}' ---")
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_collection(name="rag_collection")
        
        # Get all metadata to check filenames
        # Note: getting all might be slow if large, but for debugging it's fine
        result = collection.get()
        metadatas = result['metadatas']
        
        found_files = set()
        chunk_counts = {}
        
        for meta in metadatas:
            if meta and 'filename' in meta:
                fname = meta['filename']
                if filename_substring.lower() in fname.lower():
                    found_files.add(fname)
                    chunk_counts[fname] = chunk_counts.get(fname, 0) + 1
        
        if not found_files:
            print(f"No files found matching '{filename_substring}'")
        else:
            print(f"Found {len(found_files)} matching files:")
            for fname in found_files:
                print(f"  - {fname}: {chunk_counts[fname]} chunks")

    check_file_in_db("Dima")

    def check_embedding_distances():
        print(f"\n--- Checking raw embedding distances ---")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        t1 = "Who is Dima Fomberg?"
        t2 = "Dima Fomberg is a Cyber Threat Hunting expert."
        t3 = "Nitzan Cohen is a sales representative."
        
        e1 = model.encode([t1])
        e2 = model.encode([t2])
        e3 = model.encode([t3])
        
        # Calculate manual L2 distance
        import numpy as np
        d12 = np.sum((e1 - e2) ** 2)
        d13 = np.sum((e1 - e3) ** 2)
        
        print(f"Distance ('{t1}' vs '{t2}'): {d12:.4f}")
        print(f"Distance ('{t1}' vs '{t3}'): {d13:.4f}")
        
    check_embedding_distances()
