def generate_ranking_report(
    ats_score,
    matched_skills,
    missing_skills
):

    strengths = []

    improvements = []

    for skill in matched_skills:

        strengths.append(
            f"Strong {skill} experience"
        )

    for skill in missing_skills:

        improvements.append(
            f"Consider learning {skill}"
        )

    skills_score = min(
        len(matched_skills) * 5,
        40
    )

    semantic_score = max(
        round(
            ats_score - skills_score,
            2
        ),
        0
    )

    return {

        "score_breakdown": {

            "skills_match":
            skills_score,

            "semantic_match":
            semantic_score
        },

        "strengths":
        strengths,

        "improvements":
        improvements
    }