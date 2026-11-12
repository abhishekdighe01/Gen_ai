# Checkpoint 1 — Code Review & Walkthrough

**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  
**Project:** SuryaGharSathi (SJ-64) — PM Surya Ghar Rooftop Solar Assistant  
**Date:** Day 5 — Week 1 Milestone  

---

## 1. Project Overview

**SuryaGharSathi** is a FastAPI-based question-answering system that helps homeowners understand PM Surya Ghar: Muft Bijli Yojana rooftop solar subsidy rules, calculate Central Financial Assistance (CFA), and estimate system requirements.

**Tech Stack:**
- **Backend:** FastAPI (Python web framework)
- **Data Storage:** JSON file (`data/records.json` — 85 structured records)
- **Search:** TF-IDF + cosine similarity (scikit-learn)
- **Data Analysis:** Pandas for insights and statistics
- **Documentation:** Markdown + OpenAPI/Swagger

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  USER                                                           │
│  (Homeowner in Kopargaon)                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASTAPI WEB SERVICE (app/main.py)                              │
│  ┌──────────────┬──────────────┬──────────────┬───────────────┐ │
│  │ GET /health  │ GET /records │ GET /search  │ POST /questions│ │
│  │ GET /records/│              │              │               │ │
│  │    {id}      │              │              │               │ │
│  └──────────────┴──────────────┴──────────────┴───────────────┘ │
└────────────┬────────────────────────┬───────────────────────────┘
             │                        │
             ▼                        ▼
┌────────────────────────┐  ┌────────────────────────┐
│  app/records.py        │  │  app/smart_search.py   │
│  • load_records()      │  │  • TF-IDF vectorizer   │
│  • get_by_id()         │  │  • cosine_similarity   │
│  • search()            │  │  • smart_search()      │
└────────────┬───────────┘  └────────────┬───────────┘
             │                           │
             └──────────┬────────────────┘
                        ▼
           ┌────────────────────────┐
           │  data/records.json     │
           │  85 MNRE guideline     │
           │  records               │
           └────────────────────────┘
```

---

## 3. Core Function Walkthrough: `search_records()`

### Function Location
**File:** `app/main.py`  
**Lines:** ~95-140 (approximate)  
**Endpoint:** `GET /search?q={query}`

### Purpose
Search the PM Surya Ghar guidelines dataset for records relevant to a user query, using intelligent TF-IDF-based ranking with keyword fallback.

### Code Walkthrough

```python
@app.get("/search")
def search_records(q: str = Query(..., min_length=1)):
    """
    Search records using TF-IDF + cosine similarity ranking.
    Falls back to keyword search if smart search returns no results.
    """
    # Step 1: Try smart search first (TF-IDF + cosine similarity)
    smart_results = smart_search(q, top_k=10)
    
    if smart_results:
        # Step 2: Convert (Record, score) tuples to dict format for JSON response
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
    
    # Step 3: Fallback to keyword search if no TF-IDF results
    keyword_results = search(q)
    
    if not keyword_results:
        # Step 4: Return 404 if no results found
        raise HTTPException(
            status_code=404,
            detail="No matching records found"
        )
    
    # Step 5: Convert Record objects to dicts for JSON serialization
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
```

### Step-by-Step Explanation

#### Step 1: Smart Search (TF-IDF + Cosine Similarity)

```python
smart_results = smart_search(q, top_k=10)
```

**What happens:**
1. Calls `smart_search()` from `app/smart_search.py`
2. Query is vectorized using TF-IDF (Term Frequency-Inverse Document Frequency)
3. Computes cosine similarity between query vector and all 85 document vectors
4. Returns top 10 most relevant records with similarity scores

**Why TF-IDF?**
- Captures semantic relevance, not just keyword matching
- Ranks results by relevance (most similar documents first)
- Handles synonyms and related terms better than exact string matching

**Example:**
- Query: `"CFA subsidy for 3 kW residential solar"`
- Matches records about "Central Financial Assistance", "3 kW capacity", "residential eligibility" even if exact phrasing differs

#### Step 2: Convert to JSON Response

```python
for record, score in smart_results:
    result_dict = {
        "record_id": record.record_id,
        "topic": record.topic,
        "key_rule": record.key_rule,
        # ... all 9 fields
        "relevance_score": round(score, 4)
    }
    results.append(result_dict)
