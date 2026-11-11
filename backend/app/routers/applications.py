from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Application, Job, Candidate, Resume, User, Recruiter, ResumeAnalysis
from app.schemas.schemas import ApplicationCreate, ApplicationStatusUpdate, ApplicationResponse
from app.core.deps import get_current_user, require_roles
from app.services.matching_service import MatchingService

router = APIRouter(prefix="", tags=["Applications"])

@router.post("/jobs/{job_id}/apply", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    job_id: int,
    app_in: Optional[ApplicationCreate] = None,
    current_user: User = Depends(require_roles(["job_seeker"])),
    db: Session = Depends(get_db)
):
    # 1. Fetch Candidate
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Candidate profile not initialized")

    # 2. Check Job status
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found")
    if job.status != "active":
        raise HTTPException(status_code=400, detail="This job opening is closed and no longer accepting applications.")

    # 3. Duplicate Application Check
    existing_application = db.query(Application).filter(
        Application.job_id == job_id,
        Application.candidate_id == candidate.candidate_id
    ).first()
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted an application for this position. Duplicate applications are not permitted."
        )

    # 4. Resolve Resume
    resume_id = app_in.resume_id if app_in and app_in.resume_id else None
    if not resume_id:
        latest_resume = db.query(Resume).filter(Resume.candidate_id == candidate.candidate_id).order_by(Resume.upload_date.desc()).first()
        if latest_resume:
            resume_id = latest_resume.resume_id
        else:
            # Create a virtual resume record for profile application
            virtual_res = Resume(
                candidate_id=candidate.candidate_id,
                file_name="Candidate_Profile.pdf",
                file_path="virtual_profile",
                processing_status="Completed",
                extracted_text=f"Skills: {', '.join([s.skill_name for s in candidate.skills])}"
            )
            db.add(virtual_res)
            db.commit()
            db.refresh(virtual_res)
            resume_id = virtual_res.resume_id

    # 5. Create Application
    cover_note = app_in.cover_note if app_in else ""
    db_app = Application(
        job_id=job.job_id,
        candidate_id=candidate.candidate_id,
        resume_id=resume_id,
        status="Applied",
        cover_note=cover_note
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)

    # 6. Perform and store resume-to-job analysis
    candidate_skills = [s.skill_name for s in candidate.skills]
    job_skills = [s.skill_name for s in job.skills]
    match_data = MatchingService.calculate_match(candidate_skills, job_skills)
    
    analysis = ResumeAnalysis(
        resume_id=resume_id,
        job_id=job.job_id,
        match_score=match_data["match_score"],
        matched_skills=",".join(match_data["matched_skills"]),
        missing_skills=",".join(match_data["missing_skills"]),
        recommendations=match_data["recommendations"]
    )
    db.add(analysis)
    db.commit()

    company_name = job.recruiter.company.company_name if job.recruiter and job.recruiter.company else "Company"

    return {
        "application_id": db_app.application_id,
        "job_id": job.job_id,
        "candidate_id": candidate.candidate_id,
        "resume_id": resume_id,
        "application_date": db_app.application_date,
        "status": db_app.status,
        "cover_note": db_app.cover_note,
        "job_title": job.title,
        "company_name": company_name,
        "location": job.location,
        "candidate_name": current_user.name,
        "candidate_email": current_user.email,
        "candidate_phone": candidate.phone,
        "candidate_skills": candidate_skills,
        "candidate_experience": candidate.experience,
        "resume_file_path": db_app.resume.file_name if db_app.resume else None,
        "match_score": match_data["match_score"]
    }

