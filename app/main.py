
import os

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.llm import generate_chat_response
from app.records import get_by_id, load_records, search
from app.smart_search import smart_search

# Day 7: Vector store for semantic search
try:
    from app.vectorstore import query_vectorstore
    VECTORSTORE_AVAILABLE = True
except ImportError:
    VECTORSTORE_AVAILABLE = False

# Day 8: RAG pipeline
try:
    from app.rag import answer_question
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# Day 9: Agent with tools and graph
try:
    from app.graph import run_graph_agent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False


# Create FastAPI application
app = FastAPI(
    title="SuryaGharSathi API",
    description="API for PM Surya Ghar rooftop solar information",
    version="1.0.0"
)


# Request model for user questions
class QuestionRequest(BaseModel):
    question: str
    name: str | None = None


# Request model for chat (LLM-powered Q&A)
class ChatRequest(BaseModel):
    question: str
    use_rag: bool = True
    top_k: int = 5
    prompt_version: str = "v2"  # "v1" or "v2"


# Request model for RAG /ask endpoint (Day 8)
class AskRequest(BaseModel):
    question: str
    top_k: int | None = 4


# Request model for Agent /agent endpoint (Day 9)
class AgentRequest(BaseModel):
    question: str
    thread_id: str | None = "default"
    approved: bool | None = True


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


# LLM-powered chat endpoint with RAG (Day 6 Enhanced)
@app.post("/chat")
def chat_with_llm(request: ChatRequest):
    """
    Answer user questions using LLM with RAG (Retrieval-Augmented Generation).

    Day 6 Enhancement:
    - Returns structured JSON: {answer, confidence, follow_up}
    - Supports prompt version selection (v1 or v2)
    - Offline fallback when no API key configured

    Process:
    1. Validate question
    2. Retrieve relevant records if use_rag=true
    3. Call LLM with selected prompt version
    4. Return structured response

    Args:
        request: ChatRequest with question, use_rag, top_k, prompt_version

    Returns:
        JSON with answer, confidence, follow_up, and metadata
    """
    question = request.question.strip()

    # Validate question
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Generate response using new llm.py module
        response = generate_chat_response(
            question=question,
            prompt_version=request.prompt_version,
            use_rag=request.use_rag,
            top_k=request.top_k
        )

        # Add metadata
        result = {
            "question": question,
            "answer": response["answer"],
            "confidence": response["confidence"],
            "follow_up": response["follow_up"],
            "prompt_version": request.prompt_version,
            "rag_enabled": request.use_rag,
            "provider": os.getenv("LLM_PROVIDER", "groq"),
            "model": os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        }

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {e!s}"
        )


# Semantic search endpoint (Day 7)
@app.get("/search/semantic")
def search_semantic(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=5, ge=1, le=20, description="Number of results")
):
    """
    Semantic search using dense vector embeddings (ChromaDB).

    Day 7 Feature:
    - Uses sentence-transformers embeddings
    - Queries persistent ChromaDB vector store
    - Returns chunks with metadata and similarity scores

    Args:
        q: Search query
        limit: Number of results (1-20)

    Returns:
        JSON with query, search_method, total_results, and results list
    """
    if not VECTORSTORE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Semantic search not available. Install chromadb and sentence-transformers."
        )

    try:
        # Query vector store
        results = query_vectorstore(q, top_k=limit)

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No matching chunks found"
            )

        return {
            "query": q,
            "search_method": "semantic_embeddings",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "total_results": len(results),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {e!s}"
        )


# RAG endpoint with grounded citations (Day 8)
@app.post("/ask")
def ask_rag_endpoint(request: AskRequest):
    """
    RAG-powered Q&A with grounded citations from PM Surya Ghar guidelines.

    Day 8 Feature:
    - Retrieves top-k semantic chunks with date prioritization
    - Generates grounded answers with inline citations
    - Returns "I don't know" for unanswerable queries (Q6)
    - Includes structured citation metadata

    Args:
        request: AskRequest with question and optional top_k

    Returns:
        JSON with question, answer, citations, confidence
    """
    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not available. Check app/rag.py setup."
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Call RAG pipeline
        result = answer_question(question, top_k=request.top_k)

        return {
            "question": result["question"],
            "answer": result["answer"],
            "citations": result["citations"],
            "confidence": result["confidence"],
            "abstained": result.get("abstained", False),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {e!s}"
        )


# Agent endpoint with tools and approval gate (Day 9)
@app.post("/agent")
def agent_endpoint(request: AgentRequest):
    """
    LangGraph agent with solar CFA calculator tool and approval gate.

    Day 9 Features:
    - Calls solar_cfa_calculator for capacity/subsidy/cost calculations
    - Calls answer_question (RAG) for policy/guideline citations
    - Multi-turn memory via thread_id
    - Approval gate for >3 kW systems (subsidy capped)
    - Combines tool outputs with RAG citations

    Args:
        request: AgentRequest with question, thread_id, approved

    Returns:
        JSON with answer, tools_used, tool_output, citations, approval_status, thread_id
    """
    if not AGENT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Agent not available. Check app/graph.py and dependencies (langgraph)."
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Call graph agent
        result = run_graph_agent(
            question=question,
            thread_id=request.thread_id,
            approved=request.approved
        )

        return {
            "question": result["question"],
            "answer": result["answer"],
            "tools_used": result.get("tools_used", []),
            "tool_output": result.get("tool_output", {}),
            "citations": result.get("citations", []),
            "approval_status": result.get("approval_status", "not_required"),
            "requires_approval": result.get("requires_approval", False),
            "thread_id": result["thread_id"],
            "history_length": len(result.get("history", [])),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {e!s}"
        )
