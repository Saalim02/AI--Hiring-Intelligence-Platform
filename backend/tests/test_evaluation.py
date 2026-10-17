from types import SimpleNamespace

from app.services.ats.evaluation import build_evaluation, build_score_breakdown


def resume(skills="Python, FastAPI", text="SKILLS\nPython, FastAPI\nExperience: built APIs"):
    return SimpleNamespace(id=7, filename="jane.pdf", candidate_name="Jane Doe", extracted_email="jane@example.com", skills=skills, extracted_text=text)


def test_score_breakdown_reconciles_to_real_single_factor():
    factors = build_score_breakdown(72.34)
    assert factors[0]["weight_percent"] == 100
    assert factors[0]["contribution"] == 72.34


def test_mandatory_and_preferred_evidence_are_separate():
    result = build_evaluation(resume=resume(), score=91, job_skills=["python", "fastapi", "docker"], mandatory_skills=["python"])
    assert result["skills"]["matched_mandatory"] == ["python"]
    assert result["skills"]["matched_preferred"] == ["fastapi"]
    assert result["skills"]["missing_preferred"] == ["docker"]
    assert result["recommendation"]["code"] == "shortlist"


def test_missing_mandatory_blocks_recommendation_without_claiming_performance():
    result = build_evaluation(resume=resume("FastAPI"), score=95, job_skills=["python", "fastapi"], mandatory_skills=["python"])
    assert result["skills"]["missing_mandatory"] == ["python"]
    assert result["recommendation"]["code"] == "not_eligible"
    assert "not explicitly evidenced" in result["recommendation"]["reasons"][0]


def test_unavailable_score_requires_manual_review():
    result = build_evaluation(resume=resume(), score=None, job_skills=["python"])
    assert result["recommendation"]["code"] == "manual_review"
    assert result["evaluation_complete"] is False
