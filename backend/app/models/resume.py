from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Resume(Base):

    __tablename__ = "resumes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(String)

    extracted_text = Column(Text)

    skills = Column(Text)

    candidate_name = Column(String(200), nullable=True)
    extracted_email = Column(String(320), nullable=True, index=True)

    # Nullable by design: existing rows cannot be safely attributed to a user.
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    owner = relationship("User", back_populates="resumes")
    invitations = relationship("Invitation", back_populates="resume")
