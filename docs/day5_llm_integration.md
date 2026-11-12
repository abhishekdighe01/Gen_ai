# Day 5 — LLM Integration Complete

**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  
**Project:** SuryaGharSathi (SJ-64)  
**Date:** Day 5 — LLM Integration  

---

## Overview

Day 5 implements full LLM integration with Retrieval-Augmented Generation (RAG) for accurate question answering about PM Surya Ghar rooftop solar subsidies.

---

## Components Implemented

### 1. LLM Client (`app/llm_client.py`)

**Purpose:** Wrapper around Groq API for question answering

**Key Functions:**
- `LLMClient`: Main client class with Groq integration
- `get_system_prompt()`: Returns SuryaGharSathi system prompt
- `build_rag_context()`: Formats retrieved records for LLM context
- `get_llm_client()`: Singleton instance getter

**Configuration:**
```python
client = LLMClient(
    provider="groq",
    model="llama-3.1-70b-versatile",
    temperature=0.3,  # Low temp for factual answers
    max_tokens=1000
)
```

**Features:**
- ✅ Groq API integration (Llama 3.1 70B)
- ✅ System prompt injection
- ✅ RAG context augmentation
- ✅ Error handling for API failures
- ✅ Environment variable configuration

### 2. System Prompt

**Location:** `app/llm_client.py` → `get_system_prompt()`

**Purpose:** Instructs LLM to act as SuryaGharSathi assistant

**Key Rules:**
1. Answer ONLY from provided guideline context
2. Use exact CFA rates (₹30k/kW for first 2kW, ₹18k/kW additional)
3. Always cite source sections (e.g., "per MNRE Guidelines Section 5(h)")
4. For out-of-scope questions: "I don't know - this is outside PM Surya Ghar guidelines"
5. Explain technical terms clearly
6. Focus on residential rooftop solar

**Target User Context:**
- Homeowner in Kopargaon, Maharashtra
- MSEDCL electricity consumer
- ₹2,000/month bill
- 40 sq m terrace space

### 3. Chat Endpoint (`app/main.py`)

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "question": "How much subsidy for 3 kW?",
  "use_rag": true,
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "How much subsidy for 3 kW?",
  "answer": "For a 3 kW rooftop solar system, the Central Financial Assistance (CFA) is ₹78,000...",
  "sources": [
    {
      "record_id": 11,
      "topic": "Effective CFA Rates",
      "source_section": "Section 5(h)",
      "relevance_score": 0.4523
    }
  ],
  "rag_enabled": true,
  "rag_results_count": 5,
  "model": "llama-3.1-70b-versatile",
  "provider": "groq"
}
```

**Process Flow:**
1. Validate question (non-empty)
2. Check API key configuration
3. If `use_rag=true`: Search for relevant records via TF-IDF
4. Build RAG context from top-k records
5. Get system prompt
6. Call LLM API with system prompt + context + question
7. Return answer with source citations

**Error Handling:**
- 400: Empty question
- 500: Missing/invalid API key
- 500: LLM API call failure

### 4. Environment Configuration

**Files:**
- `.env.example`: Template with all configuration options
- `.env`: Actual configuration (gitignored, not committed)
- `.gitignore`: Excludes `.env` from version control

**Required Variables:**
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000
RAG_TOP_K=5
```

**Getting API Key:**
1. Visit: https://console.groq.com
2. Sign up (free)
3. Create API key in Keys section
4. Copy key to `.env` file

### 5. Evaluation Script (`eval/test_questions.py`)

**Purpose:** Automated testing of all 10 questions

**Features:**
- Loads questions from `eval/questions.json`
- Calls `/chat` endpoint for each question
- Checks out-of-scope handling (Q6)
- Displays answers and RAG source counts
- Summary statistics

**Usage:**
```bash
# Terminal 1: Start server
uvicorn app.main:app --reload

# Terminal 2: Run evaluation
python eval/test_questions.py
```

**Output:**
```
Question 1: CFA Calculation
  Q: How much subsidy will I get for a 3 kW rooftop solar system?...
  Expected: ₹78,000 CFA for general states...
  A: For a 3 kW rooftop solar system, the CFA is ₹78,000...
  RAG Sources: 5

Question 6: Out of Scope
  Q: What will MSEDCL's electricity tariff per unit be next year?...
  Expected: I don't know - this is outside the scope...
  A: I don't know - this is outside the scope of PM Surya Ghar guidelines.
  RAG Sources: 2
  Out-of-scope check: ✓ pass
```

