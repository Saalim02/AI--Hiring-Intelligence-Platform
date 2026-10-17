from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class InvitationEvaluationRequest(BaseModel):
    job_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=10, max_length=20000)
    resume_ids: list[int] = Field(min_length=1, max_length=50)
    minimum_ats_score: float = Field(default=85, ge=0, le=100)
    mandatory_skills: list[str] = Field(default_factory=list, max_length=100)
    require_all_mandatory_skills: bool = True
    automatic_invitations_enabled: bool = False

    @field_validator("mandatory_skills")
    @classmethod
    def normalize_skills(cls, skills: list[str]) -> list[str]:
        return list(dict.fromkeys(skill.strip().lower() for skill in skills if skill.strip()))


class SendBatchRequest(BaseModel):
    confirm: bool = False
    automatic: bool = False


class AutomationRequest(BaseModel):
    enabled: bool


class InvitationResponse(BaseModel):
    id: int
    resume_id: int
    candidate_name: str | None
    recipient_email: str | None
    score_snapshot: float | None
    matched_skills: list[str]
    missing_skills: list[str]
    eligible: bool
    eligibility_reason: str
    status: str
    failure_reason: str | None = None
    provider_message_id: str | None = None
    attempts: int
    sent_at: datetime | None = None

    class Config:
        from_attributes = True


class ScreeningSessionResponse(BaseModel):
    id: int
    job_title: str
    job_description: str
    minimum_ats_score: float
    mandatory_skills: list[str]
    require_all_mandatory_skills: bool
    automatic_invitations_enabled: bool
    first_batch_approved: bool
    invitations: list[InvitationResponse]

    class Config:
        from_attributes = True
