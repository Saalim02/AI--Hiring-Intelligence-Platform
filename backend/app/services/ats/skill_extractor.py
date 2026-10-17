import json

from app.core.ai_errors import AIServiceInvalidResponse
from app.core.openai_client import create_chat_completion


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


    response = create_chat_completion(

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

    try:
        parsed_json = json.loads(content)
        skills = parsed_json.get("skills")
        if not isinstance(skills, list):
            raise ValueError("skills must be a list")
        return [str(skill) for skill in skills]
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise AIServiceInvalidResponse("The AI service returned an invalid skill extraction result") from exc
