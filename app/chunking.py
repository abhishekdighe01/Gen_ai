"""
Day 7 S1 — Document Chunking with Metadata
===========================================
Splits PM Surya Ghar documents into overlapping chunks with preserved metadata.

Features:
- Respects page boundaries from --- Page N --- markers
- Overlapping chunks (400-600 chars with 80 char overlap)
- Complete metadata: chunk_id, text, source, page, title, date_issued
- Processes both .txt files and structured JSON records

Run with:
    python -m app.chunking
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List

# Document metadata mapping
DOCUMENT_METADATA = {
    "mnre_guidelines.txt": {
        "title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Central Financial Assistance to Residential Consumers",
        "source": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
        "date_issued": "2024-06-07"
    },
    "discom_incentives_guidelines.txt": {
        "title": "Guidelines for PM-Surya Ghar: Muft Bijli Yojana — Incentives to DISCOMs",
        "source": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
        "date_issued": "2024-07-18"
    },
    "resco_guidelines.txt": {
        "title": "PM Surya Ghar: Muft Bijli Yojana — RESCO, Utility Led Models and Payment Security Mechanism",
        "source": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
        "date_issued": "2024-12-28"
    }
}


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 80,
    min_chunk_size: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to chunk
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks
        min_chunk_size: Minimum chunk size to keep

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If this is not the last chunk, try to break at sentence/word boundary
        if end < len(text):
            # Look for sentence end markers within last 100 chars
            search_text = text[max(start, end-100):end]
            sentence_ends = [m.end() for m in re.finditer(r'[.!?]\s+', search_text)]

            if sentence_ends:
                # Use the last sentence boundary
                end = max(start, end-100) + sentence_ends[-1]
            else:
                # Try word boundary
                search_text = text[max(start, end-50):end]
                word_ends = [m.end() for m in re.finditer(r'\s+', search_text)]
                if word_ends:
                    end = max(start, end-50) + word_ends[-1]

        chunk = text[start:end].strip()
        if len(chunk) >= min_chunk_size:
            chunks.append(chunk)

        # Move start position with overlap
        start = end - overlap

        # Prevent infinite loop
        if start <= (end - overlap):
            start = end

    return chunks


def chunk_document_file(
    filepath: str,
    doc_id: str,
    metadata: Dict[str, str]
) -> List[Dict]:
    """
    Chunk a processed text file with page markers.

    Args:
        filepath: Path to .txt file
        doc_id: Document identifier (e.g., "mnre", "discom", "resco")
        metadata: Document metadata (title, source, date_issued)

    Returns:
        List of chunk dictionaries with metadata
    """
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by page markers
    page_pattern = r'--- Page (\d+) ---'
    pages = re.split(page_pattern, content)

    chunks = []
    chunk_counter = 1

    # Process pages (pages list alternates: [pre-text, page_num, page_text, page_num, page_text, ...])
    i = 1
    while i < len(pages) - 1:
        try:
            page_num = int(pages[i])
            page_text = pages[i + 1].strip()

            if len(page_text) < 50:  # Skip very short pages
                i += 2
                continue

            # Extract section heading if present (first line often contains section info)
            lines = page_text.split('\n')
            section = lines[0][:100] if lines else ""

            # Chunk the page text
            page_chunks = chunk_text(page_text, chunk_size=500, overlap=80)

            for chunk_text_content in page_chunks:
                chunk_id = f"{doc_id}_p{page_num:03d}_c{chunk_counter:02d}"

                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text_content,
                    "source": metadata["source"],
                    "page": page_num,
                    "title": f"{metadata['title']} (Page {page_num})",
                    "section": section,
                    "date_issued": metadata["date_issued"]
                })

                chunk_counter += 1

        except (ValueError, IndexError) as e:
            print(f"Error processing page section: {e}")

        i += 2

    return chunks


def chunk_json_records(json_path: str = "data/records.json") -> List[Dict]:
    """
    Chunk structured records from JSON.

    Each record becomes one or more chunks depending on key_rule length.

    Args:
        json_path: Path to records.json

    Returns:
        List of chunk dictionaries
    """
    if not os.path.exists(json_path):
        print(f"Warning: File not found: {json_path}")
        return []

    with open(json_path, 'r', encoding='utf-8') as f:
        records = json.load(f)

    chunks = []

    for record in records:
        try:
            # Use record as single chunk if rule is short enough
            text = f"{record['topic']}\n\n{record['key_rule']}"

            if len(text) <= 600:
                # Single chunk
                chunk_id = f"record_{record['record_id']:03d}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": text,
                    "source": record.get("source_url", record.get("source", "")),
                    "page": record.get("source_pages", [0])[0] if record.get("source_pages") else 0,
                    "title": f"{record['document_title']} — {record['topic']}",
                    "section": record.get("source_section", ""),
                    "date_issued": record.get("date_issued", "2024-06-07")
                })
            else:
                # Split long rules into multiple chunks
                rule_chunks = chunk_text(text, chunk_size=500, overlap=80)
                for i, chunk_text_content in enumerate(rule_chunks, 1):
                    chunk_id = f"record_{record['record_id']:03d}_c{i:02d}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": chunk_text_content,
                        "source": record.get("source_url", record.get("source", "")),
                        "page": record.get("source_pages", [0])[0] if record.get("source_pages") else 0,
                        "title": f"{record['document_title']} — {record['topic']}",
                        "section": record.get("source_section", ""),
                        "date_issued": record.get("date_issued", "2024-06-07")
                    })

        except Exception as e:
            print(f"Error processing record {record.get('record_id', '?')}: {e}")

    return chunks


def get_all_chunks(force_refresh: bool = False) -> List[Dict]:
    """
    Get all document chunks from cache or generate fresh.

    Args:
        force_refresh: Force regeneration of chunks

    Returns:
        List of all chunks with metadata
    """
    cache_path = "data/chunks_cache.json"

    # Load from cache if available and not forcing refresh
    if not force_refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")

    # Generate chunks
    all_chunks = []

    # Process .txt files
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        for filename, metadata in DOCUMENT_METADATA.items():
            filepath = processed_dir / filename
            doc_id = filename.replace("_guidelines.txt", "").replace(".txt", "")

            print(f"Chunking {filename}...")
            chunks = chunk_document_file(str(filepath), doc_id, metadata)
            all_chunks.extend(chunks)
            print(f"  Generated {len(chunks)} chunks")

    # Process JSON records
    print("Chunking records.json...")
    record_chunks = chunk_json_records()
    all_chunks.extend(record_chunks)
    print(f"  Generated {len(record_chunks)} chunks from records")

    # Save cache
    os.makedirs("data", exist_ok=True)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nTotal chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    """Test chunking functionality."""

    print("=" * 70)
    print("SuryaGharSathi Document Chunking Test")
    print("=" * 70)
    print()

    # Generate chunks
    chunks = get_all_chunks(force_refresh=True)

    print(f"\nGenerated {len(chunks)} total chunks")
    print()

    # Show sample chunks
    print("Sample chunks:")
    print("-" * 70)

    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n{i}. Chunk ID: {chunk['chunk_id']}")
        print(f"   Title: {chunk['title'][:60]}...")
        print(f"   Source: {chunk['source'][:50]}...")
        print(f"   Page: {chunk['page']}")
        print(f"   Date: {chunk['date_issued']}")
        print(f"   Text: {chunk['text'][:100]}...")

    print("\n" + "=" * 70)
    print("Chunking complete! Cache saved to data/chunks_cache.json")
    print("=" * 70)
