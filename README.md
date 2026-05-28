# PDF / Notes Chatbot using RAG

An AI-powered PDF and Notes chatbot built using Retrieval-Augmented Generation (RAG).
Users can upload PDF documents and ask questions based on the uploaded content.

The system extracts text, creates embeddings, stores them in a FAISS vector database, retrieves relevant chunks, and generates answers using an LLM.

---

# Features

* Upload PDF documents
* Extract text from PDFs
* Text chunking
* Embedding generation
* FAISS vector database
* Semantic search
* AI-powered question answering
* Chat history
* Mind map generation
* FastAPI backend
* Modern UI using HTML/CSS

---

# Tech Stack

## Backend

* Python
* FastAPI

## AI / RAG

* Sentence Transformers
* FAISS
* Groq / Gemini API

## Frontend

* HTML
* CSS
* Jinja2 Templates

---

# Project Structure

```bash
project/
│
├── main.py
├── utils.py
├── requirements.txt
├── render.yaml
│
├── templates/
│   └── index.html
│
├── data/
│   └── uploads/
│
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone YOUR_GITHUB_REPO_URL
cd PROJECT_NAME
```

---

# Create Virtual Environment

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Project

```bash
uvicorn main:app --reload
```

Open browser:

```bash
http://127.0.0.1:8000
```

---

# API Key Setup

## Groq API Key

Create API key:

https://console.groq.com/keys

Paste the key into the sidebar input inside the application.

---

# How It Works

1. User uploads PDF
2. PDF text is extracted
3. Text is chunked
4. Embeddings are created
5. Embeddings stored in FAISS
6. User asks question
7. Relevant chunks retrieved
8. LLM generates answer

---

# Deployment

## Deploy on Render

1. Push project to GitHub
2. Login to Render
3. Create Web Service
4. Connect GitHub repository
5. Add build command:

```bash
pip install -r requirements.txt
```

6. Add start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

7. Deploy

---

# Future Improvements

* Multiple PDF support
* Voice assistant
* Authentication system
* Database integration
* Streaming responses
* Better RAG pipeline
* Citation support
* PDF summarization

---





---

# Author

Developed by Vineela Srighakolapu

---

