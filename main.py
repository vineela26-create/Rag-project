from fastapi import FastAPI, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid

from utils import axon_rag

app = FastAPI()

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

current_session = str(uuid.uuid4())
status_message = "Awaiting document upload..."
stored_api_key = None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "history": axon_rag.get_history(current_session),
            "sessions": axon_rag.get_sessions(),
            "current_session": current_session,
            "status": status_message
        }
    )


@app.post("/new")
async def new_chat():

    global current_session, status_message

    current_session = str(uuid.uuid4())

    status_message = "New chat initialized."

    return RedirectResponse("/", status_code=303)


@app.post("/upload")
async def upload(file: UploadFile):

    global status_message

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = axon_rag.read_pdf(file_path)

    axon_rag.chunk_text(text)

    success = axon_rag.build_index()

    if success:
        status_message = "✅ PDF uploaded and processed."
    else:
        status_message = "⚠ Failed to process PDF."

    return RedirectResponse("/", status_code=303)


@app.post("/chat")
async def chat(question: str = Form(...), api_key: str = Form(None)):

    global stored_api_key, status_message

    # Save API key
    if api_key:
        stored_api_key = api_key

    # Check API key
    if not stored_api_key:

        status_message = "⚠ Please enter Gemini API key."

        return RedirectResponse("/", status_code=303)

    try:

        # Generate answer
        answer = axon_rag.ask(
            current_session,
            question,
            stored_api_key
        )

        print("QUESTION:", question)
        print("ANSWER:", answer)

        status_message = "✅ Response generated."

    except Exception as e:

        print("ERROR:", str(e))

        status_message = f"⚠ Error: {str(e)}"

    return RedirectResponse("/", status_code=303)