from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database import engine, Base
from app.routers import auth, resume, jobs, applications, recruiter, admin, assessment, chatbot
from app.seed import seed_database

# Create DB schema
Base.metadata.create_all(bind=engine)
try:
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(assessments)")).fetchall()]
        if 'template_id' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN template_id INTEGER REFERENCES assessment_templates(template_id)"))
        if 'passing_percentage' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN passing_percentage FLOAT DEFAULT 60.0"))
        if 'violation_count' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN violation_count INTEGER DEFAULT 0"))
        if 'auto_submitted_proctoring' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN auto_submitted_proctoring BOOLEAN DEFAULT 0"))
        if 'proctoring_submission_reason' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN proctoring_submission_reason TEXT"))
        if 'description' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN description TEXT"))
        if 'expires_at' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN expires_at DATETIME"))

        # Check assessment_templates columns
        t_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(assessment_templates)")).fetchall()]
        if 'description' not in t_cols:
            conn.execute(text("ALTER TABLE assessment_templates ADD COLUMN description TEXT"))

        # Check proctoring_events columns
        p_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(proctoring_events)")).fetchall()]
        if 'strike_number' not in p_cols:
            conn.execute(text("ALTER TABLE proctoring_events ADD COLUMN strike_number INTEGER DEFAULT 1"))
        if 'session_id' not in p_cols:
            conn.execute(text("ALTER TABLE proctoring_events ADD COLUMN session_id VARCHAR(100)"))

        # Check users columns
        u_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
        if 'last_login_at' not in u_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME"))

        conn.commit()
except Exception as e:
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-seed mock data on startup if database is empty
    try:
        seed_database()
    except Exception as e:
        print(f"Startup seed notice: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SkillSphere Career & Job Portal API - Full-Stack with OCR & Resume Matching",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://skillsphere-frontend-62ul.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory if available
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(resume.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(recruiter.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(assessment.router, prefix=settings.API_V1_STR)
app.include_router(chatbot.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "portal": "SkillSphere - Career & Job Portal",
        "status": "online",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "SkillSphere Backend"}
