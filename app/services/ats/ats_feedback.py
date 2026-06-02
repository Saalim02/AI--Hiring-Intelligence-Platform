from app.core.openai_client import (
    client
)


def generate_ats_feedback(

    ats_score,
    matched_skills,
    missing_skills,
    job_description

):

    prompt = f"""
    You are an intelligent ATS recruiter assistant.

    Analyze this candidate professionally.

    ATS Score:
    {ats_score}

    Matched Skills:
    {matched_skills}

    Missing Skills:
    {missing_skills}

    Job Description:
    {job_description}

    Explain:
    1. Why the ATS score is low/moderate/high
    2. Candidate strengths
    3. Missing skills
    4. Improvement suggestions
    5. Hiring recommendation

    Keep response concise but professional.
    """

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    return response.choices[0].message.content