First we build the frontend. It will be a simple Angular frontend, but as we are security people here we will of course wire it with GCIP (Firebase authentication). The gui has two sections: an upload file function which allows you to upload a PDF and a simple chat box to ask questions from the model.

Great! The entire thing works and we even have a small logout button. Behind the scenes you get an ID token from the authentication service and you go this protected route which has our “Upload accident report” and “AI assistant” chat.

Now on to the backend - We will use FastAPI with a couple of routes:
/upload - This gets the pdf file, assigns UUID, uploads it to Google cloud storage and finally publishes an event to pub/sub.

There is a function that sets up the ChromaDB and initializes our embedding model and Vertex AI client. We do this at startup to ensure the application is ready to serve queries immediately, loading the `all-MiniLM-L6-v2` model into memory so it’s hot and ready.

Finally, we implement the `/chat` route—the core of our RAG system. This endpoint accepts the user’s question and performs the standard retrieval dance: it embeds the text, searches our ChromaDB collection for the most relevant chunks, and feeds those "safe" context snippets into Gemini. By the time data reaches this point, it has already been sanitized by our ingestion worker, so the LLM never touches the raw, potentially malicious PDF file.

Finally, we have the "Processor"—our silent guardian. This service listens to the Pub/Sub topic for new file events. When a file lands, it wakes up, grabs the file from the Ingest Bucket, and performs the critical "Content Disarming" step.

In our demo, we use a Python script that extracts clean text from the PDF (using basic extraction for now, but conceptually replacing it with a robust CDR tool), chopping it into digestible chunks with **overlap** to maintain context across boundaries. It then runs these chunks through the same embedding model (`all-MiniLM-L6-v2`) and upserts the resulting vectors into our ChromaDB. This ensures that only safe, semantic representations of the data exist in our queryable database, leaving any potential malware behind in the cold, isolated storage bucket.
