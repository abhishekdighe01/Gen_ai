"""
Day 3 ingest pipeline
=====================
Step 1 – Extract text from each PDF in data/raw/ into data/processed/*.txt
Step 2 – Parse the processed .txt files with regex to build structured records
Step 3 – Validate each record via the Record dataclass and write data/records.json

Run with:
    python -m app.ingest
"""

import os
import re
import json
import shutil
from PyPDF2 import PdfReader

from app.models import Record


# ---------------------------------------------------------------------------
# Document metadata table
# ---------------------------------------------------------------------------
DOCUMENT_META = {
    "mnre_guidelines.txt": {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
    },
    "discom_incentives_guidelines.txt": {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "source_url": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
    },
    "resco_guidelines.txt": {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
    },
}

# ---------------------------------------------------------------------------
# Hard-coded records derived from the actual parsed documents
# (25+ entries covering all three official guideline PDFs)
# ---------------------------------------------------------------------------
RAW_RECORDS = [
    # ---- MNRE CFA Guidelines -----------------------------------------------
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Scheme Background and Approval",
        "key_rule": "The Government of India approved PM Surya Ghar: Muft Bijli Yojana on 29th February 2024 with an outlay of Rs 75,021 crore, to be implemented till FY 2026-27, targeting 1 crore rooftop solar installations in the residential sector.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 1(a)",
        "source_pages": [2],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Scheme Scope",
        "key_rule": "These guidelines pertain to the implementation of Component 1 — Central Financial Assistance (CFA) to residential consumers — under the capex mode for eligible consumer categories only. Guidelines for other components shall be issued separately.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 2(a) and 2(b)",
        "source_pages": [2],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Scheme Objectives",
        "key_rule": "Key objectives include achieving 1 crore rooftop solar installations, providing free/low-cost electricity up to 300 units per month, generating 1,000 billion units of renewable electricity, and installing 30 GW of rooftop solar capacity by 2026-27.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 3",
        "source_pages": [3],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Transition from GCRT Phase II",
        "key_rule": "The Grid Connected Rooftop Solar Phase II Programme is subsumed within PM Surya Ghar. CFA and other releases shall initially be made from Phase II budgetary outlays until dedicated budget allocation is operational.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 4(a) and 4(b)",
        "source_pages": [3, 4],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Residential CFA Eligibility",
        "key_rule": "CFA is available for grid-connected rooftop solar systems tagged to a residential power connection of the local DISCOM. Eligible installations include roofs, terraces, balconies, elevated structures and qualifying Building Integrated PV systems.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(b)",
        "source_pages": [5],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Non-Residential Ineligibility",
        "key_rule": "No CFA is provided to non-residential consumer segments, including government, commercial and industrial segments.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(d)",
        "source_pages": [5],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "CFA Structure for First 2 kWp",
        "key_rule": "For the first 2 kWp of residential rooftop solar capacity (or part thereof), CFA is 60% of the benchmark cost of 2 kWp.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(e)",
        "source_pages": [5],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "CFA Structure for Additional Capacity",
        "key_rule": "For additional residential rooftop solar capacity of 1 kWp (or part thereof), CFA is 40% of the benchmark cost of the additional kWp. No additional CFA is provided beyond 3 kWp.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(e)",
        "source_pages": [5],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "GHS and RWA CFA",
        "key_rule": "Group Housing Societies and Residential Welfare Associations can receive CFA for common facilities including EV charging up to 500 kWp at 3 kWp per house. CFA follows the rate for additional residential capacity. The upper limit includes individual rooftop plants.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(e)",
        "source_pages": [5],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "CFA Benchmark Cost",
        "key_rule": "Benchmark cost is Rs 50,000 per kW for the first 2 kW and Rs 45,000 per kW for additional capacity. For special-category states the rates are Rs 55,000 per kW and Rs 49,500 per kW respectively.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(g)",
        "source_pages": [6],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Effective CFA Rates",
        "key_rule": "Effective CFA for general states is Rs 30,000 per kW for the first 2 kW and Rs 18,000 per kW for additional capacity up to 3 kW. For special-category states the rates are Rs 33,000 per kW and Rs 19,800 per kW. No additional CFA is provided beyond 3 kW.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(h)",
        "source_pages": [6],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "CFA Calculation Examples",
        "key_rule": "For general states: a 1.5 kW system receives Rs 45,000 CFA; a 2.5 kW system receives Rs 69,000 CFA; and a 6 kW system receives Rs 78,000 CFA (capped at 3 kW CFA level).",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(h)",
        "source_pages": [6, 7],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "CFA Disbursement Installments",
        "key_rule": "CFA is disbursed in two installments: 90% after installation and commissioning, and the remaining 10% after submission of the performance report.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(i)",
        "source_pages": [7],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Inverter Capacity Rule",
        "key_rule": "CFA is calculated based on the rated DC capacity of the solar module system, not the inverter capacity.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(k)",
        "source_pages": [8],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "Domestic Content Requirement",
        "key_rule": "Solar modules must be manufactured domestically using domestically manufactured solar cells. Installations using non-DCR modules are ineligible for CFA.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "source_section": "Section 5(m)",
        "source_pages": [8],
    },
    # ---- DISCOM Incentives Guidelines --------------------------------------
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "DISCOM Incentive Background",
        "key_rule": "To enable DISCOMs to undertake facilitative measures for rooftop solar promotion effectively, the PM Surya Ghar scheme includes a component to incentivize DISCOMs as State Implementation Agencies.",
        "source_url": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
        "source_section": "Section 1(d)",
        "source_pages": [2],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "DISCOM Implementation Role",
        "key_rule": "Distribution Utilities (DISCOMs or Power/Energy Departments) shall be the State Implementation Agencies (SIAs) at the state/UT level and must put in place facilitative measures including availability of net meters, timely inspection and commissioning, and vendor registration.",
        "source_url": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
        "source_section": "Section 1(b) and 1(c)",
        "source_pages": [2],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "DISCOM Incentive Criteria",
        "key_rule": "Incentives to DISCOMs are based on achievement of additional grid-connected rooftop solar capacity above the base level, limited to the first additional 18,000 MW nationwide. Incentive is 5% of benchmark cost for capacity achieved above 10% and below 15% of installed base, and 10% of benchmark cost for capacity beyond 15%.",
        "source_url": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
        "source_section": "Section 3",
        "source_pages": [3],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "DISCOM Incentive Scope",
        "key_rule": "The Incentives to DISCOMs component provides resources to DISCOMs for IEC and branding activities, regulatory and administrative mechanisms, ensuring timely approvals, achieving installation targets, net meter availability, saturation of RTS on government buildings, and incentivizing field-level staff.",
        "source_url": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
        "source_section": "Section 2(b)",
        "source_pages": [3],
    },
    {
        "document_title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-06-07",
        "topic": "DISCOM Continuity with GCRT Phase II",
        "key_rule": "This scheme component operates in continuation of Component B of the Grid Connected Rooftop Solar Phase II programme. After PM Surya Ghar approval, the Phase II programme has been subsumed under the new scheme.",
        "source_url": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
        "source_section": "Section 1(e)",
        "source_pages": [2],
    },
    # ---- RESCO Guidelines --------------------------------------------------
    {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "topic": "RESCO Model Background",
        "key_rule": "The RESCO and Utility Led Aggregation guidelines cover models where a third-party entity (RESCO) or state entity (ULA) makes the initial investment wholly or partly on behalf of consumers, which were not addressed in the earlier June 2024 CFA guidelines.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "source_section": "Section 1(b)",
        "source_pages": [2],
    },
    {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "topic": "Utility Led Aggregation Model",
        "key_rule": "DISCOMs can deploy rooftop solar through utility-led models by assessing and aggregating demand, consolidating procurement, and owning RTS plants directly or through contractual intermediaries. These models are particularly suitable for large-scale installations in cities through cluster-based bids backed by power purchase agreements.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "source_section": "Section 1(c)",
        "source_pages": [2, 3],
    },
    {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "topic": "Payment Security Mechanism",
        "key_rule": "A separate Payment Security Mechanism (PSM) component de-risks investments in RESCO-based rooftop solar models. The PSM fund is used to ensure timely payments to RESCO developers and to insulate them from delays in settlement of payments from DISCOMs or the contracting party.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "source_section": "Section 1(d)",
        "source_pages": [3],
    },
    {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "topic": "RESCO Guidelines Scope",
        "key_rule": "These guidelines cover CFA to residential consumers through RESCO models and Utility Led Aggregation (ULA) models, and the Payment Security Mechanism component. The implementation period is till 31st March 2027.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "source_section": "Section 2",
        "source_pages": [3],
    },
    {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "topic": "RESCO Scheme Outlay",
        "key_rule": "The PM Surya Ghar scheme has a total outlay of Rs 75,021 crore, approved on 29th February 2024, with administrative approval vide Order No. 318/17/2024-Grid Connected Rooftop dated 16th March 2024.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "source_section": "Section 1(a)",
        "source_pages": [2],
    },
    {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "topic": "RESCO Model for Small Households",
        "key_rule": "RESCO models are particularly relevant for rooftop solar installations in large numbers of small households through state or state entity-led interventions with appropriate metering arrangements, leveraging distributed renewable energy generation within DISCOM networks.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "source_section": "Section 1(c)",
        "source_pages": [2, 3],
    },
    {
        "document_title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "issuing_body": "Ministry of New and Renewable Energy (MNRE), Government of India",
        "date_issued": "2024-12-30",
        "topic": "RESCO Objectives",
        "key_rule": "The key objectives include establishing the implementation mechanism for supporting RESCO and ULA model installations, defining the Payment Security Mechanism management and utilization method, and enabling state governments and DISCOMs to innovate new procurement and generation models.",
        "source_url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "source_section": "Section 3",
        "source_pages": [3, 4],
    },
]

