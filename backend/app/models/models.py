from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
    Table,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ==========================================
# MANY-TO-MANY ASSOCIATION TABLES
# ==========================================

candidate_skills = Table(
    "candidate_skills",
    Base.metadata,
    Column("candidate_id", Integer, ForeignKey("candidates.candidate_id")),
    Column("skill_id", Integer, ForeignKey("skills.skill_id")),
)

job_skills = Table(
    "job_skills",
    Base.metadata,
    Column("job_id", Integer, ForeignKey("jobs.job_id")),
    Column("skill_id", Integer, ForeignKey("skills.skill_id")),
)


# ==========================================
# USER MODEL
# ==========================================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(50), default="job_seeker")
    created_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)

    candidate = relationship(
        "Candidate",
        back_populates="user",
        uselist=False,
    )

    recruiter = relationship(
        "Recruiter",
        back_populates="user",
        uselist=False,
    )

    @property
    def candidate_profile(self):
        return self.candidate

    @property
    def recruiter_profile(self):
        return self.recruiter


# ==========================================
# COMPANY MODEL
# ==========================================

class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255))
    description = Column(Text)
    contact_info = Column(String(255))
    website = Column(String(255))
    location = Column(String(255))

    recruiters = relationship(
        "Recruiter",
        back_populates="company",
    )


# ==========================================
# CANDIDATE MODEL
# ==========================================

class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    profile_details = Column(Text)
    phone = Column(String(50))
    location = Column(String(255))
    education = Column(Text)
    experience = Column(Text)

    user = relationship(
        "User",
        back_populates="candidate",
    )

    skills = relationship(
        "Skill",
        secondary=candidate_skills,
        back_populates="candidates",
    )

    applications = relationship(
        "Application",
        back_populates="candidate",
    )

    resumes = relationship(
        "Resume",
        back_populates="candidate",
    )

    assessments = relationship(
        "Assessment",
        back_populates="candidate",
    )

    email_notifications = relationship(
        "EmailNotification",
        back_populates="candidate",
    )

    @property
    def candidate_skills(self):
        return self.skills

    @property
    def resume_analysis(self):
        results = []
        for resume in self.resumes:
            results.extend(resume.analyses)
        return results

    @property
    def resume_analyses(self):
        return self.resume_analysis


# ==========================================
# RECRUITER MODEL
# ==========================================

class Recruiter(Base):
    __tablename__ = "recruiters"

    recruiter_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    recruiter_details = Column(Text)
    designation = Column(String(150))
    phone = Column(String(50))

    user = relationship(
        "User",
        back_populates="recruiter",
    )

    company = relationship(
        "Company",
        back_populates="recruiters",
    )

    jobs = relationship(
        "Job",
        back_populates="recruiter",
    )

    recruiter_questions = relationship(
        "RecruiterQuestion",
        back_populates="recruiter",
    )

    assessment_templates = relationship(
        "AssessmentTemplate",
        back_populates="recruiter",
    )


# ==========================================
# SKILL MODEL
# ==========================================

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100))

    candidates = relationship(
        "Candidate",
        secondary=candidate_skills,
        back_populates="skills",
    )

    jobs = relationship(
        "Job",
        secondary=job_skills,
        back_populates="skills",
    )


# ==========================================
# JOB MODEL
# ==========================================

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.recruiter_id"))
    title = Column(String(255))
    description = Column(Text)
    location = Column(String(255))
    experience = Column(String(100))
    job_type = Column(String(50))
    salary_range = Column(String(100))
    status = Column(String(50), default="active")
    created_date = Column(DateTime)

    recruiter = relationship(
        "Recruiter",
        back_populates="jobs",
    )

    skills = relationship(
        "Skill",
        secondary=job_skills,
        back_populates="jobs",
    )

    applications = relationship(
        "Application",
        back_populates="job",
    )

    assessments = relationship(
        "Assessment",
        back_populates="job",
    )

    resumes_analysis = relationship(
        "ResumeAnalysis",
        back_populates="job",
    )

    assessment_templates = relationship(
        "AssessmentTemplate",
        back_populates="job",
    )

    recruiter_questions = relationship(
        "RecruiterQuestion",
        back_populates="job",
    )

    email_notifications = relationship(
        "EmailNotification",
        back_populates="job",
    )

    @property
    def company(self):
        return self.recruiter.company if self.recruiter else None


# ==========================================
# RESUME MODEL
# ==========================================

class Resume(Base):
    __tablename__ = "resumes"

    resume_id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(String(50))
    upload_date = Column(DateTime)
    processing_status = Column(String(50))
    extracted_text = Column(Text)

    candidate = relationship(
        "Candidate",
        back_populates="resumes",
    )

    analyses = relationship(
        "ResumeAnalysis",
        back_populates="resume",
    )


# ==========================================
# APPLICATION MODEL
# ==========================================

class Application(Base):
    __tablename__ = "applications"

    application_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    resume_id = Column(Integer, ForeignKey("resumes.resume_id"))
    application_date = Column(DateTime)
    status = Column(String(50))
    cover_note = Column(Text)

    candidate = relationship(
        "Candidate",
        back_populates="applications",
    )

    job = relationship(
        "Job",
        back_populates="applications",
    )

    resume = relationship("Resume")

    assessments = relationship(
        "Assessment",
        back_populates="application",
    )


