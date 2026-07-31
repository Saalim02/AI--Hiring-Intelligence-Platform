import os

import faiss
import numpy as np


# BAAI/bge-large-en-v1.5 = 1024 dimensions
dimension = 1024

VECTOR_DIR = os.getenv(
    "VECTOR_DATA_DIR",
    "vector_data"
)

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

        print(
            f"Loaded {loaded_index.ntotal} "
            "vectors from persistent FAISS store"
        )

        return loaded_index, loaded_ids

    print(
        "No persistent FAISS store found. "
        "Creating empty index."
    )

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

    print("=" * 50)
    print("ADD EMBEDDING CALLED")
    print("Resume ID:", resume_id)
    print("Embedding Length:", len(embedding))

    vector = np.array(
        [embedding],
        dtype="float32"
    )

    index.add(vector)

    resume_ids.append(
        resume_id
    )

    save_vectorstore()

    print(
        "Current Resume IDs:",
        resume_ids
    )

    print(
        "FAISS store persisted to disk"
    )

    print("=" * 50)


def search_embedding(
    query_embedding,
    top_k=5
):

    print("=" * 50)
    print("SEARCH CALLED")
    print("Resume IDs:", resume_ids)

    print(
        "Query Embedding Length:",
        len(query_embedding)
    )

    if len(resume_ids) == 0:

        print("NO RESUMES FOUND")

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

    print("Distances:", distances)
    print("Indices:", indices)

    results = []

    for idx in indices[0]:

        if (
            idx >= 0
            and idx < len(resume_ids)
        ):

            results.append(
                resume_ids[idx]
            )

    print(
        "FINAL RESULTS:",
        results
    )

    print("=" * 50)

    return results
