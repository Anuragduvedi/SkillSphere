import os
import json
import pytest
from fastapi import HTTPException
from app.database import SessionLocal
from app.models.models import (
    User, Candidate, Recruiter, Company, Skill, Job, Application, Assessment, AssessmentQuestion, EmailNotification,
    RecruiterQuestion, AssessmentTemplate
)
from app.schemas.schemas import (
    AssessmentSubmitRequest, RecruiterQuestionCreate, RecruiterQuestionUpdate,
    AssessmentTemplateCreate, AssessmentTemplateUpdate
)
from app.services.matching_service import MatchingService
from app.services.assessment_service import AssessmentService
from app.services.email_service import EmailService
from app.routers import assessment as assessment_router

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def test_setup(db):
    """Create fresh job, recruiter, and candidate for assessment testing"""
    # Recruiter & Company with unique name
    company = Company(
        company_name=f"Test Screening Corp {os.urandom(4).hex()}",
        location="San Francisco, CA"
    )
    db.add(company)
    db.commit()

    rec_user = User(
        name="Screening Recruiter",
        email=f"recruiter.{os.urandom(4).hex()}@testcorp.com",
        password_hash="fakehash",
        role="recruiter"
    )
    db.add(rec_user)
    db.commit()

    recruiter = Recruiter(user_id=rec_user.user_id, company_id=company.company_id)
    db.add(recruiter)
    db.commit()

    # Job: Python FastAPI Backend Engineer
    job = Job(
        recruiter_id=recruiter.recruiter_id,
        title="Senior Python Backend Engineer",
        description="Looking for senior Python developers with FastAPI, Docker, and PostgreSQL experience.",
        location="Remote",
        experience="3-5 years",
        job_type="Full-time"
    )
    # Skills
    for s_name in ["Python", "FastAPI", "Docker", "PostgreSQL"]:
        s_obj = db.query(Skill).filter(Skill.skill_name == s_name).first()
        if not s_obj:
            s_obj = Skill(skill_name=s_name)
            db.add(s_obj)
            db.commit()
        job.skills.append(s_obj)
    db.add(job)
    db.commit()

    # Candidate 1: High match (Python + FastAPI + Docker + PostgreSQL, 4 years exp)
    user1 = User(
        name="Alice Pythonista",
        email=f"alice.{os.urandom(4).hex()}@gmail.com",
        password_hash="fakehash",
        role="job_seeker"
    )
    db.add(user1)
    db.commit()

    cand1 = Candidate(
        user_id=user1.user_id,
        experience="4 years in backend microservices",
        education="B.Tech Computer Science",
        profile_details="Built scalable REST APIs using FastAPI and Python."
    )
    for s_name in ["Python", "FastAPI", "Docker", "PostgreSQL"]:
        s_obj = db.query(Skill).filter(Skill.skill_name == s_name).first()
        cand1.skills.append(s_obj)
    db.add(cand1)
    db.commit()

    # Candidate 2: Low match (only HTML, CSS, 0.5 years exp)
    user2 = User(
        name="Bob Junior",
        email=f"bob.{os.urandom(4).hex()}@gmail.com",
        password_hash="fakehash",
        role="job_seeker"
    )
    db.add(user2)
    db.commit()

    cand2 = Candidate(
        user_id=user2.user_id,
        experience="Fresher (6 months intern)",
        education="High School Diploma",
        profile_details="Basic website editing."
    )
    for s_name in ["HTML", "CSS"]:
        s_obj = db.query(Skill).filter(Skill.skill_name == s_name).first()
        if not s_obj:
            s_obj = Skill(skill_name=s_name)
            db.add(s_obj)
            db.commit()
        cand2.skills.append(s_obj)
    db.add(cand2)
    db.commit()

    return {
        "job": job,
        "cand1": cand1,
        "cand2": cand2,
        "user1": user1,
        "user2": user2,
        "rec_user": rec_user
    }

# ================= 1. CANDIDATE PROFILE ANALYSIS & MATCHING =================

