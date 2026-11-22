"""
Day 7 S2 — ChromaDB Vector Store
==================================
Persistent vector database for semantic search over PM Surya Ghar chunks.

Features:
- ChromaDB persistent storage (data/chroma_db/)
- Automatic indexing on first run
- Efficient similarity search with metadata filtering
- Integration with sentence-transformers embeddings

Run with:
    python -m app.vectorstore
"""


# Try to import ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Run: pip install chromadb")

# Import our modules
import sys

from app.chunking import get_all_chunks
from app.embed import embed_texts

# Collection name
COLLECTION_NAME = "suryagharsathi_chunks"
CHROMA_DB_PATH = "data/chroma_db"


def get_chroma_client():
    """Get or create ChromaDB client."""
    if not CHROMADB_AVAILABLE:
        raise ImportError("chromadb is required. Install with: pip install chromadb")

    # Create persistent client
    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )

    return client


def get_or_create_collection(client=None):
    """Get existing collection or create new one."""
    if client is None:
        client = get_chroma_client()

    # Try to get existing collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Loaded existing collection: {COLLECTION_NAME}")
        print(f"  Items: {collection.count()}")
        return collection
    except Exception:
        # Create new collection
        print(f"Creating new collection: {COLLECTION_NAME}")
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "PM Surya Ghar guideline chunks with semantic embeddings"}
        )
        return collection


def index_chunks(chunks: list[dict] | None = None) -> int:
    """
    Index chunks into ChromaDB collection.

    Args:
        chunks: List of chunk dictionaries (loads from cache if None)

    Returns:
        Number of chunks indexed
    """
    if not CHROMADB_AVAILABLE:
        print("ChromaDB not available - skipping indexing")
        return 0

    # Load chunks if not provided
    if chunks is None:
        print("Loading chunks...")
        chunks = get_all_chunks()

    if not chunks:
        print("No chunks to index")
        return 0

    print(f"Indexing {len(chunks)} chunks...")

    # Get collection
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    # Check if already indexed
    if collection.count() >= len(chunks):
        print(f"Collection already has {collection.count()} items - skipping re-indexing")
        return collection.count()

    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk['chunk_id'])
        documents.append(chunk['text'])
        metadatas.append({
            'source': chunk['source'],
            'page': str(chunk['page']),  # ChromaDB requires string metadata
            'title': chunk['title'],
            'section': chunk.get('section', ''),
            'date_issued': chunk['date_issued']
        })

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = embed_texts(documents)
    embeddings_list = embeddings.tolist()

    # Batch upsert (ChromaDB handles batching internally)
    print("Upserting to collection...")
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings_list,
        metadatas=metadatas
    )

    print(f"Successfully indexed {len(chunks)} chunks")
    print(f"Collection now has {collection.count()} items")

    return collection.count()


def query_vectorstore(
    query: str,
    top_k: int = 5,
    filter_metadata: dict | None = None
) -> list[dict]:
    """
    Query the vector store for similar chunks.

    Args:
        query: Search query
        top_k: Number of results to return
        filter_metadata: Optional metadata filter (e.g., {'date_issued': '2024-12-28'})

    Returns:
        List of result dictionaries with chunk_id, text, score, and metadata
    """
    if not CHROMADB_AVAILABLE:
        print("ChromaDB not available - returning empty results")
        return []

    try:
        # Get collection
        client = get_chroma_client()
        collection = get_or_create_collection(client)

        # Index if empty
        if collection.count() == 0:
            print("Collection is empty - indexing chunks...")
            index_chunks()

        # Generate query embedding
        query_embedding = embed_texts([query])[0].tolist()

        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            include=['documents', 'metadatas', 'distances']
        )

        # Format results
        formatted_results = []

        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                # Convert distance to similarity score (ChromaDB returns L2 distance)
                distance = results['distances'][0][i]
                # For normalized vectors, L2 distance relates to cosine similarity
                # similarity = 1 - (distance^2 / 2)
                similarity = 1 - (distance ** 2 / 2)
                similarity = max(0, min(1, similarity))  # Clamp to [0, 1]

                formatted_results.append({
                    'chunk_id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'source': results['metadatas'][0][i]['source'],
                    'page': int(results['metadatas'][0][i]['page']),
                    'title': results['metadatas'][0][i]['title'],
                    'section': results['metadatas'][0][i].get('section', ''),
                    'date_issued': results['metadatas'][0][i]['date_issued'],
                    'score': round(similarity, 4)
                })

        return formatted_results

    except Exception as e:
        print(f"Error querying vectorstore: {e}")
        return []


def reset_vectorstore():
    """Reset (delete) the vector store collection."""
    if not CHROMADB_AVAILABLE:
        print("ChromaDB not available")
        return

    try:
        client = get_chroma_client()
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted collection: {COLLECTION_NAME}")
    except Exception as e:
        print(f"Error deleting collection: {e}")


if __name__ == "__main__":
    """Test vector store functionality."""

    print("=" * 70)
    print("SuryaGharSathi Vector Store Test")
    print("=" * 70)
    print()

    if not CHROMADB_AVAILABLE:
        print("ChromaDB not available - install with: pip install chromadb")
        sys.exit(1)

    # Index chunks
    print("Step 1: Index chunks into ChromaDB")
    print("-" * 70)
    count = index_chunks()
    print()

    # Test queries
    print("Step 2: Test semantic queries")
    print("-" * 70)

    test_queries = [
        "How much subsidy for 3 kW system?",
        "DCR requirement for solar panels",
        "DISCOM net metering process"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = query_vectorstore(query, top_k=3)

        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['score']:.3f}] {result['chunk_id']}")
            print(f"     {result['title'][:60]}...")
            print(f"     Page {result['page']}, Date: {result['date_issued']}")

    print("\n" + "=" * 70)
    print("Vector store test complete!")
    print(f"Database location: {CHROMA_DB_PATH}")
    print("=" * 70)
