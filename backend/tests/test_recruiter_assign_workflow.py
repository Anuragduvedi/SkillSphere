import os
import json
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.database import SessionLocal
from app.models.models import (
    User, Candidate, Recruiter, Company, Skill, Job, Application, Assessment, 
    AssessmentQuestion, RecruiterQuestion, AssessmentTemplate
)
from app.schemas.schemas import AssignAssessmentRequest, GenerateAIQuestionsRequest, AssessmentSubmitRequest
from app.routers import assessment as assessment_router
from app.services.assessment_service import AssessmentService

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def setup_workflow_data(db):
    uid = os.urandom(4).hex()

    # Recruiter & Company
    company = Company(
        company_name=f"Workflow Tech Corp {uid}",
        location="Seattle, WA"
    )
    db.add(company)
    db.commit()

    rec_user = User(
        name="Lead Technical Recruiter",
        email=f"recruiter.{uid}@workflowcorp.com",
        password_hash="fakehash",
        role="recruiter"
    )
    db.add(rec_user)
    db.commit()

    recruiter = Recruiter(user_id=rec_user.user_id, company_id=company.company_id)
    db.add(recruiter)
    db.commit()

    # Job: Python Cloud Architect
    job = Job(
        recruiter_id=recruiter.recruiter_id,
        title=f"Cloud Solutions Architect {uid}",
        description="Design and implement scalable Python cloud architectures.",
        location="Remote",
        experience="5+ years",
        job_type="Full-time",
        salary_range="$150,000 - $190,000",
        status="active"
    )
    for s_name in ["Python", "AWS", "Docker", "FastAPI"]:
        s_obj = db.query(Skill).filter(Skill.skill_name == s_name).first()
        if not s_obj:
            s_obj = Skill(skill_name=s_name)
            db.add(s_obj)
            db.commit()
        job.skills.append(s_obj)
    db.add(job)
    db.commit()

    # Candidate 1: Alice (Job Seeker)
    alice_user = User(
        name="Alice Workflow",
        email=f"alice.{uid}@skillsphere.test",
        password_hash="fakehash",
        role="job_seeker"
    )
    db.add(alice_user)
    db.commit()

    alice_candidate = Candidate(
        user_id=alice_user.user_id,
        phone="555-0101",
        location="Seattle, WA",
        experience="4 years cloud backend development",
        education="B.S. Software Engineering"
    )
    for s in job.skills:
        alice_candidate.skills.append(s)
    db.add(alice_candidate)
    db.commit()

    # Candidate 2: Bob (Separate Candidate for Cross-Access Guard)
    bob_user = User(
        name="Bob Intruder",
        email=f"bob.{uid}@skillsphere.test",
        password_hash="fakehash",
        role="job_seeker"
    )
    db.add(bob_user)
    db.commit()

    bob_candidate = Candidate(
        user_id=bob_user.user_id,
        phone="555-0102",
        location="Chicago, IL",
        experience="1 year junior development",
        education="B.A. Graphic Design"
    )
    db.add(bob_candidate)
    db.commit()

    return {
        "recruiter_user": rec_user,
        "recruiter": recruiter,
        "job": job,
        "alice_user": alice_user,
        "alice_candidate": alice_candidate,
        "bob_user": bob_user,
        "bob_candidate": bob_candidate
    }


def test_recruiter_assignable_candidates_endpoint(setup_workflow_data, db):
    """Verify recruiter can query candidates with skills and search filter"""
    data = setup_workflow_data
    results = assessment_router.get_assignable_candidates(
        search="Alice Workflow",
        job_id=None,
        current_user=data["recruiter_user"],
        db=db
    )
    assert len(results) >= 1
    alice_entry = next((c for c in results if c["candidate_id"] == data["alice_candidate"].candidate_id), None)
    assert alice_entry is not None
    assert alice_entry["name"] == "Alice Workflow"
    assert "Python" in alice_entry["skills"]
    assert "assigned_tests" in alice_entry


def test_recruiter_direct_assignment_workflow(setup_workflow_data, db):
    """
    Complete end-to-end recruiter candidate assignment and test-taking lifecycle:
    1. Recruiter creates assignment for Alice
    2. Secure token generated (test_...)
    3. Alice loads test (correct answers hidden)
    4. Bob attempts unauthorized access -> 403 Forbidden
    5. Alice starts test -> in_progress
    6. Alice submits answers -> completed & graded
    7. Alice attempts duplicate submission -> 400 Bad Request
    8. Recruiter tracking dashboard reflects completed assessment & score
    """
    data = setup_workflow_data
    rec_user = data["recruiter_user"]
    alice_user = data["alice_user"]
    bob_user = data["bob_user"]
    alice_cand = data["alice_candidate"]
    job = data["job"]

    # 1. Recruiter assigns assessment directly to candidate
    assign_req = AssignAssessmentRequest(
        candidate_ids=[alice_cand.candidate_id],
        job_id=job.job_id,
        title="Python Cloud Architecture Evaluation",
        description="Comprehensive evaluation covering async programming, cloud patterns, and API architecture.",
        tech_stack="Python",
        duration_minutes=25,
        passing_percentage=60.0,
        expires_days=7,
        send_email=False
    )

    assign_res = assessment_router.assign_assessment_to_candidates(
        request=assign_req,
        current_user=rec_user,
        db=db
    )

    assert assign_res["assigned_count"] == 1
    assignment = assign_res["assignments"][0]
    token = assignment["test_token"]
    assert token.startswith("test_")
    assert "/assessment/test_" in assignment["test_link"]
    assessment_id = assignment["assessment_id"]

    # 2. Candidate fetches test by token
    test_view = assessment_router.get_assessment_by_token(
        token=token,
        current_user=alice_user,
        db=db
    )
    assert test_view["assessment_id"] == assessment_id
    assert test_view["title"] == "Python Cloud Architecture Evaluation"
    assert test_view["time_limit_minutes"] == 25
    assert len(test_view["questions"]) == 20

    # Strict Candidate Security: No answers or explanations leaked
    for q in test_view["questions"]:
        assert "correct_answer" not in q
        assert "explanation" not in q
        assert len(q["options"]) == 4

    # 3. Cross-candidate unauthorized access prevention
    with pytest.raises(HTTPException) as exc_info:
        assessment_router.get_assessment_by_token(
            token=token,
            current_user=bob_user,
            db=db
        )
    assert exc_info.value.status_code == 403
    assert "Unauthorized" in exc_info.value.detail

    # 4. Candidate starts assessment
    start_res = assessment_router.start_assessment(
        assessment_id=assessment_id,
        db=db,
        current_user=alice_user
    )
    assert start_res["status"] == "in_progress"

    # 5. Candidate submits answers
    answers = {str(q["question_id"]): q["options"][0] for q in test_view["questions"]}
    submit_req = AssessmentSubmitRequest(answers=answers)
    submit_res = assessment_router.submit_candidate_assessment(
        assessment_id=assessment_id,
        request=submit_req,
        current_user=alice_user,
        db=db
    )
    assert submit_res["status"] == "completed"
    assert "score" in submit_res
    assert "percentage" in submit_res
    assert submit_res["total_questions"] == 20

    # 6. Duplicate submission prevention
    with pytest.raises(HTTPException) as dup_info:
        assessment_router.submit_candidate_assessment(
            assessment_id=assessment_id,
            request=submit_req,
            current_user=alice_user,
            db=db
        )
    assert dup_info.value.status_code == 400
    assert "already been completed" in dup_info.value.detail.lower()

    # 7. Recruiter tracking dashboard updates
    tracking = assessment_router.get_assigned_assessments_tracking(
        job_id=job.job_id,
        status_filter="all",
        search=None,
        current_user=rec_user,
        db=db
    )
    tracked_item = next((t for t in tracking if t["assessment_id"] == assessment_id), None)
    assert tracked_item is not None
    assert tracked_item["candidate_name"] == "Alice Workflow"
    assert tracked_item["status"] == "completed"
    assert tracked_item["score"] == submit_res["score"]
    assert tracked_item["test_token"] == token


def test_expired_assessment_link_rejection(setup_workflow_data, db):
    """Verify that expired assessment links cannot be accessed, started, or submitted"""
    data = setup_workflow_data
    rec_user = data["recruiter_user"]
    alice_user = data["alice_user"]
    alice_cand = data["alice_candidate"]
    job = data["job"]

    past_date = datetime.utcnow() - timedelta(days=3)
    expired_test = Assessment(
        candidate_id=alice_cand.candidate_id,
        job_id=job.job_id,
        test_token=f"test_expired_{os.urandom(6).hex()}",
        title="Expired Cloud Systems Test",
        tech_stack="Python",
        total_questions=20,
        time_limit_minutes=25,
        passing_percentage=60.0,
        status="pending",
        expires_at=past_date,
        created_at=past_date - timedelta(days=7)
    )
    db.add(expired_test)
    db.commit()
    db.refresh(expired_test)

    # 1. Fetching expired token raises 400
    with pytest.raises(HTTPException) as get_exc:
        assessment_router.get_assessment_by_token(
            token=expired_test.test_token,
            current_user=alice_user,
            db=db
        )
    assert get_exc.value.status_code == 400
    assert "expired" in get_exc.value.detail.lower()

    # 2. Starting expired test raises 400
    with pytest.raises(HTTPException) as start_exc:
        assessment_router.start_assessment(
            assessment_id=expired_test.assessment_id,
            db=db,
            current_user=alice_user
        )
    assert start_exc.value.status_code == 400
    assert "expired" in start_exc.value.detail.lower()

    # 3. Submitting expired test raises 400
    with pytest.raises(HTTPException) as sub_exc:
        assessment_router.submit_candidate_assessment(
            assessment_id=expired_test.assessment_id,
            request=AssessmentSubmitRequest(answers={}),
            current_user=alice_user,
            db=db
        )
    assert sub_exc.value.status_code == 400
    assert "expired" in sub_exc.value.detail.lower()

    # 4. Tracking reflects status as expired
    tracking = assessment_router.get_assigned_assessments_tracking(
        job_id=job.job_id,
        status_filter="all",
        search=None,
        current_user=rec_user,
        db=db
    )
    tracked_item = next((t for t in tracking if t["assessment_id"] == expired_test.assessment_id), None)
    assert tracked_item is not None
    assert tracked_item["status"] == "expired"


def test_ai_question_generator_endpoint(setup_workflow_data, db):
    """Verify AI question generation endpoint works with graceful fallback to Question Bank"""
    data = setup_workflow_data
    rec_user = data["recruiter_user"]

    req = GenerateAIQuestionsRequest(
        role="FastAPI Backend Engineer",
        tech_stack="Python",
        count=5,
        difficulty="intermediate"
    )

    result = assessment_router.generate_questions_ai(
        request=req,
        current_user=rec_user,
        db=db
    )

    assert result["success"] is True
    assert result["count"] == 5
    assert len(result["questions"]) == 5
    assert result["source"] in ["gemini", "question_bank"]

    for q in result["questions"]:
        assert "question_text" in q and len(q["question_text"]) > 5
        assert "options" in q and len(q["options"]) == 4
        assert "correct_answer" in q


def test_auto_shortlisting_fix_verification(setup_workflow_data, db):
    """Verify trigger_auto_shortlisting executes cleanly without TypeError"""
    data = setup_workflow_data
    rec_user = data["recruiter_user"]
    job = data["job"]
    alice_cand = data["alice_candidate"]

    # Ensure application exists
    app_record = db.query(Application).filter(
        Application.candidate_id == alice_cand.candidate_id,
        Application.job_id == job.job_id
    ).first()
    if not app_record:
        app_record = Application(
            candidate_id=alice_cand.candidate_id,
            job_id=job.job_id,
            status="Applied",
            application_date=datetime.utcnow()
        )
        db.add(app_record)
        db.commit()

    # Trigger auto shortlisting
    res = assessment_router.trigger_auto_shortlisting(
        job_id=job.job_id,
        current_user=rec_user,
        db=db
    )

    assert "message" in res
    assert "shortlisted_candidates" in res
    assert res["job_id"] == job.job_id
