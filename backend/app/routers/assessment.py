
import json
import secrets
import random
import httpx
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.core.config import settings
from app.models.models import (
    User, Candidate, Recruiter, Job, Application, Assessment, AssessmentQuestion,
    EmailNotification, RecruiterQuestion, AssessmentTemplate, ProctoringEvent
)
from app.schemas.schemas import (
    AssessmentDetailResponse,
    AssessmentSubmitRequest,
    AssessmentResultResponse,
    ScreeningJobResponse,
    ScreeningStatsResponse,
    EmailNotificationResponse,
    RecruiterQuestionCreate,
    RecruiterQuestionUpdate,
    RecruiterQuestionResponse,
    AssessmentTemplateCreate,
    AssessmentTemplateUpdate,
    AssessmentTemplateResponse,
    RecruiterAssessmentStats,
    AssignAssessmentRequest,
    GenerateAIQuestionsRequest
)
from app.core.deps import get_current_user, require_roles, get_optional_user
from app.services.matching_service import MatchingService
from app.services.assessment_service import AssessmentService
from app.services.email_service import EmailService
from app.services.question_bank import QUESTION_BANK
from app.core.proctoring_config import (
    MAX_PROCTORING_STRIKES,
    PROCTORING_DEBOUNCE_SECONDS,
    ALLOWED_PROCTORING_EVENTS,
    CRITICAL_PROCTORING_EVENTS
)

router = APIRouter(tags=["AI Screening & Assessments"])


def is_expired(dt: Optional[datetime]) -> bool:
    if not dt:
        return False
    if dt.tzinfo is not None:
        from datetime import timezone
        return datetime.now(timezone.utc) > dt
    return datetime.utcnow() > dt


def get_recruiter_for_user(current_user: User, db: Session) -> Recruiter:
    """Retrieve recruiter profile or handle admin override."""
    recruiter = db.query(Recruiter).filter(
        Recruiter.user_id == current_user.user_id
    ).first()

    if not recruiter:
        if current_user.role == "admin":
            recruiter = db.query(Recruiter).first()

        if not recruiter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recruiter profile is required for this operation."
            )

    return recruiter


# ================= 1. RECRUITER QUESTION MANAGEMENT =================

@router.post("/assessment/questions", response_model=RecruiterQuestionResponse)
def create_question(
    data: RecruiterQuestionCreate,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)
    q_data = data.model_dump()

    created = AssessmentService.create_recruiter_question(
        db, recruiter.recruiter_id, q_data
    )

    return {
        "question_id": created.question_id,
        "recruiter_id": created.recruiter_id,
        "job_id": created.job_id,
        "job_title": created.job.title if created.job else "General Bank",
        "technology": created.technology,
        "difficulty": created.difficulty,
        "question_text": created.question_text,
        "options": json.loads(created.options),
        "correct_answer": created.correct_answer,
        "explanation": created.explanation,
        "created_at": created.created_at,
        "updated_at": created.updated_at
    }


