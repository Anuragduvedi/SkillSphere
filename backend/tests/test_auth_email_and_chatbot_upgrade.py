import os
import pytest
from datetime import datetime, timezone, timedelta
from app.database import SessionLocal
from app.models.models import User, Candidate, Recruiter, Company, Job, Application, Assessment, PasswordReset, EmailNotification
from app.schemas.schemas import (
    UserRegister, UserLogin, ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
)
from app.routers import auth
from app.services.chatbot_service import ChatbotService
from app.core.security import get_password_hash, verify_password

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_user_registration_and_welcome_email(db):
    """Test user registration triggers a professional welcome email in DB and returns JWT token."""
    unique_email = f"welcome.test.{os.urandom(4).hex()}@skillsphere.com"
    user_in = UserRegister(
        name="Simran Preet",
        email=unique_email,
        password="SecurePassword123!",
        role="job_seeker"
    )

    # Call router register function directly
    res = auth.register(user_in, db)
    assert "access_token" in res
    assert res["user"].email == unique_email

    # Verify welcome email was generated
    email_record = db.query(EmailNotification).filter(
        EmailNotification.recipient_email == unique_email,
        EmailNotification.email_type == "welcome"
    ).first()
    assert email_record is not None
    assert "Welcome to SkillSphere" in email_record.subject
    assert "Simran Preet" in email_record.body_html


def test_user_login_and_security_notification_email(db):
    """Test user login triggers a security notification email with client info."""
    unique_email = f"login.test.{os.urandom(4).hex()}@skillsphere.com"
    raw_password = "Password456!"
    user = User(
        name="Aman Verma",
        email=unique_email,
        password_hash=get_password_hash(raw_password),
        role="job_seeker",
        is_active=True,
        created_date=datetime.utcnow()
    )
    db.add(user)
    db.commit()

    login_in = UserLogin(
        email=unique_email,
        password=raw_password
    )

    # Call router login function directly
    res = auth.login(login_in, db)
    assert "access_token" in res

    # Verify login security alert email was generated
    email_record = db.query(EmailNotification).filter(
        EmailNotification.recipient_email == unique_email,
        EmailNotification.email_type == "login_alert"
    ).first()
    assert email_record is not None
    assert "Security Alert: New Sign-in" in email_record.subject
    assert "Aman Verma" in email_record.body_html


def test_forgot_password_otp_and_reset_flow(db):
    """Complete end-to-end test of Forgot Password, OTP Verification, and Password Reset."""
    unique_email = f"forgot.test.{os.urandom(4).hex()}@skillsphere.com"
    old_password = "OldPassword123!"
    new_password = "NewSuperSecret456!"

    user = User(
        name="Harpreet Singh",
        email=unique_email,
        password_hash=get_password_hash(old_password),
        role="job_seeker",
        is_active=True,
        created_date=datetime.utcnow()
    )
    db.add(user)
    db.commit()

    # Step 1: Request OTP
    forgot_res = auth.forgot_password(ForgotPasswordRequest(email=unique_email), db=db)
    assert forgot_res["status"] == "success"

    # Verify OTP record in DB
    reset_record = db.query(PasswordReset).filter(
        PasswordReset.email == unique_email,
        PasswordReset.is_used == False
    ).order_by(PasswordReset.created_at.desc()).first()
    assert reset_record is not None
    assert len(reset_record.otp) == 6

    otp_value = reset_record.otp

    # Step 2: Verify wrong OTP checks attempt counter
    with pytest.raises(Exception) as excinfo:
        auth.verify_otp(VerifyOTPRequest(email=unique_email, otp="000000"), db=db)
    assert "Invalid verification code" in str(excinfo.value)

    # Step 3: Verify correct OTP
    good_verify = auth.verify_otp(VerifyOTPRequest(email=unique_email, otp=otp_value), db=db)
    assert good_verify["status"] == "success"
    assert good_verify["reset_token"] == reset_record.reset_token

    # Step 4: Reset password using token
    reset_res = auth.reset_password(
        ResetPasswordRequest(
            email=unique_email,
            reset_token=reset_record.reset_token,
            new_password=new_password
        ),
        db=db
    )
    assert reset_res["status"] == "success"

    # Step 5: Verify login with OLD password fails
    with pytest.raises(Exception):
        auth.login(UserLogin(email=unique_email, password=old_password), db)

    # Step 6: Verify login with NEW password succeeds!
    success_login = auth.login(UserLogin(email=unique_email, password=new_password), db)
    assert "access_token" in success_login

    # Verify password changed confirmation email
    changed_email = db.query(EmailNotification).filter(
        EmailNotification.recipient_email == unique_email,
        EmailNotification.email_type == "password_changed"
    ).first()
    assert changed_email is not None
    assert "Password Has Been Reset" in changed_email.subject


