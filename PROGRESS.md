# SuryaGharSathi - Project Progress Tracker

**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  
**Project ID:** SJ-64  
**Product:** SuryaGharSathi — PM Surya Ghar Rooftop Solar Assistant  
**Repository:** https://github.com/abhishekdighe01/Gen_ai  
**Status:** ✅ **COMPLETE** (Days 1-14)

---

## Milestone Tracker

### Week 1: Foundation & Data Pipeline

#### Day 1: Project Setup & Environment
- [x] Initialize Git repository with README
- [x] Set up Python virtual environment (`.venv`)
- [x] Create project structure (`app/`, `data/`, `docs/`)
- [x] Add `.gitignore` for Python/data files
- [x] Define target user persona (Kopargaon homeowner)
- [x] Document problem statement in README
- [x] **Tag:** `week-1` (checkpoint after Day 4)

#### Day 2: Data Fetching & PDF Download
- [x] Create `app/fetch.py` for PDF downloads
- [x] Download MNRE Operational Guidelines (June 2024)
- [x] Download PM Surya Ghar Portal FAQ (Feb 2024)
- [x] Download DISCOM Incentive Guidelines
- [x] Store PDFs in `data/raw/`
- [x] Add official source URLs to README

#### Day 3: Text Extraction & Record Creation
- [x] Create `app/ingest.py` for PDF processing
- [x] Implement `extract_text_from_pdf()` with `PyPDF2`
- [x] Parse structured `Record` dataclass with validation
- [x] Extract metadata: `date_issued`, `source`, `source_pages`
- [x] Generate `data/records.json` (85+ records)
- [x] Implement schema validation with try/except

#### Day 4: Data Analysis & Search
- [x] Create `app/records.py` for record loading
- [x] Implement `search()`, `get_by_id()`, `count_by()` functions
- [x] Create `analysis/explore.py` for pandas analysis
- [x] Generate coverage stats (CFA, DISCOM, net metering topics)
- [x] Implement TF-IDF smart search in `app/smart_search.py`
- [x] **Tag:** `week-1` ✅

---

### Week 2: LLM Integration & RAG

#### Day 5: LLM Client & Chat Endpoint
- [x] Set up Groq API key (`.env.example`)
- [x] Create `app/llm_client.py` with Groq/Gemini support
- [x] Implement offline fallback for testing
- [x] Add `POST /chat` endpoint in `app/main.py`
- [x] Return structured JSON: `{answer, confidence, follow_up}`
- [x] Test with 10 questions from `eval/questions.json`

#### Day 6: Prompt Engineering
- [x] Create `prompts/system_prompt.txt` (persona + rules)
- [x] Create `prompts/task_v1_basic.txt` (zero-shot)
- [x] Create `prompts/task_v2_structured.txt` (few-shot + rubric)
- [x] Implement prompt version selector in `/chat`
- [x] Create `eval/prompt_compare.md` comparison
- [x] Results: Prompt v2 achieves 100% citation vs 10% for v1

#### Day 7: Semantic Search & Vector Store
- [x] Create `app/embed.py` with sentence-transformers
- [x] Create `app/chunking.py` (500-char chunks, 80 overlap)
- [x] Implement ChromaDB integration in `app/vectorstore.py`
- [x] Generate `data/chunks.json` (600 chunks)
- [x] Persist embeddings to `data/chroma_db/`
- [x] Add `GET /search/semantic` endpoint
- [x] Create `eval/search_results.md` evaluation

#### Day 8: RAG Pipeline & Evaluation
- [x] Create `app/rag.py` with `answer_question()` function
- [x] Implement date-prioritized re-ranking
- [x] Add inline citations with source metadata
- [x] Add `POST /ask` endpoint
- [x] Create `eval/eval_set.json` (15 questions)
- [x] Create `eval/run_eval.py` benchmark harness
- [x] Run Config A vs Config B comparison
- [x] Results: Config A wins (92.9% hit rate, 245ms latency)
- [x] **Tag:** `checkpoint-1` ✅

---

### Week 3: Agentic System & UI