def test_comprehensive_matching_algorithm(test_setup):
    """Test AI multi-vector matching score calculation & 70% shortlisting criteria"""
    job = test_setup["job"]
    cand1 = test_setup["cand1"]
    cand2 = test_setup["cand2"]

    # Candidate 1 should match >= 70% and be shortlisted
    match1 = MatchingService.calculate_comprehensive_match(cand1, job)
    assert match1["match_score"] >= 70.0
    assert match1["is_shortlisted"] is True
    assert len(match1["matched_skills"]) >= 3
    assert any("70.0% benchmark" in r for r in match1["reasons"])

    # Candidate 2 should match < 70% and NOT be shortlisted
    match2 = MatchingService.calculate_comprehensive_match(cand2, job)
    assert match2["match_score"] < 70.0
    assert match2["is_shortlisted"] is False
    assert len(match2["missing_skills"]) >= 2
    assert any("falling below the 70.0%" in r for r in match2["reasons"])

# ================= 2. AUTOMATED 20-QUESTION TECHNICAL TEST GENERATION =================

def test_generate_20_question_assessment(db, test_setup):
    """Test generating exactly 20 tailored questions with beginner, intermediate, advanced mix"""
    job = test_setup["job"]
    cand1 = test_setup["cand1"]

    assessment = AssessmentService.generate_assessment(
        db=db,
        candidate=cand1,
        job=job,
        time_limit_minutes=25
    )

    assert assessment.assessment_id is not None
    assert assessment.test_token.startswith("test_")
    assert assessment.total_questions == 20
    assert len(assessment.questions) == 20

    # Verify difficulty mix (beginner, intermediate, advanced)
    difficulties = [q.difficulty for q in assessment.questions]
    assert "beginner" in difficulties
    assert "intermediate" in difficulties
    assert "advanced" in difficulties

    # Verify each question has 4 options and 1 valid correct answer
    for q in assessment.questions:
        options = json.loads(q.options)
        assert len(options) == 4
        assert q.correct_answer in options
        assert len(q.question_text) > 10

# ================= 3. TEST ACCESS PRIVACY & CANDIDATE AUTH =================

def test_assessment_candidate_view_security(db, test_setup):
    """Verify that candidate view does not leak correct answers and prevents unauthorized access"""
    job = test_setup["job"]
    cand1 = test_setup["cand1"]
    user1 = test_setup["user1"]
    user2 = test_setup["user2"]

    assessment = db.query(Assessment).filter(Assessment.candidate_id == cand1.candidate_id).first()
    assert assessment is not None

    # Candidate 1 (owner) accesses test
    candidate_view = AssessmentService.get_assessment_for_candidate(db, assessment.test_token, user1)
    assert candidate_view["assessment_id"] == assessment.assessment_id
    assert len(candidate_view["questions"]) == 20

    # Ensure answers and explanations are NOT leaked in candidate view
    for q in candidate_view["questions"]:
        assert "correct_answer" not in q
        assert "explanation" not in q

    # Candidate 2 (unauthorized) attempts to access Candidate 1's test token -> 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        AssessmentService.get_assessment_for_candidate(db, assessment.test_token, user2)
    assert exc_info.value.status_code == 403

# ================= 4. TEST SUBMISSION, EVALUATION & APPLICATION STATUS UPDATE =================

def test_assessment_evaluation_and_anti_duplicate(db, test_setup):
    """Verify automatic scoring out of 20, percentage calculation, status progression, and duplicate prevention"""
    cand1 = test_setup["cand1"]
    job = test_setup["job"]
    user1 = test_setup["user1"]

    # Create application for cand1
    app = Application(
        candidate_id=cand1.candidate_id,
        job_id=job.job_id,
        status="Shortlisted"
    )
    db.add(app)
    db.commit()

    assessment = db.query(Assessment).filter(Assessment.candidate_id == cand1.candidate_id).first()
    assessment.application_id = app.application_id
    db.commit()

    # Prepare answers: 16 correct, 4 incorrect (80% score)
    submitted_answers = {}
    for idx, q in enumerate(assessment.questions):
        if idx < 16:
            submitted_answers[str(q.question_id)] = q.correct_answer
        else:
            submitted_answers[str(q.question_id)] = "Wrong Answer"

    res = AssessmentService.submit_and_evaluate(
        db=db,
        assessment_id=assessment.assessment_id,
        submitted_answers=submitted_answers,
        user=user1
    )

    assert res["status"] == "completed"
    assert res["score"] == 16.0
    assert res["total_questions"] == 20
    assert res["percentage"] == 80.0
    assert res["passed"] is True
    assert res["correct_answers_count"] == 16
    assert res["incorrect_answers_count"] == 4

    # Verify application status advanced to 'Interview' on pass
    db.refresh(app)
    assert app.status == "Interview"

    # Attempt duplicate submission -> Should raise 400 Bad Request
    with pytest.raises(HTTPException) as exc_dup:
        AssessmentService.submit_and_evaluate(
            db=db,
            assessment_id=assessment.assessment_id,
            submitted_answers=submitted_answers,
            user=user1
        )
    assert exc_dup.value.status_code == 400

