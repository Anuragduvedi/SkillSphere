import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Candidate, Resume, Skill, Job, ResumeAnalysis
from app.schemas.schemas import OCRExtractResponse, CandidateProfileUpdate, AnalysisResponse, AnalyzeRequest
from app.core.config import settings
from app.core.deps import get_current_user, require_roles
from app.services.ocr_service import OCRService
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/resume", tags=["Resume & OCR"])

@router.post("/upload", response_model=OCRExtractResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["job_seeker"])),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    filename = file.filename or "resume"
    ext = os.path.splitext(filename.lower())[1]
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{ext}'. Allowed extensions are: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 2. Read content and validate size (Max 10MB)
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of 10MB. Uploaded size: {round(len(content) / (1024*1024), 2)}MB"
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # 3. Save original file securely
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store resume on server: {str(e)}"
        )

    # 4. Execute OCR text extraction
    raw_text, processing_status, message = OCRService.extract_text(content, filename)

    # 5. Parse structured fields
    parsed_fields = OCRService.parse_resume_fields(raw_text)

    # 6. Lookup candidate
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
    if not candidate:
        candidate = Candidate(user_id=current_user.user_id)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    # 7. Create/record Resume
    resume = Resume(
        candidate_id=candidate.candidate_id,
        file_name=filename,
        file_path=file_path,
        file_type=ext,
        processing_status=processing_status,
        extracted_text=raw_text
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Pre-populate candidate basic info if currently empty
    if not candidate.phone and parsed_fields["phone"]:
        candidate.phone = parsed_fields["phone"]
    if not candidate.education and parsed_fields["education"]:
        candidate.education = parsed_fields["education"]
    if not candidate.experience and parsed_fields["experience"]:
        candidate.experience = parsed_fields["experience"]
    
    # Associate extracted skills with candidate
    if parsed_fields["skills"]:
        for s_name in parsed_fields["skills"]:
            existing_skill = db.query(Skill).filter(Skill.skill_name.ilike(s_name)).first()
            if not existing_skill:
                existing_skill = Skill(skill_name=s_name)
                db.add(existing_skill)
                db.commit()
                db.refresh(existing_skill)
            if existing_skill not in candidate.skills:
                candidate.skills.append(existing_skill)
    
    db.commit()

    return {
        "resume_id": resume.resume_id,
        "file_name": filename,
        "extracted_name": parsed_fields["name"],
        "extracted_email": parsed_fields["email"] or current_user.email,
        "extracted_phone": parsed_fields["phone"],
        "extracted_education": parsed_fields["education"],
        "extracted_experience": parsed_fields["experience"],
        "extracted_skills": parsed_fields["skills"],
        "raw_text": raw_text,
        "status": processing_status,
        "message": message
    }

@router.get("/profile")
def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    resumes = db.query(Resume).filter(Resume.candidate_id == candidate.candidate_id).order_by(Resume.upload_date.desc()).all()
    
    return {
        "candidate_id": candidate.candidate_id,
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "education": candidate.education,
        "experience": candidate.experience,
        "profile_details": candidate.profile_details,
        "skills": [s.skill_name for s in candidate.skills],
        "resumes": [
            {
                "resume_id": r.resume_id,
                "file_name": r.file_name,
                "file_type": r.file_type,
                "upload_date": r.upload_date,
                "processing_status": r.processing_status,
                "has_extracted_text": bool(r.extracted_text)
            } for r in resumes
        ]
    }

@router.put("/update-profile")
def update_candidate_profile(
    profile_data: CandidateProfileUpdate,
    current_user: User = Depends(require_roles(["job_seeker"])),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
    if not candidate:
        candidate = Candidate(user_id=current_user.user_id)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    if profile_data.name:
        current_user.name = profile_data.name.strip()
    if profile_data.phone is not None:
        candidate.phone = profile_data.phone.strip()
    if profile_data.location is not None:
        candidate.location = profile_data.location.strip()
    if profile_data.education is not None:
        candidate.education = profile_data.education.strip()
    if profile_data.experience is not None:
        candidate.experience = profile_data.experience.strip()
    if profile_data.profile_details is not None:
        candidate.profile_details = profile_data.profile_details.strip()

    # Update skills
    if profile_data.skills is not None:
        candidate.skills.clear()
        for s_name in profile_data.skills:
            clean_s = s_name.strip()
            if not clean_s:
                continue
            skill = db.query(Skill).filter(Skill.skill_name.ilike(clean_s)).first()
            if not skill:
                skill = Skill(skill_name=clean_s)
                db.add(skill)
                db.commit()
                db.refresh(skill)
            candidate.skills.append(skill)

    db.commit()
    return {"message": "Profile updated successfully.", "status": "success"}

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_resume_against_job(
    req: AnalyzeRequest,
    current_user: User = Depends(require_roles(["job_seeker"])),
    db: Session = Depends(get_db)
):
    # 1. Fetch Candidate
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    # 2. Fetch Job
    job = db.query(Job).filter(Job.job_id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 3. Determine Candidate Resume
    resume = None
    if req.resume_id:
        resume = db.query(Resume).filter(Resume.resume_id == req.resume_id, Resume.candidate_id == candidate.candidate_id).first()
    if not resume:
        resume = db.query(Resume).filter(Resume.candidate_id == candidate.candidate_id).order_by(Resume.upload_date.desc()).first()
    
    if not resume:
        # If no uploaded file yet, synthesize a default resume record so candidate can still test match analysis against profile skills!
        resume = Resume(
            candidate_id=candidate.candidate_id,
            file_name="profile_skills_snapshot.pdf",
            file_path="virtual_profile",
            processing_status="Completed",
            extracted_text=f"Candidate Skills: {', '.join([s.skill_name for s in candidate.skills])}"
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

    candidate_skill_names = [s.skill_name for s in candidate.skills]
    job_skill_names = [s.skill_name for s in job.skills]

    # 4. Run Matching Algorithm
    match_result = MatchingService.calculate_match(candidate_skill_names, job_skill_names)

    # 5. Persist Analysis in DB
    analysis = ResumeAnalysis(
        resume_id=resume.resume_id,
        job_id=job.job_id,
        match_score=match_result["match_score"],
        matched_skills=",".join(match_result["matched_skills"]),
        missing_skills=",".join(match_result["missing_skills"]),
        recommendations=match_result["recommendations"]
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    company_name = job.recruiter.company.company_name if job.recruiter and job.recruiter.company else "Company"

    return {
        "analysis_id": analysis.analysis_id,
        "job_id": job.job_id,
        "job_title": job.title,
        "company_name": company_name,
        "match_score": match_result["match_score"],
        "matched_skills": match_result["matched_skills"],
        "missing_skills": match_result["missing_skills"],
        "recommendations": match_result["recommendations"],
        "analysis_date": analysis.analysis_date
    }

@router.get("/download/{resume_id}")
def download_resume_file(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Authorization: Owner candidate, or recruiter/admin
    if current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
        if not candidate or candidate.candidate_id != resume.candidate_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to resume")

    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume physical file not found on disk")

    return FileResponse(
        resume.file_path,
        media_type="application/octet-stream",
        filename=resume.file_name
    )
