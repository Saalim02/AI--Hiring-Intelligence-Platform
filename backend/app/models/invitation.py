from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    job_description = Column(Text, nullable=False)
    minimum_ats_score = Column(Float, nullable=False, default=85.0)
    mandatory_skills = Column(JSON, nullable=False, default=list)
    require_all_mandatory_skills = Column(Boolean, nullable=False, default=True)
    automatic_invitations_enabled = Column(Boolean, nullable=False, default=False)
    first_batch_approved = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    recruiter = relationship("User", back_populates="screening_sessions")
    invitations = relationship("Invitation", back_populates="session", cascade="all, delete-orphan")


class Invitation(Base):
    __tablename__ = "invitations"
    __table_args__ = (UniqueConstraint("session_id", "resume_id", name="uq_invitations_session_resume"),)

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_email = Column(String(320), nullable=True)
    candidate_name = Column(String(200), nullable=True)
    score_snapshot = Column(Float, nullable=True)
    matched_skills = Column(JSON, nullable=False, default=list)
    missing_skills = Column(JSON, nullable=False, default=list)
    eligible = Column(Boolean, nullable=False, default=False)
    eligibility_reason = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="ineligible", index=True)
    provider_message_id = Column(String(255), nullable=True)
    failure_reason = Column(Text, nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    queued_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    session = relationship("ScreeningSession", back_populates="invitations")
    resume = relationship("Resume", back_populates="invitations")