# ================= 5. EMAIL NOTIFICATIONS AUDIT =================

def test_email_notifications_logged(db, test_setup):
    """Verify that automated emails are stored in database audit log"""
    cand1 = test_setup["cand1"]
    job = test_setup["job"]

    emails = db.query(EmailNotification).filter(EmailNotification.recipient_email == cand1.user.email).all()
    assert len(emails) >= 1
    email_types = [e.email_type for e in emails]
    # Should include test invitation or submission confirmation
    assert any(t in ["test_invitation", "test_submission", "shortlisting"] for t in email_types)

# ================= 6. SCREENING ROUTER TELEMETRY & BATCH SHORTLISTING =================

def test_screening_router_endpoints(db, test_setup):
    """Verify /screening/jobs/{job_id}/candidates categorizes shortlisted vs rejected candidates"""
    job = test_setup["job"]
    rec_user = test_setup["rec_user"]

    result = assessment_router.screen_candidates_for_job(job.job_id, rec_user, db)
    assert "shortlisted_candidates" in result
    assert "rejected_candidates" in result
    assert result["total_evaluated"] >= 2
    # Shortlisted candidates must all have score >= 70
    for c in result["shortlisted_candidates"]:
        assert c["match_score"] >= 70.0
        assert c["is_shortlisted"] is True
    # Rejected candidates must all have score < 70
    for c in result["rejected_candidates"]:
        assert c["match_score"] < 70.0
        assert c["is_shortlisted"] is False

# ================= 7. RECRUITER QUESTION MANAGEMENT TESTS =================

def test_recruiter_question_crud_and_validation(db, test_setup):
    """Verify recruiter can create questions with 4 options, edit, and delete with RBAC"""
    rec_user = test_setup["rec_user"]
    recruiter = rec_user.recruiter

    # 1. Reject invalid options count (!= 4)
    with pytest.raises(HTTPException) as exc_opt:
        AssessmentService.create_recruiter_question(db, recruiter.recruiter_id, {
            "technology": "Python",
            "difficulty": "beginner",
            "question_text": "Invalid question with only 2 options?",
            "options": ["Option 1", "Option 2"],
            "correct_answer": "Option 1"
        })
    assert exc_opt.value.status_code == 400

    # 2. Reject correct answer not present in options
    with pytest.raises(HTTPException) as exc_ans:
        AssessmentService.create_recruiter_question(db, recruiter.recruiter_id, {
            "technology": "Python",
            "difficulty": "beginner",
            "question_text": "What is Python?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "E"
        })
    assert exc_ans.value.status_code == 400

    # 3. Valid question creation
    created = AssessmentService.create_recruiter_question(db, recruiter.recruiter_id, {
        "technology": "Python",
        "difficulty": "intermediate",
        "question_text": "What does GIL stand for in CPython implementation?",
        "options": [
            "Global Interpreter Lock",
            "General Interface Layer",
            "Graphical Index Library",
            "Generic Iteration Loop"
        ],
        "correct_answer": "Global Interpreter Lock",
        "explanation": "GIL ensures only one thread executes Python bytecode at once."
    })
    assert created.question_id is not None
    assert created.technology == "Python"
    assert created.correct_answer == "Global Interpreter Lock"

    # 4. Edit question
    updated = AssessmentService.update_recruiter_question(db, created.question_id, recruiter.recruiter_id, {
        "difficulty": "advanced",
        "explanation": "Updated explanation for GIL."
    })
    assert updated.difficulty == "advanced"
    assert updated.explanation == "Updated explanation for GIL."

    # 5. Unauthorized modification attempt by another user
    other_user = test_setup["user1"]
    with pytest.raises(HTTPException) as exc_auth:
        AssessmentService.update_recruiter_question(db, created.question_id, recruiter_id=99999, data={"difficulty": "beginner"}, is_admin=False)
    assert exc_auth.value.status_code == 403

    # 6. Delete question
    del_res = AssessmentService.delete_recruiter_question(db, created.question_id, recruiter.recruiter_id)
    assert del_res is True