#### Day 9: LangGraph Agent & Tools
- [x] Create `app/tools.py` with `solar_cfa_calculator()`
- [x] Implement slab-based CFA calculation (±₹0 error)
- [x] Add `extract_capacity_kw()` helper
- [x] Create `app/graph.py` with LangGraph workflow
- [x] Define `AgentState` TypedDict
- [x] Implement approval_gate node for >3 kW systems
- [x] Add `MemorySaver` for multi-turn conversations
- [x] Add `POST /agent` endpoint
- [x] Test tool calling with 4 kW question

#### Day 10: Streamlit UI & Payback Chart
- [x] Create `ui/app.py` with 2 tabs (Chat + Calculator)
- [x] Implement chat interface with Agent/RAG mode selector
- [x] Add citation display with source links
- [x] Add thumbs up/down feedback to `data/feedback.jsonl`
- [x] Create `ui/generate_chart.py` for payback visualization
- [x] Implement payback calculator with KPI cards
- [x] Add 2 kW vs 3 kW comparison cards
- [x] Add roof area validation (10 sq m per kW)
- [x] Generate `docs/suryagharsathi_ui.png` screenshot
- [x] **Tag:** `checkpoint-2` ✅

---

### Week 4: Testing, CI/CD & Production

#### Day 11: Testing & Code Quality
- [x] Create `tests/test_suryagharsathi.py` (10 tests)
- [x] Test record loading and search
- [x] Test FastAPI endpoints (health, records, ask, agent)
- [x] Test RAG with fake-LLM monkeypatch
- [x] Test Q6 abstention
- [x] Test `solar_cfa_calculator` accuracy (2/2.5/3/4 kW)
- [x] Test agent approval gate
- [x] Add `ruff` linter to project
- [x] Run `ruff check --fix .` (zero errors)
- [x] Create `Dockerfile` for production
- [x] Create `docker-compose.yml` (API + UI services)
- [x] Create `.dockerignore`
- [x] Add Docker section to README

#### Day 12: CI/CD Pipeline
- [x] Create `.github/workflows/ci.yml`
- [x] Add lint-and-test job (ruff + pytest)
- [x] Add docker-build job with cache
- [x] Update Dockerfile CMD for dynamic PORT
- [x] Create `render.yaml` (Render Blueprint)
- [x] Add CI status badge to README
- [x] Add "Day 12: CI/CD Pipeline & Live Deployment" section
- [x] Fix pytest collection errors with `pytest.ini`
- [x] All tests passing, CI green ✅

#### Day 13: Observability, Security & Portfolio
- [x] Create `app/observability.py` (154 lines)
- [x] Implement `SimpleTTLCache` (128 entries, 1hr TTL)
- [x] Implement `validate_user_input()` (500-char limit, 9 injection patterns)
- [x] Implement `estimate_tokens()` (~4 chars/token)
- [x] Implement `log_request_metric()` (JSONL logging)
- [x] Add `GET /metrics` endpoint
- [x] Add latency middleware (X-Process-Time-Ms header)
- [x] Integrate caching in `/ask`, `/chat`, `/agent`
- [x] Add 3 new pytest tests (injection, length, cache)
- [x] All 13 tests passing ✅
- [x] Upgrade README.md to portfolio-grade:
  - [x] Problem & Target User section
  - [x] Mermaid architecture diagram
  - [x] Demo video section with timestamps
  - [x] Results & evaluation tables
  - [x] Production notes (latency, tokens, cost)
  - [x] Security guardrails documentation
- [x] Create `docs/resume.md` (3 quantified bullets)
- [x] Fix CI lint errors (S110, UP017)
- [x] CI passing with green badge ✅

#### Day 14: Interview Prep & Final Verification
- [x] Create `docs/interview.md`:
  - [x] 60-second elevator pitch
  - [x] Hardest problem story (STAR format)
  - [x] 10 likely interview Q&As
  - [x] Demo Day failure-fixed section
  - [x] 5-minute live demo checklist
- [x] Create `PROGRESS.md` (this file):
  - [x] All 14 days tracked with checkboxes
  - [x] Git tags documented
  - [x] Demo Day rehearsal script
- [x] Run final verification:
  - [x] `pytest -v` → 13/13 passing
  - [x] `ruff check .` → All checks passed
  - [x] Docker build successful
- [x] Commit with `day-14:` prefix
- [x] Push `final` Git tag
- [x] **Tag:** `final` ✅

