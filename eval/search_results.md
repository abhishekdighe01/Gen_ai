# Semantic Search Evaluation — SuryaGharSathi

**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  
**Project:** SJ-64 SuryaGharSathi  
**Date:** Day 7 — Semantic Search  

---

## Overview

This report evaluates semantic search using dense vector embeddings (sentence-transformers all-MiniLM-L6-v2) over PM Surya Ghar guideline chunks.

**Embedding Model:** sentence-transformers/all-MiniLM-L6-v2  
**Similarity Metric:** Cosine similarity  
**Top-K Results:** 3 per question  
**Total Chunks:** 600 (237 from MNRE guidelines, 38 from DISCOM, 58 from RESCO, 267 from records.json)

---

## Q1: CFA Calculation

**Question:** How much subsidy will I get for a 3 kW rooftop solar system?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.7823)

- **Chunk ID:** `record_011_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Effective CFA Rates
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 6
- **Date Issued:** 2024-06-07
- **Section:** Section 5(h)

**Text Snippet:**
```
Effective CFA Rates

For general states, effective CFA is Rs 30,000 per kW for the first 2 kW and Rs 18,000 per kW for additional capacity up to 3 kW. For special-category states, the rates are Rs 33,000 per kW and Rs 19,800 per kW respectively. No additional CFA is provided beyond 3 kW.
```

### Result 2 (Score: 0.7654)

- **Chunk ID:** `record_012_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — CFA Calculation Examples
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 6
- **Date Issued:** 2024-06-07
- **Section:** Section 5(h)

**Text Snippet:**
```
CFA Calculation Examples

The guidelines give these examples for general states: 1.5 kW receives Rs 45,000 CFA; 2.5 kW receives Rs 69,000 CFA; and 6 kW receives Rs 78,000 CFA.
```

### Result 3 (Score: 0.7421)

- **Chunk ID:** `mnre_p006_c03`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 6)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 6
- **Date Issued:** 2024-06-07
- **Section:** Central Financial Assistance

**Text Snippet:**
```
The benchmark cost is Rs 50,000 per kW for the first 2 kW of rooftop solar capacity and Rs 45,000 per kW for additional capacity. For special-category states, the benchmark cost is Rs 55,000 per kW for the first 2 kW and Rs 49,500 per kW for additional capacity...
```

---

## Q2: Space Requirements

**Question:** How much terrace area do I need for 1 kW?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.6234)

- **Chunk ID:** `mnre_p012_c02`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 12)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 12
- **Date Issued:** 2024-06-07
- **Section:** Technical Requirements

**Text Snippet:**
```
For rooftop solar installations, the space requirement varies based on panel efficiency and mounting configuration. Typically, 1 kW of solar capacity requires approximately 10 square meters of roof area, though this can range from 9-12 square meters depending on the technology used...
```

### Result 2 (Score: 0.5987)

- **Chunk ID:** `record_002_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Residential Eligibility
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 5
- **Date Issued:** 2024-06-07
- **Section:** Section 5(b)

**Text Snippet:**
```
CFA is available for grid-connected rooftop solar systems tagged to a residential power connection of the local DISCOM. Eligible installations include roofs, terraces, balconies, elevated structures and qualifying Building Integrated PV systems.
```

### Result 3 (Score: 0.5723)

- **Chunk ID:** `mnre_p005_c04`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 5)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 5
- **Date Issued:** 2024-06-07
- **Section:** Eligibility Criteria

**Text Snippet:**
```
The scheme will support the installation of grid-connected rooftop solar projects in the residential sector through Central Financial Support (CFA) support from the Central Government. The installations can be on roofs, terraces, or other suitable areas...
```

---

## Q3: Technical Specifications

**Question:** What is the minimum warranty on solar panels under this scheme?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.7112)

- **Chunk ID:** `mnre_p014_c02`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 14)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 14
- **Date Issued:** 2024-06-07
- **Section:** Technical Specifications

**Text Snippet:**
```
Solar modules must comply with MNRE technical specifications including a minimum 25-year performance warranty and 10-12 year manufacturing defects warranty. Additionally, vendors must provide a 5-year Comprehensive Maintenance Contract (CMC) for the entire system...
```

### Result 2 (Score: 0.6854)

- **Chunk ID:** `mnre_p015_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 15)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 15
- **Date Issued:** 2024-06-07
- **Section:** Quality Standards

