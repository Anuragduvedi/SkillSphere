from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_optional_user
from app.database import get_db
from app.models.models import User, Candidate, Application, Assessment
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[ChatMessage]] = []
    context: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    reply: str
    provider: str
    timestamp: str


def format_date(value):
    if not value:
        return "Not available"
    return value.strftime("%d %b %Y %I:%M %p")


@router.post("/message", response_model=ChatResponse)
def send_chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    message = request.message.strip()
    history = [m.model_dump() for m in request.history] if request.history else []

    # Safeguard for direct unit test invocations where FastAPI Depends objects are not evaluated
    real_user = current_user if isinstance(current_user, User) else None
    real_db = db if isinstance(db, Session) else None
    should_close_db = False

    if not real_db:
        from app.database import SessionLocal
        real_db = SessionLocal()
        should_close_db = True

    # Gather verified user journey data from backend DB if user is authenticated
    user_data = None
    try:
        if real_user and real_db:
            user_data = {
                "authenticated": True,
                "user_id": real_user.user_id,
                "name": real_user.name,
                "email": real_user.email,
                "role": real_user.role,
            }

            # Extract candidate journey if user has candidate profile (job_seeker, student, etc.)
            candidate = (
                real_db.query(Candidate)
                .filter(Candidate.user_id == real_user.user_id)
                .first()
            )
            if candidate:
                missing_fields = []
                if not candidate.phone:
                    missing_fields.append("Phone Number")
                if not candidate.location:
                    missing_fields.append("Location")
                if not candidate.education:
                    missing_fields.append("Education")
                if not candidate.experience:
                    missing_fields.append("Experience")

                skills_list = [s.skill_name for s in candidate.skills]
                if not skills_list:
                    missing_fields.append("Key Skills")

                resumes_count = len(candidate.resumes)
                if resumes_count == 0:
                    missing_fields.append("Resume Upload (PDF/Image)")

                total_items = 6
                completed_items = total_items - len(missing_fields)
                profile_pct = int((completed_items / total_items) * 100)

                # Fetch real applications
                apps = (
                    real_db.query(Application)
                    .filter(Application.candidate_id == candidate.candidate_id)
                    .order_by(Application.application_date.desc())
                    .all()
                )
                app_list = []
                for a in apps:
                    job_title = a.job.title if a.job else "Job Position"
                    company = (
                        a.job.recruiter.company.company_name
                        if a.job and a.job.recruiter and a.job.recruiter.company
                        else "Company Partner"
                    )
                    app_list.append({
                        "application_id": a.application_id,
                        "job_title": job_title,
                        "company": company,
                        "status": a.status or "Applied",
                        "date": a.application_date.strftime("%d %b %Y") if a.application_date else None
                    })

                # Fetch real assessments
                assessments = (
                    real_db.query(Assessment)
                    .filter(Assessment.candidate_id == candidate.candidate_id)
                    .order_by(Assessment.created_at.desc())
                    .all()
                )
                test_list = []
                for t in assessments:
                    test_job = t.job.title if t.job else (t.title or "Technical Assessment")
                    test_list.append({
                        "assessment_id": t.assessment_id,
                        "title": t.title or "Technical Assessment",
                        "job": test_job,
                        "status": t.status or "pending",
                        "score": t.score,
                        "percentage": t.percentage,
                        "passed": bool(t.passed),
                        "violations": t.violation_count or 0,
                        "auto_submitted": bool(t.auto_submitted_proctoring),
                        "time_limit": t.time_limit_minutes or 25,
                        "token": t.test_token
                    })

                completed_count = len([t for t in test_list if t.get("status") == "completed" or t.get("score") is not None])
                pending_count = len([t for t in test_list if t.get("status") in ["pending", "assigned", "in_progress"] and not t.get("passed")])
                passed_count = len([t for t in test_list if t.get("passed")])

                user_data["candidate"] = {
                    "candidate_id": candidate.candidate_id,
                    "profile_percentage": profile_pct,
                    "missing_fields": missing_fields,
                    "skills": skills_list,
                    "resumes_count": resumes_count,
                    "resume_uploaded": resumes_count > 0,
                    "latest_resume": candidate.resumes[0].file_name if candidate.resumes else None,
                    "phone": candidate.phone,
                    "location": candidate.location,
                    "education": candidate.education,
                    "experience": candidate.experience,
                    "applications": app_list,
                    "applications_count": len(app_list),
                    "assessments": test_list,
                    "completed_assessments_count": completed_count,
                    "pending_assessments_count": pending_count,
                    "passed_assessments_count": passed_count
                }
    finally:
        if should_close_db and real_db:
            real_db.close()

    # Generate response via ChatbotService (multilingual, context-aware, journey-aware)
    result = ChatbotService.get_response(
        message=message,
        history=history,
        context=request.context,
        user_data=user_data
    )

    return result


@router.get("/status")
def get_chatbot_status():
    has_gemini = bool(
        settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip()
    )

    return {
        "status": "online",
        "gemini_configured": has_gemini,
        "active_model": (
            settings.GEMINI_MODEL
            if has_gemini
            else "SkillSphere Built-in Knowledge Engine"
        ),
        "mode": (
            "Gemini API"
            if has_gemini
            else "SkillSphere Native AI Engine"
        ),
        "multilingual_support": ["English", "Hindi", "Punjabi", "Hinglish"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
