
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import os

from app.records import load_records, search, get_by_id
from app.smart_search import smart_search
from app.llm_client import get_llm_client, get_system_prompt, build_rag_context


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


# Request model for chat (LLM-powered Q&A)
class ChatRequest(BaseModel):
    question: str
    use_rag: bool = True
    top_k: int = 5


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


# LLM-powered chat endpoint with RAG
@app.post("/chat")
def chat_with_llm(request: ChatRequest):
    """
    Answer user questions using LLM with RAG (Retrieval-Augmented Generation).
    
    Process:
    1. Validate question
    2. Search for relevant records (RAG)
    3. Build context from retrieved records
    4. Send to LLM with system prompt
    5. Return LLM-generated answer with sources
    
    Args:
        request: ChatRequest with question, use_rag flag, and top_k
    
    Returns:
        JSON with answer, sources, and metadata
    """
    question = request.question.strip()
    
    # Validate question
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        # Check if LLM is configured
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here" or api_key == "gsk_demo_key_for_testing":
            return {
                "question": question,
                "answer": "LLM is not configured. Please set GROQ_API_KEY in .env file. Get your free API key from https://console.groq.com/keys",
                "sources": [],
                "rag_enabled": False,
                "error": "API key not configured"
            }
        
        # Step 1: RAG - Retrieve relevant records
        rag_context = None
        retrieved_sources = []
        
        if request.use_rag:
            smart_results = smart_search(question, top_k=request.top_k)
            
            if smart_results:
                # Convert to dict format for context building
                retrieved_records = []
                for record, score in smart_results:
                    rec_dict = {
                        "record_id": record.record_id,
                        "topic": record.topic,
                        "key_rule": record.key_rule,
                        "source_section": record.source_section,
                        "relevance_score": round(score, 4)
                    }
                    retrieved_records.append(rec_dict)
                    
                    # Track sources for response
                    retrieved_sources.append({
                        "record_id": record.record_id,
                        "topic": record.topic,
                        "source_section": record.source_section,
                        "relevance_score": round(score, 4)
                    })
                
                # Build context string
                rag_context = build_rag_context(retrieved_records)
        
        # Step 2: Initialize LLM client
        llm_client = get_llm_client()
        
        # Step 3: Get system prompt
        system_prompt = get_system_prompt()
        
        # Step 4: Generate LLM response
        answer = llm_client.generate(
            prompt=question,
            system_prompt=system_prompt,
            context=rag_context,
        )
        
        # Step 5: Return structured response
        return {
            "question": question,
            "answer": answer,
            "sources": retrieved_sources,
            "rag_enabled": request.use_rag,
            "rag_results_count": len(retrieved_sources),
            "model": llm_client.model,
            "provider": llm_client.provider
        }
    
    except ValueError as e:
        # Configuration error (missing API key, etc.)
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    
    except Exception as e:
        # LLM API error or other failures
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )
