import os
import json
import pytest
from datetime import datetime

from app.database import SessionLocal
from app.models.models import (
    User, Candidate, Recruiter, Company, Job, Application, Assessment, AssessmentQuestion, ProctoringEvent
)
from app.routers import assessment as assessment_router
from app.routers import chatbot as chatbot_router
from app.routers.chatbot import ChatRequest
from app.services.chatbot_service import ChatbotService

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def setup_proctoring_test_data(db):
    # Create Recruiter
    company = Company(
        company_name=f"Proctoring Corp {os.urandom(4).hex()}",
        location="Austin, TX"
    )
    db.add(company)
    db.commit()

    rec_user = User(
        name="Proctoring Recruiter",
        email=f"recruiter.{os.urandom(4).hex()}@proctorcorp.com",
        password_hash="fakehash",
        role="recruiter"
    )
    db.add(rec_user)
    db.commit()

    recruiter = Recruiter(user_id=rec_user.user_id, company_id=company.company_id)
    db.add(recruiter)
    db.commit()

    # Job
    job = Job(
        recruiter_id=recruiter.recruiter_id,
        title="Senior Python Backend Architect",
        description="Lead backend development",
        location="Austin, TX",
        experience="5+ years",
        job_type="Full-time",
        salary_range="$140k - $180k",
        status="active"
    )
    db.add(job)
    db.commit()

    # Candidate
    cand_user = User(
        name="Candidate John Doe",
        email=f"candidate.{os.urandom(4).hex()}@proctorcand.com",
        password_hash="fakehash",
        role="job_seeker"
    )
    db.add(cand_user)
    db.commit()

    candidate = Candidate(
        user_id=cand_user.user_id,
        phone="+1234567890",
        location="Austin, TX"
    )
    db.add(candidate)
    db.commit()

    # Application
    application = Application(
        job_id=job.job_id,
        candidate_id=candidate.candidate_id,
        status="Screening",
        application_date=datetime.utcnow()
    )
    db.add(application)
    db.commit()

    # Assessment
    test_token = f"tok_proctor_{os.urandom(6).hex()}"
    assessment = Assessment(
        application_id=application.application_id,
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        test_token=test_token,
        title="Python & Security Assessment",
        tech_stack="Python, FastAPI",
        total_questions=2,
        time_limit_minutes=25,
        status="in_progress",
        passing_percentage=60.0,
        started_at=datetime.utcnow()
    )
    db.add(assessment)
    db.commit()

    # Add 2 questions
    q1 = AssessmentQuestion(
        assessment_id=assessment.assessment_id,
        question_text="What is a FastAPI dependency?",
        skill_category="FastAPI",
        difficulty="beginner",
        options=json.dumps(["A callable", "A variable", "A decorator", "A database"]),
        correct_answer="A callable",
        explanation="Depends takes a callable",
        order_index=1
    )
    q2 = AssessmentQuestion(
        assessment_id=assessment.assessment_id,
        question_text="What status code is Unauthorized?",
        skill_category="HTTP",
        difficulty="beginner",
        options=json.dumps(["200", "401", "403", "404"]),
        correct_answer="401",
        explanation="401 is Unauthorized",
        order_index=2
    )
    db.add_all([q1, q2])
    db.commit()

    return {
        "candidate_user": cand_user,
        "candidate": candidate,
        "recruiter_user": rec_user,
        "recruiter": recruiter,
        "job": job,
        "assessment": assessment,
        "q1": q1,
        "q2": q2
    }

# ================= 1. CHATBOT TESTS =================

def test_chatbot_service_knowledge_fallback():
    """Verify chatbot returns intelligent contextual answers when Gemini API key is unset"""
    resp = ChatbotService.get_response("How does proctoring work and what is the three strike policy?")
    assert "Three-Strike" in resp["reply"] or "proctoring" in resp["reply"].lower()
    assert resp["provider"] == "skillsphere_assistant"

def test_chatbot_service_camera_help():
    """Verify chatbot provides camera troubleshooting tips"""
    resp = ChatbotService.get_response("My camera is not working, what should I do?")
    assert "Camera" in resp["reply"] or "permission" in resp["reply"].lower()

def test_chatbot_router_endpoints():
    """Verify chatbot router status and message endpoints"""
    stat = chatbot_router.get_chatbot_status()
    assert stat["status"] == "online"

    req = ChatRequest(message="What is the passing score for technical assessments?", history=[])
    res = chatbot_router.send_chat_message(req)
    assert "60%" in res["reply"] or "passing" in res["reply"].lower()
    assert "timestamp" in res

# ================= 2. PROCTORING & THREE-STRIKE TESTS =================

def test_proctoring_strike_one_and_debouncing(setup_proctoring_test_data, db):
    """Verify Strike 1 is recorded, and immediate duplicate events are debounced"""
    data = setup_proctoring_test_data
    aid = data["assessment"].assessment_id
    cand_user = data["candidate_user"]

    # First violation -> Strike 1
    res1 = assessment_router.record_proctoring_event(
        assessment_id=aid,
        payload={
            "event_type": "face_not_detected",
            "details": "Face absent from camera frame for 3 seconds",
            "answers": {str(data["q1"].question_id): "A callable"}
        },
        db=db,
        current_user=cand_user
    )

    assert res1["strikes"] == 1
    assert res1["terminated"] is False

    # Immediate second call with identical event_type -> debounced!
    res_dup = assessment_router.record_proctoring_event(
        assessment_id=aid,
        payload={
            "event_type": "face_not_detected",
            "details": "Face absent from camera frame for 3 seconds"
        },
        db=db,
        current_user=cand_user
    )

    assert res_dup.get("duplicate") is True
    assert res_dup["strikes"] == 1  # Strike was NOT incremented

def test_proctoring_strike_two_and_three_auto_submission(setup_proctoring_test_data, db):
    """Verify Strike 2 issues warning, Strike 3 terminates & auto-submits with answers saved and scored"""
    data = setup_proctoring_test_data
    aid = data["assessment"].assessment_id
    cand_user = data["candidate_user"]

    # Strike 2 (different event type to bypass 8s debounce)
    res2 = assessment_router.record_proctoring_event(
        assessment_id=aid,
        payload={
            "event_type": "tab_switch",
            "details": "Candidate switched away from browser tab",
            "answers": {str(data["q1"].question_id): "A callable"}
        },
        db=db,
        current_user=cand_user
    )

    assert res2["strikes"] == 2
    assert res2["terminated"] is False

    # Strike 3 (Final termination & auto-submission)
    res3 = assessment_router.record_proctoring_event(
        assessment_id=aid,
        payload={
            "event_type": "multiple_faces",
            "details": "2 faces detected in frame",
            "answers": {
                str(data["q1"].question_id): "A callable",
                str(data["q2"].question_id): "401"
            }
        },
        db=db,
        current_user=cand_user
    )

    assert res3["strikes"] == 3
    assert res3["terminated"] is True
    assert res3["auto_submitted"] is True
    assert res3["status"] == "terminated_proctoring"
    assert res3["score"] == 2.0  # Both answered questions were scored and preserved!

    # DB persistence check
    db.expire_all()
    ass = db.query(Assessment).filter(Assessment.assessment_id == aid).first()
    assert ass.status == "terminated_proctoring"
    assert ass.violation_count == 3
    assert ass.auto_submitted_proctoring is True
    assert "multiple_faces" in ass.proctoring_submission_reason

