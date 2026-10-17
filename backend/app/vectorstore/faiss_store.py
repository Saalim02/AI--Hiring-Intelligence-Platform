import os

import faiss
import numpy as np

from app.core.config import settings


# BAAI/bge-large-en-v1.5 = 1024 dimensions
dimension = 1024

VECTOR_DIR = settings.VECTOR_DATA_DIR

INDEX_PATH = os.path.join(
    VECTOR_DIR,
    "index.faiss"
)

IDS_PATH = os.path.join(
    VECTOR_DIR,
    "resume_ids.npy"
)

os.makedirs(
    VECTOR_DIR,
    exist_ok=True
)


def load_vectorstore():

    if (
        os.path.exists(INDEX_PATH)
        and os.path.exists(IDS_PATH)
    ):

        loaded_index = faiss.read_index(
            INDEX_PATH
        )

        loaded_ids = np.load(
            IDS_PATH
        ).tolist()

        if loaded_index.d != dimension:
            raise ValueError(
                f"FAISS dimension mismatch: "
                f"expected {dimension}, "
                f"got {loaded_index.d}"
            )

        if loaded_index.ntotal != len(loaded_ids):
            raise ValueError(
                "FAISS index and resume ID mapping "
                "are inconsistent"
            )

        return loaded_index, loaded_ids

    return (
        faiss.IndexFlatL2(dimension),
        []
    )


index, resume_ids = load_vectorstore()


def save_vectorstore():

    faiss.write_index(
        index,
        INDEX_PATH
    )

    np.save(
        IDS_PATH,
        np.array(
            resume_ids,
            dtype=np.int64
        )
    )


def add_embedding(
    embedding,
    resume_id
):

    vector = np.array(
        [embedding],
        dtype="float32"
    )

    index.add(vector)

    resume_ids.append(
        resume_id
    )

    save_vectorstore()


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
            idx >= 0
            and idx < len(resume_ids)
        ):

            results.append(
                resume_ids[idx]
            )

    return results
