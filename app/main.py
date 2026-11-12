
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.records import load_records, search, get_by_id
from app.smart_search import smart_search


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

    # Convert Record objects to dicts for JSON serialization
    records_dict = []
    for record in records:
        records_dict.append({
            "record_id": record.record_id,
            "document_title": record.document_title,
            "issuing_body": record.issuing_body,
            "date_issued": record.date_issued,
            "topic": record.topic,
            "key_rule": record.key_rule,
            "source": record.source,
            "source_section": record.source_section,
            "source_pages": record.source_pages
        })

    return {
        "total_records": len(records_dict),
        "records": records_dict
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

    # Convert Record object to dict for JSON serialization
    return {
        "record_id": record.record_id,
        "document_title": record.document_title,
        "issuing_body": record.issuing_body,
        "date_issued": record.date_issued,
        "topic": record.topic,
        "key_rule": record.key_rule,
        "source": record.source,
        "source_section": record.source_section,
        "source_pages": record.source_pages
    }


# Search records using smart TF-IDF search
@app.get("/search")
def search_records(q: str = Query(..., min_length=1)):
    """
    Search records using TF-IDF + cosine similarity ranking.
    Falls back to keyword search if smart search returns no results.
    """
    # Try smart search first (TF-IDF + cosine similarity)
    smart_results = smart_search(q, top_k=10)
    
    if smart_results:
        # Convert (Record, score) tuples to dict format for JSON response
        results = []
        for record, score in smart_results:
            result_dict = {
                "record_id": record.record_id,
                "topic": record.topic,
                "key_rule": record.key_rule,
                "document_title": record.document_title,
                "issuing_body": record.issuing_body,
                "date_issued": record.date_issued,
                "source": record.source,
                "source_section": record.source_section,
                "source_pages": record.source_pages,
                "relevance_score": round(score, 4)
            }
            results.append(result_dict)
        
        return {
            "query": q,
            "search_method": "smart_search",
            "total_results": len(results),
            "results": results
        }
    
    # Fallback to keyword search
    keyword_results = search(q)
    
    if not keyword_results:
        raise HTTPException(
            status_code=404,
            detail="No matching records found"
        )
    
    # Convert Record objects to dicts
    results = []
    for record in keyword_results:
        result_dict = {
            "record_id": record.record_id,
            "topic": record.topic,
            "key_rule": record.key_rule,
            "document_title": record.document_title,
            "issuing_body": record.issuing_body,
            "date_issued": record.date_issued,
            "source": record.source,
            "source_section": record.source_section,
            "source_pages": record.source_pages
        }
        results.append(result_dict)

    return {
        "query": q,
        "search_method": "keyword_search",
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
