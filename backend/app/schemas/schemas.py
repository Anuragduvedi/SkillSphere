from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# ================= AUTH & USER SCHEMAS =================
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=EMAIL_PATTERN)
    password: str = Field(..., min_length=6)
    role: str = Field("job_seeker", pattern="^(job_seeker|recruiter|admin)$")
    company_name: Optional[str] = None  # If registering as recruiter

class UserLogin(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)
    password: str

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ================= SKILL SCHEMAS =================
class SkillSchema(BaseModel):
    skill_id: int
    skill_name: str

    class Config:
        from_attributes = True

# ================= RESUME & OCR SCHEMAS =================
class ResumeResponse(BaseModel):
    resume_id: int
    candidate_id: int
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    upload_date: Optional[datetime] = None
    processing_status: str
    extracted_text: Optional[str] = None

    class Config:
        from_attributes = True

class OCRExtractResponse(BaseModel):
    resume_id: Optional[int] = None
    file_name: str
    extracted_name: Optional[str] = None
    extracted_email: Optional[str] = None
    extracted_phone: Optional[str] = None
    extracted_education: Optional[str] = None
    extracted_experience: Optional[str] = None
    extracted_skills: List[str] = []
    raw_text: Optional[str] = None
    status: str = "Completed"
    message: Optional[str] = None

# ================= CANDIDATE SCHEMAS =================
class CandidateProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    profile_details: Optional[str] = None
    skills: List[str] = []

class CandidateResponse(BaseModel):
    candidate_id: int
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    profile_details: Optional[str] = None
    skills: List[str] = []
    resumes: List[ResumeResponse] = []

    class Config:
        from_attributes = True

# ================= COMPANY SCHEMAS =================
class CompanyBase(BaseModel):
    company_name: str
    description: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    description: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None

class CompanyResponse(CompanyBase):
    company_id: int

    class Config:
        from_attributes = True

# ================= JOB SCHEMAS =================
class JobCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    location: str
    experience: str  # e.g., "1-3 years", "Fresher", "5+ years"
    job_type: str = "Full-time"  # Full-time, Remote, Contract, Part-time
    salary_range: Optional[str] = None
    skills: List[str] = []

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = None  # active, closed
    skills: Optional[List[str]] = None

class JobResponse(BaseModel):
    job_id: int
    recruiter_id: int
    title: str
    description: str
    location: str
    experience: str
    job_type: str
    salary_range: Optional[str] = None
    status: str
    created_date: Optional[datetime] = None
    company_name: Optional[str] = None
    skills: List[str] = []
    applicant_count: int = 0
    user_has_applied: bool = False
    match_score: Optional[float] = None

    class Config:
        from_attributes = True

# ================= APPLICATION SCHEMAS =================
class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    cover_note: Optional[str] = None

class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Applied|Under Review|Shortlisted|Interview|Selected|Rejected)$")

class ApplicationResponse(BaseModel):
    application_id: int
    job_id: int
    candidate_id: int
    resume_id: Optional[int] = None
    application_date: Optional[datetime] = None
    status: str
    cover_note: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    candidate_skills: List[str] = []
    candidate_experience: Optional[str] = None
    resume_file_path: Optional[str] = None
    match_score: Optional[float] = None

    class Config:
        from_attributes = True

# ================= RESUME ANALYSIS SCHEMAS =================
class AnalyzeRequest(BaseModel):
    job_id: int
    resume_id: Optional[int] = None

class AnalysisResponse(BaseModel):
    analysis_id: Optional[int] = None
    job_id: int
    job_title: str
    company_name: Optional[str] = None
    match_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    recommendations: str
    analysis_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# ================= ADMIN & ANALYTICS SCHEMAS =================
class AdminAnalyticsResponse(BaseModel):
    total_users: int
    total_candidates: int
    total_recruiters: int
    total_jobs: int
    active_jobs: int
    total_applications: int
    total_resumes_processed: int
    average_match_score: float
    status_distribution: dict
    jobs_by_type: dict
