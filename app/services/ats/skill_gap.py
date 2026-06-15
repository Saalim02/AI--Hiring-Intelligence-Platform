def analyze_skill_gap(

    resume_skills,
    jd_skills
):

    resume_skills = set(

        skill.lower().strip()

        for skill in resume_skills
    )

    jd_skills = set(

        skill.lower().strip()

        for skill in jd_skills
    )

    matched_skills = sorted(
        list(
            resume_skills.intersection(
                jd_skills
            )
        )
    )

    missing_skills = sorted(
        list(
            jd_skills.difference(
                resume_skills
            )
        )
    )

    return (
        matched_skills,
        missing_skills
    )