---

## Git Tags Summary

| Tag | Commit | Description |
|-----|--------|-------------|
| `week-1` | `2c84096` | Completed Days 1-4 (data pipeline) |
| `checkpoint-1` | (moved) | Completed Day 8 (RAG evaluation) |
| `checkpoint-2` | `2c84096` | Completed Day 10 (Streamlit UI) |
| `final` | (current) | Completed Day 14 (all deliverables) |

---

## Demo Day Rehearsal Script (5 Minutes)

### Preparation (Before Demo)

**Technical Setup:**
- [ ] Start FastAPI: `uvicorn app.main:app --reload`
- [ ] Start Streamlit: `streamlit run ui/app.py`
- [ ] Verify `/health` endpoint: `curl http://localhost:8000/health`
- [ ] Verify `/metrics` endpoint has data
- [ ] Open browser tabs:
  1. GitHub README (CI badge)
  2. Streamlit UI (localhost:8501)
  3. FastAPI Swagger (localhost:8000/docs)
  4. `eval/prompt_compare.md`

**Mental Prep:**
- [ ] Review 60-second pitch (docs/interview.md)
- [ ] Review hardest problem story
- [ ] Practice Q&A responses (Q1-Q10)
- [ ] Time full demo (target: 4:30-4:45 to leave buffer)

---

### Demo Script (Timed Segments)

#### **0:00-0:45 - Introduction & Architecture (45 seconds)**

**What to say:**
> "Hi, I'm Abhishek. This is **SuryaGharSathi**, a production RAG system for PM Surya Ghar rooftop solar guidance. The core challenge is that LLMs hallucinate subsidy math, and older FAQs conflict with newer MNRE guidelines.
>
> My solution combines **ChromaDB vector retrieval** tagged with document issue dates, a **LangGraph agent** with a deterministic Python calculator, and a **Streamlit UI** with payback charts. It achieves **92.9% retrieval accuracy**, **±₹0 calculation error**, and **100% Q6 abstention**."

**What to show:**
- [ ] GitHub README open
- [ ] Point to CI green badge
- [ ] Point to Mermaid architecture diagram
- [ ] Point to Results table (92.9%, ±₹0, 100%)

**Transition:** *"Let me show you the UI..."*

---

#### **0:45-2:15 - Signature Payback Chart (90 seconds)**

**What to say:**
> "This is the Streamlit UI's signature feature—the solar payback calculator. I'll enter inputs for our target user: a Kopargaon homeowner with a ₹2,000 monthly bill and 40 square meters of terrace."

**Actions:**
1. [ ] Switch to Streamlit tab
2. [ ] Navigate to "Solar Payback Calculator" tab
3. [ ] Enter:
   - Monthly Bill: **₹2,000**
   - System Size: **3.0 kW**
   - Terrace Area: **40 sq m**
   - State: **General (Maharashtra)**
4. [ ] Click "Calculate Payback"
5. [ ] Point to KPI cards:
   - Gross Cost: ₹1,45,000
   - **CFA Subsidy: ₹78,000**
   - Net Cost: ₹67,000
   - **Payback: 4 years**
6. [ ] Point to chart:
   - Orange line = net cost
   - Blue line = cumulative savings
   - **Break-even at year 4**
   - **Year 10: ₹1 lakh profit**

**What to say:**
> "For 3 kW, gross cost is ₹1.45 lakh. After ₹78,000 subsidy—computed using the deterministic slab structure: 2 kW at ₹30k plus 1 kW at ₹18k—net cost is ₹67,000. With 70% solar offset, annual savings are ₹16,800, giving a 4-year payback. By year 10, the homeowner has made ₹1 lakh net profit."

**Transition:** *"Now let me show the agentic RAG capabilities..."*

---

#### **2:15-3:45 - Live RAG + Agent Demo (90 seconds)**

**Demo 1: Multi-Part Question with Tool Calling**

**What to say:**
> "I'll ask a multi-part question that requires both tool calling and policy retrieval."

