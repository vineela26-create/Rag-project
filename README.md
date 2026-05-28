# PDF / Notes Chatbot using RAG

This project allows users to upload a PDF and ask questions about its content
using Retrieval-Augmented Generation (RAG).

## Features
- Upload PDF
- Convert PDF to text
- Chunk text
- Create embeddings
- Store in FAISS
- Retrieve relevant content
- Answer using Gemini

## Run Project
```bash
pip install -r requirements.txt
uvicorn main:app --reload
