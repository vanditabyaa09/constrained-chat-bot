import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Ensure the app can find the 'app' module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import PDFAgent

load_dotenv()

app = FastAPI(title="PDF Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton Agent instance
HF_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_API_TOKEN not found in environment variables")

agent = PDFAgent(HF_TOKEN)

class ChatRequest(BaseModel):
    query: str
    history: List[Dict] = []

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file, processes it, and builds the retrieval index.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Use a temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Load and process the PDF
        # We rename the file internally to keep the original filename in metadata
        final_path = os.path.join(os.path.dirname(tmp_path), file.filename)
        os.rename(tmp_path, final_path)
        
        result = agent.load_pdf(final_path)
        
        # Cleanup
        if os.path.exists(final_path):
            os.remove(final_path)
            
        return result
        
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Processes a chat query using the loaded PDF context.
    """
    try:
        # Pass the history to the agent
        # The agent.chat refactor now handles the history list format
        response = agent.chat(request.query, request.history)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reset")
async def reset():
    """
    Clears the current agent state (retriever and history).
    """
    try:
        agent.retriever = None
        agent.clear_history()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files from the React build directory
# This should be at the end so it doesn't override other routes
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
