from sentence_transformers import (
    SentenceTransformer
)

from langsmith import traceable


model = SentenceTransformer(
    "BAAI/bge-large-en-v1.5"
)


@traceable(
    name="Embedding Generation"
)
def generate_embedding(
    text: str
):

    embedding = model.encode(
        text
    )

    return embedding