def test_chatbot_multilingual_hindi():
    """Verify chatbot understands Hindi questions and replies warmly in Hindi/Hinglish."""
    resp = ChatbotService.get_response("mera test kab hai?")
    reply = resp["reply"]
    assert any(term in reply.lower() for term in ["assessment", "test", "dashboard", "portal", "login"])
    assert resp["provider"] == "skillsphere_assistant"


def test_chatbot_multilingual_punjabi():
    """Verify chatbot understands Punjabi questions and replies in Punjabi."""
    resp = ChatbotService.get_response("job apply kitti c hun ki hovega?")
    reply = resp["reply"]
    assert any(term in reply.lower() for term in ["recruiter", "assessment", "interview", "resume", "test"])


def test_chatbot_broken_english_and_informal():
    """Verify chatbot handles informal speech and frustration politely."""
    resp = ChatbotService.get_response("yaar mera assessment complete nahi ho rha")
    reply = resp["reply"]
    assert any(term in reply.lower() for term in ["camera", "permission", "refresh", "problem", "madad", "help"])


def test_chatbot_context_followup_uske_baad():
    """Verify chatbot resolves conversational follow-ups like 'uske baad?' using history."""
    history = [
        {"role": "user", "content": "How can I apply for a job?"},
        {"role": "model", "content": "Go to the Jobs section, review the match score, and click Apply Now."}
    ]
    resp = ChatbotService.get_response(message="uske baad?", history=history)
    reply = resp["reply"]
    assert any(term in reply.lower() for term in ["assessment", "test", "shortlist", "interview", "recruiter"])


def test_chatbot_user_journey_with_real_candidate_data(db):
    """Verify chatbot provides accurate guidance using real DB candidate data without hallucinating."""
    user = User(
        name="Rohit Sharma",
        email=f"rohit.{os.urandom(4).hex()}@test.com",
        password_hash="hash",
        role="job_seeker",
        created_date=datetime.utcnow()
    )
    db.add(user)
    db.commit()

    cand = Candidate(user_id=user.user_id, phone="9876543210", location="Delhi")
    db.add(cand)
    db.commit()

    comp_name = f"Acme Tech {os.urandom(4).hex()}"
    company = Company(
        company_name=comp_name,
        description="Pioneering AI tech systems",
        contact_info="contact@acmetech.com",
        location="Delhi"
    )
    db.add(company)
    db.commit()

    rec_user = User(name="Recruiter One", email=f"rec.{os.urandom(4).hex()}@test.com", password_hash="h", role="recruiter")
    db.add(rec_user)
    db.commit()
    rec = Recruiter(user_id=rec_user.user_id, company_id=company.company_id)
    db.add(rec)
    db.commit()

    job = Job(
        recruiter_id=rec.recruiter_id,
        title="Frontend React Developer",
        description="Build high-performance React web interfaces",
        location="Remote",
        experience="3+ years",
        job_type="Full-time",
        salary_range="$100k-$130k",
        status="active"
    )
    db.add(job)
    db.commit()

    app = Application(job_id=job.job_id, candidate_id=cand.candidate_id, status="Applied", application_date=datetime.utcnow())
    db.add(app)
    db.commit()

    user_data = {
        "authenticated": True,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "candidate": {
            "profile_percentage": 50,
            "missing_fields": ["Education", "Experience", "Key Skills", "Resume Upload"],
            "applications": [{"job_title": "Frontend React Developer", "company": comp_name, "status": "Applied"}],
            "assessments": []
        }
    }

    resp = ChatbotService.get_response(message="mera status kya hai?", user_data=user_data)
    reply = resp["reply"]
    assert "Rohit Sharma" in reply
    assert "Frontend React Developer" in reply
    assert comp_name in reply


