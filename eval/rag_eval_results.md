# RAG Evaluation Results — Day 8

**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  
**Project:** SJ-64 SuryaGharSathi  
**Date:** Day 8 — RAG Pipeline & Evaluation  

---

## Overview

This report evaluates RAG (Retrieval-Augmented Generation) performance across 2 chunk/retrieval configurations on a 15-question evaluation set covering PM Surya Ghar: Muft Bijli Yojana guidelines.

**Evaluation Set:** 15 questions (10 from Day 5 + 5 additional guideline questions)  
**Configurations Tested:** 2  
**Metrics:** Retrieval Hit Rate, Keyword Recall, Q6 Abstention, Citation Rate, Latency  

---

## Configuration Comparison

| Metric | Config A (chunk_500_topk_3) | Config B (chunk_300_topk_5) |
|--------|----------------------------|----------------------------|
| **Chunk Size** | 500 | 300 |
| **Overlap** | 80 | 50 |
| **Top-K** | 3 | 5 |
| **Retrieval Hit Rate** | 92.9% | 85.7% |
| **Avg Keyword Recall** | 78.3% | 81.2% |
| **Q6 Abstention Pass** | ✓ PASS | ✓ PASS |
| **Citation Rate** | 100.0% | 100.0% |
| **Avg Latency (ms)** | 245 | 312 |

### 🏆 Winner: Config A (chunk_500_topk_3)

**Reasoning:**
- Higher retrieval hit rate (92.9% vs 85.7%) - larger chunks capture more context
- Lower latency (245ms vs 312ms) - fewer chunks to process
- Comparable keyword recall (78.3% vs 81.2%)
- Both configs correctly handle Q6 abstention
- Both configs achieve 100% citation rate

Config A provides better balance of accuracy and performance with larger, more contextual chunks and fewer retrievals needed.

---

## Key Findings

### Retrieval Hit Rate
- **Config A (92.9%):** Larger chunks (500 chars) better capture complete guideline rules and section context
- **Config B (85.7%):** Smaller chunks (300 chars) sometimes split rules across multiple chunks, reducing hit rate

### Answer Quality (Keyword Recall)
- **Config A (78.3%):** Slightly lower recall due to fewer chunks retrieved (top_k=3)
- **Config B (81.2%):** Higher recall with top_k=5, but at cost of increased latency and noise

### Q6 Abstention (Critical Test)
- **Both configs: ✓ PASS**
- Successfully returns "I don't know" for out-of-scope question about future MSEDCL electricity tariffs
- Pattern matching correctly identifies unanswerable queries

### Citation Completeness
- **Both configs: 100%**
- All answerable questions receive proper citations with chunk_id, title, source, page, date_issued
- Inline citations in answer text follow format: [Title, Page X]

### Performance
- **Config A: 245ms average** - 27% faster than Config B
- **Config B: 312ms average** - Additional overhead from processing 5 chunks vs 3

---

## Detailed Results — Sample Questions

### Q1: How much subsidy will I get for a 3 kW rooftop solar system?

**Config A Answer:**
For a 3 kW residential rooftop solar system in general states (such as Maharashtra), you will get Rs 78,000 in Central Financial Assistance (CFA): Rs 30,000 per kW for the first 2 kW (Rs 60,000) plus Rs 18,000 per kW for the additional 1 kW between 2 kW and 3 kW [Guidelines for PM-Surya Ghar: Muft Bijli Yojana, Page 6].

**Keyword Recall:** 100% (all keywords present: 78,000, Rs, 60,000, 18,000, CFA, 3 kW)  
**Retrieval Hit:** ✓ PASS (Page 6 retrieved)  
**Citations:** 3 chunks from MNRE guidelines

---

### Q6: What will MSEDCL's electricity tariff per unit be next year?

**Config A Answer:**
I don't know. The official MNRE PM Surya Ghar: Muft Bijli Yojana guidelines and FAQs do not contain future MSEDCL electricity tariff rates for next year.

**Keyword Recall:** 100% (correct abstention with "don't know")  
**Retrieval Hit:** N/A (unanswerable question)  
**Citations:** 0 (correctly abstained)  
**Q6 Abstention:** ✓ PASS

---

### Q11: What is the benchmark cost for rooftop solar installations in general states?

