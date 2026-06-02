import os

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.resume import Resume

from app.utils.logger import logger

from app.services.pdf_parser import (
    extract_text_from_pdf
)

from app.services.skill_extractor import (
    extract_skills
)

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

@router.get("/all")
def get_all_resumes(
    db: Session = Depends(get_db)
):

    resumes = db.query(Resume).all()

    return resumes

@router.get("/{resume_id}")
def get_resume_by_id(
    resume_id: int,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    if not resume:

        return {
            "message": "Resume not found"
        }

    return resume

@router.post("/upload")
async def upload_resume(
    
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logger.info(
    f"Uploading file: {file.filename}"
)
    
    if not file.filename.endswith(".pdf"):
        return {
            "message": "Only PDF files are allowed"
    }

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        buffer.write(
            await file.read()
        )

    extracted_text = extract_text_from_pdf(
        file_path
    )

    skills = extract_skills(
        extracted_text
    )

    resume = Resume(
        filename=file.filename,
        extracted_text=extracted_text,
        skills=", ".join(skills)
    )

    db.add(resume)

    db.commit()

    db.refresh(resume)

    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "skills": skills
    }