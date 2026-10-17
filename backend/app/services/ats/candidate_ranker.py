from app.services.ats.ats_score import (
    calculate_ats_score
)

from app.services.jd_skill_extractor import (
    extract_jd_skills
)

from app.services.ats.skill_gap import (
    analyze_skill_gap
)
from app.services.ats.evaluation import build_evaluation


def rank_candidates(
    resumes,
    job_description
):

    rankings = []

    jd_skills = extract_jd_skills(
        job_description
    )

    for resume in resumes:

        score = calculate_ats_score(
            resume.extracted_text,
            job_description
        )

        resume_skills = [

            skill.strip()

            for skill in resume.skills.split(",")
        ]

        evaluation = build_evaluation(resume=resume, score=score, job_skills=jd_skills)

        rankings.append({

            "resume_id":
            resume.id,

            "filename":
            resume.filename,

            "ats_score":
            score,

            "matched_skills": evaluation["skills"]["matched_preferred"],
            "missing_skills": evaluation["skills"]["missing_preferred"],
            "evaluation": evaluation,

            "total_matched_skills":
            len(evaluation["skills"]["matched_preferred"])
        })

    rankings.sort(

        key=lambda x: x["ats_score"],

        reverse=True
    )

    for idx, candidate in enumerate(

        rankings,

        start=1
    ):

        candidate["rank"] = idx

    return rankings