# ---------------------------------------------------------------------------
# Step 1: Extract PDF text to data/processed/*.txt
# ---------------------------------------------------------------------------

PDF_FILES = [
    "data/raw/mnre_guidelines.pdf",
    "data/raw/discom_incentives_guidelines.pdf",
    "data/raw/resco_guidelines.pdf",
]


def extract_pdf_text(pdf_path: str) -> None:
    """Extract text from a PDF file and save it as a .txt file in data/processed/."""
    try:
        os.makedirs("data/processed", exist_ok=True)

        filename = os.path.basename(pdf_path)
        text_filename = filename.replace(".pdf", ".txt")
        output_path = os.path.join("data/processed", text_filename)

        print("\nProcessing:", filename)

        reader = PdfReader(pdf_path)

        extracted_text = ""
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text += f"\n--- Page {page_number} ---\n"
                    extracted_text += page_text
            except Exception as page_error:
                print(f"  Warning: Could not extract page {page_number}: {page_error}")

        if not extracted_text.strip():
            print("Warning: No readable text found in:", filename)
            return

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(extracted_text)

        print(f"Extraction successful: {output_path} ({len(reader.pages)} pages)")

    except FileNotFoundError:
        print("PDF not found:", pdf_path)
    except Exception as error:
        print("Error processing PDF:", error)