```

**What happens:**
- Iterates through (Record, score) tuples returned by smart_search
- Converts each Record dataclass object to a dictionary
- Adds `relevance_score` field (0.0 to 1.0) indicating similarity
- Builds list of result dictionaries for JSON serialization

**Why convert?**
- FastAPI automatically serializes Python dicts to JSON
- Dataclass objects need manual conversion via `.to_dict()` or manual dictionary construction
- Allows adding extra fields like `relevance_score` not in the original Record schema

#### Step 3: Keyword Fallback

```python
keyword_results = search(q)
```

**What happens:**
- If TF-IDF search returns no results (empty list), fall back to simple keyword search
- `search()` from `app/records.py` does case-insensitive substring matching on `topic` and `key_rule` fields

**Why fallback?**
- TF-IDF might return no results for very short queries or typos
- Keyword search provides broader coverage
- Ensures users always get some results if the term appears anywhere in the dataset

**Example:**
- Query: `"DCR"` (very short)
- TF-IDF might not vectorize well, but keyword search finds records containing "DCR" or "Domestic Content Requirement"

#### Step 4: Handle No Results

```python
if not keyword_results:
    raise HTTPException(
        status_code=404,
        detail="No matching records found"
    )
```

**What happens:**
- If both smart search AND keyword search return nothing, raise HTTP 404 error
- FastAPI automatically converts HTTPException to proper HTTP response
- Returns JSON: `{"detail": "No matching records found"}`

**Why 404?**
- RESTful API convention: 404 means "resource not found"
- Distinguishes between "no results" (404) and "server error" (500)
- Allows client applications to handle gracefully

#### Step 5: Return Results

```python
return {
    "query": q,
    "search_method": "smart_search",  # or "keyword_search"
    "total_results": len(results),
    "results": results
}
```

**What happens:**
- Returns structured JSON response with metadata
- Includes original query for context
- Specifies which search method was used
- Provides result count and full results array

**Response Example:**
```json
{
  "query": "CFA subsidy 3 kW",
  "search_method": "smart_search",
  "total_results": 5,
  "results": [
    {
      "record_id": 11,
      "topic": "Effective CFA Rates",
      "key_rule": "Effective CFA for general states is Rs 30,000 per kW...",
      "document_title": "Guidelines for PM-Surya Ghar...",
      "issuing_body": "Ministry of New and Renewable Energy (MNRE)...",
      "date_issued": "2024-06-07",
      "source": "https://cdnbbsr.s3waas.gov.in/...",
      "source_section": "Section 5(h)",
      "source_pages": [6],
      "relevance_score": 0.4523
    },
    ...
  ]
}
```

---

## 4. Alternative Function: `get_record()` Walkthrough

### Function Location
**File:** `app/main.py`  
**Endpoint:** `GET /records/{record_id}`

### Purpose
Retrieve a single record by its unique ID, or return 404 if not found.

### Code

```python
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
```

### Explanation

**Step 1: Path Parameter Extraction**
- `{record_id}` in URL path is automatically parsed by FastAPI
- Converted to Python `int` type
- Example: `GET /records/5` → `record_id = 5`

**Step 2: Database Lookup**
```python
record = get_by_id(record_id)
```
- Calls `get_by_id()` from `app/records.py`
- Iterates through all loaded records
- Returns first record where `record.record_id == record_id`
- Returns `None` if no match found

**Step 3: 404 Handling**
```python
if record is None:
    raise HTTPException(status_code=404, detail="Record not found")
