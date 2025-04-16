from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings


def semantic_search(records, user_query, top_k=3):
    """Filter semantically relevant records from list of dictionaries."""
    embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b", top_p=0.1)

    records_str = merge_records(records)
    metadata = get_metadata(records)
    found_indices = perform_similarity_search(records_str, user_query, embeddings, top_k)

    return [records[i] for i in found_indices]


def merge_records(records):
    """ ""Merge list of dictionaries into a single string."""
    return [" ".join(map(str, record.values())) for record in records]


def get_metadata(records):
    """Get metadata from records."""
    return [{"id": str(i)} for i in range(len(records))]


def perform_similarity_search(records, user_query, embeddings, metadata, top_k=3):
    """Perform semantic search on records."""
    vector_store = FAISS.from_texts(records, embeddings, metadata)

    results = vector_store.similarity_search(user_query, k=min(top_k, len(records)))
    return [int(doc.metadata["id"]) for doc in results]