# ==========================================
# RESUME ANALYSIS MODEL
# ==========================================

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    analysis_id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.resume_id"))
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    match_score = Column(Float)
    matched_skills = Column(Text)
    missing_skills = Column(Text)
    recommendations = Column(Text)
    analysis_date = Column(DateTime)

    resume = relationship(
        "Resume",
        back_populates="analyses",
    )

    job = relationship(
        "Job",
        back_populates="resumes_analysis",
    )


# ==========================================
# ASSESSMENT MODEL
# ==========================================

class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.application_id"))
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    test_token = Column(String(100), unique=True, index=True)
    title = Column(String(255))
    tech_stack = Column(String(255))
    total_questions = Column(Integer, default=20)
    time_limit_minutes = Column(Integer)
    status = Column(String(50), default="pending")
    score = Column(Float)
    percentage = Column(Float)
    passed = Column(Boolean)
    correct_answers_count = Column(Integer)
    incorrect_answers_count = Column(Integer)
    candidate_answers = Column(Text)
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    template_id = Column(
        Integer,
        ForeignKey("assessment_templates.template_id"),
    )
    passing_percentage = Column(Float, default=60.0)
    violation_count = Column(Integer, default=0)
    auto_submitted_proctoring = Column(Boolean, default=False)
    proctoring_submission_reason = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    application = relationship(
        "Application",
        back_populates="assessments",
    )

    candidate = relationship(
        "Candidate",
        back_populates="assessments",
    )

    job = relationship(
        "Job",
        back_populates="assessments",
    )

    questions = relationship(
        "AssessmentQuestion",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )

    template = relationship(
        "AssessmentTemplate",
        back_populates="assessments",
    )

    proctoring_events = relationship(
        "ProctoringEvent",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )


# ==========================================
# ASSESSMENT QUESTION MODEL
# ==========================================

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    question_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id"))
    question_text = Column(Text)
    skill_category = Column(String(100))
    difficulty = Column(String(50))
    options = Column(Text)
    correct_answer = Column(String(255))
    explanation = Column(Text)
    order_index = Column(Integer)

    assessment = relationship(
        "Assessment",
        back_populates="questions",
    )


# ==========================================
# RECRUITER QUESTION MODEL
# ==========================================

class RecruiterQuestion(Base):
    __tablename__ = "recruiter_questions"

    question_id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.recruiter_id"))
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    technology = Column(String(100))
    difficulty = Column(String(50))
    question_text = Column(Text)
    options = Column(Text)
    correct_answer = Column(String(255))
    explanation = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    recruiter = relationship(
        "Recruiter",
        back_populates="recruiter_questions",
    )

    job = relationship(
        "Job",
        back_populates="recruiter_questions",
    )


# ==========================================
# ASSESSMENT TEMPLATE MODEL
# ==========================================

class AssessmentTemplate(Base):
    __tablename__ = "assessment_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.recruiter_id"))
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    title = Column(String(255))
    description = Column(Text, nullable=True)
    tech_stack = Column(String(255))
    duration_minutes = Column(Integer, default=25)
    passing_percentage = Column(Float, default=60.0)
    status = Column(String(50), default="draft")
    question_ids = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    recruiter = relationship(
        "Recruiter",
        back_populates="assessment_templates",
    )

    job = relationship(
        "Job",
        back_populates="assessment_templates",
    )

    assessments = relationship(
        "Assessment",
        back_populates="template",
    )


# ==========================================
# EMAIL NOTIFICATION MODEL
# ==========================================

class EmailNotification(Base):
    __tablename__ = "email_notifications"

    email_id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String(255))
    recipient_name = Column(String(255))
    subject = Column(String(255))
    body_html = Column(Text)
    email_type = Column(String(50))
    status = Column(String(50))
    sent_date = Column(DateTime)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    job_id = Column(Integer, ForeignKey("jobs.job_id"))

    candidate = relationship(
        "Candidate",
        back_populates="email_notifications",
    )

    job = relationship(
        "Job",
        back_populates="email_notifications",
    )


# ==========================================

# ==========================================
# PROCTORING EVENT MODEL
# ==========================================

class ProctoringEvent(Base):
    __tablename__ = "proctoring_events"

    event_id = Column(Integer, primary_key=True, index=True)

    assessment_id = Column(
        Integer,
        ForeignKey("assessments.assessment_id"),
        nullable=False,
        index=True,
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.candidate_id"),
        nullable=True,
        index=True,
    )

    event_type = Column(String(100), nullable=False)
    details = Column(Text)
    severity = Column(String(50), default="warning")
    strike_number = Column(Integer, default=1)
    session_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="proctoring_events")
    candidate = relationship("Candidate")


# ==========================================
# PASSWORD RESET / OTP MODEL
# ==========================================

class PasswordReset(Base):
    __tablename__ = "password_resets"

    reset_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    otp = Column(String(10), nullable=False)
    reset_token = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    is_used = Column(Boolean, default=False)


# BACKWARD-COMPATIBILITY ALIASES
# ==========================================

CandidateProfile = Candidate
RecruiterProfile = Recruiter
