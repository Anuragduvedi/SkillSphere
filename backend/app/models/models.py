from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Table, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

# 7. Candidate_Skills Association Table
candidate_skills = Table(
    "candidate_skills",
    Base.metadata,
    Column("candidate_id", Integer, ForeignKey("candidates.candidate_id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), primary_key=True)
)

# 9. Job_Skills Association Table
job_skills = Table(
    "job_skills",
    Base.metadata,
    Column("job_id", Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), primary_key=True)
)

# 1. Users Table
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="job_seeker")  # job_seeker, recruiter, admin
    created_date = Column(DateTime, default=utc_now)
    is_active = Column(Boolean, default=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recruiter = relationship("Recruiter", back_populates="user", uselist=False, cascade="all, delete-orphan")

# 4. Companies Table
class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    contact_info = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)

    # Relationships
    recruiters = relationship("Recruiter", back_populates="company")

# 2. Candidates Table
class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    profile_details = Column(Text, nullable=True)  # JSON or text notes, phone, summary
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="candidate")
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", secondary=candidate_skills, back_populates="candidates")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")

# 3. Recruiters Table
class Recruiter(Base):
    __tablename__ = "recruiters"

    recruiter_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id", ondelete="SET NULL"), nullable=True)
    recruiter_details = Column(Text, nullable=True)
    designation = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="recruiter")
    company = relationship("Company", back_populates="recruiters")
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")

# 6. Skills Table
class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), unique=True, index=True, nullable=False)

    # Relationships
    candidates = relationship("Candidate", secondary=candidate_skills, back_populates="skills")
    jobs = relationship("Job", secondary=job_skills, back_populates="skills")

# 5. Resumes Table
class Resume(Base):
    __tablename__ = "resumes"

    resume_id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)
    upload_date = Column(DateTime, default=utc_now)
    processing_status = Column(String(50), default="Completed")  # Pending, Completed, Failed
    extracted_text = Column(Text, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")
    analyses = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")

# 8. Jobs Table
class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.recruiter_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    experience = Column(String(100), nullable=False)  # e.g., "0-2 years", "3-5 years"
    job_type = Column(String(50), nullable=False, default="Full-time")  # Full-time, Remote, Contract, Part-time
    salary_range = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="active")  # active, closed
    created_date = Column(DateTime, default=utc_now)

    # Relationships
    recruiter = relationship("Recruiter", back_populates="jobs")
    skills = relationship("Skill", secondary=job_skills, back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    analyses = relationship("ResumeAnalysis", back_populates="job", cascade="all, delete-orphan")

# 10. Applications Table
class Application(Base):
    __tablename__ = "applications"

    application_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.resume_id", ondelete="SET NULL"), nullable=True)
    application_date = Column(DateTime, default=utc_now)
    status = Column(String(50), nullable=False, default="Applied")  # Applied, Under Review, Shortlisted, Interview, Selected, Rejected
    cover_note = Column(Text, nullable=True)

    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")

# 11. Resume_Analysis Table
class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    analysis_id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0.0 to 100.0
    matched_skills = Column(Text, nullable=True)  # JSON string or comma-separated list
    missing_skills = Column(Text, nullable=True)  # JSON string or comma-separated list
    recommendations = Column(Text, nullable=True)
    analysis_date = Column(DateTime, default=utc_now)

    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    job = relationship("Job", back_populates="analyses")
