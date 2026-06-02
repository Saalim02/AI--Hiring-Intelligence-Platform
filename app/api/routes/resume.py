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

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# =========================
# GET ALL RESUMES
# =========================

@router.get("/all")
def get_all_resumes(
    db: Session = Depends(get_db)
):

    resumes = db.query(Resume).all()

    return resumes


# =========================
# SEMANTIC SEARCH
# =========================

@router.get("/search/")
def search_resumes(
    query: str,
    db: Session = Depends(get_db)
):

    matched_resume_ids = semantic_resume_search(
        query
    )

    resumes = db.query(Resume).filter(
        Resume.id.in_(matched_resume_ids)
    ).all()

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


# =========================
# UPLOAD RESUME
# =========================

@router.post("/upload")
async def upload_resume(

    file: UploadFile = File(...),

    db: Session = Depends(get_db)

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

    # Extract ONLY skills section

    skills_section = extract_skills_section(
        extracted_text
    )

    # AI Resume Skill Extraction

    skills = extract_skills(
        skills_section
    )
    
    print("RESUME SKILLS:", skills)

    # Semantic embeddings

    embedding = generate_embedding(
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

    job_description: str,

    db: Session = Depends(get_db)

):

    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    if not resume:

        return {
            "message": "Resume not found"
        }

    # Semantic ATS score

    score = calculate_ats_score(

        resume.extracted_text,

        job_description
    )

    # Extract JD skills using dedicated JD extractor

    jd_skills = extract_jd_skills(
        job_description
    )
    print("JD SKILLS:", jd_skills)
    

    # Resume stored skills

    resume_skills = [

        skill.strip()

        for skill in resume.skills.split(",")
    ]

    # Skill gap analysis

    matched_skills, missing_skills = analyze_skill_gap(

        resume_skills,

        jd_skills
    )

    # Basic recommendation

    if score >= 80:

        recommendation = (
            "Strong candidate match"
        )

    elif score >= 60:

        recommendation = (
            "Moderate candidate match"
        )

    else:

        recommendation = (
            "Low candidate match"
        )

    # AI recruiter feedback

    feedback = generate_ats_feedback(

        ats_score=score,

        matched_skills=matched_skills,

        missing_skills=missing_skills,

        job_description=job_description
    )

    return {

        "resume_id": resume.id,

        "filename": resume.filename,

        "ats_score": score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "recommendation": recommendation,

        "ai_feedback": feedback
    }
