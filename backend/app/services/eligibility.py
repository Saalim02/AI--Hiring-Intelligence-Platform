def normalize_skill(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").replace("_", " ").split())


def evaluate_eligibility(*, score: float | None, resume_skills: list[str], mandatory_skills: list[str], require_all: bool, email: str | None, email_status: str, threshold: float) -> dict:
    available = {normalize_skill(item) for item in resume_skills}
    matched = [skill for skill in mandatory_skills if normalize_skill(skill) in available]
    matched_norm = {normalize_skill(skill) for skill in matched}
    missing = [skill for skill in mandatory_skills if normalize_skill(skill) not in matched_norm]
    if score is None:
        return {"eligible": False, "reason": "ATS evaluation is unavailable", "matched": matched, "missing": missing, "status": "ineligible"}
    if email_status != "valid" or not email:
        return {"eligible": False, "reason": f"Candidate email is {email_status}", "matched": matched, "missing": missing, "status": "invalid_email"}
    if score < threshold:
        return {"eligible": False, "reason": f"ATS score {score:.2f} is below the {threshold:.2f} threshold", "matched": matched, "missing": missing, "status": "ineligible"}
    if require_all and missing:
        return {"eligible": False, "reason": "Missing mandatory skills: " + ", ".join(missing), "matched": matched, "missing": missing, "status": "ineligible"}
    return {"eligible": True, "reason": "Meets the configured ATS and mandatory-skill requirements", "matched": matched, "missing": missing, "status": "awaiting_approval"}
