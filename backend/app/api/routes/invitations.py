from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.invitation import Invitation, ScreeningSession
from app.models.resume import Resume
from app.models.user import User
from app.schemas.invitation_schema import AutomationRequest, InvitationEvaluationRequest, ScreeningSessionResponse, SendBatchRequest
from app.services.ats.ats_score import calculate_ats_score
from app.services.candidate_email import extract_candidate_email
from app.services.eligibility import evaluate_eligibility
from app.services.email_service import EmailDeliveryError, send_invitation

router = APIRouter()


def _session(db: Session, session_id: int, user: User) -> ScreeningSession:
    item = db.query(ScreeningSession).filter(ScreeningSession.id == session_id, ScreeningSession.recruiter_id == user.id).first()
    if not item:
        raise HTTPException(404, "Screening session not found")
    return item


@router.post("/evaluate", response_model=ScreeningSessionResponse)
@router.post("/preview", response_model=ScreeningSessionResponse, include_in_schema=True)
def evaluate(request: InvitationEvaluationRequest, db: Session = Depends(get_db), user: User = Depends(require_role("recruiter"))):
    resumes = db.query(Resume).filter(Resume.owner_id == user.id, Resume.id.in_(request.resume_ids)).all()
    if len(resumes) != len(set(request.resume_ids)):
        raise HTTPException(404, "One or more resumes were not found in your library")
    session = ScreeningSession(recruiter_id=user.id, job_title=request.job_title, job_description=request.job_description, minimum_ats_score=request.minimum_ats_score, mandatory_skills=request.mandatory_skills, require_all_mandatory_skills=request.require_all_mandatory_skills)
    db.add(session)
    db.flush()
    for resume in resumes:
        score = None
        try:
            score = calculate_ats_score(resume.extracted_text or "", request.job_description)
        except Exception:
            pass
        extraction = extract_candidate_email(resume.extracted_text or "")
        decision = evaluate_eligibility(score=score, resume_skills=[s.strip() for s in (resume.skills or "").split(",") if s.strip()], mandatory_skills=request.mandatory_skills, require_all=request.require_all_mandatory_skills, email=extraction.email, email_status=extraction.status, threshold=request.minimum_ats_score)
        db.add(Invitation(session=session, resume=resume, recipient_email=extraction.email, candidate_name=resume.candidate_name or extraction.candidate_name, score_snapshot=score, matched_skills=decision["matched"], missing_skills=decision["missing"], eligible=decision["eligible"], eligibility_reason=decision["reason"], status=decision["status"]))
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=ScreeningSessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("recruiter"))):
    return _session(db, session_id, user)


@router.post("/sessions/{session_id}/send", response_model=ScreeningSessionResponse)
def send_batch(session_id: int, request: SendBatchRequest, db: Session = Depends(get_db), user: User = Depends(require_role("recruiter"))):
    session = _session(db, session_id, user)
    if not request.confirm:
        raise HTTPException(400, "Explicit confirmation is required before sending")
    if request.automatic and not session.first_batch_approved:
        raise HTTPException(409, "The first batch must be approved before automatic invitations are enabled")
    eligible = [item for item in session.invitations if item.eligible and item.status in {"awaiting_approval", "failed"}]
    if len(eligible) > settings.MAX_INVITATION_BATCH_SIZE:
        raise HTTPException(413, f"Batch exceeds the {settings.MAX_INVITATION_BATCH_SIZE} recipient limit")
    session.first_batch_approved = True
    session.updated_at = now = datetime.now(timezone.utc)
    for item in eligible:
        item.approved_at = now
        item.status = "queued"
        item.queued_at = now
        item.attempts += 1
        try:
            item.provider_message_id = send_invitation(recipient=item.recipient_email, job_title=session.job_title, candidate_name=item.candidate_name, recruiter_name=user.username, recruiter_contact=settings.RECRUITER_CONTACT_EMAIL or user.email)
            item.status = "sent"
            item.sent_at = datetime.now(timezone.utc)
            item.failure_reason = None
        except EmailDeliveryError as exc:
            item.status = "failed"
            item.failure_reason = str(exc)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/sessions/{session_id}/automation", response_model=ScreeningSessionResponse)
def set_automation(session_id: int, request: AutomationRequest, db: Session = Depends(get_db), user: User = Depends(require_role("recruiter"))):
    session = _session(db, session_id, user)
    if request.enabled and not session.first_batch_approved:
        raise HTTPException(409, "Approve and send the first batch before enabling automatic invitations")
    session.automatic_invitations_enabled = request.enabled
    db.commit()
    db.refresh(session)
    return session


@router.post("/sessions/{session_id}/automatic-send", response_model=ScreeningSessionResponse)
def automatic_send(session_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("recruiter"))):
    session = _session(db, session_id, user)
    if not session.automatic_invitations_enabled or not session.first_batch_approved:
        raise HTTPException(409, "Automatic invitations are not enabled and approved for this session")
    return send_batch(session_id, SendBatchRequest(confirm=True, automatic=True), db, user)


@router.post("/sessions/{session_id}/retry/{invitation_id}", response_model=ScreeningSessionResponse)
def retry_failed(session_id: int, invitation_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("recruiter"))):
    session = _session(db, session_id, user)
    invitation = next((item for item in session.invitations if item.id == invitation_id), None)
    if not invitation or invitation.status != "failed":
        raise HTTPException(400, "Only failed invitations can be retried")
    invitation.status = "awaiting_approval"
    invitation.failure_reason = None
    db.commit()
    return session
