import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Recruiter, Job, Application, Candidate, User, Company, Skill
from app.schemas.schemas import ApplicationResponse, CompanyResponse, CompanyUpdate
from app.core.deps import get_current_user, require_roles
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/recruiter", tags=["Recruiter ATS"])

@router.get("/applicants", response_model=List[ApplicationResponse])
def get_recruiter_applicants(
    job_id: Optional[int] = Query(None, description="Filter applicants by job ID"),
    skill: Optional[str] = Query(None, description="Filter applicants by candidate skill"),
    status: Optional[str] = Query(None, description="Filter applicants by status"),
    search: Optional[str] = Query(None, description="Search by candidate name or email"),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    query = db.query(Application).join(Job)

    if current_user.role == "recruiter":
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
        if not recruiter:
            return []
        query = query.filter(Job.recruiter_id == recruiter.recruiter_id)

    if isinstance(job_id, int):
        query = query.filter(Application.job_id == job_id)

    if isinstance(status, str) and status != "all":
        query = query.filter(Application.status == status)

    if isinstance(search, str) and search.strip():
        s_term = f"%{search.strip()}%"
        query = query.join(Candidate).join(User).filter(
            (User.name.ilike(s_term)) | (User.email.ilike(s_term))
        )

    apps = query.order_by(Application.application_date.desc()).all()

    skill_filter = skill.strip().lower() if isinstance(skill, str) and skill.strip() else None

    results = []
    for a in apps:
        cand = a.candidate
        c_skills = [s.skill_name for s in cand.skills] if cand else []
        j_skills = [s.skill_name for s in a.job.skills] if a.job else []

        # Filter by candidate skill if requested
        if skill_filter and not any(skill_filter in cs.lower() for cs in c_skills):
            continue

        match_info = MatchingService.calculate_match(c_skills, j_skills)
        comp_name = a.job.recruiter.company.company_name if a.job.recruiter and a.job.recruiter.company else "Company"

        results.append({
            "application_id": a.application_id,
            "job_id": a.job_id,
            "candidate_id": a.candidate_id,
            "resume_id": a.resume_id,
            "application_date": a.application_date,
            "status": a.status,
            "cover_note": a.cover_note,
            "job_title": a.job.title if a.job else "Role",
            "company_name": comp_name,
            "location": a.job.location if a.job else "",
            "candidate_name": cand.user.name if cand and cand.user else "Candidate",
            "candidate_email": cand.user.email if cand and cand.user else "",
            "candidate_phone": cand.phone if cand else "",
            "candidate_skills": c_skills,
            "candidate_experience": cand.experience if cand else "",
            "resume_file_path": a.resume.file_name if a.resume else None,
            "match_score": match_info["match_score"]
        })

    return results

@router.get("/stats")
def get_recruiter_stats(
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
    if not recruiter:
        return {"total_jobs": 0, "active_jobs": 0, "total_applicants": 0, "shortlisted": 0, "interviews": 0, "selected": 0}

    job_ids = [j.job_id for j in recruiter.jobs]
    active_jobs = [j for j in recruiter.jobs if j.status == "active"]
    
    total_apps = db.query(Application).filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    shortlisted = db.query(Application).filter(Application.job_id.in_(job_ids), Application.status == "Shortlisted").count() if job_ids else 0
    interviews = db.query(Application).filter(Application.job_id.in_(job_ids), Application.status == "Interview").count() if job_ids else 0
    selected = db.query(Application).filter(Application.job_id.in_(job_ids), Application.status == "Selected").count() if job_ids else 0

    return {
        "total_jobs": len(recruiter.jobs),
        "active_jobs": len(active_jobs),
        "total_applicants": total_apps,
        "shortlisted": shortlisted,
        "interviews": interviews,
        "selected": selected
    }

@router.get("/export-applicants")
def export_applicants_csv(
    job_id: Optional[int] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    """Bonus Requirement: Export recruiter applicant data to CSV."""
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
    query = db.query(Application).join(Job)

    if current_user.role == "recruiter" and recruiter:
        query = query.filter(Job.recruiter_id == recruiter.recruiter_id)

    if job_id:
        query = query.filter(Application.job_id == job_id)

    apps = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Application ID", "Job Title", "Candidate Name", "Candidate Email",
        "Candidate Phone", "Experience", "Skills", "Match Score (%)", "Status", "Application Date"
    ])

    for a in apps:
        cand = a.candidate
        c_skills = [s.skill_name for s in cand.skills] if cand else []
        j_skills = [s.skill_name for s in a.job.skills] if a.job else []
        match_info = MatchingService.calculate_match(c_skills, j_skills)

        writer.writerow([
            a.application_id,
            a.job.title if a.job else "",
            cand.user.name if cand and cand.user else "",
            cand.user.email if cand and cand.user else "",
            cand.phone if cand else "",
            cand.experience if cand else "",
            "; ".join(c_skills),
            match_info["match_score"],
            a.status,
            a.application_date.strftime("%Y-%m-%d %H:%M:%S") if a.application_date else ""
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=skillsphere_applicants.csv"}
    )

@router.get("/company", response_model=CompanyResponse)
def get_company_profile(
    current_user: User = Depends(require_roles(["recruiter"])),
    db: Session = Depends(get_db)
):
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
    if not recruiter or not recruiter.company:
        raise HTTPException(status_code=404, detail="Company profile not found")
    return recruiter.company

@router.put("/company", response_model=CompanyResponse)
def update_company_profile(
    comp_in: CompanyUpdate,
    current_user: User = Depends(require_roles(["recruiter"])),
    db: Session = Depends(get_db)
):
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
    if not recruiter or not recruiter.company:
        raise HTTPException(status_code=404, detail="Company profile not found")

    company = recruiter.company
    if comp_in.company_name:
        company.company_name = comp_in.company_name.strip()
    if comp_in.description is not None:
        company.description = comp_in.description.strip()
    if comp_in.contact_info is not None:
        company.contact_info = comp_in.contact_info.strip()
    if comp_in.website is not None:
        company.website = comp_in.website.strip()
    if comp_in.location is not None:
        company.location = comp_in.location.strip()

    db.commit()
    db.refresh(company)
    return company
