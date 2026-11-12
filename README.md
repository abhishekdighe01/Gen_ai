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