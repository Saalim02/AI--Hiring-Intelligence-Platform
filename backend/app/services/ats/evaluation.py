"""Deterministic candidate evaluation built around the existing ATS engine."""
import re
from typing import Iterable

from app.services.eligibility import normalize_skill


def clean_skills(skills: Iterable[str] | None) -> list[str]:
    return list(dict.fromkeys(skill.strip() for skill in (skills or []) if skill and skill.strip()))


def match_skill_sets(resume_skills: Iterable[str], required_skills: Iterable[str]) -> tuple[list[str], list[str]]:
    available = {normalize_skill(item) for item in resume_skills if item and item.strip()}
    required = clean_skills(required_skills)
    return ([skill for skill in required if normalize_skill(skill) in available],
            [skill for skill in required if normalize_skill(skill) not in available])


def skill_evidence(resume_text: str, skills: Iterable[str]) -> list[dict]:
    lines = [line.strip() for line in (resume_text or "").splitlines() if line.strip()]
    result = []
    for skill in clean_skills(skills):
        pattern = re.compile(r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])", re.IGNORECASE)
        line = next((candidate for candidate in lines if pattern.search(candidate)), None)
        result.append({"skill": skill, "status": "explicitly_evidenced", "snippet": line[:280] if line else None})
    return result


def build_score_breakdown(score: float) -> list[dict]:
    return [{"key": "semantic_similarity", "label": "Resume / job-description semantic similarity", "weight": 1.0, "weight_percent": 100, "contribution": round(score, 2), "explanation": "Cosine similarity between the resume and job-description embeddings."}]


def recommendation(*, score: float | None, threshold: float, missing_mandatory: list[str], email_status: str | None = None) -> dict:
    reasons = []
    if score is None:
        reasons.append("The ATS score is unavailable.")
    if score is not None and score < threshold:
        reasons.append(f"ATS score {score:.2f} is below the configured {threshold:.2f} threshold.")
    if missing_mandatory:
        reasons.append("Mandatory skills are not explicitly evidenced: " + ", ".join(missing_mandatory) + ".")
    if email_status and email_status != "valid":
        reasons.append(f"Candidate email is {email_status}.")
    if reasons:
        code = "manual_review" if score is None else "not_eligible"
        return {"label": "Manual review" if code == "manual_review" else "Not currently eligible", "code": code, "reasons": reasons}
    return {"label": "Strong match — shortlist", "code": "shortlist", "reasons": [f"ATS score meets the {threshold:.2f} threshold and all configured mandatory skills are evidenced."]}


def build_evaluation(*, resume, score: float | None, job_skills: list[str], mandatory_skills: list[str] | None = None, threshold: float = 85.0, require_all: bool = True, email_status: str | None = None) -> dict:
    resume_skills = clean_skills((resume.skills or "").split(","))
    mandatory = clean_skills(mandatory_skills)
    mandatory_norm = {normalize_skill(item) for item in mandatory}
    preferred = [skill for skill in clean_skills(job_skills) if normalize_skill(skill) not in mandatory_norm]
    matched_mandatory, missing_mandatory = match_skill_sets(resume_skills, mandatory)
    matched_preferred, missing_preferred = match_skill_sets(resume_skills, preferred)
    rule_missing = missing_mandatory if require_all else []
    strengths = [f"Explicitly evidenced skill: {skill}." for skill in matched_mandatory + matched_preferred]
    gaps = [f"Add clear resume evidence for {skill}; it was not found in the extracted skills section." for skill in missing_mandatory + missing_preferred]
    return {
        "candidate": {"id": resume.id, "filename": resume.filename, "name": resume.candidate_name, "email": resume.extracted_email},
        "overall_score": score,
        "score_breakdown": build_score_breakdown(score) if score is not None else [],
        "skills": {"matched_mandatory": matched_mandatory, "matched_preferred": matched_preferred, "missing_mandatory": missing_mandatory, "missing_preferred": missing_preferred, "ambiguous": [], "evidence": skill_evidence(resume.extracted_text or "", resume_skills)},
        "strengths": strengths or ["No configured job skill was explicitly evidenced in the extracted skills section."],
        "gaps": gaps,
        "recommendations": gaps[:5],
        "recommendation": recommendation(score=score, threshold=threshold, missing_mandatory=rule_missing, email_status=email_status),
        "evaluation_complete": score is not None,
        "rules": {"threshold": threshold, "require_all_mandatory_skills": require_all, "mandatory_skills_configured": mandatory},
    }
