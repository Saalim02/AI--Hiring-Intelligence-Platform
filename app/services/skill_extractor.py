import json

from app.core.openai_client import (
    client
)


def extract_skills(
    text: str
):

    prompt = f"""
    You are an ATS resume skill extraction system.

    Extract ONLY the skills explicitly mentioned
    inside the SKILLS or TECHNICAL SKILLS section.

    Ignore:
    - project technologies
    - certifications
    - profile summary
    - achievements
    - experience section

    Return ONLY valid JSON.

    Example:

    {{
        "skills": [
            "Python",
            "FastAPI",
            "Docker"
        ]
    }}

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

