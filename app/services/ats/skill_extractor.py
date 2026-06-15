import json

from app.core.openai_client import (
    client
)


def extract_skills(
    text: str
):

    prompt = f"""
You are an ATS resume skill extraction system.

Extract ONLY the technical skills explicitly mentioned
inside the SKILLS or TECHNICAL SKILLS section.

IMPORTANT:
- Return lowercase skills
- Remove duplicates
- Use concise canonical skill names
- Extract only skills actually present
- Do NOT infer missing skills
- Do NOT overmatch related technologies

Examples:
- "Hugging Face Transformers" → "transformers"
- "REST APIs" → "rest api"
- "CI CD pipelines" → "ci/cd"
- "Postgres" → "postgresql"

Ignore:
- projects
- certifications
- profile summary
- achievements
- experience section

Return ONLY valid JSON.

Example:

{{
    "skills": [
        "python",
        "fastapi",
        "docker",
        "transformers",
        "ci/cd"
    ]
}}
Use lowercase canonical skill names.

Extract ONLY concrete technical skills:

programming languages
frameworks
libraries
databases
cloud/devops tools
AI/ML technologies

Do NOT extract:

responsibilities
abstract concepts
generic engineering phrases

GOOD:
python
fastapi
docker
langchain
transformers
postgresql
ci/cd

BAD:
semantic search
backend optimization
observability
ai infrastructure scaling

Resume Skills Section:
{text}
"""


    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    content = response.choices[0].message.content

    parsed_json = json.loads(content)

    return parsed_json["skills"]