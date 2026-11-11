import os
import io
import pytest
from fastapi import HTTPException
from app.database import SessionLocal
from app.models.models import (
    User, Candidate, Recruiter, Company, Skill, Job, Application, Resume, ResumeAnalysis
)
from app.schemas.schemas import (
    UserRegister, UserLogin, JobCreate, JobUpdate, ApplicationCreate, 
    ApplicationStatusUpdate, CandidateProfileUpdate, AnalyzeRequest
)
from app.routers import auth, resume, jobs, applications, recruiter, admin
from app.services.matching_service import MatchingService
from app.services.ocr_service import OCRService

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

# ================= 1. AUTHENTICATION & RBAC TESTS =================

def test_qa_01_user_registration_and_jwt_tokens(db):
    """QA-01: Verify new user registration, bcrypt hash, and valid JWT generation"""
    email = f"qa.candidate.{os.urandom(4).hex()}@skillsphere.com"
    reg_data = UserRegister(
        name="QA Tester Candidate",
        email=email,
        password="SecurePassword2026!",
        role="job_seeker"
    )
    result = auth.register(reg_data, db)
    
    assert "access_token" in result
    assert result["user"].email == email.lower()
    assert result["user"].role == "job_seeker"
    assert result["user"].is_active is True

    # Verify Candidate record auto-created
    candidate = db.query(Candidate).filter(Candidate.user_id == result["user"].user_id).first()
    assert candidate is not None

def test_qa_02_recruiter_registration_with_company(db):
    """QA-02: Verify recruiter registration auto-links or creates employer company"""
    email = f"qa.recruiter.{os.urandom(4).hex()}@skillsphere.com"
    company_name = f"Apex Quantum Labs {os.urandom(2).hex()}"
    reg_data = UserRegister(
        name="QA Recruiter Lead",
        email=email,
        password="SecurePassword2026!",
        role="recruiter",
        company_name=company_name
    )
    result = auth.register(reg_data, db)
    
    assert result["user"].role == "recruiter"
    recruiter_rec = db.query(Recruiter).filter(Recruiter.user_id == result["user"].user_id).first()
    assert recruiter_rec is not None
    assert recruiter_rec.company.company_name == company_name

def test_qa_03_invalid_login_rejection(db):
    """QA-03: Verify wrong password rejection with HTTP 401 Unauthorized"""
    bad_login = UserLogin(email="candidate@skillsphere.com", password="IncorrectPassword")
    with pytest.raises(HTTPException) as exc:
        auth.login(bad_login, db)
    assert exc.value.status_code == 401
    assert "invalid" in exc.value.detail.lower()

def test_qa_04_role_based_access_control_guard(db):
    """QA-04: Candidate role forbidden from performing recruiter-only actions"""
    candidate_user = db.query(User).filter(User.email == "candidate@skillsphere.com").first()
    job_payload = JobCreate(
        title="Unauthorized Job",
        description="Candidate trying to post job",
        location="Remote",
        experience="2 years",
        job_type="Full-time",
        skills=["Python"]
    )
    # create_job requires role recruiter or admin
    with pytest.raises(HTTPException) as exc:
        jobs.create_job(job_in=job_payload, current_user=candidate_user, db=db)
    # Candidate lacks recruiter record -> 400 or 403
    assert exc.value.status_code in [400, 403]

# ================= 2. OCR EXTRACTION & PROFILE TESTS =================

def test_qa_05_ocr_entity_and_skill_parsing():
    """QA-05: Verify OCR parser extracts contact info, education, and canonical skills accurately"""
    raw_resume = (
        "Jonathan Archer\n"
        "Email: j.archer@starfleet.org\n"
        "Phone: (555) 839-2041\n"
        "Education: Master of Science in Aerospace Engineering, MIT\n"
        "Experience: 5+ years of experience developing mission critical distributed systems.\n"
        "Technical Skills: Python, FastAPI, React, PostgreSQL, Docker, Kubernetes, AWS, Git"
    )
    parsed = OCRService.parse_resume_fields(raw_resume)

    assert parsed["name"] == "Jonathan Archer"
    assert parsed["email"] == "j.archer@starfleet.org"
    assert parsed["phone"] == "(555) 839-2041"
    assert "MIT" in parsed["education"]
    assert "5+ years" in parsed["experience"]
    for expected_skill in ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Git"]:
        assert expected_skill in parsed["skills"]