---

## RAG Implementation Details

### What is RAG?

**Retrieval-Augmented Generation** combines:
1. **Retrieval:** Search for relevant documents (TF-IDF + cosine similarity)
2. **Augmentation:** Inject retrieved context into LLM prompt
3. **Generation:** LLM generates answer grounded in retrieved facts

### Why RAG for SuryaGharSathi?

**Problem:** Pure LLMs hallucinate on factual queries
- Wrong subsidy amounts (e.g., "₹75,000 for 3 kW" instead of ₹78,000)
- Outdated information (2019 Phase-II rates instead of 2024 PM Surya Ghar)
- Made-up rules (confusing RESCO with residential CFA)

**Solution:** RAG ensures answers come from official MNRE guidelines
- ✅ Always cite source sections
- ✅ Use exact CFA calculation rules
- ✅ No hallucinated numbers
- ✅ Up-to-date June 2024 guidelines

### RAG Pipeline in Code

```python
# Step 1: User asks question
question = "How much subsidy for 3 kW?"

# Step 2: Retrieve relevant records (TF-IDF)
smart_results = smart_search(question, top_k=5)
# Returns: [(record1, 0.45), (record2, 0.38), ...]

# Step 3: Build context string
context = build_rag_context(retrieved_records)
# Format:
# [1] Topic: Effective CFA Rates
#     Rule: Effective CFA for general states is Rs 30,000 per kW...
#     Source: Section 5(h)
#
# [2] Topic: CFA Structure
#     Rule: For additional capacity of 1 kWp, CFA is 40% of benchmark...
#     Source: Section 5(e)

# Step 4: Build LLM prompt
prompt = f"""Based on these official guidelines:

{context}

Question: {question}

Answer based only on the guidelines provided above."""

# Step 5: Call LLM with system prompt
answer = llm_client.generate(
    prompt=prompt,
    system_prompt=get_system_prompt()
)

# Step 6: Return answer with sources
return {
    "answer": answer,
    "sources": [record metadata with relevance scores]
}
```

---

## Testing & Verification

### Manual Testing via Swagger UI

1. Start server: `uvicorn app.main:app --reload`
2. Open: http://127.0.0.1:8000/docs
3. Find `POST /chat` endpoint
4. Click "Try it out"
5. Enter test question:
   ```json
   {
     "question": "How much subsidy for 2.5 kW?",
     "use_rag": true,
     "top_k": 5
   }
   ```
6. Execute and verify response

### Command-Line Testing

```bash
# Test with RAG
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Are imported solar panels eligible for subsidy?",
    "use_rag": true,
    "top_k": 5
  }'

# Test without RAG (pure LLM)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is PM Surya Ghar?",
    "use_rag": false
  }'
```

### Automated Evaluation

```bash
python eval/test_questions.py
```

Expected results:
- 10/10 questions answered
- Q6 correctly returns "I don't know"
- All answers cite source sections
- RAG retrieves 3-5 relevant records per question

---

## Key Design Decisions

### 1. Why Groq (not OpenAI/Anthropic)?

**Reasons:**
- ✅ **Free tier:** Generous API limits for development
- ✅ **Fast inference:** Low latency (<1 second)
- ✅ **Llama 3.1 70B:** High-quality open model
- ✅ **Simple API:** Compatible with OpenAI format
- ✅ **No credit card:** Easy signup for students

**Alternative:** Google Gemini (also free, good quality)

### 2. Why Temperature 0.3?

**Temperature controls randomness:**
- 0.0: Deterministic, always same output
- 0.3: **Focused but not robotic** ← We use this
- 1.0: Balanced creativity
- 2.0: Very creative/random

**Reasoning:** CFA subsidy questions need factual accuracy, not creativity. Low temperature ensures consistent, grounded answers citing exact guidelines.

### 3. Why Top-K = 5 for RAG?

**Balances:**
- **Too few (k=1-2):** May miss important context
- **Just right (k=5):** Covers multiple aspects (eligibility, calculation, disbursement)
- **Too many (k=10+):** Noise, dilutes relevance, exceeds context limit

