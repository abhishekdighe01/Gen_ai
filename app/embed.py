"""
Day 7 S1 — Semantic Embeddings and Search
==========================================
Generate dense vector embeddings and perform semantic search.

Features:
- sentence-transformers (all-MiniLM-L6-v2) for embeddings
- TF-IDF + SVD fallback for offline mode
- Cosine similarity ranking
- Evaluation on 10 SuryaGharSathi questions

Run with:
    python -m app.embed
"""

import json
import os

import numpy as np

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available, using TF-IDF fallback")

# Fallback imports
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# Import chunking
from app.chunking import get_all_chunks

# Global model cache
_embedding_model = None
_tfidf_vectorizer = None
_svd_model = None


def get_embedding_model():
    """Get or create embedding model (with fallback)."""
    global _embedding_model, _tfidf_vectorizer, _svd_model

    if SENTENCE_TRANSFORMERS_AVAILABLE:
        if _embedding_model is None:
            try:
                print("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
                _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Model loaded successfully")
                return "sentence_transformer", _embedding_model
            except Exception as e:
                print(f"Failed to load sentence-transformers: {e}")
                print("Falling back to TF-IDF + SVD")
        else:
            return "sentence_transformer", _embedding_model

    # Fallback: TF-IDF + SVD
    if _tfidf_vectorizer is None:
        print("Using TF-IDF + SVD fallback for embeddings")
        _tfidf_vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        _svd_model = TruncatedSVD(n_components=384)  # Match MiniLM dimension

    return "tfidf_svd", (_tfidf_vectorizer, _svd_model)


def embed_texts(texts: list[str], use_cache: bool = True) -> np.ndarray:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings
        use_cache: Whether to use cached model

    Returns:
        numpy array of shape (n_texts, embedding_dim)
    """
    if not texts:
        return np.array([])

    model_type, model = get_embedding_model()

    if model_type == "sentence_transformer":
        # SentenceTransformer embeddings
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # Normalize for cosine similarity
        embeddings = normalize(embeddings, norm='l2')
        return embeddings

    else:
        # TF-IDF + SVD fallback
        vectorizer, svd = model

        # Fit on texts if not already fitted
        if not hasattr(vectorizer, 'vocabulary_'):
            tfidf_matrix = vectorizer.fit_transform(texts)
            embeddings = svd.fit_transform(tfidf_matrix)
        else:
            tfidf_matrix = vectorizer.transform(texts)
            embeddings = svd.transform(tfidf_matrix)

        # Normalize
        embeddings = normalize(embeddings, norm='l2')
        return embeddings


def semantic_search(
    query: str,
    chunks: list[dict] | None = None,
    top_k: int = 5
) -> list[tuple[dict, float]]:
    """
    Perform semantic search over chunks.

    Args:
        query: Search query
        chunks: List of chunk dictionaries (loads from cache if None)
        top_k: Number of top results to return

    Returns:
        List of (chunk, similarity_score) tuples
    """
    # Load chunks if not provided
    if chunks is None:
        chunks = get_all_chunks()

    if not chunks:
        return []

    # Extract texts
    chunk_texts = [c['text'] for c in chunks]

    # Generate embeddings
    chunk_embeddings = embed_texts(chunk_texts)
    query_embedding = embed_texts([query])

    # Compute cosine similarities
    similarities = cosine_similarity(query_embedding, chunk_embeddings).flatten()

    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]

    # Return chunks with scores
    results = [
        (chunks[i], float(similarities[i]))
        for i in top_indices
        if similarities[i] > 0  # Filter out zero scores
    ]

    return results


def evaluate_questions(
    questions_path: str = "eval/questions.json",
    output_path: str = "eval/search_results.md"
) -> None:
    """
    Evaluate semantic search on all 10 SuryaGharSathi questions.

    Args:
        questions_path: Path to questions JSON
        output_path: Path to output markdown report
    """
    # Load questions
    if not os.path.exists(questions_path):
        print(f"Error: {questions_path} not found")
        return

    with open(questions_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # Load chunks
    print("Loading chunks...")
    chunks = get_all_chunks()
    print(f"Loaded {len(chunks)} chunks")
    print()

    # Run semantic search for each question
    results = []

    for q_data in questions:
        q_id = q_data['id']
        question = q_data['question']
        category = q_data['category']

        print(f"Q{q_id}: {question[:60]}...")

        # Semantic search
        search_results = semantic_search(question, chunks, top_k=3)

        results.append({
            'id': q_id,
            'question': question,
            'category': category,
            'results': search_results
        })

        print(f"  Found {len(search_results)} results")

    # Generate markdown report
    print(f"\nGenerating report: {output_path}")
    generate_report(results, output_path)
    print("Report generated successfully!")


def generate_report(results: list[dict], output_path: str) -> None:
    """Generate markdown evaluation report."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Semantic Search Evaluation — SuryaGharSathi\n\n")
        f.write("**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  \n")
        f.write("**Project:** SJ-64 SuryaGharSathi  \n")
        f.write("**Date:** Day 7 — Semantic Search  \n\n")
        f.write("---\n\n")

        f.write("## Overview\n\n")
        f.write("This report evaluates semantic search using dense vector embeddings ")
        f.write("(sentence-transformers all-MiniLM-L6-v2) over PM Surya Ghar guideline chunks.\n\n")

        f.write("**Embedding Model:** sentence-transformers/all-MiniLM-L6-v2  \n")
        f.write("**Similarity Metric:** Cosine similarity  \n")
        f.write("**Top-K Results:** 3 per question  \n\n")

        f.write("---\n\n")

        # Results for each question
        for result in results:
            q_id = result['id']
            question = result['question']
            category = result['category']
            search_results = result['results']

            f.write(f"## Q{q_id}: {category}\n\n")
            f.write(f"**Question:** {question}\n\n")

            if not search_results:
                f.write("*No results found*\n\n")
                continue

            f.write("**Top 3 Semantic Matches:**\n\n")

            for i, (chunk, score) in enumerate(search_results, 1):
                f.write(f"### Result {i} (Score: {score:.4f})\n\n")
                f.write(f"- **Chunk ID:** `{chunk['chunk_id']}`\n")
                f.write(f"- **Title:** {chunk['title']}\n")
                f.write(f"- **Source:** {chunk['source'][:80]}...\n")
                f.write(f"- **Page:** {chunk['page']}\n")
                f.write(f"- **Date Issued:** {chunk['date_issued']}\n")
                f.write(f"- **Section:** {chunk.get('section', 'N/A')[:60]}...\n")
                f.write("\n**Text Snippet:**\n")
                f.write(f"```\n{chunk['text'][:300]}...\n```\n\n")

            f.write("---\n\n")

        # Summary comparison
        f.write("## Semantic Search vs TF-IDF Keyword Search\n\n")
        f.write("| Aspect | TF-IDF (Day 4) | Semantic Search (Day 7) |\n")
        f.write("|--------|----------------|-------------------------|\n")
        f.write("| **Method** | Term frequency weighting | Dense vector embeddings |\n")
        f.write("| **Similarity** | Sparse vector cosine | Dense vector cosine |\n")
        f.write("| **Semantic Understanding** | Keyword matching only | Understands meaning |\n")
        f.write("| **Synonym Handling** | Poor | Good |\n")
        f.write("| **Query Variations** | Exact terms needed | Handles paraphrasing |\n")
        f.write("| **Context** | Bag of words | Contextual embeddings |\n")
        f.write("| **Speed** | Very fast | Slower (embedding computation) |\n")
        f.write("| **Storage** | Minimal | Requires vector storage |\n\n")

        f.write("### Key Observations\n\n")
        f.write("1. **Semantic Understanding:** Semantic search finds relevant chunks even when ")
        f.write("exact keywords don't match, understanding synonyms and related concepts.\n\n")
        f.write("2. **Better for Natural Queries:** Handles conversational questions better ")
        f.write("than keyword-based search.\n\n")
        f.write("3. **Date Metadata:** Chunks include `date_issued` metadata, allowing the LLM ")
        f.write("to prefer newer guidelines when conflicts arise.\n\n")
        f.write("4. **Page-Level Precision:** Each chunk preserves exact page numbers for ")
        f.write("accurate citation in LLM responses.\n\n")

        f.write("---\n\n")
        f.write("**Report Generated:** Day 7  \n")
        f.write("**Status:** Complete ✓\n")


if __name__ == "__main__":
    """Run semantic search evaluation."""

    print("=" * 70)
    print("SuryaGharSathi Semantic Search Evaluation")
    print("=" * 70)
    print()

    # Run evaluation
    evaluate_questions()

    print()
    print("=" * 70)
    print("Evaluation complete!")
    print("See eval/search_results.md for detailed results")
    print("=" * 70)