def test_chatbot_conversational_10_exact_prompts():
    """Verify chatbot responds naturally to all 10 user-specified conversational test cases."""
    # 1. Hello bro, how are you?
    r1 = ChatbotService.get_response("Hello bro, how are you?")["reply"]
    assert any(w in r1.lower() for w in ["great", "doing great", "what's up", "day going", "heyy"])
    assert "i am your skillsphere ai career assistant" not in r1.lower()

    # 2. ki haal aa veere?
    r2 = ChatbotService.get_response("ki haal aa veere?")["reply"]
    assert any(w in r2.lower() for w in ["chardi kala", "haal-chaal", "sat sri akal", "theek-thaak"])

    # 3. yaar aj mood off hai
    r3 = ChatbotService.get_response("yaar aj mood off hai")["reply"]
    assert any(w in r3.lower() for w in ["kya hua", "mood off", "sun raha", "tension", "halka"])

    # 4. what is artificial intelligence?
    r4 = ChatbotService.get_response("what is artificial intelligence?")["reply"]
    assert any(w in r4.lower() for w in ["computer science", "machine learning", "neural networks", "smart systems", "patterns"])

    # 5. suggest me some thriller movies
    r5 = ChatbotService.get_response("suggest me some thriller movies")["reply"]
    assert any(w in r5.lower() for w in ["inception", "shutter island", "gone girl", "andhadhun", "drishyam"])

    # 6. bro mujhe Python seekhni hai
    r6 = ChatbotService.get_response("bro mujhe Python seekhni hai")["reply"]
    assert any(w in r6.lower() for w in ["roadmap", "fundamentals", "oop", "projects", "fastapi", "django"])

    # 7. mainu samajh ni aa reha
    r7 = ChatbotService.get_response("mainu samajh ni aa reha")["reply"]
    assert any(w in r7.lower() for w in ["koi gal nahi", "saans lo", "confusion", "step-by-step", "theek"])

    # 8. what can you do?
    r8 = ChatbotService.get_response("what can you do?")["reply"]
    assert any(w in r8.lower() for w in ["casual chat", "entertainment", "coding", "skillsphere", "assessments"])

    # 9. mera assessment pending hai, ab kya karun?
    r9 = ChatbotService.get_response("mera assessment pending hai, ab kya karun?")["reply"]
    assert any(w in r9.lower() for w in ["20", "25", "60%", "timer", "camera", "proctoring", "start"])

    # 10. haha you're funny bro
    r10 = ChatbotService.get_response("haha you're funny bro")["reply"]
    assert any(w in r10.lower() for w in ["smile", "robotic", "humor", "shukriya", "masti", "laugh"])


def test_chatbot_conversational_casual_and_interview_multiturn():
    """Verify chatbot retains context across casual chat and interview preparation dialogues."""
    # Conversation 1: Casual Chat
    h1 = []
    r1 = ChatbotService.get_response("Hi bro!", history=h1)["reply"]
    h1.append({"role": "user", "content": "Hi bro!"})
    h1.append({"role": "model", "content": r1})

    r2 = ChatbotService.get_response("kuch khaas nahi yaar", history=h1)["reply"]
    assert any(w in r2.lower() for w in ["routine", "college", "office", "busy"])
    h1.append({"role": "user", "content": "kuch khaas nahi yaar"})
    h1.append({"role": "model", "content": r2})

    r3 = ChatbotService.get_response("bore ho raha hu", history=h1)["reply"]
    assert any(w in r3.lower() for w in ["interesting", "movies", "facts", "challenge", "bore"])

    # Conversation 2: Interview Multi-turn
    h2 = []
    r4 = ChatbotService.get_response("I am preparing for an interview.", history=h2)["reply"]
    assert any(w in r4.lower() for w in ["role", "preparing for", "questions", "python developer"])
    h2.append({"role": "user", "content": "I am preparing for an interview."})
    h2.append({"role": "model", "content": r4})

    r5 = ChatbotService.get_response("Python developer.", history=h2)["reply"]
    assert any(w in r5.lower() for w in ["fundamentals", "basics", "comfortable"])
    h2.append({"role": "user", "content": "Python developer."})
    h2.append({"role": "model", "content": r5})

    r6 = ChatbotService.get_response("basics aate hain.", history=h2)["reply"]
    assert any(w in r6.lower() for w in ["oop", "decorators", "question", "is", "=="])
    h2.append({"role": "user", "content": "basics aate hain."})
    h2.append({"role": "model", "content": r6})

    r7 = ChatbotService.get_response("Haan bata.", history=h2)["reply"]
    assert any(w in r7.lower() for w in ["value", "identity", "memory", "mutable", "default"])