```
- Explicit check for missing record
- Raises proper HTTP 404 error
- Clear error message for API consumers

**Step 4: Return Single Record**
- Converts Record object to dictionary
- Returns all 9 fields
- No `relevance_score` (not a search result)

**Why this pattern?**
- Clean separation of concerns: route handler → business logic → data access
- Type safety: FastAPI validates `record_id` is an integer
- Proper HTTP semantics: 200 for success, 404 for not found
- Consistent JSON structure across all endpoints

---

## 5. Data Flow Summary

### 1. User Request
```
GET /search?q=CFA+subsidy+3+kW
```

### 2. FastAPI Routing
```python
@app.get("/search")
def search_records(q: str = Query(..., min_length=1)):
```
- FastAPI matches route pattern
- Extracts query parameter `q`
- Validates `min_length=1` constraint

### 3. Smart Search
```python
# app/smart_search.py
def smart_search(query: str, top_k: int = 5):
    vectorizer, doc_vectors, records = _build_index()  # Load cached index
    query_vector = vectorizer.transform([query])       # Vectorize query
    similarities = cosine_similarity(query_vector, doc_vectors)  # Compute scores
    results = [(records[i], similarities[i]) for i in top_indices]  # Rank
    return results[:top_k]
```

### 4. Response Construction
```python
results = []
for record, score in smart_results:
    results.append({
        "record_id": record.record_id,
        "topic": record.topic,
        # ... all fields
        "relevance_score": round(score, 4)
    })

return {
    "query": q,
    "search_method": "smart_search",
    "total_results": len(results),
    "results": results
}
```

### 5. JSON Serialization
- FastAPI converts Python dict to JSON automatically
- Returns with HTTP 200 status code
- Content-Type: application/json

### 6. User Receives Response
```json
{
  "query": "CFA subsidy 3 kW",
  "search_method": "smart_search",
  "total_results": 5,
  "results": [...]
}
```

---

## 6. Key Design Decisions

### 1. Two-Tier Search Strategy
**Decision:** Try TF-IDF first, fall back to keyword search  
**Rationale:**
- TF-IDF provides superior relevance ranking for complex queries
- Keyword search ensures coverage for simple/short queries
- Best of both worlds: intelligence + robustness

### 2. Explicit 404 Handling
**Decision:** Return HTTP 404 for missing records/no results  
**Rationale:**
- RESTful API best practice
- Distinguishes "not found" from "server error"
- Allows client applications to handle gracefully
- Better than returning empty list with 200 status

### 3. Full Record Serialization
**Decision:** Return all 9 fields in every response  
**Rationale:**
- Reduces need for follow-up requests
- Provides complete context for citations
- Allows rich UI display (source section, page numbers)
- Minimal overhead (records are small)

### 4. Relevance Score Inclusion
**Decision:** Include `relevance_score` in smart search results  
**Rationale:**
- Transparency: users can see why results ranked this way
- Debugging: developers can tune thresholds
- UI enhancement: show confidence indicators
- Future filtering: "only show results above 0.3 score"

### 5. Caching in Smart Search
**Decision:** Cache TF-IDF vectorizer and document vectors globally  
**Rationale:**
- Performance: avoid re-computing on every search
- Consistency: same index for all requests
- Memory efficient: single copy shared across requests
- Trade-off: manual refresh needed when records change

---

## 7. Testing Checkpoint 1

### Manual Testing Commands

#### 1. Start the server
```bash
uvicorn app.main:app --reload
```

#### 2. Test health endpoint
```bash
curl http://127.0.0.1:8000/health
```
**Expected:**
```json
{"status": "healthy", "message": "SuryaGharSathi API is running"}
```

#### 3. Test get all records
```bash
curl "http://127.0.0.1:8000/records?limit=5"
```
**Expected:** JSON with 5 records

#### 4. Test get single record
```bash
curl http://127.0.0.1:8000/records/1
```
**Expected:** Full record with ID 1

#### 5. Test get non-existent record
```bash
curl http://127.0.0.1:8000/records/9999
```
**Expected:** HTTP 404 with error message

#### 6. Test smart search
```bash
curl "http://127.0.0.1:8000/search?q=CFA+subsidy+3+kW"
```
**Expected:** Ranked results with relevance scores

#### 7. Test POST questions
```bash
curl -X POST http://127.0.0.1:8000/questions \
  -H "Content-Type: application/json" \
  -d '{"question":"How much subsidy for 3 kW?","name":"Test User"}'
