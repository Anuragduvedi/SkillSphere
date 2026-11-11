import pytest
from fastapi import HTTPException
from app.database import SessionLocal
from app.models.models import User, Candidate, Recruiter, Job, Application, Resume, Skill
from app.schemas.schemas import UserRegister, UserLogin, JobCreate, ApplicationStatusUpdate
from app.routers import auth, jobs, applications, recruiter, admin
from app.services.matching_service import MatchingService
from app.services.ocr_service import OCRService

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_resume_matching_algorithm():
    """Test 1: Explainable Resume-to-Job Matching Engine"""
    candidate_skills = ["React", "Python", "FastAPI", "PostgreSQL", "Docker", "Tailwind CSS"]
    required_skills = ["React", "TypeScript", "FastAPI", "Docker", "Kubernetes"]

    result = MatchingService.calculate_match(candidate_skills, required_skills)
    
    assert "React" in result["matched_skills"]
    assert "FastAPI" in result["matched_skills"]
    assert "Docker" in result["matched_skills"]
    assert "TypeScript" in result["missing_skills"]
    assert "Kubernetes" in result["missing_skills"]
    assert result["match_score"] >= 60.0
    assert "recommendations" in result
    assert "Outstanding" in result["recommendations"] or "Promising" in result["recommendations"]

def test_ocr_extraction_and_field_parsing():
    """Test 2: OCR Parser extraction of candidate metadata and skills"""
    sample_raw_text = (
        "Sarah Connor\n"
        "Email: sarah.connor@cyberdyne.io\n"
        "Phone: (555) 019-2834\n"
        "Education: Bachelor of Science in Computer Science, Stanford University\n"
        "Experience: 4 years of experience building resilient cloud microservices.\n"
        "Skills: Python, FastAPI, Docker, Kubernetes, AWS, PostgreSQL, React, Git"
    )

    parsed = OCRService.parse_resume_fields(sample_raw_text)
    assert parsed["name"] == "Sarah Connor"
    assert parsed["email"] == "sarah.connor@cyberdyne.io"
    assert parsed["phone"] == "(555) 019-2834"
    assert "Stanford University" in parsed["education"]
    assert "4 years" in parsed["experience"]
    assert "Python" in parsed["skills"]
    assert "FastAPI" in parsed["skills"]
    assert "Docker" in parsed["skills"]

def test_auth_login_verification(db):
    """Test 3: Authentication verification for valid and invalid credentials"""
    # Valid login
    login_req = UserLogin(email="candidate@skillsphere.com", password="password123")
    res = auth.login(login_req, db)
    assert "access_token" in res
    assert res["user"].role == "job_seeker"
    assert res["user"].email == "candidate@skillsphere.com"

    # Invalid password
    bad_req = UserLogin(email="candidate@skillsphere.com", password="wrong_password")
    with pytest.raises(HTTPException) as exc_info:
        auth.login(bad_req, db)
    assert exc_info.value.status_code == 401

def test_job_listing_and_filtering(db):
    """Test 4: Job listing and multi-parameter filtering"""
    candidate_user = db.query(User).filter(User.email == "candidate@skillsphere.com").first()
    
    # List all active jobs
    all_jobs = jobs.list_jobs(current_user=candidate_user, db=db)
    assert len(all_jobs) >= 4
    for j in all_jobs:
        assert j["title"]
        assert j["company_name"]
        assert isinstance(j["skills"], list)

    # Filter by keyword
    filtered = jobs.list_jobs(keyword="Full-Stack", current_user=candidate_user, db=db)
    assert len(filtered) >= 1
    assert any("Full-Stack" in j["title"] for j in filtered)

def test_duplicate_application_prevention(db):
    """Test 5: Prevention of duplicate job applications by the same candidate"""
    candidate_user = db.query(User).filter(User.email == "candidate@skillsphere.com").first()
    candidate = db.query(Candidate).filter(Candidate.user_id == candidate_user.user_id).first()
    
    # Candidate Alex Rivera already applied to Job 1 in seed data
    first_job = db.query(Job).filter(Job.job_id == 1).first()
    assert first_job is not None

    with pytest.raises(HTTPException) as exc_info:
        applications.apply_to_job(job_id=1, app_in=None, current_user=candidate_user, db=db)
    
    assert exc_info.value.status_code == 400
    assert "duplicate" in exc_info.value.detail.lower()

def test_recruiter_applicant_tracking_and_status_update(db):
    """Test 6: Recruiter ATS applicants retrieval and status modification"""
    recruiter_user = db.query(User).filter(User.email == "recruiter@skillsphere.com").first()
    
    # Fetch applicants for recruiter's posted openings
    applicants = recruiter.get_recruiter_applicants(current_user=recruiter_user, db=db)
    assert len(applicants) >= 1
    target_app = applicants[0]
    app_id = target_app["application_id"]

    # Update status to Shortlisted
    status_update = ApplicationStatusUpdate(status="Shortlisted")
    updated = applications.update_application_status(
        application_id=app_id,
        status_update=status_update,
        current_user=recruiter_user,
        db=db
    )
    assert updated["status"] == "Shortlisted"

def test_admin_analytics_metrics(db):
    """Test 7: Admin platform-wide statistics and metrics overview"""
    admin_user = db.query(User).filter(User.email == "admin@skillsphere.com").first()
    stats = admin.get_platform_analytics(current_user=admin_user, db=db)
    
    assert stats["total_users"] >= 3
    assert stats["total_jobs"] >= 3
    assert stats["total_applications"] >= 2
    assert "status_distribution" in stats
    assert stats["average_match_score"] > 0
