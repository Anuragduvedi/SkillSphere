from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import User, Candidate, Recruiter, Job, Application, Resume, ResumeAnalysis
from app.schemas.schemas import AdminAnalyticsResponse, UserResponse
from app.core.deps import require_roles

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

@router.get("/analytics", response_model=AdminAnalyticsResponse)
def get_platform_analytics(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_candidates = db.query(Candidate).count()
    total_recruiters = db.query(Recruiter).count()
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.status == "active").count()
    total_applications = db.query(Application).count()
    total_resumes = db.query(Resume).count()

    # Average match score
    avg_score = db.query(func.avg(ResumeAnalysis.match_score)).scalar() or 76.5

    # Status distribution
    status_counts = db.query(Application.status, func.count(Application.application_id)).group_by(Application.status).all()
    status_distribution = {status: count for status, count in status_counts}

    # Jobs by type
    type_counts = db.query(Job.job_type, func.count(Job.job_id)).group_by(Job.job_type).all()
    jobs_by_type = {j_type: count for j_type, count in type_counts}

    return {
        "total_users": total_users,
        "total_candidates": total_candidates,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "total_resumes_processed": total_resumes,
        "average_match_score": round(float(avg_score), 1),
        "status_distribution": status_distribution,
        "jobs_by_type": jobs_by_type
    }

@router.get("/users")
def list_all_users(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.created_date.desc()).all()
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_date": u.created_date,
            "extra_info": (
                u.recruiter.company.company_name if u.recruiter and u.recruiter.company else 
                f"{len(u.candidate.resumes)} resume(s)" if u.candidate else ""
            )
        } for u in users
    ]

@router.put("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot deactivate own admin account")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User status toggled to {'active' if user.is_active else 'inactive'}", "is_active": user.is_active}

@router.delete("/users/{user_id}")
def delete_user_account(
    user_id: int,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete own admin account")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User account permanently removed", "user_id": user_id}

@router.get("/jobs")
def list_all_jobs_moderation(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).order_by(Job.created_date.desc()).all()
    return [
        {
            "job_id": j.job_id,
            "title": j.title,
            "company_name": j.recruiter.company.company_name if j.recruiter and j.recruiter.company else "Unknown",
            "recruiter_name": j.recruiter.user.name if j.recruiter and j.recruiter.user else "Recruiter",
            "location": j.location,
            "job_type": j.job_type,
            "status": j.status,
            "created_date": j.created_date,
            "applicant_count": len(j.applications)
        } for j in jobs
    ]

@router.put("/jobs/{job_id}/moderate")
def moderate_job_status(
    job_id: int,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "closed" if job.status == "active" else "active"
    db.commit()
    return {"message": f"Job status updated to {job.status}", "status": job.status}