**Actions:**
1. [ ] Switch to "Chat Assistant" tab
2. [ ] Select "Agent (with tools)" mode
3. [ ] Type: **"I want 4 kW on my house in Kopargaon. How much subsidy do I get, and do I still need net metering from MSEDCL?"**
4. [ ] Click Send (wait ~3 seconds)
5. [ ] Point to response:
   - **Tool badge:** 🔧 solar_cfa_calculator
   - **Subsidy:** ₹78,000 (capped at 3 kW)
   - **Net metering:** Yes, required per MNRE Section X
   - **Citations:** Links to PDF pages

**What to say:**
> "Notice the agent called `solar_cfa_calculator` to compute the exact ₹78,000 subsidy—correctly capping at 3 kW—and also retrieved net metering requirements from ChromaDB. Every claim has a PDF citation."

**Demo 2: Q6 Abstention Test**

**Actions:**
1. [ ] Type: **"What will MSEDCL's electricity tariff per unit be next year?"**
2. [ ] Click Send
3. [ ] Point to response: **"I don't know. This asks about future rates not in guidelines."**

**What to say:**
> "This is Q6—the out-of-scope abstention test. The system cleanly returns 'I don't know' with zero speculation. No hallucination. This is validated in our pytest suite with `test_ask_endpoint_q6_abstention`."

**Transition:** *"Finally, let me show a concrete failure I fixed..."*

---

#### **3:45-4:30 - Failure Fixed & Measured (45 seconds)**

**What to say:**
> "During Day 6 prompt engineering, I discovered my zero-shot prompt only cited MNRE sections in 10% of answers and hedged on Q6 by speculating about MSEDCL tariff trends."

**Actions:**
1. [ ] Switch to browser tab showing `eval/prompt_compare.md`
2. [ ] Point to Results Table:
   - **Citation Accuracy: 10% → 100%** (+900%)
   - **Step-by-Step Math: 0% → 100%**
   - **Answer Completeness: 60% → 100%**
   - **Q6 Abstention: Partial → 100%**

**What to say:**
> "I fixed this with Prompt v2—a structured rubric with few-shot examples—and re-ran the 10-question benchmark. Citation accuracy jumped to 100%, completeness improved by 67%, and Q6 abstention became strict. This is documented in `eval/prompt_compare.md` with before/after examples."

**Transition:** *"Thank you! I'm happy to take questions."*

---

#### **4:30-5:00 - Buffer & Closing (30 seconds)**

**If time permits:**
- [ ] Show `GET /metrics` endpoint in Swagger UI
- [ ] Point out cache hit rate, latency stats
- [ ] Mention 13/13 tests passing in CI

**Closing statement:**
> "SuryaGharSathi is production-ready with Docker, GitHub Actions CI/CD, security guardrails, and full observability. The code is on GitHub at `abhishekdighe01/Gen_ai`. Thank you!"

---

## Q&A Preparation (3 Minutes)

### Quick Reference Answers

**Q: "How did you handle conflicting documents?"**
> Date-aware metadata. Each chunk stores `date_issued`. During retrieval re-ranking, when similarity scores are close, newer documents win. June 2024 MNRE guidelines always override Feb 2024 FAQ.

**Q: "What if the LLM hallucinates subsidy amounts?"**
> Agent uses deterministic `solar_cfa_calculator` tool, not LLM arithmetic. Pytest validates ±₹0 error across 2/2.5/3/4 kW. LLM only synthesizes natural language around tool output.

**Q: "How do you prevent prompt injection?"**
> Three layers: (1) 500-char input limit, (2) 9-pattern regex filter blocking "ignore instructions", "reveal prompt", etc., (3) HTTP 400 rejection. Tested with 5 injection attacks in pytest—all blocked.

**Q: "Can this scale to other schemes?"**
> Yes, modular design. Replace MNRE PDFs, retrain chunking, update tools. RAG pipeline and agent framework remain unchanged. Would take ~2-3 days to adapt to new scheme.

**Q: "What's your deployment strategy?"**
> Docker + GitHub Actions CI/CD. Every push triggers lint (ruff) + test (pytest) + docker build. Deployed via Render Blueprint with `/health` monitoring. API live at Render URL.

**Q: "How long did this take?"**
> 14 days structured build. Days 1-4: data pipeline. Days 5-7: LLM + RAG. Days 8-9: Agent + tools. Days 10-11: UI + tests. Days 12-14: CI/CD + observability + portfolio docs.

---

## Success Metrics Summary

