from sentence_transformers import util

from app.services.embeddings.embedding_service import (
    generate_embedding
)


def calculate_ats_score(
    resume_text: str,
    job_description: str
):

    resume_embedding = generate_embedding(
        resume_text
    )

    jd_embedding = generate_embedding(
        job_description
    )

    similarity_score = util.cos_sim(
        resume_embedding,
        jd_embedding
    )

    score = float(
        similarity_score[0][0]
    ) * 100

    return round(score, 2)