def test_qa_06_ocr_error_resilience_unsupported_and_empty_files():
    """QA-06: Verify OCR service fails gracefully without crashing on bad inputs"""
    # Unsupported file extension
    text, status, msg = OCRService.extract_text(b"some content", "malicious.bat")
    assert status == "Failed"
    assert "unsupported file extension" in msg.lower()

    # Empty content
    text, status, msg = OCRService.extract_text(b"", "empty.pdf")
    assert status in ["Completed", "Failed"]  # Returns meaningful message without unhandled exception

def test_qa_07_candidate_profile_editing_and_skill_tagging(db):
    """QA-07: Candidate reviews OCR output, modifies fields, and saves verified skills"""
    candidate_user = db.query(User).filter(User.email == "candidate@skillsphere.com").first()
    update_data = CandidateProfileUpdate(
        name="Alex Rivera, Lead Engineer",
        phone="+1 (555) 999-8888",
        location="San Francisco, CA (Open to Remote)",
        education="B.S. in Computer Science - UC Berkeley (Summa Cum Laude)",
        experience="4+ years developing microservices and glassmorphic UI systems.",
        skills=["React", "TypeScript", "Python", "FastAPI", "Docker", "PostgreSQL", "Redis", "GraphQL"]
    )
    res = resume.update_candidate_profile(update_data, current_user=candidate_user, db=db)
    assert res["status"] == "success"

    # Verify persisted in database
    cand_record = db.query(Candidate).filter(Candidate.user_id == candidate_user.user_id).first()
    assert cand_record.phone == "+1 (555) 999-8888"
    assert cand_record.education.startswith("B.S. in Computer Science")
    skill_names = [s.skill_name for s in cand_record.skills]
    assert "GraphQL" in skill_names
    assert "Redis" in skill_names

# ================= 3. MATCHING ALGORITHM & EXPLAINABILITY =================

def test_qa_08_explainable_skill_matching_engine():
    """QA-08: Test multi-vector matching score, matched competencies, skill gaps, and advice"""
    candidate_skills = ["React", "TypeScript", "Tailwind CSS", "Next.js", "Python"]
    job_skills = ["React", "TypeScript", "Tailwind CSS", "Next.js", "GraphQL"]

    match_result = MatchingService.calculate_match(candidate_skills, job_skills)

    # 4 out of 5 matched = 80% + depth bonus
    assert match_result["match_score"] >= 80.0
    assert len(match_result["matched_skills"]) == 4
    assert "GraphQL" in match_result["missing_skills"]
    assert "recommendations" in match_result
    assert len(match_result["recommendations"]) > 20

# ================= 4. JOB SEARCH, APPLICATION & DUPLICATE BLOCKING =================

def test_qa_09_job_multi_parameter_search_matrix(db):
    """QA-09: Verify job catalog search by keyword, location, type, and skill"""
    candidate_user = db.query(User).filter(User.email == "candidate@skillsphere.com").first()
    
    # Filter by job type
    remote_jobs = jobs.list_jobs(job_type="Remote", current_user=candidate_user, db=db)
    for j in remote_jobs:
        assert "remote" in j["job_type"].lower() or "remote" in j["location"].lower()

    # Filter by skill
    python_jobs = jobs.list_jobs(skill="Python", current_user=candidate_user, db=db)
    assert len(python_jobs) > 0
    for j in python_jobs:
        assert any("python" in s.lower() for s in j["skills"])

def test_qa_10_duplicate_application_prevention(db):
    """QA-10: Critical business rule: Candidate cannot submit duplicate applications for same job"""
    candidate_user = db.query(User).filter(User.email == "candidate@skillsphere.com").first()
    candidate = db.query(Candidate).filter(Candidate.user_id == candidate_user.user_id).first()

    # Find job candidate already applied to (Job 1)
    existing_app = db.query(Application).filter(
        Application.candidate_id == candidate.candidate_id,
        Application.job_id == 1
    ).first()
    assert existing_app is not None

    # Attempt to apply again
    with pytest.raises(HTTPException) as exc:
        applications.apply_to_job(job_id=1, app_in=None, current_user=candidate_user, db=db)
    
    assert exc.value.status_code == 400
    assert "duplicate" in exc.value.detail.lower()