@router.get("/applications", response_model=List[ApplicationResponse])
def get_user_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
        if not candidate:
            return []
        apps = db.query(Application).filter(Application.candidate_id == candidate.candidate_id).order_by(Application.application_date.desc()).all()
    elif current_user.role == "recruiter":
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
        if not recruiter:
            return []
        recruiter_job_ids = [j.job_id for j in recruiter.jobs]
        apps = db.query(Application).filter(Application.job_id.in_(recruiter_job_ids)).order_by(Application.application_date.desc()).all()
    else:  # Admin
        apps = db.query(Application).order_by(Application.application_date.desc()).all()

    results = []
    for a in apps:
        comp_name = a.job.recruiter.company.company_name if a.job.recruiter and a.job.recruiter.company else "Partner Company"
        
        # Calculate or lookup match score
        c_skills = [s.skill_name for s in a.candidate.skills] if a.candidate else []
        j_skills = [s.skill_name for s in a.job.skills] if a.job else []
        match_info = MatchingService.calculate_match(c_skills, j_skills)

        results.append({
            "application_id": a.application_id,
            "job_id": a.job_id,
            "candidate_id": a.candidate_id,
            "resume_id": a.resume_id,
            "application_date": a.application_date,
            "status": a.status,
            "cover_note": a.cover_note,
            "job_title": a.job.title if a.job else "Unknown Role",
            "company_name": comp_name,
            "location": a.job.location if a.job else "N/A",
            "candidate_name": a.candidate.user.name if a.candidate and a.candidate.user else "Candidate",
            "candidate_email": a.candidate.user.email if a.candidate and a.candidate.user else "",
            "candidate_phone": a.candidate.phone if a.candidate else "",
            "candidate_skills": c_skills,
            "candidate_experience": a.candidate.experience if a.candidate else "",
            "resume_file_path": a.resume.file_name if a.resume else None,
            "match_score": match_info["match_score"]
        })

    return results

@router.put("/applications/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    app_record = db.query(Application).filter(Application.application_id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "recruiter":
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
        if not recruiter or app_record.job.recruiter_id != recruiter.recruiter_id:
            raise HTTPException(status_code=403, detail="Unauthorized to modify applications for other recruiters' jobs")

    app_record.status = status_update.status
    db.commit()
    db.refresh(app_record)

    comp_name = app_record.job.recruiter.company.company_name if app_record.job.recruiter and app_record.job.recruiter.company else "Company"
    c_skills = [s.skill_name for s in app_record.candidate.skills] if app_record.candidate else []
    j_skills = [s.skill_name for s in app_record.job.skills] if app_record.job else []
    match_info = MatchingService.calculate_match(c_skills, j_skills)

    return {
        "application_id": app_record.application_id,
        "job_id": app_record.job_id,
        "candidate_id": app_record.candidate_id,
        "resume_id": app_record.resume_id,
        "application_date": app_record.application_date,
        "status": app_record.status,
        "cover_note": app_record.cover_note,
        "job_title": app_record.job.title if app_record.job else "Role",
        "company_name": comp_name,
        "location": app_record.job.location if app_record.job else "",
        "candidate_name": app_record.candidate.user.name if app_record.candidate and app_record.candidate.user else "Candidate",
        "candidate_email": app_record.candidate.user.email if app_record.candidate and app_record.candidate.user else "",
        "candidate_phone": app_record.candidate.phone if app_record.candidate else "",
        "candidate_skills": c_skills,
        "candidate_experience": app_record.candidate.experience if app_record.candidate else "",
        "resume_file_path": app_record.resume.file_name if app_record.resume else None,
        "match_score": match_info["match_score"]
    }

@router.post("/applications/{application_id}/withdraw")
def withdraw_application(
    application_id: int,
    current_user: User = Depends(require_roles(["job_seeker"])),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Candidate not found")

    app_record = db.query(Application).filter(
        Application.application_id == application_id,
        Application.candidate_id == candidate.candidate_id
    ).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found or unauthorized")

    if app_record.status not in ["Applied", "Under Review"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot withdraw application currently in '{app_record.status}' status."
        )

    db.delete(app_record)
    db.commit()
    return {"message": "Application withdrawn successfully", "application_id": application_id}
