import json

from app.core.ai_errors import AIServiceInvalidResponse
from app.core.openai_client import create_chat_completion


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

        skills = parsed_json.get("skills")
        if not isinstance(skills, list):
            raise ValueError("skills must be a list")
        return [str(skill) for skill in skills]

    except Exception:
        raise AIServiceInvalidResponse("The AI service returned an invalid skill extraction result")

