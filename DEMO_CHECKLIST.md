# Day 10 Live Demo Checklist

## Pre-Demo Setup

### 1. Start Backend API (Terminal 1)
```bash
cd e:\GitHub\Gen_ai
uvicorn app.main:app --reload
```

Verify running at: http://127.0.0.1:8000/docs

### 2. Start Streamlit UI (Terminal 2)
```bash
streamlit run ui/app.py
```

Verify running at: http://localhost:8501

### 3. Test Quick Questions (DO THIS FIRST)
- Click "How much subsidy for 3 kW?" → Should show answer with tools badge
- Click thumbs up → Verify saved to data/feedback.jsonl
- Click "What will MSEDCL's tariff be next year?" (Q6) → Should say "I don't know"

## Demo Flow

### Tab 1: Chat Assistant

1. **Show Sample Question**
   - Click "How much subsidy for 3 kW?"
   - Point out:
     - Answer with CFA calculation
     - Tool badge showing `solar_cfa_calculator` was called
     - Citations expandable section (MNRE, page, date, score)
     - Thumbs up/down feedback buttons

2. **Q6 Abstention Test**
   - Click "What will MSEDCL's tariff be next year?"
   - Point out: "I don't know" response (correctly abstains on out-of-scope)

3. **Multi-turn with Memory**
   - Type: "I want 4 kW in Kopargaon"
   - Show approval gate (if approved=False in sidebar)
   - Point out thread_id maintains conversation context

### Tab 2: Solar Payback Calculator ⭐ Signature Feature

1. **Default Scenario (3 kW)**
   - Show sliders: ₹2,000/month bill, 3.0 kW, 40 sq m
   - Click "Calculate Subsidy & Payback"
   - Point out KPI metrics:
     - Gross Cost: ₹145,000
     - CFA Subsidy: ₹78,000 (capped at 3 kW)
     - Net Cost: ₹67,000
     - Payback: **4.0 years**
   
2. **Payback Chart**
   - Green line: Cumulative savings (₹16,800/year)
   - Red line: Net cost (₹67,000)
   - Orange marker: Break-even at Year 4
   - Point out assumptions caption (MNRE Section 5(g) benchmark costs)

3. **2 kW vs 3 kW Comparison**
   - Show side-by-side cards for Kopargaon homeowner
   - Point out computed recommendation (not hard-coded)
   - Mention "informational analysis, not financial advice"

4. **Test >3 kW (4 kW)**
   - Change slider to 4.0 kW
   - Click Calculate
   - Show:
     - CFA still ₹78,000 (capped)
     - Warning: "No CFA beyond 3 kW"
     - Higher net cost
     - Longer payback

5. **Roof Area Check**
   - 4 kW needs 40 sq m (exactly available)
   - Change to 5 kW → Should warn insufficient space
   - Suggests optimal size

### Safety & Compliance

- Point out disclaimer in sidebar
- Point out footer disclaimer with DISCOM/portal links
- Mention: "Information from MNRE, not financial advice"

## Key Numbers to Remember

- **3 kW System (Target User):**
  - CFA: ₹78,000
  - Gross: ₹145,000
  - Net: ₹67,000
  - Payback: **4.0 years**
  - Annual savings: ₹16,800

- **2 kW System:**
  - CFA: ₹60,000
  - Net: ₹40,000
  - Payback: 2.4 years

## Fixed Issues for Demo

✅ Quick-question buttons now work (pending state pattern)  
✅ Payback shows decimal years consistently (4.0 not 4)  
✅ app.tools imported separately (won't break if chromadb fails)  
✅ Assumptions cite MNRE Section 5(g)  
✅ 3kW recommendation is computed, not hard-coded  
✅ requirements.txt is UTF-8 encoded  

## Fallback Mode

If API not running, UI automatically falls back to direct function calls:
- `answer_question()` for RAG
- `run_graph_agent()` for agent
- `solar_cfa_calculator()` for payback

**Demo will never crash!**

## Feedback Tracking

Check `data/feedback.jsonl` after demo:
```bash
cat data/feedback.jsonl
```

Should contain timestamped thumbs up/down entries.

## Git Status

- Commit: `2c84096` (fix: Day 10 critical fixes for live demo)
- Tag: `checkpoint-2` (points to 2c84096)
- All fixes pushed to origin/main

## Test Before Demo

```bash
# Verify calculator
python -c "from app.tools import solar_cfa_calculator; print(solar_cfa_calculator(3.0)['net_cost_inr'])"
# Should print: 67000.0

# Verify Streamlit starts
streamlit run ui/app.py
# Should open browser
```

---

**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  
**Project:** SJ-64 SuryaGharSathi  
**Checkpoint:** 2 (Days 1-10 Complete)
