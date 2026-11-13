# SuryaGharSathi

## Product
SuryaGharSathi helps homeowners understand PM Surya Ghar rooftop solar rules, calculate the applicable central government subsidy, and estimate how long a rooftop solar system will take to recover its cost.

## Target User
A homeowner in Kopargaon with:
- Monthly MSEDCL electricity bill: ₹2,000
- Available terrace area: 40 sq. m.
- Requirement: Compare 2 kW and 3 kW rooftop solar systems.

## Problem
Homeowners often find it difficult to understand government solar scheme guidelines, calculate the applicable subsidy, compare system capacities, and estimate their return on investment.

## Data Sources
1. MNRE – Operational Guidelines for PM Surya Ghar:
   https://mnre.gov.in/en/notice/operational-guidelines-for-implementation-of-the-component-central-financial-assistance-to-residential-consumers-of-pm-surya-ghar-muft-bijli-yojana/

2. Official Guidelines PDF:
   https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf

## Project Goal
To make rooftop solar scheme information easier to understand and help homeowners make informed decisions using official government guidelines.

## How to run

### 1. Install Dependencies

First, create a virtual environment and install required packages:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download and Ingest Data

Download official PM Surya Ghar guideline documents and process them:

```bash
# Download PDFs
python -m app.fetch

# Extract text and build records.json
python -m app.ingest
```

This creates `data/records.json` with 85+ structured records from official MNRE guidelines.

### 3. Run the FastAPI Web Service

Start the SuryaGharSathi API server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Base URL:** http://127.0.0.1:8000
- **Interactive Docs:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

#### Available Endpoints:

- `GET /health` — Health check
- `GET /records?limit=10` — Get all records (default limit: 100)
- `GET /records/{record_id}` — Get specific record by ID
- `GET /search?q=CFA+subsidy` — Smart search using TF-IDF + cosine similarity
- `POST /questions` — Submit a question (with JSON body: `{"question": "...", "name": "..."}`)

### 4. Run Data Analysis

Analyze the dataset using pandas:

```bash
python analysis/explore.py
```

This prints comprehensive insights including:
- Record distribution by document and issuing body
- Rule length statistics and top topics
- Coverage analysis of key solar policy themes (CFA, DISCOM, RESCO, net metering, etc.)

### 5. Test Smart Search

Test the TF-IDF search engine directly:

```bash
python -m app.smart_search
```

Or use it via the API at `/search?q=your+query`

---

## Day 6: Prompt Engineering & Structured Output

### 1. Prompt Templates

SuryaGharSathi uses carefully engineered prompts for accurate, consistent responses:

**System Prompt** (`prompts/system_prompt.txt`):
- Defines SuryaGharSathi persona and knowledge domain
- Includes exact MNRE CFA rules (₹30k/₹18k rates, 3 kW cap)
- Enforces citation requirements and "I don't know" responses
- Sets target user context (Kopargaon homeowner)

**Task Prompts:**
- **v1 (Basic):** Zero-shot JSON formatting (`prompts/task_v1_basic.txt`)
- **v2 (Structured):** Step-by-step rubric + few-shot examples (`prompts/task_v2_structured.txt`) ← **Recommended**

### 2. Structured Output Format

All `/chat` responses return JSON with:
```json
{
  "answer": "Detailed answer with calculations and citations",
  "confidence": "high" | "medium" | "low",
  "follow_up": "Helpful next question for the homeowner"
}
```

### 3. Testing Different Prompts

```bash
# Test with prompt v1 (basic)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How much subsidy for 2.5 kW?",
    "prompt_version": "v1"
  }'

# Test with prompt v2 (structured) - recommended
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How much subsidy for 2.5 kW?",
    "prompt_version": "v2"
  }'
```

### 4. Prompt Evaluation Results

See `eval/prompt_compare.md` for detailed analysis:

| Metric | Prompt v1 | Prompt v2 | Winner |
|--------|-----------|-----------|---------|
| Citation Accuracy | 60% | **100%** | v2 |
| Step-by-Step Math | 0% | **100%** | v2 |
| Answer Completeness | 60% | **100%** | v2 |
| Out-of-Scope Detection | 100% | 100% | Tie |
| JSON Validity | 70% | **90%** | v2 |

**Conclusion:** Prompt v2 with step-by-step rubric and few-shot examples significantly outperforms basic prompting.

---

## Day 5: LLM Integration & Chat

### 1. Get Groq API Key

1. Sign up for free at: https://console.groq.com
2. Go to API Keys section
3. Create a new API key
4. Copy the key (starts with `gsk_...`)

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# Set: GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Test LLM Client

Test the LLM integration without running the server:

```bash
python -m app.llm_client
```

### 4. Use the /chat Endpoint

Start the server and test the LLM-powered Q&A:

```bash
# Terminal 1: Start server
uvicorn app.main:app --reload

# Terminal 2: Test chat endpoint
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How much subsidy for 3 kW?", "use_rag": true}'
```

**Interactive API Testing:**
- Open: http://127.0.0.1:8000/docs
- Find `POST /chat` endpoint
- Click "Try it out"
- Enter your question
- Execute

### 5. Evaluate All 10 Questions

Run the automated evaluation script:

```bash
# Make sure server is running first
python eval/test_questions.py
```

This tests all 10 questions from `eval/questions.json` including:
- Questions 1-6 from project card (including out-of-scope Q6)
- Questions 7-10 from MNRE guidelines

### 6. How RAG Works in SuryaGharSathi

```
User Question
     ↓
TF-IDF Search → Top 5 relevant records
     ↓
Build Context (topic + rule + section)
     ↓
LLM (Groq/Llama 3.1) + System Prompt + Context
     ↓
Grounded Answer with Source Citations
```

**Key Features:**
- ✅ Retrieval-Augmented Generation (RAG) prevents hallucinations
- ✅ Official MNRE guideline citations
- ✅ Out-of-scope detection (returns "I don't know")
- ✅ Accurate CFA subsidy calculations
- ✅ Temperature 0.3 for focused, factual responses