| Category | Metric | Value |
|----------|--------|-------|
| **Accuracy** | RAG Retrieval Hit Rate | 92.9% (13/14) |
| **Accuracy** | CFA Calculation Error | ±₹0 (100%) |
| **Accuracy** | Q6 Abstention | 100% |
| **Accuracy** | Citation Rate | 100% |
| **Performance** | Cold Latency (P50) | ~250ms |
| **Performance** | Cached Latency (P50) | <50ms |
| **Performance** | Cache Hit Rate | 35-40% |
| **Cost** | Per 1,000 Requests | $0.027 |
| **Cost** | Cache Savings | ~40% |
| **Security** | Injection Defense | 5/5 blocked |
| **Security** | Input Limit | 500 chars |
| **Testing** | Pytest Coverage | 13/13 passing |
| **Testing** | Ruff Linting | 0 errors |
| **CI/CD** | Build Status | ✅ Green |

---

## Project Statistics

- **Total Days:** 14
- **Total Commits:** 50+
- **Lines of Code (app/):** ~3,500
- **Test Coverage:** 13 tests (unit, integration, security)
- **Documents Ingested:** 3 PDFs (85+ records, 600 chunks)
- **Endpoints:** 10 REST APIs
- **UI Pages:** 2 (Chat + Calculator)
- **Deployment:** Docker + Render + GitHub Actions
- **Documentation:** 8 markdown files (README, interview, resume, progress, eval reports)

---

## Files Created (by Day)

**Days 1-4 (Data Pipeline):**
- `app/fetch.py`, `app/ingest.py`, `app/records.py`
- `analysis/explore.py`, `app/smart_search.py`
- `data/records.json` (85 records)

**Days 5-7 (LLM & RAG):**
- `app/llm_client.py`, `app/llm.py`
- `prompts/system_prompt.txt`, `prompts/task_v1_basic.txt`, `prompts/task_v2_structured.txt`
- `app/embed.py`, `app/chunking.py`, `app/vectorstore.py`
- `eval/prompt_compare.md`, `eval/search_results.md`
- `data/chunks.json` (600 chunks), `data/chroma_db/` (vector store)

**Days 8-9 (RAG & Agent):**
- `app/rag.py`, `app/tools.py`, `app/graph.py`
- `eval/eval_set.json` (15 questions), `eval/run_eval.py`
- `eval/rag_eval_results.md`

**Days 10-11 (UI & Tests):**
- `ui/app.py`, `ui/generate_chart.py`
- `tests/test_suryagharsathi.py` (10 tests → 13 tests)
- `Dockerfile`, `docker-compose.yml`, `.dockerignore`
- `docs/suryagharsathi_ui.png`

**Days 12-14 (CI/CD & Production):**
- `.github/workflows/ci.yml`
- `pytest.ini`, `ruff.toml`
- `render.yaml`
- `app/observability.py` (Day 13)
- `docs/resume.md` (Day 13)
- `docs/day-12-completion-summary.md`, `docs/day-13-completion-summary.md`
- `docs/interview.md` (Day 14)
- `PROGRESS.md` (Day 14, this file)

---

## Next Steps (Post-Day 14)

### Day 15: Demo Day
- [ ] Rehearse 5-minute demo (3 run-throughs)
- [ ] Test all systems 30 minutes before demo
- [ ] Have backup screenshots ready
- [ ] Deliver demo + Q&A
- [ ] Submit final evaluation

### Future Enhancements (if continuing)
- [ ] Add more MNRE documents (RESCO guidelines, state-specific rules)
- [ ] Implement user authentication and session persistence
- [ ] Add multi-language support (Hindi, Marathi)
- [ ] Integrate real-time DISCOM portal data
- [ ] Add email notification for subsidy deadlines
- [ ] Mobile-responsive UI redesign
- [ ] Add more tools (roof angle calculator, inverter sizing)
- [ ] Improve RAG with re-ranking models (Cohere, Jina)
- [ ] Add observability dashboard (Grafana/Prometheus)

---

**Status:** ✅ **PROJECT COMPLETE - READY FOR DEMO DAY**

**Last Updated:** Day 14  
**Repository:** https://github.com/abhishekdighe01/Gen_ai  
**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  
**Project ID:** SJ-64