**Config A Answer:**
Under Section 5(g), the benchmark cost for general states is Rs 50,000 per kW for the first 2 kW and Rs 45,000 per kW for additional capacity. For special-category states, the benchmark cost is Rs 55,000 per kW for the first 2 kW and Rs 49,500 per kW for additional capacity [Guidelines for PM-Surya Ghar: Muft Bijli Yojana, Page 6].

**Keyword Recall:** 100% (50,000, 45,000, benchmark, general states, first 2 kW, additional)  
**Retrieval Hit:** ✓ PASS (Page 6 retrieved)  
**Citations:** 3 chunks from MNRE guidelines

---

### Q12: What is the time period for grievance redressal under the PM Surya Ghar scheme?

**Config A Answer:**
Under Section 11(a), consumers and vendors can raise grievances through the National Portal or National Call Centre, and grievances are resolved within a period of 30 days [Guidelines for PM-Surya Ghar: Muft Bijli Yojana, Page 15].

**Keyword Recall:** 100% (30 days, grievance, National Portal, Call Centre)  
**Retrieval Hit:** ✓ PASS (Page 15 retrieved)  
**Citations:** 3 chunks from MNRE guidelines

---

### Q13: Which organization is designated as the National Programme Implementation Agency (NPIA) for PM Surya Ghar?

**Config A Answer:**
Under Section 13(a), REC Limited is designated as the National Programme Implementation Agency (NPIA) at the national level, while local DISCOMs act as the State Implementation Agencies (SIAs) [Guidelines for PM-Surya Ghar: Muft Bijli Yojana, Page 17].

**Keyword Recall:** 100% (REC Limited, NPIA, National Programme, Implementation Agency)  
**Retrieval Hit:** ✓ PASS (Page 17 retrieved)  
**Citations:** 3 chunks from MNRE guidelines

---

### Q14: What is the total financial outlay of PM Surya Ghar: Muft Bijli Yojana and till which financial year is it implemented?

**Config A Answer:**
The PM Surya Ghar: Muft Bijli Yojana was approved on 29th February 2024 with a total financial outlay of Rs 75,021 crore (including Rs 65,700 crore for residential CFA) and is implemented till FY 2026-27 (31st March 2027) [Guidelines for PM-Surya Ghar: Muft Bijli Yojana, Page 2].

**Keyword Recall:** 100% (75,021 crore, 65,700 crore, FY 2026-27, 31st March 2027, outlay)  
**Retrieval Hit:** ✓ PASS (Page 2 retrieved)  
**Citations:** 3 chunks from MNRE guidelines

---

### Q15: What is the Payment Security Mechanism (PSM) for RESCO vendors, and what is the bank guarantee requirement?

**Config A Answer:**
Under the RESCO and Utility Led Aggregation Guidelines, there is a Rs 100 crore corpus for the Payment Security Mechanism (PSM-RTS) with a one-time PSM fee of Rs 2,000 per installation, and RESCO vendors must submit a bank guarantee of Rs 25 lakh (valid for at least 5 years) for national registration [PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism, Page 5].

**Keyword Recall:** 100% (100 crore, PSM, 2,000, 25 lakh, bank guarantee, RESCO, 5 years)  
**Retrieval Hit:** ✓ PASS (Page 5 retrieved)  
**Citations:** 3 chunks from RESCO guidelines (date_issued: 2024-12-28)

---

## Date Prioritization Feature

The RAG pipeline correctly prioritizes newer documents when guidelines conflict. For example:

- **RESCO Guidelines (2024-12-28):** Most recent, highest priority for RESCO-related questions
- **DISCOM Incentives (2024-07-18):** Mid-priority for DISCOM-specific rules
- **MNRE Guidelines (2024-06-07):** Core CFA rules, primary source for subsidy calculations

When retrieval scores are similar (within 0.02), the system sorts by `date_issued` descending to ensure latest guidelines are preferred.

---

## Conclusion

**Config A (chunk_500_topk_3) is the winner** for the SuryaGharSathi RAG pipeline, providing:

1. **Higher Accuracy:** 92.9% retrieval hit rate captures more complete guideline context
2. **Better Performance:** 27% faster with 245ms average latency
3. **Robust Abstention:** Correctly handles unanswerable questions (Q6)
4. **Complete Citations:** 100% citation rate with structured metadata
5. **Date-Aware:** Prioritizes newer documents when guidelines evolve

The larger chunk size (500 chars) with moderate overlap (80 chars) preserves complete subsidy rules and section context, while top_k=3 provides sufficient coverage without noise or latency overhead.

---

**Report Generated:** Day 8  
**Status:** Complete ✓
