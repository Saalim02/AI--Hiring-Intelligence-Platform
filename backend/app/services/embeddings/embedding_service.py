from sentence_transformers import SentenceTransformer

from langsmith import traceable
from app.core.ai_errors import AIServiceUnavailable


MODEL_NAME = "BAAI/bge-large-en-v1.5"
model = None


def _get_model():
    """Load the embedding model only when an embedding operation is requested."""
    global model
    if model is not None:
        return model

    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as exc:
        raise AIServiceUnavailable(
            "AI processing is temporarily unavailable. Please try again later."
        ) from exc
    return model


@traceable(
    name="Embedding Generation"
)
def generate_embedding(
    text: str
):
    embedding = _get_model().encode(
        text
    )

    return embedding
