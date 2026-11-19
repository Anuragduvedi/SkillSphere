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

# ================= PASSWORD RESET SCHEMAS =================
class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)

class VerifyOTPRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)
    otp: str = Field(..., min_length=4, max_length=10)

class ResetPasswordRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)
    reset_token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=6)

class ResendOTPRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)

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

# ================= AI SCREENING & ASSESSMENT SCHEMAS =================
class AssessmentQuestionSchema(BaseModel):
    question_id: int
    question_text: str
    skill_category: str
    difficulty: str
    options: List[str]
    order_index: int

    class Config:
        from_attributes = True

class AssessmentDetailResponse(BaseModel):
    assessment_id: int
    test_token: str
    title: str
    tech_stack: str
    total_questions: int
    time_limit_minutes: int
    status: str
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    questions: List[AssessmentQuestionSchema] = []

    class Config:
        from_attributes = True

class AssessmentSubmitRequest(BaseModel):
    answers: dict  # {"question_id_or_index": "chosen_option_string"}

class AssessmentQuestionEvaluation(BaseModel):
    question_id: int
    question_text: str
    skill_category: str
    difficulty: str
    options: List[str]
    candidate_answer: Optional[str] = None
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None

class AssessmentResultResponse(BaseModel):
    assessment_id: int
    test_token: str
    title: str
    tech_stack: str
    status: str
    score: float
    percentage: float
    passed: bool
    total_questions: int
    correct_count: int
    incorrect_count: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    questions: List[AssessmentQuestionEvaluation] = []

class ScreeningCandidateItem(BaseModel):
    candidate_id: int
    application_id: Optional[int] = None
    name: str
    email: str
    skills: List[str] = []
    experience: Optional[str] = None
    education: Optional[str] = None
    match_score: float
    is_shortlisted: bool
    shortlist_status: str
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    reasons: List[str] = []
    breakdown: Optional[dict] = None
    assessment: Optional[dict] = None  # {assessment_id, status, score, percentage, passed, test_token}

class ScreeningJobResponse(BaseModel):
    job_id: int
    job_title: str
    required_skills: List[str] = []
    total_evaluated: int
    shortlisted_count: int
    rejected_count: int
    shortlisted_candidates: List[ScreeningCandidateItem] = []
    rejected_candidates: List[ScreeningCandidateItem] = []

class ScreeningStatsResponse(BaseModel):
    total_applicants: int
    total_matched: int
    shortlisted_count: int
    rejected_count: int
    shortlist_threshold: float = 70.0
    awaiting_assessment: int
    assessments_completed: int
    pending_tests: int
    passed_tests: int
    average_assessment_score: float

class EmailNotificationResponse(BaseModel):
    email_id: int
    recipient_email: str
    recipient_name: str
    subject: str
    email_type: str
    status: str
    sent_date: Optional[datetime] = None
    body_html: str
    job_id: Optional[int] = None

    class Config:
        from_attributes = True

# ================= RECRUITER QUESTION & ASSESSMENT TEMPLATE SCHEMAS =================
class RecruiterQuestionCreate(BaseModel):
    technology: str = Field(..., min_length=1, max_length=100)
    difficulty: str = Field("intermediate", pattern="^(beginner|intermediate|advanced)$")
    question_text: str = Field(..., min_length=5)
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    job_id: Optional[int] = None

class RecruiterQuestionUpdate(BaseModel):
    technology: Optional[str] = None
    difficulty: Optional[str] = None
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    job_id: Optional[int] = None

class RecruiterQuestionResponse(BaseModel):
    question_id: int
    recruiter_id: int
    job_id: Optional[int] = None
    job_title: Optional[str] = None
    technology: str
    difficulty: str
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AssessmentTemplateCreate(BaseModel):
    job_id: int
    title: str = Field(..., min_length=3, max_length=255)
    tech_stack: str = Field(..., min_length=2, max_length=255)
    duration_minutes: int = Field(25, ge=5, le=180)
    passing_percentage: float = Field(60.0, ge=10.0, le=100.0)
    status: str = Field("draft", pattern="^(draft|published)$")
    question_ids: List[int] = Field(..., min_items=1)  # Must be 20 when publishing

class AssessmentTemplateUpdate(BaseModel):
    title: Optional[str] = None
    tech_stack: Optional[str] = None
    duration_minutes: Optional[int] = None
    passing_percentage: Optional[float] = None
    status: Optional[str] = None
    question_ids: Optional[List[int]] = None

class AssessmentTemplateResponse(BaseModel):
    template_id: int
    recruiter_id: int
    job_id: int
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    title: str
    tech_stack: str
    duration_minutes: int
    passing_percentage: float
    status: str
    question_ids: List[int] = []
    questions_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RecruiterAssessmentStats(BaseModel):
    total_questions: int
    published_assessments: int
    draft_assessments: int
    total_candidates_tested: int
    tests_completed: int
    tests_passed: int
    average_score: float

class AssignAssessmentRequest(BaseModel):
    candidate_ids: List[int] = Field(..., min_items=1)
    job_id: Optional[int] = None
    template_id: Optional[int] = None
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[str] = "General Technical"
    duration_minutes: Optional[int] = Field(25, ge=5, le=180)
    passing_percentage: Optional[float] = Field(60.0, ge=10.0, le=100.0)
    expires_days: Optional[int] = Field(7, ge=1, le=90)
    send_email: Optional[bool] = True
    question_ids: Optional[List[int]] = None

class GenerateAIQuestionsRequest(BaseModel):
    role: str = Field(..., min_length=2)
    tech_stack: str = Field(..., min_length=2)
    count: int = Field(5, ge=1, le=20)
    difficulty: str = Field("intermediate", pattern="^(beginner|intermediate|advanced)$")


