from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.models import Job, User, Recruiter, Skill, Candidate, Application, ResumeAnalysis
from app.schemas.schemas import JobCreate, JobUpdate, JobResponse
from app.core.deps import get_current_user, get_optional_user, require_roles
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobResponse])
def list_jobs(
    keyword: Optional[str] = Query(None, description="Search in job title or description"),
    location: Optional[str] = Query(None, description="Filter by location"),
    experience: Optional[str] = Query(None, description="Filter by experience requirement"),
    job_type: Optional[str] = Query(None, description="Filter by job type (Full-time, Remote, etc.)"),
    skill: Optional[str] = Query(None, description="Filter by skill requirement"),
    status: Optional[str] = Query("active", description="Filter by job status (active/closed)"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    query = db.query(Job)

    status_val = status if isinstance(status, str) else "active"
    if status_val and status_val != "all":
        query = query.filter(Job.status == status_val)

    if isinstance(keyword, str) and keyword.strip():
        term = f"%{keyword.strip()}%"
        query = query.filter(or_(Job.title.ilike(term), Job.description.ilike(term)))

    if isinstance(location, str) and location.strip():
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

    if isinstance(experience, str) and experience.strip():
        query = query.filter(Job.experience.ilike(f"%{experience.strip()}%"))

    if isinstance(job_type, str) and job_type.strip():
        query = query.filter(Job.job_type.ilike(f"%{job_type.strip()}%"))

    if isinstance(skill, str) and skill.strip():
        query = query.join(Job.skills).filter(Skill.skill_name.ilike(f"%{skill.strip()}%"))

    jobs = query.order_by(Job.created_date.desc()).all()

    # Pre-fetch candidate skills & applied jobs if candidate is logged in
    candidate_skills = []
    applied_job_ids = set()
    if current_user and current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
        if candidate:
            candidate_skills = [s.skill_name for s in candidate.skills]
            user_apps = db.query(Application.job_id).filter(Application.candidate_id == candidate.candidate_id).all()
            applied_job_ids = {a[0] for a in user_apps}

    results = []
    for j in jobs:
        comp_name = j.recruiter.company.company_name if j.recruiter and j.recruiter.company else "SkillSphere Partner"
        req_skills = [s.skill_name for s in j.skills]
        
        # Calculate dynamic match score
        m_score = None
        if candidate_skills:
            analysis = MatchingService.calculate_match(candidate_skills, req_skills)
            m_score = analysis["match_score"]

        results.append({
            "job_id": j.job_id,
            "recruiter_id": j.recruiter_id,
            "title": j.title,
            "description": j.description,
            "location": j.location,
            "experience": j.experience,
            "job_type": j.job_type,
            "salary_range": j.salary_range,
            "status": j.status,
            "created_date": j.created_date,
            "company_name": comp_name,
            "skills": req_skills,
            "applicant_count": len(j.applications),
            "user_has_applied": j.job_id in applied_job_ids,
            "match_score": m_score
        })

    return results

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
    if not recruiter:
        raise HTTPException(status_code=400, detail="Recruiter profile not found for this account")

    db_job = Job(
        recruiter_id=recruiter.recruiter_id,
        title=job_in.title.strip(),
        description=job_in.description.strip(),
        location=job_in.location.strip(),
        experience=job_in.experience.strip(),
        job_type=job_in.job_type,
        salary_range=job_in.salary_range,
        status="active"
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Attach skills
    for s_name in job_in.skills:
        clean = s_name.strip()
        if not clean:
            continue
        skill = db.query(Skill).filter(Skill.skill_name.ilike(clean)).first()
        if not skill:
            skill = Skill(skill_name=clean)
            db.add(skill)
            db.commit()
            db.refresh(skill)
        db_job.skills.append(skill)

    db.commit()
    db.refresh(db_job)

    comp_name = recruiter.company.company_name if recruiter.company else "Company"

    return {
        "job_id": db_job.job_id,
        "recruiter_id": db_job.recruiter_id,
        "title": db_job.title,
        "description": db_job.description,
        "location": db_job.location,
        "experience": db_job.experience,
        "job_type": db_job.job_type,
        "salary_range": db_job.salary_range,
        "status": db_job.status,
        "created_date": db_job.created_date,
        "company_name": comp_name,
        "skills": [s.skill_name for s in db_job.skills],
        "applicant_count": 0,
        "user_has_applied": False,
        "match_score": None
    }

@router.get("/{job_id}", response_model=JobResponse)
def get_job_details(
    job_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found")

    comp_name = job.recruiter.company.company_name if job.recruiter and job.recruiter.company else "Company"
    req_skills = [s.skill_name for s in job.skills]

    user_has_applied = False
    match_score = None
    if current_user and current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
        if candidate:
            existing_app = db.query(Application).filter(
                Application.job_id == job.job_id,
                Application.candidate_id == candidate.candidate_id
            ).first()
            user_has_applied = bool(existing_app)
            cand_skills = [s.skill_name for s in candidate.skills]
            match_res = MatchingService.calculate_match(cand_skills, req_skills)
            match_score = match_res["match_score"]

    return {
        "job_id": job.job_id,
        "recruiter_id": job.recruiter_id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "experience": job.experience,
        "job_type": job.job_type,
        "salary_range": job.salary_range,
        "status": job.status,
        "created_date": job.created_date,
        "company_name": comp_name,
        "skills": req_skills,
        "applicant_count": len(job.applications),
        "user_has_applied": user_has_applied,
        "match_score": match_score
    }

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_in: JobUpdate,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if current_user.role == "recruiter":
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
        if not recruiter or job.recruiter_id != recruiter.recruiter_id:
            raise HTTPException(status_code=403, detail="You can only edit jobs posted by your account")

    if job_in.title is not None:
        job.title = job_in.title.strip()
    if job_in.description is not None:
        job.description = job_in.description.strip()
    if job_in.location is not None:
        job.location = job_in.location.strip()
    if job_in.experience is not None:
        job.experience = job_in.experience.strip()
    if job_in.job_type is not None:
        job.job_type = job_in.job_type
    if job_in.salary_range is not None:
        job.salary_range = job_in.salary_range
    if job_in.status is not None:
        job.status = job_in.status

    if job_in.skills is not None:
        job.skills.clear()
        for s_name in job_in.skills:
            clean = s_name.strip()
            if not clean:
                continue
            skill = db.query(Skill).filter(Skill.skill_name.ilike(clean)).first()
            if not skill:
                skill = Skill(skill_name=clean)
                db.add(skill)
                db.commit()
                db.refresh(skill)
            job.skills.append(skill)

    db.commit()
    db.refresh(job)

    comp_name = job.recruiter.company.company_name if job.recruiter and job.recruiter.company else "Company"

    return {
        "job_id": job.job_id,
        "recruiter_id": job.recruiter_id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "experience": job.experience,
        "job_type": job.job_type,
        "salary_range": job.salary_range,
        "status": job.status,
        "created_date": job.created_date,
        "company_name": comp_name,
        "skills": [s.skill_name for s in job.skills],
        "applicant_count": len(job.applications),
        "user_has_applied": False,
        "match_score": None
    }

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if current_user.role == "recruiter":
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
        if not recruiter or job.recruiter_id != recruiter.recruiter_id:
            raise HTTPException(status_code=403, detail="Unauthorized to delete this job")

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully", "job_id": job_id}
