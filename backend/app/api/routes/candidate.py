from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.resume import Resume
from app.models.user import User
from app.schemas.auth_schema import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def candidate_profile(user: User = Depends(require_role("candidate"))):
    return user

@router.get("/resumes")
def candidate_resumes(db: Session = Depends(get_db), user: User = Depends(require_role("candidate"))):
    return db.query(Resume).filter(Resume.owner_id == user.id).all()
