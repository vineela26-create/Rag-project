from fastapi import FastAPI, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import os
import shutil
import uuid

from utils import axon_rag

# ================= APP =================
app = FastAPI()

templates = Jinja2Templates(directory="templates")

# ================= UPLOAD FOLDER =================
UPLOAD_DIR = "data/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ================= GLOBALS =================
current_session = str(uuid.uuid4())

status_message = "Awaiting document upload..."

stored_api_key = None


# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={
            "history": axon_rag.get_history(current_session),
            "sessions": axon_rag.get_sessions(),
            "current_session": current_session,
            "status": status_message
        }
    )


# ================= NEW CHAT =================
@app.post("/new")
async def new_chat():

    global current_session, status_message

    current_session = str(uuid.uuid4())

    status_message = "🆕 New chat initialized."

    return RedirectResponse("/", status_code=303)


# ================= SWITCH CHAT =================
@app.post("/switch/{session_id}")
async def switch_chat(session_id: str):

    global current_session

    if session_id in axon_rag.sessions:

        current_session = session_id

    return RedirectResponse("/", status_code=303)


# ================= DELETE CHAT =================
@app.post("/delete/{session_id}")
async def delete_chat(session_id: str):

    global current_session, status_message

    if session_id in axon_rag.sessions:

        del axon_rag.sessions[session_id]

        status_message = "🗑️ Chat deleted."

    # If current session deleted
    if current_session == session_id:

        current_session = str(uuid.uuid4())

    return RedirectResponse("/", status_code=303)


# ================= RENAME CHAT =================
@app.post("/rename/{session_id}")
async def rename_chat(
    session_id: str,
    new_name: str = Form(...)
):

    if session_id in axon_rag.sessions:

        axon_rag.sessions[session_id]["name"] = new_name

    return RedirectResponse("/", status_code=303)


# ================= UPLOAD PDF =================
@app.post("/upload")
async def upload(file: UploadFile):

    global status_message

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    # Read PDF
    text = axon_rag.read_pdf(file_path)

    # Chunk text
    axon_rag.chunk_text(text)

    # Build vector index
    success = axon_rag.build_index()

    if success:

        status_message = "✅ PDF uploaded and processed."

    else:

        status_message = "⚠ Failed to process PDF."

    return RedirectResponse("/", status_code=303)


# ================= CHAT =================
@app.post("/chat")
async def chat(
    question: str = Form(...),
    api_key: str = Form(None)
):

    global stored_api_key, status_message

    # Save API key
    if api_key:

        stored_api_key = api_key

    # Validate API key
    if not stored_api_key:

        status_message = "⚠ Please enter API key."

        return RedirectResponse("/", status_code=303)

    try:

        # Generate answer
        answer = axon_rag.ask(
            current_session,
            question,
            stored_api_key
        )

        print("\nQUESTION:", question)

        print("\nANSWER:", answer)

        status_message = "✅ Response generated."

    except Exception as e:

        print("\nERROR:", str(e))

        status_message = f"⚠ Error: {str(e)}"

    return RedirectResponse("/", status_code=303)