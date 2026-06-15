import json

from app.core.openai_client import (
    client
)


def extract_jd_skills(
    text: str
):

    prompt = f"""
   Extract ALL technical skills from this job description. 
   IMPORTANT: 
   - Return lowercase skills 
   - Remove duplicates 
   - Use concise canonical skill names 
   - Normalize similar wording consistently 
   
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

   Examples: 
   - "Hugging Face Transformers" → "transformers"- "REST APIs" → "rest api" - "CI CD pipelines" → "ci/cd" - "Postgres" → "postgresql" Return ONLY valid JSON. 
   
   Example: {{ "skills": [ "python", "fastapi", "docker", "kubernetes", "ci/cd" ] }} Job Description: {text}
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

    content = response.choices[0].message.content.strip()

    # Remove markdown formatting if present

    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    try:

        parsed_json = json.loads(
            content
        )

        return parsed_json.get(
            "skills",
            []
        )

    except Exception as e:

        print(
            "JSON Parsing Error:",
            e
        )

        print(
            "Raw OpenAI Response:",
            content
        )

        return []