@router.get("/assessment/questions", response_model=List[RecruiterQuestionResponse])
def list_questions(
    job_id: Optional[int] = Query(None),
    technology: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter_id = None

    if current_user.role != "admin":
        recruiter = get_recruiter_for_user(current_user, db)
        recruiter_id = recruiter.recruiter_id

    return AssessmentService.get_recruiter_questions(
        db=db,
        recruiter_id=recruiter_id,
        job_id=job_id,
        technology=technology,
        difficulty=difficulty,
        search=search
    )


@router.put("/assessment/questions/{question_id}", response_model=RecruiterQuestionResponse)
def update_question(
    question_id: int,
    data: RecruiterQuestionUpdate,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    updated = AssessmentService.update_recruiter_question(
        db=db,
        question_id=question_id,
        recruiter_id=recruiter.recruiter_id,
        data=data.model_dump(exclude_unset=True),
        is_admin=(current_user.role == "admin")
    )

    return {
        "question_id": updated.question_id,
        "recruiter_id": updated.recruiter_id,
        "job_id": updated.job_id,
        "job_title": updated.job.title if updated.job else "General Bank",
        "technology": updated.technology,
        "difficulty": updated.difficulty,
        "question_text": updated.question_text,
        "options": json.loads(updated.options),
        "correct_answer": updated.correct_answer,
        "explanation": updated.explanation,
        "created_at": updated.created_at,
        "updated_at": updated.updated_at
    }


@router.delete("/assessment/questions/{question_id}")
def delete_question(
    question_id: int,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    AssessmentService.delete_recruiter_question(
        db,
        question_id,
        recruiter.recruiter_id,
        is_admin=(current_user.role == "admin")
    )

    return {
        "message": "Question deleted successfully",
        "question_id": question_id
    }


@router.get("/assessment/question-library")
def get_question_library(
    technology: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    library = {}

    if technology and technology.lower() in QUESTION_BANK:
        library[technology.lower()] = QUESTION_BANK[technology.lower()]
    else:
        library = QUESTION_BANK

    items = []

    for cat, questions in library.items():
        for question in questions:
            items.append({
                "technology": cat.replace("_", " ").title(),
                "difficulty": question["difficulty"],
                "question_text": question["question"],
                "options": question["options"],
                "correct_answer": question["correct_answer"],
                "explanation": question.get("explanation", "")
            })

    return items


@router.post("/assessment/questions/import-from-library")
def import_questions_from_library(
    technology: str = Query(...),
    count: int = Query(20, ge=1, le=50),
    job_id: Optional[int] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    imported = AssessmentService.import_library_questions(
        db=db,
        recruiter_id=recruiter.recruiter_id,
        technology=technology,
        count=count,
        job_id=job_id
    )

    return {
        "message": f"Successfully imported {len(imported)} questions for {technology} into your question bank.",
        "imported_count": len(imported),
        "technology": technology
    }


# ================= 2. ASSESSMENT TEMPLATES =================

@router.post("/assessment/templates", response_model=AssessmentTemplateResponse)
def create_assessment_template(
    data: AssessmentTemplateCreate,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    template = AssessmentService.create_assessment_template(
        db=db,
        recruiter_id=recruiter.recruiter_id,
        data=data.model_dump()
    )

    q_ids = json.loads(template.question_ids) if template.question_ids else []

    return {
        "template_id": template.template_id,
        "recruiter_id": template.recruiter_id,
        "job_id": template.job_id,
        "job_title": template.job.title if template.job else "Job Opening",
        "company_name": template.job.recruiter.company.company_name if template.job and template.job.recruiter and template.job.recruiter.company else "Company",
        "title": template.title,
        "tech_stack": template.tech_stack,
        "duration_minutes": template.duration_minutes,
        "passing_percentage": template.passing_percentage,
        "status": template.status,
        "question_ids": q_ids,
        "questions_count": len(q_ids),
        "created_at": template.created_at,
        "updated_at": template.updated_at
    }


@router.get("/assessment/templates", response_model=List[AssessmentTemplateResponse])
def list_assessment_templates(
    status_filter: Optional[str] = Query(None),
    job_id: Optional[int] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter_id = None

    if current_user.role != "admin":
        recruiter = get_recruiter_for_user(current_user, db)
        recruiter_id = recruiter.recruiter_id

    return AssessmentService.get_assessment_templates(
        db=db,
        recruiter_id=recruiter_id,
        job_id=job_id,
        status_filter=status_filter
    )


@router.get("/assessment/templates/{template_id}")
def get_template_details(
    template_id: int,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    template = db.query(AssessmentTemplate).filter(
        AssessmentTemplate.template_id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Assessment template not found.")

    recruiter = get_recruiter_for_user(current_user, db)

    if current_user.role != "admin" and template.recruiter_id != recruiter.recruiter_id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this template.")

    q_ids = json.loads(template.question_ids) if template.question_ids else []

    questions = db.query(RecruiterQuestion).filter(
        RecruiterQuestion.question_id.in_(q_ids)
    ).all()

    questions_map = {q.question_id: q for q in questions}
    ordered_qs = []

    for qid in q_ids:
        q_obj = questions_map.get(qid)

        if q_obj:
            ordered_qs.append({
                "question_id": q_obj.question_id,
                "technology": q_obj.technology,
                "difficulty": q_obj.difficulty,
                "question_text": q_obj.question_text,
                "options": json.loads(q_obj.options),
                "correct_answer": q_obj.correct_answer,
                "explanation": q_obj.explanation
            })

    return {
        "template_id": template.template_id,
        "recruiter_id": template.recruiter_id,
        "job_id": template.job_id,
        "job_title": template.job.title if template.job else "",
        "company_name": template.job.recruiter.company.company_name if template.job and template.job.recruiter and template.job.recruiter.company else "Company",
        "title": template.title,
        "tech_stack": template.tech_stack,
        "duration_minutes": template.duration_minutes,
        "passing_percentage": template.passing_percentage,
        "status": template.status,
        "questions_count": len(ordered_qs),
        "questions": ordered_qs,
        "created_at": template.created_at,
        "updated_at": template.updated_at
    }


@router.put("/assessment/templates/{template_id}", response_model=AssessmentTemplateResponse)
def update_assessment_template(
    template_id: int,
    data: AssessmentTemplateUpdate,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    updated = AssessmentService.update_assessment_template(
        db=db,
        template_id=template_id,
        recruiter_id=recruiter.recruiter_id,
        data=data.model_dump(exclude_unset=True),
        is_admin=(current_user.role == "admin")
    )

    q_ids = json.loads(updated.question_ids) if updated.question_ids else []

    return {
        "template_id": updated.template_id,
        "recruiter_id": updated.recruiter_id,
        "job_id": updated.job_id,
        "job_title": updated.job.title if updated.job else "Job Opening",
        "company_name": updated.job.recruiter.company.company_name if updated.job and updated.job.recruiter and updated.job.recruiter.company else "Company",
        "title": updated.title,
        "tech_stack": updated.tech_stack,
        "duration_minutes": updated.duration_minutes,
        "passing_percentage": updated.passing_percentage,
        "status": updated.status,
        "question_ids": q_ids,
        "questions_count": len(q_ids),
        "created_at": updated.created_at,
        "updated_at": updated.updated_at
    }


@router.post("/assessment/templates/{template_id}/publish", response_model=AssessmentTemplateResponse)
def publish_assessment_template(
    template_id: int,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    published = AssessmentService.publish_assessment_template(
        db=db,
        template_id=template_id,
        recruiter_id=recruiter.recruiter_id,
        is_admin=(current_user.role == "admin")
    )

    q_ids = json.loads(published.question_ids) if published.question_ids else []

    return {
        "template_id": published.template_id,
        "recruiter_id": published.recruiter_id,
        "job_id": published.job_id,
        "job_title": published.job.title if published.job else "Job Opening",
        "company_name": published.job.recruiter.company.company_name if published.job and published.job.recruiter and published.job.recruiter.company else "Company",
        "title": published.title,
        "tech_stack": published.tech_stack,
        "duration_minutes": published.duration_minutes,
        "passing_percentage": published.passing_percentage,
        "status": published.status,
        "question_ids": q_ids,
        "questions_count": len(q_ids),
        "created_at": published.created_at,
        "updated_at": published.updated_at
    }


@router.delete("/assessment/templates/{template_id}")
def delete_assessment_template(
    template_id: int,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    AssessmentService.delete_assessment_template(
        db,
        template_id,
        recruiter.recruiter_id,
        is_admin=(current_user.role == "admin")
    )

    return {
        "message": "Assessment template deleted successfully",
        "template_id": template_id
    }


# ================= 3. RECRUITER RESULTS & STATS =================

@router.get("/assessment/recruiter/stats", response_model=RecruiterAssessmentStats)
def get_recruiter_assessment_telemetry(
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)
    return AssessmentService.get_recruiter_stats(db, recruiter.recruiter_id)


@router.get("/assessment/recruiter/candidate-results")
def get_recruiter_candidate_results(
    job_id: Optional[int] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    recruiter = get_recruiter_for_user(current_user, db)

    job_query = db.query(Job.job_id)

    if current_user.role != "admin":
        job_query = job_query.filter(Job.recruiter_id == recruiter.recruiter_id)

    if job_id:
        job_query = job_query.filter(Job.job_id == job_id)

    recruiter_job_ids = [j[0] for j in job_query.all()]

    if not recruiter_job_ids:
        return []

    assessments = db.query(Assessment).filter(
        Assessment.job_id.in_(recruiter_job_ids)
    ).order_by(
        desc(Assessment.completed_at),
        desc(Assessment.created_at)
    ).all()

    results = []

    for a in assessments:
        results.append({
            "assessment_id": a.assessment_id,
            "test_token": a.test_token,
            "title": a.title,
            "tech_stack": a.tech_stack,
            "candidate_id": a.candidate_id,
            "candidate_name": a.candidate.user.name if a.candidate and a.candidate.user else "Candidate",
            "candidate_email": a.candidate.user.email if a.candidate and a.candidate.user else "",
            "job_id": a.job_id,
            "job_title": a.job.title if a.job else "Position",
            "status": a.status,
            "score": a.score,
            "total_questions": a.total_questions or 20,
            "percentage": a.percentage,
            "passed": a.passed,
            "passing_percentage": a.passing_percentage or 60.0,
            "correct_answers_count": a.correct_answers_count,
            "incorrect_answers_count": a.incorrect_answers_count,
            "started_at": a.started_at,
            "completed_at": a.completed_at,
            "created_at": a.created_at
        })

    return results


# ================= 3B. RECRUITER DIRECT ASSIGNMENT & TRACKING =================

@router.get("/assessment/recruiter/assignable-candidates")
def get_assignable_candidates(
    search: Optional[str] = Query(None),
    job_id: Optional[int] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Returns searchable list of job seekers for recruiters to assign technical assessments to.
    Includes candidate details, skills, applications, and existing assessment statuses.
    """
    candidates = db.query(Candidate).all()
    results = []

    for c in candidates:
        user = c.user
        if not user:
            continue

        c_name = user.name or "Candidate"
        c_email = user.email or ""

        # Filter by search term if provided
        if search:
            s_lower = search.lower()
            skills_str = " ".join([s.skill_name.lower() for s in c.skills])
            if (s_lower not in c_name.lower() and 
                s_lower not in c_email.lower() and 
                s_lower not in skills_str):
                continue

        # Get applications
        apps = []
        for app in c.applications:
            if job_id and app.job_id != job_id:
                continue
            apps.append({
                "application_id": app.application_id,
                "job_id": app.job_id,
                "job_title": app.job.title if app.job else "Job",
                "status": app.status,
                "application_date": app.application_date
            })

        # Get assessments
        assigned_tests = []
        for a in c.assessments:
            assigned_tests.append({
                "assessment_id": a.assessment_id,
                "title": a.title,
                "test_token": a.test_token,
                "test_link": f"http://localhost:5173/assessment/{a.test_token}",
                "status": a.status,
                "score": a.score,
                "percentage": a.percentage,
                "created_at": a.created_at,
                "expires_at": a.expires_at
            })

        results.append({
            "candidate_id": c.candidate_id,
            "user_id": user.user_id,
            "name": c_name,
            "email": c_email,
            "phone": c.phone,
            "location": c.location,
            "experience": c.experience,
            "education": c.education,
            "skills": [s.skill_name for s in c.skills],
            "applications": apps,
            "assigned_tests": assigned_tests
        })

    return results


@router.post("/assessment/recruiter/assign")
def assign_assessment_to_candidates(
    request: AssignAssessmentRequest,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Direct recruiter assignment of an assessment to one or multiple candidates.
    Independent of auto-shortlisting.
    Generates a unique unguessable test link for each candidate, sets expiry,
    optionally sends email, and returns assignment records.
    """
    recruiter = get_recruiter_for_user(current_user, db)

    # 1. Verify candidates
    candidates = db.query(Candidate).filter(
        Candidate.candidate_id.in_(request.candidate_ids)
    ).all()

    if not candidates:
        raise HTTPException(
            status_code=400,
            detail="No valid candidates found for assignment."
        )

    # 2. Get or resolve questions pool
    questions_to_use = []

    # If template_id provided
    if request.template_id:
        template = db.query(AssessmentTemplate).filter(
            AssessmentTemplate.template_id == request.template_id
        ).first()
        if template and template.question_ids:
            try:
                t_qids = json.loads(template.question_ids)
                questions_to_use = db.query(RecruiterQuestion).filter(
                    RecruiterQuestion.question_id.in_(t_qids)
                ).all()
            except Exception:
                questions_to_use = []

    # If specific question_ids passed
    if not questions_to_use and request.question_ids:
        questions_to_use = db.query(RecruiterQuestion).filter(
            RecruiterQuestion.question_id.in_(request.question_ids)
        ).all()

    # If still not enough questions, pull from recruiter's pool
    if len(questions_to_use) < 20:
        recruiter_qs = db.query(RecruiterQuestion).filter(
            RecruiterQuestion.recruiter_id == recruiter.recruiter_id
        ).all()
        existing_ids = {q.question_id for q in questions_to_use}
        for rq in recruiter_qs:
            if rq.question_id not in existing_ids:
                questions_to_use.append(rq)
                existing_ids.add(rq.question_id)
            if len(questions_to_use) >= 20:
                break

    # If still < 20, import from library
    if len(questions_to_use) < 20:
        needed = 20 - len(questions_to_use)
        imported = AssessmentService.import_library_questions(
            db=db,
            recruiter_id=recruiter.recruiter_id,
            technology=request.tech_stack or "Python",
            count=needed,
            job_id=request.job_id
        )
        questions_to_use.extend(imported)

    # Verify job if provided
    job = None
    if request.job_id:
        job = db.query(Job).filter(Job.job_id == request.job_id).first()

    now = datetime.utcnow()
    expires_at = now + timedelta(days=request.expires_days or 7)

    created_assignments = []

    for candidate in candidates:
        # Generate unpredictable secure token
        token_str = f"test_{secrets.token_urlsafe(24)}"

        assessment = Assessment(
            candidate_id=candidate.candidate_id,
            job_id=request.job_id if job else None,
            test_token=token_str,
            title=request.title,
            description=request.description,
            tech_stack=request.tech_stack or (job.skills[0].skill_name if job and job.skills else "General Technical"),
            total_questions=len(questions_to_use),
            time_limit_minutes=request.duration_minutes or 25,
            passing_percentage=request.passing_percentage or 60.0,
            status="pending",
            expires_at=expires_at,
            created_at=now
        )
        db.add(assessment)
        db.flush()

        # Copy questions with randomized sequence and options
        shuffled_pool = list(questions_to_use)
        random.shuffle(shuffled_pool)

        for idx, rq in enumerate(shuffled_pool):
            orig_opts = json.loads(rq.options) if isinstance(rq.options, str) else list(rq.options)
            shuffled_opts = list(orig_opts)
            random.shuffle(shuffled_opts)

            q_obj = AssessmentQuestion(
                assessment_id=assessment.assessment_id,
                question_text=rq.question_text,
                skill_category=rq.technology,
                difficulty=rq.difficulty,
                options=json.dumps(shuffled_opts),
                correct_answer=rq.correct_answer,
                explanation=rq.explanation or "",
                order_index=idx + 1
            )
            db.add(q_obj)

        db.flush()

        test_link = f"http://localhost:5173/assessment/{token_str}"

        # Send email if requested
        if request.send_email and candidate.user and candidate.user.email:
            try:
                EmailService.send_test_invitation_email(
                    db=db,
                    candidate=candidate,
                    job=job,
                    test_link=test_link,
                    time_limit=request.duration_minutes or 25,
                    title=request.title
                )
            except Exception as e:
                print(f"Notice: Failed to dispatch invitation email to {candidate.user.email}: {e}")

        created_assignments.append({
            "assessment_id": assessment.assessment_id,
            "candidate_id": candidate.candidate_id,
            "candidate_name": candidate.user.name if candidate.user else "Candidate",
            "candidate_email": candidate.user.email if candidate.user else "",
            "test_token": token_str,
            "test_link": test_link,
            "title": assessment.title,
            "expires_at": expires_at.isoformat(),
            "status": "pending"
        })

    db.commit()

    return {
        "message": f"Successfully assigned assessment to {len(created_assignments)} candidate(s).",
        "assigned_count": len(created_assignments),
        "assignments": created_assignments
    }


@router.get("/assessment/recruiter/assigned-tracking")
def get_assigned_assessments_tracking(
    job_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Returns full tracking list of assessments assigned by recruiters.
    Displays Candidate Name, Email, Job, Title, Status (Pending, In Progress, Completed, Terminated, Expired),
    Assigned Date, Deadline (expires_at), Start & Completion times, Score, and Link.
    """
    query = db.query(Assessment)

    if current_user.role == "recruiter":
        recruiter = get_recruiter_for_user(current_user, db)
        recruiter_job_ids = [j.job_id for j in recruiter.jobs]
        query = query.filter(Assessment.job_id.in_(recruiter_job_ids))

    if job_id:
        query = query.filter(Assessment.job_id == job_id)

    assessments = query.order_by(desc(Assessment.created_at)).all()

    now = datetime.utcnow()
    has_status_change = False
    tracking_data = []

    for a in assessments:
        effective_status = a.status
        if effective_status not in ["completed", "terminated_proctoring"] and is_expired(a.expires_at):
            effective_status = "expired"
            a.status = "expired"
            has_status_change = True

        if status_filter and status_filter.lower() != "all":
            if effective_status.lower() != status_filter.lower():
                continue

        cand_name = a.candidate.user.name if a.candidate and a.candidate.user else "Candidate"
        cand_email = a.candidate.user.email if a.candidate and a.candidate.user else ""

        if search:
            s_lower = search.lower()
            if (s_lower not in cand_name.lower() and 
                s_lower not in cand_email.lower() and 
                s_lower not in a.title.lower()):
                continue

        tracking_data.append({
            "assessment_id": a.assessment_id,
            "test_token": a.test_token,
            "test_link": f"http://localhost:5173/assessment/{a.test_token}",
            "title": a.title,
            "description": getattr(a, "description", None),
            "tech_stack": a.tech_stack,
            "candidate_id": a.candidate_id,
            "candidate_name": cand_name,
            "candidate_email": cand_email,
            "job_id": a.job_id,
            "job_title": a.job.title if a.job else "Technical Role",
            "company_name": a.job.recruiter.company.company_name if a.job and a.job.recruiter and a.job.recruiter.company else "Company",
            "status": effective_status,
            "created_at": a.created_at,
            "expires_at": a.expires_at,
            "started_at": a.started_at,
            "completed_at": a.completed_at,
            "time_limit_minutes": a.time_limit_minutes,
            "total_questions": a.total_questions,
            "score": a.score,
            "percentage": a.percentage,
            "passed": a.passed,
            "passing_percentage": a.passing_percentage or 60.0,
            "violations_count": getattr(a, "violation_count", 0) or 0
        })

    if has_status_change:
        db.commit()

    return tracking_data


@router.post("/assessment/generate-questions-ai")
def generate_questions_ai(
    request: GenerateAIQuestionsRequest,
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Generates technical assessment questions using Gemini API if configured,
    or falls back gracefully to SkillSphere's comprehensive Question Bank.
    """
    api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
    generated_questions = []
    source = "question_bank"

    if api_key:
        try:
            model = settings.GEMINI_MODEL or "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

            prompt = (
                f"Generate {request.count} multiple-choice technical interview questions for the role '{request.role}' "
                f"focused on technology '{request.tech_stack}' with difficulty '{request.difficulty}'.\n"
                f"Return ONLY a valid JSON array of objects with the following schema:\n"
                f"[\n"
                f"  {{\n"
                f"    \"question_text\": \"Question text here?\",\n"
                f"    \"technology\": \"{request.tech_stack}\",\n"
                f"    \"difficulty\": \"{request.difficulty}\",\n"
                f"    \"options\": [\"Option A text\", \"Option B text\", \"Option C text\", \"Option D text\"],\n"
                f"    \"correct_answer\": \"Option A text\",\n"
                f"    \"explanation\": \"Detailed explanation of why this answer is correct.\"\n"
                f"  }}\n"
                f"]\n"
                f"Ensure options is a list of exactly 4 strings. Do not include markdown code block backticks if possible, or return strictly valid JSON."
            )

            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 2048
                }
            }

            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload, headers={"Content-Type": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            text = parts[0]["text"].strip()
                            if text.startswith("```"):
                                text = text.split("```")[1]
                                if text.startswith("json"):
                                    text = text[4:]
                                text = text.strip()
                            parsed = json.loads(text)
                            if isinstance(parsed, list) and len(parsed) > 0:
                                for item in parsed:
                                    if "question_text" in item and "options" in item and len(item["options"]) == 4:
                                        generated_questions.append({
                                            "question_text": item["question_text"],
                                            "technology": item.get("technology", request.tech_stack),
                                            "difficulty": item.get("difficulty", request.difficulty),
                                            "options": item["options"],
                                            "correct_answer": item.get("correct_answer", item["options"][0]),
                                            "explanation": item.get("explanation", "")
                                        })
                                if generated_questions:
                                    source = "gemini"
        except Exception as e:
            print(f"[AI Question Generator] Gemini generation note: {e}. Falling back to internal Question Bank.")

    # Fallback to Question Bank if Gemini unavailable or returned empty
    if not generated_questions:
        tech_key = request.tech_stack.lower().replace(" ", "_")
        bank_pool = QUESTION_BANK.get(tech_key) or QUESTION_BANK.get("python") or []
        diff_pool = [q for q in bank_pool if q.get("difficulty") == request.difficulty]
        if not diff_pool:
            diff_pool = bank_pool

        sample_count = min(request.count, len(diff_pool))
        selected = random.sample(diff_pool, sample_count) if diff_pool else []

        for q in selected:
            generated_questions.append({
                "question_text": q["question"],
                "technology": request.tech_stack,
                "difficulty": q.get("difficulty", request.difficulty),
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "explanation": q.get("explanation", "")
            })

    return {
        "success": True,
        "source": source,
        "count": len(generated_questions),
        "questions": generated_questions
    }



# ================= 4. ADMIN MONITORING =================

@router.get("/assessment/admin/statistics")
def get_admin_assessment_telemetry(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    return AssessmentService.get_admin_stats(db)


@router.get("/assessment/admin/all-templates")
def get_all_assessment_templates(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    return AssessmentService.get_assessment_templates(db)


@router.get("/assessment/admin/all-questions")
def get_all_recruiter_questions(
    technology: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    return AssessmentService.get_recruiter_questions(
        db=db,
        technology=technology,
        difficulty=difficulty,
        search=search
    )


@router.get("/assessment/admin/proctoring-events")
@router.get("/assessment/proctoring/all-events")
def get_admin_proctoring_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "recruiter"]))
):
    query = db.query(ProctoringEvent)
    
    if current_user.role == "recruiter":
        recruiter = get_recruiter_for_user(current_user, db)
        recruiter_job_ids = [j.job_id for j in recruiter.jobs]
        query = query.join(Assessment).filter(Assessment.job_id.in_(recruiter_job_ids))
        
    events = query.order_by(ProctoringEvent.created_at.desc()).all()

    result = []
    for event in events:
        assessment = db.query(Assessment).filter(
            Assessment.assessment_id == event.assessment_id
        ).first()

        candidate = db.query(Candidate).filter(
            Candidate.candidate_id == event.candidate_id
        ).first()

        user = db.query(User).filter(
            User.user_id == candidate.user_id
        ).first() if candidate else None

        result.append({
            "event_id": event.event_id,
            "assessment_id": event.assessment_id,
            "candidate_id": event.candidate_id,
            "candidate_name": user.name if user else "Unknown",
            "candidate_email": user.email if user else "Unknown",
            "assessment_title": assessment.title if assessment else "Unknown",
            "assessment_status": assessment.status if assessment else "Unknown",
            "event_type": event.event_type,
            "details": event.details,
            "severity": event.severity,
            "strike_number": event.strike_number if hasattr(event, "strike_number") else 1,
            "created_at": event.created_at
        })

    return result


@router.get("/assessment/proctoring/reports")
def get_proctoring_reports(
    job_id: Optional[int] = Query(None),
    risk_level: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_roles(["recruiter", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Comprehensive proctoring report for recruiters and admins.
    Summarizes candidate violation counts, strike status, auto-submission status,
    and event breakdown.
    """
    query = db.query(Assessment)

    if current_user.role == "recruiter":
        recruiter = get_recruiter_for_user(current_user, db)
        recruiter_job_ids = [j.job_id for j in recruiter.jobs]
        query = query.filter(Assessment.job_id.in_(recruiter_job_ids))

    if job_id:
        query = query.filter(Assessment.job_id == job_id)

    if status_filter:
        query = query.filter(Assessment.status == status_filter)

    assessments = query.order_by(desc(Assessment.started_at)).all()

    reports = []
    for a in assessments:
        candidate = a.candidate
        c_user = candidate.user if candidate else None
        job = a.job

        # Query all events for this assessment
        events = db.query(ProctoringEvent).filter(
            ProctoringEvent.assessment_id == a.assessment_id
        ).order_by(ProctoringEvent.created_at.asc()).all()

        violations_count = len(events)
        strikes = min(violations_count, 3)

        # Risk classification
        if a.status == "terminated_proctoring" or a.auto_submitted_proctoring or strikes >= 3:
            calc_risk = "Terminated"
        elif strikes in [1, 2]:
            calc_risk = "Warning"
        else:
            calc_risk = "Clean"

        if risk_level and risk_level.lower() != "all":
            if calc_risk.lower() != risk_level.lower():
                continue

        # Breakdown by event type
        breakdown: Dict[str, int] = {}
        for ev in events:
            breakdown[ev.event_type] = breakdown.get(ev.event_type, 0) + 1

        reports.append({
            "assessment_id": a.assessment_id,
            "test_token": a.test_token,
            "title": a.title,
            "job_id": a.job_id,
            "job_title": job.title if job else "N/A",
            "candidate_id": a.candidate_id,
            "candidate_name": c_user.name if c_user else "Unknown Candidate",
            "candidate_email": c_user.email if c_user else "N/A",
            "status": a.status,
            "score": a.score,
            "percentage": a.percentage,
            "passed": a.passed,
            "violation_count": violations_count,
            "strikes": strikes,
            "risk_level": calc_risk,
            "auto_submitted_proctoring": getattr(a, "auto_submitted_proctoring", False) or (a.status == "terminated_proctoring"),
            "proctoring_submission_reason": getattr(a, "proctoring_submission_reason", None),
            "started_at": a.started_at,
            "completed_at": a.completed_at,
            "violations_breakdown": breakdown,
            "total_events": violations_count
        })

    return reports


@router.get("/assessment/{assessment_id}/proctoring-events")
@router.get("/assessment/proctoring-events/{assessment_id}")
def get_assessment_proctoring_events(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full proctoring violation timeline for a specific assessment.
    Accessible to the candidate who took it, assigned recruiter, or admin.
    """
    assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    if current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
        if not candidate or assessment.candidate_id != candidate.candidate_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to this proctoring report.")
    elif current_user.role == "recruiter":
        recruiter = get_recruiter_for_user(current_user, db)
        recruiter_job_ids = [j.job_id for j in recruiter.jobs]
        if assessment.job_id not in recruiter_job_ids:
            raise HTTPException(status_code=403, detail="Unauthorized access to this candidate's report.")

    events = db.query(ProctoringEvent).filter(
        ProctoringEvent.assessment_id == assessment_id
    ).order_by(ProctoringEvent.created_at.asc()).all()

    return [
        {
            "event_id": ev.event_id,
            "assessment_id": ev.assessment_id,
            "candidate_id": ev.candidate_id,
            "event_type": ev.event_type,
            "details": ev.details,
            "severity": ev.severity,
            "strike_number": ev.strike_number if hasattr(ev, "strike_number") else 1,
            "session_id": ev.session_id if hasattr(ev, "session_id") else None,
            "created_at": ev.created_at
        }
        for ev in events
    ]


# ================= 5. CANDIDATE ASSESSMENT & PROCTORING =================

@router.post("/{assessment_id}/start")
def start_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=403,
            detail="Only candidates can start assessments"
        )

    candidate = db.query(Candidate).filter(
        Candidate.user_id == current_user.user_id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()

    if not assessment or assessment.candidate_id != candidate.candidate_id:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.status == "terminated_proctoring":
        raise HTTPException(
            status_code=403,
            detail="This assessment was terminated due to proctoring violations."
        )

    if assessment.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Assessment already completed"
        )

    if assessment.status == "expired" or is_expired(assessment.expires_at):
        assessment.status = "expired"
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="This assessment link has expired and cannot be started."
        )

    if not assessment.started_at:
        assessment.started_at = datetime.utcnow()
        assessment.status = "in_progress"
        db.commit()
        db.refresh(assessment)

    return {
        "message": "Assessment started",
        "status": assessment.status,
        "started_at": assessment.started_at
    }


@router.post("/{assessment_id}/proctoring-events")
@router.post("/assessment/{assessment_id}/proctoring-events")
def record_proctoring_event(
    assessment_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=403,
            detail="Only candidates can report events"
        )

    candidate = db.query(Candidate).filter(
        Candidate.user_id == current_user.user_id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()

    if not assessment or assessment.candidate_id != candidate.candidate_id:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.status == "terminated_proctoring":
        return {
            "message": "Assessment already terminated",
            "strikes": MAX_PROCTORING_STRIKES,
            "remaining_strikes": 0,
            "terminated": True,
            "auto_submitted": True,
            "status": assessment.status
        }

    if assessment.status != "in_progress":
        raise HTTPException(
            status_code=400,
            detail="Assessment is not active"
        )

    event_type = payload.get("event_type")

    if event_type not in ALLOWED_PROCTORING_EVENTS:
        raise HTTPException(
            status_code=400,
            detail="Invalid event type"
        )

    now = datetime.utcnow()
    raw_details = str(payload.get("details", ""))
    confidence = payload.get("confidence")
    if confidence is not None:
        try:
            formatted_details = f"{raw_details} [confidence: {float(confidence):.2f}]"[:1000]
        except (ValueError, TypeError):
            formatted_details = raw_details[:1000]
    else:
        formatted_details = raw_details[:1000]

    instant_terminate = bool(payload.get("instant_terminate", False))
    severity_param = payload.get("severity")

    # Immediate termination if instant_terminate=True or sustained multiple faces / critical violation
    is_immediate_termination = (
        instant_terminate or
        (event_type == "multiple_faces" and severity_param == "critical")
    )

    # Save latest candidate answers before recording the violation.
    answers = payload.get("answers")
    if answers is not None and isinstance(answers, dict):
        assessment.candidate_answers = json.dumps(answers)

    # Count prior recorded violations for this assessment and candidate.
    prior_strikes = db.query(ProctoringEvent).filter(
        ProctoringEvent.assessment_id == assessment_id,
        ProctoringEvent.candidate_id == candidate.candidate_id
    ).count()

    # Debounce non-critical identical events within PROCTORING_DEBOUNCE_SECONDS
    if not is_immediate_termination and severity_param != "critical":
        previous_event = db.query(ProctoringEvent).filter(
            ProctoringEvent.assessment_id == assessment_id,
            ProctoringEvent.candidate_id == candidate.candidate_id,
            ProctoringEvent.event_type == event_type
        ).order_by(
            ProctoringEvent.created_at.desc()
        ).first()

        if (
            previous_event
            and previous_event.created_at
            and (now - previous_event.created_at).total_seconds() < PROCTORING_DEBOUNCE_SECONDS
        ):
            return {
                "message": "Duplicate event ignored",
                "duplicate": True,
                "strikes": min(prior_strikes, MAX_PROCTORING_STRIKES),
                "remaining_strikes": max(0, MAX_PROCTORING_STRIKES - prior_strikes),
                "terminated": prior_strikes >= MAX_PROCTORING_STRIKES,
                "auto_submitted": prior_strikes >= MAX_PROCTORING_STRIKES,
                "status": assessment.status
            }

    # Determine strike number and severity
    if is_immediate_termination:
        strike_num = MAX_PROCTORING_STRIKES
        severity = "critical"
    else:
        strike_num = min(prior_strikes + 1, MAX_PROCTORING_STRIKES)
        severity = severity_param or ("critical" if strike_num >= MAX_PROCTORING_STRIKES else "warning")

    # Record the proctoring violation.
    event = ProctoringEvent(
        assessment_id=assessment_id,
        candidate_id=candidate.candidate_id,
        event_type=event_type,
        details=formatted_details,
        severity=severity,
        strike_number=strike_num,
        session_id=str(payload.get("session_id", ""))[:100] if payload.get("session_id") else None,
        created_at=now
    )
    db.add(event)
    db.flush()

    strikes = strike_num
    assessment.violation_count = strikes

    # Termination triggers: reaching MAX strikes or immediate termination
    if strikes >= MAX_PROCTORING_STRIKES or is_immediate_termination:
        assessment.status = "terminated_proctoring"
        assessment.auto_submitted_proctoring = True
        if is_immediate_termination:
            assessment.proctoring_submission_reason = f"Immediate examination termination: {formatted_details}"
        else:
            assessment.proctoring_submission_reason = f"Auto-submitted due to {MAX_PROCTORING_STRIKES} proctoring violations. Final event ({event_type}): {formatted_details}"
        assessment.completed_at = now

        # Grade any answers submitted up to this point so progress is preserved
        submitted_dict = answers if isinstance(answers, dict) else {}
        if not submitted_dict and assessment.candidate_answers:
            try:
                parsed_answers = json.loads(assessment.candidate_answers)
                if isinstance(parsed_answers, dict):
                    submitted_dict = parsed_answers
            except Exception:
                submitted_dict = {}

        correct_count = 0
        breakdown = []
        for q in assessment.questions:
            user_chosen = submitted_dict.get(str(q.question_id)) or submitted_dict.get(q.question_id)
            is_correct = (user_chosen == q.correct_answer)
            if is_correct:
                correct_count += 1
            breakdown.append({
                "question_id": q.question_id,
                "order_index": q.order_index,
                "question_text": q.question_text,
                "skill_category": q.skill_category,
                "difficulty": q.difficulty,
                "options": json.loads(q.options) if isinstance(q.options, str) else q.options,
                "candidate_answer": user_chosen,
                "correct_answer": q.correct_answer,
                "is_correct": is_correct,
                "explanation": q.explanation
            })

        total = assessment.total_questions or 20
        assessment.score = float(correct_count)
        assessment.percentage = round((correct_count / total) * 100.0, 1)
        assessment.passed = False  # Terminated due to proctoring violation
        assessment.correct_answers_count = correct_count
        assessment.incorrect_answers_count = total - correct_count
        assessment.candidate_answers = json.dumps(breakdown)

        # Update candidate application status
        app_record = None
        if assessment.application_id:
            app_record = db.query(Application).filter(Application.application_id == assessment.application_id).first()
        if not app_record:
            app_record = db.query(Application).filter(
                Application.candidate_id == assessment.candidate_id,
                Application.job_id == assessment.job_id
            ).first()

        if app_record:
            app_record.status = "Under Review"

        # Log an email notification for candidate and recruiter
        try:
            notif = EmailNotification(
                candidate_id=candidate.candidate_id,
                job_id=assessment.job_id,
                recipient_email=current_user.email,
                subject=f"Notice: SkillSphere Assessment Auto-Submitted – {assessment.title}",
                content=(
                    f"Dear {current_user.name},\n\n"
                    f"Your technical assessment '{assessment.title}' was terminated and automatically submitted "
                    f"due to strict proctoring policy enforcement.\n\n"
                    f"Violation Recorded: {event_type} ({formatted_details})\n"
                    f"All questions answered prior to termination have been saved and delivered to the hiring recruiter."
                ),
                status="sent",
                created_at=now
            )
            db.add(notif)
        except Exception as e:
            print(f"Notice: Failed to log proctoring termination notification: {e}")

        db.commit()

        return {
            "message": "Assessment auto-submitted due to proctoring policy violation",
            "event_id": event.event_id,
            "strikes": MAX_PROCTORING_STRIKES,
            "remaining_strikes": 0,
            "warning": "Assessment auto-submitted due to proctoring violations.",
            "terminated": True,
            "auto_submitted": True,
            "status": "terminated_proctoring",
            "score": assessment.score,
            "percentage": assessment.percentage
        }

    db.commit()

    return {
        "message": "Proctoring violation recorded",
        "event_id": event.event_id,
        "strikes": strikes,
        "remaining_strikes": max(0, MAX_PROCTORING_STRIKES - strikes),
        "warning": "Warning 1/3 (First Violation)" if strikes == 1 else "Final Warning 2/3 (One violation remaining before auto-submission)",
        "terminated": False,
        "auto_submitted": False,
        "status": assessment.status
    }


@router.get("/assessment/by-token/{token}")
def get_assessment_by_token(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return AssessmentService.get_assessment_for_candidate(
        db,
        token,
        current_user
    )


@router.post("/assessment/{assessment_id}/submit")
def submit_candidate_assessment(
    assessment_id: int,
    request: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit candidate answers for grading.
    Terminated assessments cannot be submitted again.
    """

    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found."
        )

    if current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(
            Candidate.user_id == current_user.user_id
        ).first()

        if not candidate or assessment.candidate_id != candidate.candidate_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to submit this assessment."
            )

    if assessment.status == "terminated_proctoring":
        raise HTTPException(
            status_code=403,
            detail="This assessment was terminated due to proctoring violations and cannot be submitted."
        )

    return AssessmentService.submit_and_evaluate(
        db,
        assessment_id,
        request.answers,
        current_user
    )


@router.get("/assessment/{assessment_id}/results")
def get_assessment_evaluation_results(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found."
        )

    if current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(
            Candidate.user_id == current_user.user_id
        ).first()

        if not candidate or assessment.candidate_id != candidate.candidate_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized to view this assessment's results."
            )

    return AssessmentService.get_assessment_results(
        db,
        assessment_id
    )


@router.get("/assessment/my-tests")
def get_my_candidate_assessments(
    current_user: User = Depends(require_roles(["job_seeker"])),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.user_id == current_user.user_id
    ).first()

    if not candidate:
        return []

    assessments = db.query(Assessment).filter(
        Assessment.candidate_id == candidate.candidate_id
    ).order_by(
        desc(Assessment.created_at)
    ).all()

    results = []
    has_status_change = False
    now = datetime.utcnow()

    for a in assessments:
        # Check if test expired
        if a.status not in ["completed", "terminated_proctoring"] and is_expired(a.expires_at):
            a.status = "expired"
            has_status_change = True

        results.append({
            "assessment_id": a.assessment_id,
            "test_token": a.test_token,
            "title": a.title,
            "description": getattr(a, "description", None),
            "tech_stack": a.tech_stack,
            "job_id": a.job_id,
            "job_title": a.job.title if a.job else "Position",
            "company_name": a.job.recruiter.company.company_name if a.job and a.job.recruiter and a.job.recruiter.company else "Company",
            "status": a.status,
            "score": a.score,
            "total_questions": a.total_questions,
            "percentage": a.percentage,
            "passed": a.passed,
            "passing_percentage": a.passing_percentage or 60.0,
            "time_limit_minutes": a.time_limit_minutes,
            "created_at": a.created_at,
            "expires_at": a.expires_at,
            "completed_at": a.completed_at
        })

    if has_status_change:
        db.commit()

    return results


# ================= 6. SCREENING & SHORTLISTING =================

@router.get("/screening/jobs/{job_id}/candidates")
def screen_candidates_for_job(
    job_id: int,
    current_user: User = Depends(require_roles(["admin", "recruiter"])),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found."
        )

    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).all()

    applied_candidates_map = {
        app.candidate_id: app for app in applications
    }

    all_candidates = db.query(Candidate).all()
    shortlisted_list = []
    rejected_list = []

    published_template = db.query(AssessmentTemplate).filter(
        AssessmentTemplate.job_id == job_id,
        AssessmentTemplate.status == "published"
    ).first()

    for candidate in all_candidates:
        match_data = MatchingService.calculate_comprehensive_match(
            candidate,
            job
        )

        score = match_data["match_score"]
        is_short = match_data["is_shortlisted"]

        assessment = db.query(Assessment).filter(
            Assessment.candidate_id == candidate.candidate_id,
            Assessment.job_id == job.job_id
        ).first()

        assessment_info = None

        if assessment:
            assessment_info = {
                "assessment_id": assessment.assessment_id,
                "test_token": assessment.test_token,
                "status": assessment.status,
                "score": assessment.score,
                "percentage": assessment.percentage,
                "passed": assessment.passed,
                "passing_percentage": assessment.passing_percentage or 60.0,
                "completed_at": assessment.completed_at
            }

        app_record = applied_candidates_map.get(candidate.candidate_id)

        item = {
            "candidate_id": candidate.candidate_id,
            "application_id": app_record.application_id if app_record else None,
            "name": candidate.user.name if candidate.user else "Unknown Candidate",
            "email": candidate.user.email if candidate.user else "",
            "skills": [s.skill_name for s in candidate.skills],
            "experience": candidate.experience,
            "education": candidate.education,
            "match_score": score,
            "is_shortlisted": is_short,
            "shortlist_status": "Shortlisted" if is_short else "Not Shortlisted",
            "application_status": app_record.status if app_record else "Not Applied",
            "matched_skills": match_data["matched_skills"],
            "missing_skills": match_data["missing_skills"],
            "reasons": match_data["reasons"],
            "breakdown": match_data["breakdown"],
            "assessment": assessment_info,
            "has_recruiter_template": bool(published_template)
        }

        if is_short:
            shortlisted_list.append(item)
        else:
            rejected_list.append(item)

    shortlisted_list.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    rejected_list.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return {
        "job_id": job.job_id,
        "job_title": job.title,
        "required_skills": [s.skill_name for s in job.skills],
        "has_published_template": bool(published_template),
        "template_id": published_template.template_id if published_template else None,
        "total_evaluated": len(shortlisted_list) + len(rejected_list),
        "shortlisted_count": len(shortlisted_list),
        "rejected_count": len(rejected_list),
        "shortlisted_candidates": shortlisted_list,
        "rejected_candidates": rejected_list
    }


@router.post("/screening/jobs/{job_id}/auto-shortlist")
def trigger_auto_shortlisting(
    job_id: int,
    current_user: User = Depends(require_roles(["admin", "recruiter"])),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job posting not found."
        )

    candidates = db.query(Candidate).all()
    shortlisted_results = []
    rejected_results = []

    for candidate in candidates:
        match_data = MatchingService.calculate_comprehensive_match(
            candidate,
            job
        )

        score = match_data["match_score"]
        is_short = score >= 70.0

        app_record = db.query(Application).filter(
            Application.candidate_id == candidate.candidate_id,
            Application.job_id == job.job_id
        ).first()

        if is_short:
            if app_record:
                app_record.status = "Shortlisted"

            assessment = AssessmentService.generate_assessment(
                db=db,
                candidate=candidate,
                job=job,
                application_id=app_record.application_id if app_record else None
            )

            test_link = f"http://localhost:5173/assessment/{assessment.test_token}"

            try:
                EmailService.send_shortlisting_email(
                    db=db,
                    candidate=candidate,
                    job=job,
                    match_percentage=score,
                    reasons=match_data.get("reasons", []),
                    test_link=test_link
                )
            except Exception as e:
                print(f"Notice: Failed to dispatch shortlisting email: {e}")

            shortlisted_results.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.user.name if candidate.user else "Candidate",
                "email": candidate.user.email if candidate.user else "",
                "match_score": score,
                "assessment_id": assessment.assessment_id,
                "test_token": assessment.test_token,
                "test_link": test_link,
                "status": "Shortlisted & Recruiter Assessment Assigned"
            })

        else:
            if app_record and app_record.status == "Applied":
                app_record.status = "Rejected"

            rejected_results.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.user.name if candidate.user else "Candidate",
                "email": candidate.user.email if candidate.user else "",
                "match_score": score,
                "status": "Not Shortlisted (< 70%)"
            })

    db.commit()

    return {
        "message": f"Screening complete. {len(shortlisted_results)} candidates shortlisted (>= 70%) and assigned recruiter assessment.",
        "job_id": job.job_id,
        "job_title": job.title,
        "shortlisted_count": len(shortlisted_results),
        "rejected_count": len(rejected_results),
        "shortlisted_candidates": shortlisted_results,
        "rejected_candidates": rejected_results
    }


@router.post("/screening/candidates/{candidate_id}/generate-test")
def manual_generate_assessment(
    candidate_id: int,
    job_id: int = Query(...),
    current_user: User = Depends(require_roles(["admin", "recruiter"])),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.candidate_id == candidate_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    app_record = db.query(Application).filter(
        Application.candidate_id == candidate_id,
        Application.job_id == job_id
    ).first()

    assessment = AssessmentService.generate_assessment(
        db=db,
        candidate=candidate,
        job=job,
        application_id=app_record.application_id if app_record else None
    )

    return {
        "assessment_id": assessment.assessment_id,
        "test_token": assessment.test_token,
        "test_link": f"http://localhost:5173/assessment/{assessment.test_token}",
        "title": assessment.title,
        "total_questions": assessment.total_questions,
        "time_limit_minutes": assessment.time_limit_minutes,
        "status": assessment.status
    }


@router.get("/screening/dashboard-stats", response_model=ScreeningStatsResponse)
def get_screening_dashboard_telemetry(
    current_user: User = Depends(require_roles(["admin", "recruiter"])),
    db: Session = Depends(get_db)
):
    total_candidates = db.query(Candidate).count()
    total_applications = db.query(Application).count()

    shortlisted_apps = db.query(Application).filter(
        Application.status.in_(["Shortlisted", "Interview", "Selected"])
    ).count()

    rejected_apps = db.query(Application).filter(
        Application.status == "Rejected"
    ).count()

    assessments = db.query(Assessment).all()

    completed_assessments = [
        a for a in assessments if a.status == "completed"
    ]

    pending_assessments = [
        a for a in assessments if a.status in ["pending", "in_progress"]
    ]

    passed_assessments = [
        a for a in assessments if a.passed is True
    ]

    avg_score = 0.0

    if completed_assessments:
        scores = [
            a.percentage for a in completed_assessments
            if a.percentage is not None
        ]

        if scores:
            avg_score = round(
                sum(scores) / len(scores),
                1
            )

    return {
        "total_applicants": total_applications,
        "total_matched": total_candidates,
        "shortlisted_count": shortlisted_apps,
        "rejected_count": rejected_apps,
        "shortlist_threshold": 70.0,
        "awaiting_assessment": len(pending_assessments),
        "assessments_completed": len(completed_assessments),
        "pending_tests": len(pending_assessments),
        "passed_tests": len(passed_assessments),
        "average_assessment_score": avg_score
    }


@router.get("/screening/all-assessments")
def get_all_assessments(
    current_user: User = Depends(require_roles(["admin", "recruiter"])),
    db: Session = Depends(get_db)
):
    assessments = db.query(Assessment).order_by(
        desc(Assessment.created_at)
    ).all()

    records = []

    for a in assessments:
        records.append({
            "assessment_id": a.assessment_id,
            "test_token": a.test_token,
            "title": a.title,
            "tech_stack": a.tech_stack,
            "candidate_id": a.candidate_id,
            "candidate_name": a.candidate.user.name if a.candidate and a.candidate.user else "Candidate",
            "candidate_email": a.candidate.user.email if a.candidate and a.candidate.user else "",
            "job_id": a.job_id,
            "job_title": a.job.title if a.job else "Job",
            "company_name": a.job.recruiter.company.company_name if a.job and a.job.recruiter and a.job.recruiter.company else "Company",
            "status": a.status,
            "score": a.score,
            "total_questions": a.total_questions,
            "percentage": a.percentage,
            "passed": a.passed,
            "passing_percentage": a.passing_percentage or 60.0,
            "created_at": a.created_at,
            "completed_at": a.completed_at
        })

    return records


@router.get("/screening/emails", response_model=List[EmailNotificationResponse])
def get_email_notifications_log(
    current_user: User = Depends(require_roles(["admin", "recruiter"])),
    db: Session = Depends(get_db)
):
    emails = db.query(EmailNotification).order_by(
        desc(EmailNotification.sent_date)
    ).limit(100).all()

    return emails