```
**Expected:** Confirmation message

#### 8. Access Swagger UI
Open browser: `http://127.0.0.1:8000/docs`  
**Expected:** Interactive API documentation with all 5 endpoints

---

## 8. Code Quality Observations

### Strengths
✅ **Clear separation of concerns:** Routes (main.py) → Logic (records.py, smart_search.py) → Data (records.json)  
✅ **Type hints throughout:** Improves IDE support and catches bugs early  
✅ **Proper error handling:** HTTP exceptions with meaningful messages  
✅ **Documentation strings:** Every function has docstrings  
✅ **RESTful design:** Follows HTTP semantics (GET, POST, status codes)  
✅ **Smart caching:** Vectorizer cached to avoid recomputation  

### Areas for Future Enhancement
🔧 **Add logging:** Track searches, errors, performance metrics  
🔧 **Rate limiting:** Prevent abuse of API endpoints  
🔧 **Pagination:** For large result sets (currently limited to 10/100)  
🔧 **CORS configuration:** Allow frontend applications from different domains  
🔧 **Authentication:** Secure POST /questions endpoint  
🔧 **Database migration:** Move from JSON file to SQLite/PostgreSQL  
🔧 **Caching layer:** Redis for frequently accessed records  
🔧 **Testing:** Unit tests, integration tests, API contract tests  

---

## 9. Checkpoint 1 Completion Checklist

| Task | Status | Notes |
|------|--------|-------|
| FastAPI server runs cleanly | ✅ | `uvicorn app.main:app --reload` |
| `/health` endpoint works | ✅ | Returns healthy status |
| `/records` endpoint works | ✅ | Returns paginated list |
| `/records/{id}` endpoint works | ✅ | Returns single record or 404 |
| `/search` endpoint works | ✅ | TF-IDF + keyword fallback |
| `POST /questions` endpoint works | ✅ | Accepts and validates questions |
| Swagger UI accessible | ✅ | http://127.0.0.1:8000/docs |
| 85 records loaded | ✅ | All with 9 required fields |
| Smart search functional | ✅ | Relevance-ranked results |
| Documentation complete | ✅ | how_llms_work.md, questions.md |
| 10 questions defined | ✅ | questions.md + questions.json |
| Code walkthrough written | ✅ | This document |
| Git tag created | ✅ | `checkpoint-1` |

---

## 10. Next Steps (Post-Checkpoint 1)

### Week 2 Priorities
1. **LLM Integration:** Connect to OpenAI/Anthropic API or local LLM
2. **RAG Implementation:** Use smart_search results as context for LLM
3. **CFA Calculator Tool:** Build deterministic subsidy calculator function
4. **Prompt Engineering:** Design system prompt for SuryaGharSathi persona
5. **Question Answering:** Test all 10 questions end-to-end
6. **Evaluation Framework:** Measure accuracy, relevance, citation quality
7. **UI Development:** Build simple web interface or Streamlit app

### Long-term Enhancements
- Multi-language support (Hindi, Marathi for Kopargaon users)
- Document upload: Parse user's MSEDCL bill PDF
- ROI calculator: Estimate payback period with local tariff data
- Vendor directory: List approved installers in Kopargaon area
- Real-time monitoring: Dashboard showing installation progress

---

**Document Version:** 1.0  
**Last Updated:** Day 5 — Checkpoint 1  
**Status:** Complete ✓  
**Author:** Abhishek Sanjay Dighe (2124UMLM2056)