# ================= 8. RECRUITER ASSESSMENT TEMPLATE LIFECYCLE (DRAFT & PUBLISHED) =================

def test_recruiter_assessment_template_lifecycle(db, test_setup):
    """Verify draft creation, 20-question requirement on publish, and publication state"""
    rec_user = test_setup["rec_user"]
    recruiter = rec_user.recruiter

    # Create dedicated job for lifecycle testing
    job_qa = Job(
        recruiter_id=recruiter.recruiter_id,
        title=f"Cloud Backend QA {os.urandom(3).hex()}",
        description="Testing recruiter assessment template lifecycle",
        location="Remote",
        experience="2-4 years",
        job_type="Full-time"
    )
    db.add(job_qa)
    db.commit()
    test_setup["job_qa"] = job_qa

    # Import questions into recruiter's question bank
    imported = AssessmentService.import_library_questions(db, recruiter.recruiter_id, technology="Python", count=25, job_id=job_qa.job_id)
    assert len(imported) >= 20
    q_ids = [q.question_id for q in imported]

    # 1. Create a draft template with 10 questions (draft allows < 20)
    draft_template = AssessmentService.create_assessment_template(db, recruiter.recruiter_id, {
        "job_id": job_qa.job_id,
        "title": "Backend Python Evaluation (Draft)",
        "tech_stack": "Python / FastAPI",
        "duration_minutes": 30,
        "passing_percentage": 65.0,
        "status": "draft",
        "question_ids": q_ids[:10]
    })
    assert draft_template.template_id is not None
    assert draft_template.status == "draft"
    assert len(json.loads(draft_template.question_ids)) == 10

    # 2. Attempt to publish template with < 20 questions -> Must raise 400 Bad Request
    with pytest.raises(HTTPException) as exc_pub:
        AssessmentService.publish_assessment_template(db, draft_template.template_id, recruiter.recruiter_id)
    assert exc_pub.value.status_code == 400
    assert "20 questions" in exc_pub.value.detail

    # 3. Update template to select exactly 20 questions
    updated = AssessmentService.update_assessment_template(db, draft_template.template_id, recruiter.recruiter_id, {
        "question_ids": q_ids[:20]
    })
    assert len(json.loads(updated.question_ids)) == 20

    # 4. Now publish succeeds
    published = AssessmentService.publish_assessment_template(db, draft_template.template_id, recruiter.recruiter_id)
    assert published.status == "published"
    assert published.duration_minutes == 30
    assert published.passing_percentage == 65.0

# ================= 9. CANDIDATE RECEIVES RECRUITER-ASSIGNED QUESTIONS =================

def test_candidate_receives_recruiter_assigned_questions(db, test_setup):
    """Verify that shortlisted candidate gets strictly the 20 questions chosen by the recruiter"""
    job_qa = test_setup["job_qa"]
    cand1 = test_setup["cand1"]

    # Generate assessment for candidate for job_qa
    cand_assessment = AssessmentService.generate_assessment(db, candidate=cand1, job=job_qa)
    assert cand_assessment.template_id is not None
    assert cand_assessment.time_limit_minutes == 30
    assert cand_assessment.passing_percentage == 65.0
    assert len(cand_assessment.questions) == 20

    # Verify questions match the template's question IDs
    template = db.query(AssessmentTemplate).filter(AssessmentTemplate.template_id == cand_assessment.template_id).first()
    template_q_ids = json.loads(template.question_ids)
    template_questions = db.query(RecruiterQuestion).filter(RecruiterQuestion.question_id.in_(template_q_ids)).all()
    template_texts = {q.question_text for q in template_questions}

    for cq in cand_assessment.questions:
        assert cq.question_text in template_texts

# ================= 10. RECRUITER & ADMIN ASSESSMENT TELEMETRY =================

def test_recruiter_and_admin_telemetry(db, test_setup):
    """Verify recruiter and admin stats endpoints report accurate question & assessment counts"""
    rec_user = test_setup["rec_user"]
    recruiter = rec_user.recruiter

    rec_stats = AssessmentService.get_recruiter_stats(db, recruiter.recruiter_id)
    assert rec_stats["total_questions"] >= 20
    assert rec_stats["published_assessments"] >= 1

    admin_stats = AssessmentService.get_admin_stats(db)
    assert admin_stats["total_questions"] >= 20
    assert admin_stats["total_templates"] >= 1
    assert len(admin_stats["job_statistics"]) >= 1