**Text Snippet:**
```
All equipment including solar modules, inverters, and mounting structures must meet BIS standards and be sourced from vendors registered under the Approved List of Models and Manufacturers (ALMM). The warranty requirements ensure long-term performance and consumer protection...
```

### Result 3 (Score: 0.6432)

- **Chunk ID:** `record_003_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — DCR Requirement
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 8
- **Date Issued:** 2024-06-07
- **Section:** Section 5(m)

**Text Snippet:**
```
Solar modules must be manufactured domestically using domestically manufactured solar cells. Non-DCR modules make the installation ineligible for CFA.
```

---

## Q4: Multi-part Query

**Question:** I want 4 kW on my house in Kopargaon. How much subsidy do I get, and do I still need net metering from MSEDCL?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.7534)

- **Chunk ID:** `record_010_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — CFA Structure for Additional Capacity
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 5
- **Date Issued:** 2024-06-07
- **Section:** Section 5(e)

**Text Snippet:**
```
For additional residential rooftop solar capacity of 1 kWp, or part thereof, CFA is 40% of the benchmark cost of the additional kWp. No additional CFA is provided beyond 3 kWp.
```

### Result 2 (Score: 0.7198)

- **Chunk ID:** `mnre_p016_c03`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 16)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 16
- **Date Issued:** 2024-06-07
- **Section:** Net Metering Requirements

**Text Snippet:**
```
All grid-connected rooftop solar installations require net metering to be installed by the local DISCOM. The DISCOM will install a bidirectional meter that tracks both electricity imported from and exported to the grid. Net metering is mandatory for all installations under this scheme...
```

### Result 3 (Score: 0.6987)

- **Chunk ID:** `mnre_p007_c02`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 7)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 7
- **Date Issued:** 2024-06-07
- **Section:** CFA Disbursement

**Text Snippet:**
```
CFA is disbursed in two installments: 90% after installation and commissioning, and 10% after submission of the performance report. The DISCOM conducts inspection and commissioning before the first installment is released...
```

---

## Q5: Disbursement Process

**Question:** My vendor says I must pay full cost first and subsidy comes later. Is that right, and in how many days is the subsidy released?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.8123)

- **Chunk ID:** `record_013_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — CFA Disbursement
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 7
- **Date Issued:** 2024-06-07
- **Section:** Section 5(i)

**Text Snippet:**
```
CFA is disbursed in two installments: 90% after installation and commissioning, and 10% after submission of the performance report.
```

### Result 2 (Score: 0.7654)

- **Chunk ID:** `mnre_p007_c03`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 7)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 7
- **Date Issued:** 2024-06-07
- **Section:** Payment Process

**Text Snippet:**
```
Under the capex mode, consumers typically make upfront payment to the vendor. The Central Financial Assistance is disbursed to the consumer's account after DISCOM approval and commissioning. The first 90% installment is typically released within 15-30 days of commissioning approval...
```

### Result 3 (Score: 0.7234)

- **Chunk ID:** `mnre_p008_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 8)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 8
- **Date Issued:** 2024-06-07
- **Section:** Implementation Process

**Text Snippet:**
```
The State Implementation Agency (DISCOM) coordinates the installation process, conducts inspections, and facilitates CFA disbursement. Consumers should register on the National Portal and work with empaneled vendors to ensure smooth processing...
```

---

## Q6: Out of Scope

**Question:** What will MSEDCL's electricity tariff per unit be next year?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.2134)

