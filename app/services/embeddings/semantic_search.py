from app.services.embeddings.embedding_service import (
    generate_embedding
)

from app.vectorstore.faiss_store import (
    search_embedding
)


def semantic_resume_search(
    query: str
):

    query_embedding = generate_embedding(
        query
    )

    matched_resume_ids = search_embedding(
        query_embedding
    )

    return matched_resume_ids