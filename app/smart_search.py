"""
Day 4 S2 — Smart Search Engine
================================
TF-IDF + cosine similarity ranking over SuryaGharSathi records.

Indexes: topic + key_rule + document_title
Returns: Top-k records ranked by relevance (cosine similarity score)

Run with:
    from app.smart_search import smart_search
    results = smart_search("CFA subsidy rates", top_k=5)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from app.records import load_records
from app.models import Record


# Cache vectorizer and document vectors globally to avoid recomputation
_vectorizer = None
_doc_vectors = None
_records_cache = None


def _build_index():
    """
    Build TF-IDF index over all records.
    
    Combines topic + key_rule + document_title into a single searchable text.
    Returns: (vectorizer, doc_vectors, records)
    """
    global _vectorizer, _doc_vectors, _records_cache
    
    if _records_cache is not None:
        return _vectorizer, _doc_vectors, _records_cache
    
    records = load_records()
    
    # Combine searchable fields into one text per record
    documents = []
    for record in records:
        searchable_text = f"{record.topic} {record.key_rule} {record.document_title}"
        documents.append(searchable_text)
    
    # Build TF-IDF vectorizer and transform documents
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2),  # unigrams and bigrams
        min_df=1,
        lowercase=True
    )
    
    doc_vectors = vectorizer.fit_transform(documents)
    
    # Cache for future searches
    _vectorizer = vectorizer
    _doc_vectors = doc_vectors
    _records_cache = records
    
    return vectorizer, doc_vectors, records


def smart_search(query: str, top_k: int = 5) -> List[Tuple[Record, float]]:
    """
    Search records using TF-IDF + cosine similarity.
    
    Args:
        query: Search query string
        top_k: Number of top results to return (default: 5)
    
    Returns:
        List of (Record, similarity_score) tuples, sorted by score descending
        Only returns results with similarity > 0
    
    Example:
        >>> results = smart_search("CFA subsidy residential", top_k=3)
        >>> for record, score in results:
        ...     print(f"{score:.3f} - {record.topic}")
    """
    if not query or not query.strip():
        return []
    
    # Build/retrieve index
    vectorizer, doc_vectors, records = _build_index()
    
    # Vectorize query
    try:
        query_vector = vectorizer.transform([query])
    except Exception as e:
        print(f"Error vectorizing query: {e}")
        return []
    
    # Compute cosine similarity
    similarities = cosine_similarity(query_vector, doc_vectors).flatten()
    
    # Pair records with scores and filter out zeros
    results = [
        (records[i], float(similarities[i]))
        for i in range(len(records))
        if similarities[i] > 0
    ]
    
    # Sort by similarity descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k
    return results[:top_k]


# Alias for backward compatibility and explicit naming
rank_records = smart_search


def reset_index():
    """Clear the cached index (useful for testing or when records change)."""
    global _vectorizer, _doc_vectors, _records_cache
    _vectorizer = None
    _doc_vectors = None
    _records_cache = None


if __name__ == "__main__":
    # Test the search engine
    print("=" * 70)
    print("SuryaGharSathi Smart Search Test")
    print("=" * 70)
    
    test_queries = [
        "CFA subsidy rates for residential solar",
        "DISCOM incentives",
        "domestic content requirement",
        "RESCO payment security",
        "net metering rooftop",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 70)
        
        results = smart_search(query, top_k=3)
        
        if results:
            for i, (record, score) in enumerate(results, 1):
                print(f"{i}. [Score: {score:.4f}] ID: {record.record_id}")
                print(f"   Topic: {record.topic}")
                print(f"   Rule: {record.key_rule[:100]}...")
        else:
            print("   No results found")
    
    print("\n" + "=" * 70)
    print(f"Search engine ready with {len(_records_cache)} records indexed")
    print("=" * 70)
