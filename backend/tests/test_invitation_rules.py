from app.services.candidate_email import extract_candidate_email
from app.services.eligibility import evaluate_eligibility


def decision(score, skills=None, email="candidate@example.com", email_status="valid", threshold=85):
    return evaluate_eligibility(score=score, resume_skills=skills or ["python", "fastapi"], mandatory_skills=["python"], require_all=True, email=email, email_status=email_status, threshold=threshold)


def test_threshold_is_inclusive():
    assert decision(84.99)["eligible"] is False
    assert decision(85)["eligible"] is True
    assert decision(85.01)["eligible"] is True


def test_all_mandatory_skills_and_missing_skill():
    assert decision(90, ["python", "fastapi"])["eligible"] is True
    assert decision(90, ["fastapi"])["eligible"] is False
    assert "python" in decision(90, ["fastapi"])["missing"]


def test_email_extraction_is_normalized_and_never_guessed():
    assert extract_candidate_email("Jane Doe\n JANE@Example.COM ").email == "jane@example.com"
    assert extract_candidate_email("Jane Doe").status == "missing"
    assert extract_candidate_email("Jane Doe\njane@bad").status == "invalid"
    assert extract_candidate_email("Jane Doe\na@example.com\nb@example.com").status == "ambiguous"
    assert decision(90, email=None, email_status="invalid")["status"] == "invalid_email"


def test_ats_failure_cannot_send():
    result = decision(None)
    assert result["eligible"] is False
    assert result["status"] == "ineligible"