def test_recruiter_proctoring_reports(setup_proctoring_test_data, db):
    """Verify recruiters can retrieve candidate proctoring reports and timeline"""
    data = setup_proctoring_test_data
    aid = data["assessment"].assessment_id
    rec_user = data["recruiter_user"]

    reports = assessment_router.get_proctoring_reports(
        job_id=None,
        risk_level=None,
        status_filter=None,
        current_user=rec_user,
        db=db
    )

    assert len(reports) >= 1
    target = next((r for r in reports if r["assessment_id"] == aid), None)
    assert target is not None
    assert target["strikes"] == 3
    assert target["risk_level"] == "Terminated"
    assert target["auto_submitted_proctoring"] is True

    # Timeline check
    timeline = assessment_router.get_assessment_proctoring_events(
        assessment_id=aid,
        current_user=rec_user,
        db=db
    )
    assert len(timeline) >= 3
    event_types = [e["event_type"] for e in timeline]
    assert "face_not_detected" in event_types
    assert "tab_switch" in event_types
    assert "multiple_faces" in event_types


def test_proctoring_instant_terminate_sustained_multiple_faces(db):
    """Verify that sustained multiple faces triggers instant termination without needing 3 prior strikes"""
    # Create distinct candidate and assessment
    user = User(
        name="Multi Face Candidate",
        email=f"multiface.{os.urandom(4).hex()}@test.com",
        password_hash="hash",
        role="job_seeker"
    )
    db.add(user)
    db.commit()

    cand = Candidate(user_id=user.user_id)
    db.add(cand)
    db.commit()

    ass = Assessment(
        candidate_id=cand.candidate_id,
        test_token=f"tok_mf_{os.urandom(6).hex()}",
        title="Security Exam",
        tech_stack="Python",
        total_questions=1,
        time_limit_minutes=20,
        status="in_progress",
        passing_percentage=60.0,
        started_at=datetime.utcnow()
    )
    db.add(ass)
    db.commit()

    q = AssessmentQuestion(
        assessment_id=ass.assessment_id,
        question_text="Sample Q",
        skill_category="Python",
        difficulty="beginner",
        options=json.dumps(["A", "B", "C", "D"]),
        correct_answer="A",
        explanation="Explanation A",
        order_index=1
    )
    db.add(q)
    db.commit()

    # Instant terminate on sustained multiple faces
    res = assessment_router.record_proctoring_event(
        assessment_id=ass.assessment_id,
        payload={
            "event_type": "multiple_faces",
            "details": "2 faces detected continuously for >2s",
            "instant_terminate": True,
            "severity": "critical",
            "confidence": 0.88,
            "answers": {str(q.question_id): "A"}
        },
        db=db,
        current_user=user
    )

    assert res["terminated"] is True
    assert res["auto_submitted"] is True
    assert res["strikes"] == 3
    assert res["status"] == "terminated_proctoring"
    assert res["score"] == 1.0  # Answer preserved and scored

    # DB verify
    db.expire_all()
    reloaded = db.query(Assessment).filter(Assessment.assessment_id == ass.assessment_id).first()
    assert reloaded.status == "terminated_proctoring"
    assert reloaded.auto_submitted_proctoring is True
    assert "Immediate examination termination" in reloaded.proctoring_submission_reason


def test_proctoring_already_terminated_idempotency(db):
    """Verify that calls to an already-terminated assessment safely return terminated status without error"""
    user = User(
        name="Terminated Cand",
        email=f"term.{os.urandom(4).hex()}@test.com",
        password_hash="hash",
        role="job_seeker"
    )
    db.add(user)
    db.commit()

    cand = Candidate(user_id=user.user_id)
    db.add(cand)
    db.commit()

    ass = Assessment(
        candidate_id=cand.candidate_id,
        test_token=f"tok_term_{os.urandom(6).hex()}",
        title="Terminated Exam",
        status="terminated_proctoring",
        auto_submitted_proctoring=True,
        violation_count=3
    )
    db.add(ass)
    db.commit()

    res = assessment_router.record_proctoring_event(
        assessment_id=ass.assessment_id,
        payload={
            "event_type": "phone_detected",
            "details": "Phone visible"
        },
        db=db,
        current_user=user
    )

    assert res["terminated"] is True
    assert res["auto_submitted"] is True
    assert res["strikes"] == 3
    assert res["message"] == "Assessment already terminated"
