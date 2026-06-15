import faiss
import numpy as np

dimension = 384

index = faiss.IndexFlatL2(dimension)

resume_ids = []


def add_embedding(
    embedding,
    resume_id
):

    vector = np.array(
        [embedding],
        dtype="float32"
    )

    index.add(vector)

    resume_ids.append(resume_id)


def search_embedding(
    query_embedding,
    top_k=5
):

    if len(resume_ids) == 0:

        return []

    actual_top_k = min(
        top_k,
        len(resume_ids)
    )

    vector = np.array(
        [query_embedding],
        dtype="float32"
    )

    distances, indices = index.search(
        vector,
        actual_top_k
    )

    results = []

    for idx in indices[0]:

        if (
            idx >= 0 and
            idx < len(resume_ids)
        ):

            results.append(
                resume_ids[idx]
            )

    return results