
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.records import load_records, search, get_by_id


# Create FastAPI application
app = FastAPI(
    title="SuryaGharSathi API",
    description="API for PM Surya Ghar rooftop solar information",
    version="1.0.0"
)


# Request model for user questions
class QuestionRequest(BaseModel):
    question: str
    name: Optional[str] = None


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to SuryaGharSathi API",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "SuryaGharSathi API is running"
    }


# Get all records
@app.get("/records")
def get_all_records(limit: int = Query(default=100, ge=1, le=100)):
    records = load_records()

    records = records[:limit]

    return {
        "total_records": len(records),
        "records": records
    }


# Get record by ID
@app.get("/records/{record_id}")
def get_record(record_id: int):

    record = get_by_id(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return record


# Search records
@app.get("/search")
def search_records(q: str = Query(..., min_length=1)):

    results = search(q)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No matching records found"
        )

    return {
        "keyword": q,
        "total_results": len(results),
        "results": results
    }


# Accept user questions
@app.post("/questions")
def submit_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    return {
        "status": "received",
        "name": request.name,
        "question": question,
        "message": "Your question has been received successfully."
    }