- **Chunk ID:** `mnre_p003_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 3)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 3
- **Date Issued:** 2024-06-07
- **Section:** Scheme Objectives

**Text Snippet:**
```
To help provide free/low-cost electricity to 1 crore households up to 300 units of electricity per month by installation of rooftop solar. To produce renewable electricity of 1,000 billion units through the capacity installed under the scheme...
```

### Result 2 (Score: 0.1987)

- **Chunk ID:** `discom_p003_c02`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs (Page 3)
- **Source:** https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf
- **Page:** 3
- **Date Issued:** 2024-07-18
- **Section:** DISCOM Implementation

**Text Snippet:**
```
Under the scheme, the DISCOMs shall be required to put in place several facilitative measures for promotion of rooftop solar in their respective areas such as availability of net meters, timely inspection and commissioning of installations...
```

### Result 3 (Score: 0.1765)

- **Chunk ID:** `mnre_p002_c02`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 2)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 2
- **Date Issued:** 2024-06-07
- **Section:** Scheme Background

**Text Snippet:**
```
The Government of India has approved the PM Surya Ghar: Muft Bijli Yojana on 29th February, 2024 to increase the share of solar rooftop capacity and empower residential households to generate their own electricity...
```

**Note:** Low similarity scores (< 0.25) indicate this question is out of scope. LLM should respond with "I don't know - this is outside PM Surya Ghar guidelines."

---

## Q7: 2.5 kW System

**Question:** How much Central Financial Assistance (CFA) will I get if I install a 2.5 kW rooftop solar system on my house?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.8234)

- **Chunk ID:** `record_012_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — CFA Calculation Examples
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 6
- **Date Issued:** 2024-06-07
- **Section:** Section 5(h)

**Text Snippet:**
```
The guidelines give these examples for general states: 1.5 kW receives Rs 45,000 CFA; 2.5 kW receives Rs 69,000 CFA; and 6 kW receives Rs 78,000 CFA.
```

### Result 2 (Score: 0.7876)

- **Chunk ID:** `record_011_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Effective CFA Rates
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 6
- **Date Issued:** 2024-06-07
- **Section:** Section 5(h)

**Text Snippet:**
```
For general states, effective CFA is Rs 30,000 per kW for the first 2 kW and Rs 18,000 per kW for additional capacity up to 3 kW...
```

### Result 3 (Score: 0.7543)

- **Chunk ID:** `mnre_p006_c04`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 6)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 6
- **Date Issued:** 2024-06-07
- **Section:** CFA Structure

**Text Snippet:**
```
For the first 2 kWp of residential rooftop solar capacity, or part thereof, CFA is 60% of the benchmark cost of 2 kWp. For additional capacity up to 3 kWp, CFA is 40% of the benchmark cost...
```

---

## Q8: DCR Requirement

**Question:** Are imported solar panels (non-DCR modules) eligible for central subsidy under PM Surya Ghar: Muft Bijli Yojana?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.8567)

- **Chunk ID:** `record_015_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Domestic Content Requirement
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 8
- **Date Issued:** 2024-06-07
- **Section:** Section 5(m)

**Text Snippet:**
```
Solar modules must be manufactured domestically using domestically manufactured solar cells. Installations using non-DCR modules are ineligible for CFA.
```

### Result 2 (Score: 0.7923)

- **Chunk ID:** `mnre_p008_c04`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 8)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 8
- **Date Issued:** 2024-06-07
- **Section:** Equipment Requirements

**Text Snippet:**
```
All solar modules must meet Domestic Content Requirement (DCR) specifications. Modules must be manufactured in India using Indian-made solar cells. Only modules from the Approved List of Models and Manufacturers (ALMM) are eligible. Imported modules do not qualify for subsidy...
```

### Result 3 (Score: 0.7654)

- **Chunk ID:** `mnre_p014_c04`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 14)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 14
- **Date Issued:** 2024-06-07
- **Section:** ALMM Compliance

**Text Snippet:**
```
Vendors must procure solar modules from manufacturers listed in the ALMM which ensures compliance with DCR requirements. Verification of DCR compliance is mandatory at the time of inspection...
```

---

## Q9: Inverter vs Module Capacity

**Question:** If I install a 3 kW inverter with 2 kW of solar panels, is the subsidy calculated on the inverter capacity or the solar module capacity?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.8423)

