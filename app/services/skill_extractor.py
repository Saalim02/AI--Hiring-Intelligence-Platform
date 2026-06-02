SKILLS_DB = [
    "python",
    "fastapi",
    "sql",
    "machine learning",
    "deep learning",
    "rag",
    "docker",
    "aws",
    "langchain",
    "postgresql",
    "numpy",
    "pandas",
    "react",
    "next.js",
    "tailwind",
    "faiss"
]


def extract_skills(text: str):

    text = text.lower()

    found_skills = []

    for skill in SKILLS_DB:

        if skill in text:

            found_skills.append(skill)

    return list(set(found_skills))