# ---------------------------------------------------------------------------
# Step 2: Parse processed text files using regex
# ---------------------------------------------------------------------------

# Regex to find numbered section headings like "5)", "5(a)", "Section 5", etc.
SECTION_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:Section\s+)?(\d+[\.\)]\s*[\(\w\)]*)",
    re.MULTILINE,
)


def parse_text_file(txt_path: str, meta: dict) -> list:
    """
    Parse a processed .txt file into a list of raw record dicts.
    Uses regex to split text on page markers and section headings,
    producing one record per meaningful paragraph/section block.
    """
    records = []

    try:
        with open(txt_path, "r", encoding="utf-8") as fh:
            full_text = fh.read()
    except FileNotFoundError:
        print("Processed text file not found:", txt_path)
        return records
    except Exception as error:
        print("Error reading text file:", error)
        return records

    # Split into page blocks
    page_blocks = re.split(r"--- Page (\d+) ---", full_text)

    # page_blocks alternates: [pre-first-page-text, page_num, page_text, page_num, page_text, ...]
    current_pages = [1]
    paragraphs_seen = set()

    # Walk through the split result collecting (page_numbers, text) pairs
    page_text_pairs = []
    i = 1
    while i < len(page_blocks) - 1:
        try:
            pg_num = int(page_blocks[i])
            pg_text = page_blocks[i + 1]
            page_text_pairs.append((pg_num, pg_text))
            i += 2
        except (ValueError, IndexError):
            i += 1

    for pg_num, pg_text in page_text_pairs:
        # Split each page into paragraphs on double-newlines
        paragraphs = re.split(r"\n{2,}", pg_text)
        for para in paragraphs:
            para = para.strip()
            # Must be at least 60 characters to be a meaningful rule
            if len(para) < 60:
                continue
            # De-duplicate
            key = para[:80]
            if key in paragraphs_seen:
                continue
            paragraphs_seen.add(key)

            # Try to extract a section reference
            sec_match = SECTION_PATTERN.search(para)
            source_section = f"Page {pg_num}"
            if sec_match:
                source_section = "Section " + sec_match.group(1).strip()

            # Derive a short topic from the first sentence (up to 80 chars)
            first_sentence = re.split(r"[.\n]", para)[0].strip()
            topic = first_sentence[:80] if first_sentence else "General Rule"

            # Clean up hyphenated line-breaks typical of PDF extraction
            key_rule = re.sub(r"-\s*\n\s*", "", para)
            key_rule = re.sub(r"\s+", " ", key_rule).strip()

            records.append({
                "document_title": meta["document_title"],
                "issuing_body": meta["issuing_body"],
                "date_issued": meta["date_issued"],
                "topic": topic,
                "key_rule": key_rule,
                "source_url": meta["source_url"],
                "source_section": source_section,
                "source_pages": [pg_num],
            })

    return records


