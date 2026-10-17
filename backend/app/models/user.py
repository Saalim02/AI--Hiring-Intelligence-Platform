from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        index=True
    )

    email = Column(
        String,
        unique=True,
        index=True
    )

    hashed_password = Column(String)

    role = Column(String(20), nullable=False, default="recruiter", server_default="recruiter")

    resumes = relationship("Resume", back_populates="owner")
    screening_sessions = relationship("ScreeningSession", back_populates="recruiter", cascade="all, delete-orphan")
