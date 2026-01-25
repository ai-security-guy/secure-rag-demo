---
title: "Securing RAG Systems: Part 1 - Building the Foundation"
date: 2025-12-31T10:00:00Z
draft: false
tags: ["security", "RAG", "AI", "GCP", "AppSec"]
categories: ["Security"]
description: "Part 1 of a series on securing RAG systems. We build a simple RAG application on GCP to set the stage for threat modeling."
thumbnail: "rag_architecture.png"
---

In a past life, I worked in highly secure, regulated government environments. Bringing in *any* software—even simple tools like Putty or Notepad++—was a nightmare. If I needed files from an untrusted source (like my USB drive), they had to pass through a **CDR** (Content Disarm and Reconstruction) station. This system would churn through antivirus engines and rule sets for 20 minutes just to give me a sanitized 30KB file.

Fast forward to today.

We are all discussing RAG (Retrieval Augmented Generation) systems. AI is impressive on its own, but it becomes truly transformational when you ground it in your own data. Imagine a "Receipt Management System" where you upload your personal expenses, and the AI answers questions about your spending habits.

But here is the catch: **If you allow users to upload files, you are opening a door.** Untrusted input is a classic attack vector. In the world of GenAI, this isn't just about malware; it's about prompt injection and persistent threats stored directly in your knowledge base.

In this three-part series, we are going to tackle this head-on.
*   **Part 1 (This post will cover):** Building a simple, functional RAG system on GCP.
*   **Part 2:** Threat Modeling the risks (the fun stuff).
*   **Part 3:** Securing the system using GCP native controls.

Let's start by building a Content Disarming system and a functional RAG demo on Google Cloud Platform.

### The Hitchhiker's Guide to RAG (in 30 Seconds)

First, a quick refresher. What is RAG?

Large Language Models (LLMs) are trained on vast amounts of internet data—Reddit threads, books, Wikipedia, and more. They know a lot, but they have two major limitations:
1.  **Cutoff Dates:** Their training data is frozen in time. They don't know who won the football game last September.
2.  **Private Knowledge:** They know nothing about *your* private data, like that receipt from your lunch yesterday.

{{< figure src="knowledge_cutoff.png" caption="Models have a knowledge cutoff date." >}}

To fix this, we need to connect the model to an external data source. This is **Retrieval Augmented Generation**—generating answers based on information retrieved from a trusted source.

{{< figure src="receipt_question.png" caption="RAG connects the model to your private data." >}}

#### Two Key Concepts: Embeddings & Vector Databases

1.  **Embeddings**: Think of these as a universal translator. They turn human language (text, images, audio) into long lists of numbers (vectors) that capture *meaning* and *context*. In this space, the numbers for "dog" are mathematically closer to "puppy" than to "sandwich."

2.  **Vector Database**: If embeddings are the coordinates, the Vector Database is the map. Unlike a standard SQL database that looks for exact keyword matches (which fails if you search "sofa" but the document says "couch"), a Vector Database searches for *similarity*.

{{< figure src="rag_architecture.png" caption="How RAG Retrieval works." >}}

When you ask a question, the system acts like a librarian:
1.  It converts your question into numbers (embedding).
2.  It finds the most relevant pages in the library (retrieval from Vector DB).
3.  It hands those pages to the AI and says, "Use this to answer the user's question."

*(If you want a deeper dive, [this article by Pinecone](https://www.pinecone.io/learn/retrieval-augmented-generation/) is excellent.)*

---

### Let's Build It: The Demo App

Our demo will be a **Simulated Insurance Claims Bot**. Customers upload PDF accident reports, and the bot helps customer service agents process the claims.

**The functional requirements are simple:**
*   User uploads a car accident report (PDF).
*   User asks questions (e.g., "How much is the refund request?").
*   System answers based *only* on the uploaded document.

### The Tech Stack

*   **Frontend**: Angular on Cloud Run (with simple file upload & chat UI).
*   **Auth**: Google Cloud Identity Platform (GCIP) / Firebase Auth.
*   **Storage**: Google Cloud Storage (for raw PDFs).
*   **Messaging**: Pub/Sub (triggers events when files are uploaded).
*   **Processing**:
    *   **PDF Parsing**: Docling (to extracting text).
    *   **Embeddings**: `all-MiniLM-L6-v2` (via Hugging Face).
*   **Database**: ChromaDB (Vector Database).
*   **AI**: Vertex AI (Gemini).

{{< figure src="demo_architecture.png" caption="The RAG Demo Architecture." >}}

### Step 1: The Frontend

We'll start with a simple Angular app. Since we are security professionals, we wouldn't dare build this without authentication, so it's wired up with GCIP.

The UI has two main sections:
1.  **Upload**: Select and send your PDF.
2.  **Chat**: Ask the "AI Assistant" questions about the report.

{{< figure src="working_gui.png" caption="The simple Angular frontend." >}}

Behind the scenes, when you log in, you get an ID token. This token allows access to our protected backend routes.

### Step 2: The Backend (FastAPI)

We use FastAPI for our heavy lifting with two main routes:

1.  `POST /upload`:
    *   Receives the PDF.
    *   Assigns a unique UUID.
    *   Uploads it to Cloud Storage.
    *   Publishes a "New File" event to Pub/Sub.

2.  `POST /chat`:
    *   Embeds the user's query.
    *   Searches ChromaDB for relevant chunks.
    *   Constructs a prompt with those chunks.
    *   Sends the package to Gemini on Vertex AI.

*Note: On startup, we initialize ChromaDB and load our embedding model (`all-MiniLM-L6-v2`) into memory so the system is snappy and ready to serve.*

### Step 3: The "Processor" (The Worker)

This is the engine room. This service listens to our Pub/Sub topic.
1.  **Trigger**: A "New File" event arrives.
2.  **Extract**: It grabs the PDF from the Ingest Bucket and uses **Docling** to extract clean text. (In a real production system, this is where we'd build our robust CDR pipeline).
3.  **Chunk & Embed**: It chops the text into digestible pieces, runs them through the embedding model, and upserts the vectors to ChromaDB.

This architecture ensures that only the *semantic representation* of the data enters our queryable database. The raw file—potentially containing malware—stays isolated in the storage bucket.

*(You can find the full source code on [GitHub](https://github.com/ai-security-guy/secure-rag-demo) so you can run it yourself!)*

### Does it work?

We have a working pipeline. Let's test it.

1.  **Upload**: [Action: Uploading a sample PDF file] -> Success.

{{< figure src="upload_working.png" caption="File upload successful." >}}

2.  **Ask**: "Who is Dima Fomberg?"
3.  **Answer**: "Dima Fomberg is an AI security guy..."

{{< figure src="example_question.png" caption="RAG in action: Answering questions from the uploaded report." >}}

Not bad! We have a functional RAG system.

### What's Next? Threat Modeling.

We built it, it works, and it looks cool. But as security people, when we see a design like this, our alarm bells should be ringing.

In **Part 2**, we will perform a full Threat Model of this architecture, identify the attack surface, and see exactly how bad actors could exploit our shiny new toy.

See you in Part 2!