**Testing showed:** 5 records provide sufficient context for most questions while staying under token limits.

### 4. Why Check for Demo API Key?

```python
if api_key == "gsk_demo_key_for_testing":
    return {
        "answer": "LLM not configured. Get API key from console.groq.com",
        "error": "API key not configured"
    }
```

**Reasoning:**
- Prevents cryptic API errors
- Guides users to get real API key
- Allows server to start without crashing
- Better UX for reviewers/instructors testing the code

### 5. Why Separate /questions and /chat?

**`POST /questions`:**
- Simple submission (Day 4 requirement)
- No LLM processing
- Just stores/acknowledges question

**`POST /chat`:**
- Full LLM processing (Day 5 requirement)
- RAG retrieval + generation
- Returns actual answer

**Reasoning:** Clean separation of concerns, allows disabling LLM while keeping basic functionality.

---

## Error Handling

### 1. Missing API Key

**Scenario:** User forgot to set `GROQ_API_KEY` in `.env`

**Response:**
```json
{
  "answer": "LLM is not configured. Please set GROQ_API_KEY in .env file...",
  "sources": [],
  "rag_enabled": false,
  "error": "API key not configured"
}
```

**HTTP Status:** 200 (not 500) — graceful degradation

### 2. LLM API Failure

**Scenario:** Network error, rate limit, invalid key

**Response:**
```json
{
  "detail": "Failed to generate answer: API rate limit exceeded"
}
```

**HTTP Status:** 500

### 3. Empty Question

**Scenario:** User sends empty/whitespace-only question

**Response:**
```json
{
  "detail": "Question cannot be empty"
}
```

**HTTP Status:** 400

### 4. No RAG Results

**Scenario:** Question has zero similarity to any record

**Behavior:**
- RAG returns empty list
- LLM still called with system prompt only
- No context provided
- LLM may respond with general knowledge or "I don't know"

---

## Dependencies Added

### requirements.txt

```
groq>=0.4.0          # Groq API client for Llama 3.1
python-dotenv>=1.0.0 # Load environment variables from .env
```

### Installation

```bash
pip install groq python-dotenv
```

---

## Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `app/llm_client.py` | LLM wrapper and RAG integration |
| `.env.example` | Environment configuration template |
| `.env` | Actual API keys (gitignored) |
| `eval/test_questions.py` | Automated question evaluation |
| `docs/day5_llm_integration.md` | This document |

### Modified Files

| File | Changes |
|------|---------|
| `app/main.py` | Added `POST /chat` endpoint, imports |
| `requirements.txt` | Added groq, python-dotenv |
| `README.md` | Added Day 5 usage section |
| `.gitignore` | Ensured .env excluded |

---

## Checkpoint 1 Status — UPDATED

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **LLM Provider** | ✅ | Groq (Llama 3.1 70B) |
| **LLM Wrapper** | ✅ | `app/llm_client.py` with `LLMClient` class |
| **Environment Variables** | ✅ | `.env` with `GROQ_API_KEY` |
| **`.env.example`** | ✅ | Template with all config options |
| **System Prompt** | ✅ | `get_system_prompt()` with SuryaGharSathi instructions |
| **`POST /chat`** | ✅ | Accepts question, returns LLM answer |
| **Error Handling** | ✅ | Missing key, empty question, API failures |
| **RAG Integration** | ✅ | TF-IDF search → context building → LLM |
| **10 Questions** | ✅ | `eval/questions.json` with evaluation script |
| **Documentation** | ✅ | README, how_llms_work.md, this doc |

---

## Next Steps (Week 2)

1. **Evaluation Metrics:**
   - Implement answer quality scoring
   - Citation accuracy checking
   - Out-of-scope detection rate

2. **CFA Calculator Tool:**
   - Deterministic subsidy calculator function
   - Tool calling / function invocation
   - Fallback for arithmetic

3. **UI Development:**
   - Streamlit or Gradio web interface
   - Chat history
   - Source highlighting

4. **Performance Optimization:**
   - Cache LLM responses
   - Batch question processing
   - Response streaming

5. **Deployment:**
   - Dockerize application
   - Deploy to cloud (Render, Railway, etc.)
   - Production API key management

---

**Document Version:** 1.0  
**Last Updated:** Day 5 — LLM Integration Complete  
**Status:** ✓ Ready for Review
