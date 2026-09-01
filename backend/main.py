"""
main.py — FastAPI Web Server
Provides REST endpoints for the AI Smart Automation Agent.
Endpoints:
- POST /api/upload: Upload & extract text from .txt, .pdf, .md, .csv
- POST /api/summarize: Run text summarization (short/medium/detailed)
- POST /api/qa: Answer grounded questions about document context
- POST /api/generate: Generate follow-ups/emails/content from context
- POST /api/analyze: Deep analysis (Key points, action items, tone)
- GET /api/health: Health check endpoint
"""

import os
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ai_service
import file_utils

app = FastAPI(
    title="AI Smart Automation Agent API",
    description="High-performance backend for document intelligence, summarization, Q&A, and content generation.",
    version="1.0.0"
)

# Enable CORSp for local development and web UI clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Request & Response Models
class SummarizeRequest(BaseModel):
    text: str
    length: Optional[str] = "medium"


class QARequest(BaseModel):
    text: str
    question: str


class GenerateRequest(BaseModel):
    text: str
    instruction: Optional[str] = "Write a professional follow-up email based on this content."


class AnalyzeRequest(BaseModel):
    text: str


class ActionResponse(BaseModel):
    status: str
    result: str
    mode: str
    suggested_actions: List[dict]


@app.get("/api/health")
def health_check():
    """Returns status of backend service and configured AI API providers."""
    return {
        "status": "online",
        "gemini_configured": bool(ai_service.GEMINI_KEY),
        "anthropic_configured": bool(ai_service.ANTHROPIC_KEY)
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a document file (.txt, .pdf, .md, .csv) and extracts clean text."""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided in request.")

    try:
        contents = await file.read()
        extracted_text, error = file_utils.extract_text_from_file(file.filename, contents)
        
        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "filename": file.filename,
            "size_bytes": len(contents),
            "extracted_text": extracted_text,
            "character_count": len(extracted_text)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error processing file upload: {str(e)}")


@app.post("/api/summarize", response_model=ActionResponse)
def summarize_endpoint(req: SummarizeRequest):
    """Executes text summarization."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")

    res = ai_service.summarize(req.text, req.length or "medium")
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    suggestions = ai_service.suggest_next_actions("summarize")

    return ActionResponse(
        status="success",
        result=res["result"],
        mode=res.get("mode", "api"),
        suggested_actions=suggestions
    )


@app.post("/api/qa", response_model=ActionResponse)
def qa_endpoint(req: QARequest):
    """Executes grounded question answering."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Document text context cannot be empty.")
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    res = ai_service.answer_question(req.text, req.question)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    suggestions = ai_service.suggest_next_actions("qa")

    return ActionResponse(
        status="success",
        result=res["result"],
        mode=res.get("mode", "api"),
        suggested_actions=suggestions
    )


@app.post("/api/generate", response_model=ActionResponse)
def generate_endpoint(req: GenerateRequest):
    """Executes content generation based on prompt instruction & context."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Document context text cannot be empty.")

    instruction = req.instruction or "Write a professional follow-up email based on this document."
    res = ai_service.generate_content(req.text, instruction)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    suggestions = ai_service.suggest_next_actions("generate")

    return ActionResponse(
        status="success",
        result=res["result"],
        mode=res.get("mode", "api"),
        suggested_actions=suggestions
    )


@app.post("/api/analyze", response_model=ActionResponse)
def analyze_endpoint(req: AnalyzeRequest):
    """Executes document analysis for key points, action items, and tone."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    res = ai_service.analyze_text(req.text)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    suggestions = ai_service.suggest_next_actions("analyze")

    return ActionResponse(
        status="success",
        result=res["result"],
        mode=res.get("mode", "api"),
        suggested_actions=suggestions
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"[AURA AI] Starting AI Smart Automation Agent Backend on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
