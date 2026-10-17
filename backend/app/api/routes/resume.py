import os
import re
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.ai_errors import AIServiceError

from app.models.resume import Resume
from app.models.user import User

from app.utils.logger import logger

from app.services.pdf_parser import (
    extract_text_from_pdf
)

from app.services.skill_extractor import (
    extract_skills
)

from app.services.jd_skill_extractor import (
    extract_jd_skills
)

from app.services.section_parser import (
    extract_skills_section
)

from app.services.embeddings.embedding_service import (
    generate_embedding
)

from app.vectorstore.faiss_store import (
    add_embedding
)

from app.services.embeddings.semantic_search import (
    semantic_resume_search
)

from app.services.ats.ats_score import (
    calculate_ats_score
)

from app.services.ats.skill_gap import (
    analyze_skill_gap
)

from app.services.ats.ats_feedback import (
    generate_ats_feedback
)

from app.services.ats.candidate_ranker import (
    rank_candidates
)

from app.services.ranking.explainable_ranker import (
    generate_ranking_report
)
from app.services.ats.evaluation import build_evaluation
from app.services.candidate_email import extract_candidate_email

router = APIRouter()

UPLOAD_DIR = settings.UPLOAD_DIR
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_BYTES

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# =========================
# GET ALL RESUMES
# =========================

@router.get("/all")
def get_all_resumes(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("recruiter"))
):

    resumes = db.query(Resume).filter(Resume.owner_id == user.id).all()

    return resumes


# =========================
# SEMANTIC SEARCH
# =========================

@router.get("/search/")
def search_resumes(
    query: str = Query(..., min_length=2, max_length=500),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("recruiter"))
):

    matched_resume_ids = semantic_resume_search(
        query
    )

    resumes = db.query(Resume).filter(Resume.owner_id == user.id, Resume.id.in_(matched_resume_ids)).all()

    results = []

    for resume in resumes:

        results.append({

            "id": resume.id,

            "filename": resume.filename,

            "skills": resume.skills
        })

    return {

        "query": query,

        "matched_candidates": results
    }


# =========================
# GET RESUME BY ID
# =========================

@router.get("/{resume_id}")
def get_resume_by_id(

    resume_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("recruiter", "candidate"))

):

    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == user.id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume


# =========================
# UPLOAD RESUME
# =========================

@router.post("/upload")
async def upload_resume(

    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("recruiter", "candidate"))

):

    original_filename = file.filename or "resume.pdf"
    logger.info("Uploading resume PDF")

    if file.content_type != "application/pdf" or not original_filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are allowed")

    safe_stem = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.splitext(original_filename)[0])[:120] or "resume"
    stored_filename = f"{safe_stem}-{uuid.uuid4().hex[:12]}.pdf"

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_filename
    )

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Resume exceeds the 10 MB upload limit")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid PDF")
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    try:
        extracted_text = extract_text_from_pdf(file_path)

        # Extract ONLY skills section
        skills_section = extract_skills_section(extracted_text)

        # AI Resume Skill Extraction
        skills = extract_skills(skills_section)

        # Semantic embeddings
        embedding = generate_embedding(extracted_text)
    except AIServiceError:
        try:
            os.remove(file_path)
        except OSError:
            pass
        raise

    email_details = extract_candidate_email(extracted_text)
    resume = Resume(

        filename=original_filename,

        extracted_text=extracted_text,
        skills=", ".join(skills),
        candidate_name=email_details.candidate_name,
        extracted_email=email_details.email,
        owner_id=user.id
    )

    db.add(resume)

    db.commit()

    db.refresh(resume)

    # Store vector in FAISS

    add_embedding(
        embedding,
        resume.id
    )

    return {

        "message": "Resume uploaded successfully",

        "resume_id": resume.id,

        "skills": skills
    }


# =========================
# ATS SCORE
# =========================

@router.post("/ats-score/{resume_id}")
def ats_score(

    resume_id: int,

    job_description: str = Query(..., min_length=10, max_length=20000),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("recruiter"))

):

    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == user.id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Semantic ATS score

    score = calculate_ats_score(

        resume.extracted_text,

        job_description
    )

    # Extract JD skills using dedicated JD extractor

    jd_skills = extract_jd_skills(
        job_description
    )
    evaluation = build_evaluation(resume=resume, score=score, job_skills=jd_skills)

    # AI recruiter feedback

    feedback = generate_ats_feedback(

        ats_score=score,

        matched_skills=evaluation["skills"]["matched_preferred"],

        missing_skills=evaluation["skills"]["missing_preferred"],

        job_description=job_description
    )

    return {**evaluation, "resume_id": resume.id,

    "resume_id":
    resume.id,

    "filename":
    resume.filename,

    "overall_score":
    score,

    "matched_skills": evaluation["skills"]["matched_preferred"],

    "missing_skills": evaluation["skills"]["missing_preferred"],

    "recommendation": evaluation["recommendation"]["label"],

    "ai_feedback":
    feedback,

    "score_breakdown":
    evaluation["score_breakdown"],

    "strengths":
    evaluation["strengths"],

    "improvements":
    evaluation["recommendations"]
}
# =========================
# CANDIDATE RANKING
# =========================

@router.post("/rank-candidates")
def rank_all_candidates(

    job_description: str = Query(..., min_length=10, max_length=20000),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("recruiter"))

):

    resumes = db.query(Resume).filter(Resume.owner_id == user.id).all()

    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")

    rankings = rank_candidates(

        resumes,

        job_description
    )

    return {

        "total_candidates": len(rankings),

        "rankings": rankings
    }