def test_qa_11_candidate_application_withdrawal(db):
    """QA-11: Candidate can withdraw active application in Applied/Under Review status"""
    candidate_user = db.query(User).filter(User.email == "candidate@skillsphere.com").first()
    candidate = db.query(Candidate).filter(Candidate.user_id == candidate_user.user_id).first()

    # Find an open job Alex hasn't applied to yet (e.g. Job 5)
    target_job = db.query(Job).filter(Job.job_id == 5, Job.status == "active").first()
    if target_job:
        # Check if already applied
        existing = db.query(Application).filter(
            Application.job_id == target_job.job_id,
            Application.candidate_id == candidate.candidate_id
        ).first()
        if not existing:
            new_app = applications.apply_to_job(job_id=target_job.job_id, app_in=None, current_user=candidate_user, db=db)
            app_id = new_app["application_id"]
            
            # Withdraw application
            withdraw_res = applications.withdraw_application(application_id=app_id, current_user=candidate_user, db=db)
            assert "withdrawn successfully" in withdraw_res["message"].lower()

            # Confirm removed from database
            check_del = db.query(Application).filter(Application.application_id == app_id).first()
            assert check_del is None

# ================= 5. RECRUITER ATS KANBAN & EXPORT =================

def test_qa_12_recruiter_ats_stage_transition(db):
    """QA-12: Recruiter moves candidate between ATS stages (Under Review -> Shortlisted -> Interview)"""
    recruiter_user = db.query(User).filter(User.email == "recruiter@skillsphere.com").first()
    applicants = recruiter.get_recruiter_applicants(current_user=recruiter_user, db=db)
    assert len(applicants) > 0
    target_app = applicants[0]
    app_id = target_app["application_id"]

    for stage in ["Under Review", "Shortlisted", "Interview", "Selected"]:
        update_data = ApplicationStatusUpdate(status=stage)
        updated = applications.update_application_status(
            application_id=app_id,
            status_update=update_data,
            current_user=recruiter_user,
            db=db
        )
        assert updated["status"] == stage

def test_qa_13_recruiter_csv_export(db):
    """QA-13: Recruiter exports applicant dataset as downloadable RFC-compliant CSV"""
    recruiter_user = db.query(User).filter(User.email == "recruiter@skillsphere.com").first()
    response = recruiter.export_applicants_csv(job_id=None, current_user=recruiter_user, db=db)
    
    assert response.status_code == 200
    assert response.media_type == "text/csv"
    assert "attachment; filename=" in response.headers["Content-Disposition"]
    
    csv_text = response.body.decode("utf-8")
    assert "Application ID" in csv_text
    assert "Candidate Name" in csv_text
    assert "Match Score (%)" in csv_text

# ================= 6. ADMIN GOVERNANCE & TELEMETRY =================

def test_qa_14_admin_telemetry_metrics(db):
    """QA-14: Admin receives platform statistics, user breakdowns, and match rates"""
    admin_user = db.query(User).filter(User.email == "admin@skillsphere.com").first()
    telemetry = admin.get_platform_analytics(current_user=admin_user, db=db)
    
    assert telemetry["total_users"] >= 4
    assert telemetry["total_jobs"] >= 4
    assert telemetry["total_applications"] >= 2
    assert telemetry["average_match_score"] > 0
    assert isinstance(telemetry["status_distribution"], dict)

def test_qa_15_admin_user_and_job_moderation(db):
    """QA-15: Admin deactivates/reactivates accounts and toggles job moderation status"""
    admin_user = db.query(User).filter(User.email == "admin@skillsphere.com").first()
    
    # Moderate a job (toggle active <-> closed)
    job = db.query(Job).first()
    orig_status = job.status
    mod_res = admin.moderate_job_status(job_id=job.job_id, current_user=admin_user, db=db)
    expected_toggled = "closed" if orig_status == "active" else "active"
    assert mod_res["status"] == expected_toggled

    # Toggle back to restore
    admin.moderate_job_status(job_id=job.job_id, current_user=admin_user, db=db)