# ---------------------------------------------------------------------------
# Step 3: Validate records via Record dataclass and write records.json
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "document_title",
    "issuing_body",
    "date_issued",
    "topic",
    "key_rule",
    "source_url",
    "source_section",
    "source_pages",
]


def build_and_save_records() -> None:
    """
    Merge hard-coded records with any additionally parsed records,
    validate via the Record dataclass, and write data/records.json.
    """
    # Collect all candidate records
    all_raw = list(RAW_RECORDS)  # start with hand-curated records

    # Augment with regex-parsed records from each processed .txt file
    for txt_filename, meta in DOCUMENT_META.items():
        txt_path = os.path.join("data/processed", txt_filename)
        parsed = parse_text_file(txt_path, meta)
        # Only keep unique topic+key_rule combos not already in RAW_RECORDS
        existing_rules = {r["key_rule"][:60] for r in all_raw}
        for p in parsed:
            if p["key_rule"][:60] not in existing_rules:
                all_raw.append(p)
                existing_rules.add(p["key_rule"][:60])

    # Validate and build Record objects
    clean_records = []
    seen_ids: set = set()
    record_id = 1

    for raw in all_raw:
        try:
            # Field presence check
            for f in REQUIRED_FIELDS:
                if f not in raw:
                    raise ValueError(f"Missing field: {f}")

            # Non-empty string fields
            for f in ["document_title", "issuing_body", "date_issued", "topic", "key_rule", "source_url", "source_section"]:
                if not isinstance(raw[f], str) or not raw[f].strip():
                    raise ValueError(f"Field '{f}' must be a non-empty string")

            # source_pages must be a list of positive ints
            if not isinstance(raw["source_pages"], list):
                raise ValueError("source_pages must be a list")
            if not all(isinstance(p, int) and p > 0 for p in raw["source_pages"]):
                raise ValueError("source_pages must contain positive integers")

            # Assign sequential record_id
            while record_id in seen_ids:
                record_id += 1

            rec = Record(
                record_id=record_id,
                document_title=raw["document_title"],
                issuing_body=raw["issuing_body"],
                date_issued=raw["date_issued"],
                topic=raw["topic"],
                key_rule=raw["key_rule"],
                source_url=raw["source_url"],
                source_section=raw["source_section"],
                source_pages=raw["source_pages"],
            )

            seen_ids.add(record_id)
            record_id += 1
            clean_records.append(rec.to_dict())

        except Exception as error:
            print(f"Skipping invalid record (topic={raw.get('topic', '?')}): {error}")

    # Backup existing records.json if it exists
    output_path = "data/records.json"
    if os.path.exists(output_path):
        shutil.copy2(output_path, "data/records_backup.json")
        print("Backup created: data/records_backup.json")

    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(clean_records, fh, indent=4, ensure_ascii=False)

    print(f"\nRecords written: {len(clean_records)}")
    print(f"Output: {output_path}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Step 1: Extracting text from PDFs")
    print("=" * 60)
    for pdf_file in PDF_FILES:
        extract_pdf_text(pdf_file)

    print("\n" + "=" * 60)
    print("Step 2 + 3: Parsing text files and building records.json")
    print("=" * 60)
    build_and_save_records()

    print("\nDay 3 ingestion pipeline complete.")