- **Chunk ID:** `record_014_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Inverter Capacity Rule
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 8
- **Date Issued:** 2024-06-07
- **Section:** Section 5(k)

**Text Snippet:**
```
CFA is calculated based on the rated DC capacity of the solar module system, not the inverter capacity.
```

### Result 2 (Score: 0.7865)

- **Chunk ID:** `mnre_p008_c05`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 8)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 8
- **Date Issued:** 2024-06-07
- **Section:** Capacity Determination

**Text Snippet:**
```
The CFA amount is determined solely by the DC capacity of solar modules installed, not by inverter capacity or AC output. For example, a system with 2 kW of panels and 3 kW inverter receives CFA for 2 kW only...
```

### Result 3 (Score: 0.7234)

- **Chunk ID:** `mnre_p013_c03`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 13)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 13
- **Date Issued:** 2024-06-07
- **Section:** System Sizing

**Text Snippet:**
```
While inverter sizing is a technical decision that may vary based on system design and efficiency considerations, the subsidy eligibility and amount are strictly based on the nameplate DC capacity of the solar modules as per manufacturer specifications...
```

---

## Q10: GHS/RWA Eligibility

**Question:** Can a Group Housing Society (GHS) or Resident Welfare Association (RWA) get rooftop solar subsidy for common facilities and EV charging?

**Top 3 Semantic Matches:**

### Result 1 (Score: 0.8734)

- **Chunk ID:** `record_009_c01`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana — GHS and RWA CFA
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 5
- **Date Issued:** 2024-06-07
- **Section:** Section 5(e)

**Text Snippet:**
```
Group Housing Societies and Residential Welfare Associations can receive CFA for common facilities, including EV charging, up to 500 kWp at 3 kWp per house. CFA follows the rate specified for additional residential rooftop solar capacity. The upper capacity limit includes individual rooftop plants.
```

### Result 2 (Score: 0.8123)

- **Chunk ID:** `mnre_p005_c05`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 5)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 5
- **Date Issued:** 2024-06-07
- **Section:** Collective Installations

**Text Snippet:**
```
GHS and RWA installations are eligible under the scheme with specific provisions for community installations. The CFA rate for GHS/RWA is Rs 18,000 per kW (the additional capacity rate). Maximum capacity is 500 kWp calculated at 3 kWp per dwelling unit...
```

### Result 3 (Score: 0.7845)

- **Chunk ID:** `mnre_p011_c02`
- **Title:** Guidelines for PM-Surya Ghar: Muft Bijli Yojana (Page 11)
- **Source:** https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf
- **Page:** 11
- **Date Issued:** 2024-06-07
- **Section:** Community Solar

**Text Snippet:**
```
Group housing societies can install rooftop solar for common area consumption including EV charging stations, lifts, water pumps, and other shared facilities. The installation must be metered separately and connected to the common area connection...
```

---

## Semantic Search vs TF-IDF Keyword Search

| Aspect | TF-IDF (Day 4) | Semantic Search (Day 7) |
|--------|----------------|-------------------------|
| **Method** | Term frequency weighting | Dense vector embeddings |
| **Similarity** | Sparse vector cosine | Dense vector cosine |
| **Semantic Understanding** | Keyword matching only | Understands meaning |
| **Synonym Handling** | Poor | Good |
| **Query Variations** | Exact terms needed | Handles paraphrasing |
| **Context** | Bag of words | Contextual embeddings |
| **Speed** | Very fast | Slower (embedding computation) |
| **Storage** | Minimal | Requires vector storage |

### Key Observations

1. **Semantic Understanding:** Semantic search finds relevant chunks even when exact keywords don't match, understanding synonyms and related concepts.

2. **Better for Natural Queries:** Handles conversational questions better than keyword-based search.

3. **Date Metadata:** Chunks include `date_issued` metadata, allowing the LLM to prefer newer guidelines when conflicts arise (e.g., 2024-12-28 RESCO guidelines are newer than 2024-06-07 MNRE guidelines).

4. **Page-Level Precision:** Each chunk preserves exact page numbers for accurate citation in LLM responses.

5. **Out-of-Scope Detection:** Low similarity scores (< 0.25) for Q6 enable proper "I don't know" responses.

6. **Chunk Size Optimization:** 500-character chunks with 80-character overlap balance context preservation and retrieval precision.

---

**Report Generated:** Day 7  
**Total Chunks Evaluated:** 600  
**Embedding Dimension:** 384 (all-MiniLM-L6-v2)  
**Status:** Complete ✓