def test_chatbot_project_aware_exact_queries():
    """Verify chatbot handles exact required project-aware queries with real DB evidence."""
    sample_user_data = {
        "authenticated": True,
        "name": "Karan Singhania",
        "email": "karan@example.com",
        "role": "job_seeker",
        "candidate": {
            "profile_percentage": 85,
            "missing_fields": ["Experience"],
            "resumes_count": 1,
            "resume_uploaded": True,
            "applications_count": 2,
            "applications": [
                {"job_title": "Python Backend Intern", "company": "AlphaTech", "status": "Assessment", "date": "18 Nov 2026"},
                {"job_title": "Junior Data Analyst", "company": "DataHub", "status": "Applied", "date": "15 Nov 2026"}
            ],
            "assessments": [
                {"title": "FastAPI & Python Assessment", "status": "pending", "score": None, "time_limit": 25, "passed": False},
                {"title": "Core CS MCQ Exam", "status": "completed", "score": 15, "percentage": 75, "passed": True}
            ]
        }
    }

    # 1. Main kaunsi stage par hoon?
    r1 = ChatbotService.get_response("Main kaunsi stage par hoon?", user_data=sample_user_data)["reply"]
    assert "Karan Singhania" in r1
    assert "Stage 3" in r1 or "Assessment" in r1
    assert "85%" in r1
    assert "AlphaTech" not in r1 or "Stage" in r1
    assert "FastAPI & Python Assessment" in r1

    # 2. Meri application ka kya status hai?
    r2 = ChatbotService.get_response("Meri application ka kya status hai?", user_data=sample_user_data)["reply"]
    assert "Python Backend Intern" in r2
    assert "AlphaTech" in r2
    assert "Junior Data Analyst" in r2
    assert "DataHub" in r2

    # 3. Internship ke liye kaise apply karun?
    r3 = ChatbotService.get_response("Internship ke liye kaise apply karun?")["reply"]
    assert any(w in r3.lower() for w in ["jobs", "match score", "apply now", "stipend", "20-question"])

    # 4. Mera next step kya hai?
    r4 = ChatbotService.get_response("Mera next step kya hai?", user_data=sample_user_data)["reply"]
    assert "FastAPI & Python Assessment" in r4 or "next step" in r4.lower()

    # 5. Maine kitne assessments complete kiye?
    r5 = ChatbotService.get_response("Maine kitne assessments complete kiye?", user_data=sample_user_data)["reply"]
    assert "1" in r5  # 1 completed
    assert "Core CS MCQ Exam" in r5
    assert "15/20" in r5 or "75%" in r5

    # 6. Bro mujhe Python seekhni hai.
    r6 = ChatbotService.get_response("Bro mujhe Python seekhni hai.")["reply"]
    assert any(w in r6.lower() for w in ["roadmap", "fundamentals", "oop", "projects", "fastapi"])

    # 7. Casual Greetings (Natural & Friendly)
    for casual in ["Hi", "Hello", "Ki haal aa veere?", "How are you?"]:
        rc = ChatbotService.get_response(casual)["reply"]
        assert any(w in rc.lower() for w in ["doing great", "heyy", "chardi kala", "mast"])
        assert "main kaunsi stage" not in rc.lower()

