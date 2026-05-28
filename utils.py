import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from google import genai
import datetime
import markdown
import os

# ================= LOAD EMBEDDING MODEL =================
model = SentenceTransformer("all-MiniLM-L6-v2")


class AXONRAG:

    def __init__(self):

        self.index = None
        self.chunks = []
        self.sessions = {}
        self.document_type = None

    # ================= READ PDF =================
    def read_pdf(self, path):

        self.document_type = os.path.splitext(path)[1]

        reader = PdfReader(path)

        text = ""

        for page in reader.pages:

            content = page.extract_text()

            if content:
                text += content + "\n"

        return text

    # ================= CHUNK TEXT =================
    def chunk_text(self, text, chunk_size=200):

        words = text.split()

        self.chunks = []

        for i in range(0, len(words), chunk_size):

            chunk = " ".join(words[i:i + chunk_size])

            self.chunks.append(chunk)

    # ================= BUILD VECTOR INDEX =================
    def build_index(self):

        if not self.chunks:
            return False

        embeddings = model.encode(self.chunks)

        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings)

        return True

    # ================= RETRIEVE =================
    def retrieve(self, query, k=1):

        if self.index is None:
            return []

        query_embedding = model.encode([query])

        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, k)

        results = []

        for i in indices[0]:

            if i < len(self.chunks):
                results.append(self.chunks[i])

        return results

    # ================= SEARCH DOCS =================
    def tool_search_docs(self, query):

        results = self.retrieve(query)

        return "\n\n".join(results)

    # ================= MIND MAP =================
    def tool_mind_map(self, topic):

        nodes = {
            topic: [
                "Definition",
                "Service Models",
                "Deployment Models",
                "Benefits",
                "Providers"
            ],
            "Service Models": ["IaaS", "PaaS", "SaaS"],
            "Deployment Models": [
                "Public Cloud",
                "Private Cloud",
                "Hybrid Cloud"
            ],
            "Benefits": [
                "Scalability",
                "Cost Efficiency",
                "Flexibility"
            ],
            "Providers": [
                "AWS",
                "Azure",
                "GCP"
            ]
        }

        diagram = "mindmap\n"

        diagram += f"  root(({topic}))\n"

        for main in nodes[topic]:

            diagram += f"    {main}\n"

            if main in nodes:

                for sub in nodes[main]:

                    diagram += f"      {sub}\n"

        return diagram

    # ================= DOCUMENT TYPE =================
    def tool_document_type(self):

        if not self.document_type:
            return "No document uploaded."

        ext = self.document_type.lower()

        if ext == ".pdf":
            return "Document Type: PDF"

        if ext in [".ppt", ".pptx"]:
            return "Document Type: PowerPoint"

        if ext in [".doc", ".docx"]:
            return "Document Type: Word Document"

        return f"Document Type: {ext}"

    # ================= TOOL ROUTER =================
    def choose_tool(self, question):

        q = question.lower()

        if "mind map" in q or "mindmap" in q:
            return "mindmap"

        if (
            "document type" in q
            or "file type" in q
            or "pdf or ppt" in q
        ):
            return "doctype"

        return "search"

    # ================= ASK =================
    def ask(self, session_id, question, api_key):

        if self.index is None:
            return "⚠ Please upload a document first."

        tool = self.choose_tool(question)

        # ================= MIND MAP =================
        if tool == "mindmap":

            diagram = self.tool_mind_map(question)

            answer = f"<div class='mermaid'>{diagram}</div>"

        # ================= DOCUMENT TYPE =================
        elif tool == "doctype":

            answer = markdown.markdown(
                self.tool_document_type()
            )

        # ================= NORMAL RAG =================
        else:

            if not api_key:
                answer = "⚠ Please enter Gemini API key."

            else:

                context = self.tool_search_docs(question)

                prompt = f"""
You are an AI study assistant.

Use the provided document context to answer clearly and shortly.

Context:
{context}

Question:
{question}
"""

                try:

                    client = genai.Client(api_key=api_key)

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    if not response:

                        answer = "⚠ No response received."

                    elif not hasattr(response, "text"):

                        answer = "⚠ Empty response from Gemini."

                    elif not response.text:

                        answer = "⚠ Gemini returned blank response."

                    else:

                        answer = markdown.markdown(
                            response.text
                        )

                except Exception as e:

                    error_message = str(e)

                    if "429" in error_message:

                        answer = """
                        ⚠ Gemini quota exceeded.<br><br>

                        Please:
                        <br>
                        • Create a new API key
                        <br>
                        • Or wait some time
                        <br>
                        • Or try again later
                        """

                    else:

                        answer = f"""
                        ⚠ Gemini Error:<br><br>
                        {error_message}
                        """

        # ================= STORE CHAT =================
        if session_id not in self.sessions:

            self.sessions[session_id] = {
                "history": [],
                "name": "New Chat",
                "created_at": datetime.datetime.now()
            }

        if len(self.sessions[session_id]["history"]) == 0:

            self.sessions[session_id]["name"] = question[:30]

        self.sessions[session_id]["history"].append(
            (question, answer)
        )

        return answer

    # ================= GET HISTORY =================
    def get_history(self, session_id):

        return self.sessions.get(
            session_id,
            {}
        ).get("history", [])

    # ================= GET SESSIONS =================
    def get_sessions(self):

        return self.sessions


# ================= OBJECT =================
axon_rag = AXONRAG()