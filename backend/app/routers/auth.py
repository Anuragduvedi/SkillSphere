import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User, Candidate, Recruiter, Company, PasswordReset
from app.schemas.schemas import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    ResendOTPRequest
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user
from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_meta(request: Request):
    ip_address = None
    if request.client:
        ip_address = request.client.host
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    user_agent = request.headers.get("user-agent", "Standard Web Browser / Client")
    return {"ip": ip_address, "user_agent": user_agent}


# =============================================================================
# REGISTER ENDPOINT
# =============================================================================
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserRegister,
    db: Session = Depends(get_db),
    client_meta: dict = Depends(get_client_meta)
):
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Hash password securely
    hashed_pwd = get_password_hash(user_in.password)

    # Create User record
    db_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hashed_pwd,
        role=user_in.role,
        is_active=True,
        created_date=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Auto-create related role profile
    company_name = user_in.company_name
    if db_user.role == "job_seeker":
        candidate = Candidate(
            user_id=db_user.user_id,
            profile_details="",
            education="",
            experience=""
        )
        db.add(candidate)
        db.commit()
    elif db_user.role == "recruiter":
        # Check or create company
        resolved_company = user_in.company_name or f"{user_in.name}'s Enterprise"
        company = db.query(Company).filter(Company.company_name == resolved_company).first()
        if not company:
            company = Company(
                company_name=resolved_company,
                description=f"Innovating technology solutions at {resolved_company}",
                contact_info=db_user.email,
                location="Remote / Hybrid"
            )
            db.add(company)
            db.commit()
            db.refresh(company)

        recruiter = Recruiter(
            user_id=db_user.user_id,
            company_id=company.company_id,
            designation="Talent Acquisition Specialist",
            recruiter_details=f"Lead recruiter for {company.company_name}"
        )
        db.add(recruiter)
        db.commit()

    # Dispatch Welcome Email via EmailService
    try:
        EmailService.send_welcome_email(db, db_user, company_name)
    except Exception as e:
        print(f"[AUTH] Welcome email dispatch caught: {e}")

    # Generate JWT
    access_token = create_access_token(data={"sub": str(db_user.user_id), "role": db_user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }


# =============================================================================
# LOGIN ENDPOINT
# =============================================================================
@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
    client_meta: dict = Depends(get_client_meta)
):
    user = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password combination.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )

    # Update last login timestamp
    try:
        user.last_login_at = datetime.utcnow()
        db.commit()
    except Exception:
        pass

    # Extract client metadata for security notification
    ip_address = None
    user_agent = "Standard Web Browser / Client"
    if isinstance(client_meta, dict):
        ip_address = client_meta.get("ip")
        user_agent = client_meta.get("user_agent", user_agent)

    # Dispatch Login Security Notification Email
    try:
        EmailService.send_login_notification_email(db, user, ip_address, user_agent)
    except Exception as e:
        print(f"[AUTH] Login security email dispatch caught: {e}")

    access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# =============================================================================
# FORGOT PASSWORD - REQUEST OTP
# =============================================================================
@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()

    # Rate limiting: check recent reset requests for this email
    recent_cutoff = datetime.utcnow() - timedelta(seconds=60)
    recent_request = (
        db.query(PasswordReset)
        .filter(PasswordReset.email == email_clean, PasswordReset.created_at >= recent_cutoff)
        .first()
    )
    if recent_request:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="A password reset code was requested recently. Please check your inbox or wait 60 seconds before requesting another."
        )

    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        # Avoid user enumeration while confirming action politely
        return {
            "status": "success",
            "message": "If this email address is registered with SkillSphere, a 6-digit verification code has been dispatched to your inbox."
        }

    # Invalidate previous unused reset tokens for this email
    db.query(PasswordReset).filter(
        PasswordReset.email == email_clean,
        PasswordReset.is_used == False
    ).update({"is_used": True})
    db.commit()

    # Generate secure 6-digit numeric OTP and reset token
    otp = f"{secrets.randbelow(900000) + 100000}"
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    reset_record = PasswordReset(
        email=email_clean,
        otp=otp,
        reset_token=reset_token,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        attempts=0,
        is_used=False
    )
    db.add(reset_record)
    db.commit()

    # Dispatch OTP Email
    EmailService.send_password_reset_otp_email(
        db=db,
        email=email_clean,
        user_name=user.name,
        otp=otp,
        expires_minutes=15
    )

    return {
        "status": "success",
        "message": "A 6-digit verification code has been dispatched to your email. It will expire in 15 minutes."
    }


# =============================================================================
# VERIFY OTP
# =============================================================================
@router.post("/verify-otp")
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()
    otp_input = req.otp.strip()

    # Find the most recent active reset record
    record = (
        db.query(PasswordReset)
        .filter(PasswordReset.email == email_clean, PasswordReset.is_used == False)
        .order_by(PasswordReset.created_at.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active password reset request found for this email. Please request a new code."
        )

    # Check expiration
    if datetime.utcnow() > record.expires_at:
        record.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The verification code has expired. Please request a fresh OTP."
        )

    # Check rate limiting / max attempts
    if record.attempts >= 5:
        record.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect attempts. This verification code has been locked for your security. Please request a new code."
        )

    # Check OTP match
    if record.otp != otp_input:
        record.attempts += 1
        db.commit()
        remaining = max(0, 5 - record.attempts)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. You have {remaining} attempt(s) remaining."
        )

    return {
        "status": "success",
        "message": "OTP verified successfully. You may now enter your new password.",
        "reset_token": record.reset_token
    }


# =============================================================================
# RESET PASSWORD
# =============================================================================
@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()
    token_input = req.reset_token.strip()
    new_password = req.new_password.strip()

    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters in length."
        )

    # Verify reset token against database record
    record = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.email == email_clean,
            PasswordReset.reset_token == token_input,
            PasswordReset.is_used == False
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset session. Please restart the password recovery process."
        )

    if datetime.utcnow() > record.expires_at:
        record.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your reset session has expired. Please request a new verification code."
        )

    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found."
        )

    # Securely hash new password with bcrypt
    user.password_hash = get_password_hash(new_password)
    record.is_used = True
    db.commit()

    # Dispatch confirmation email
    try:
        EmailService.send_password_changed_confirmation_email(db, user)
    except Exception as e:
        print(f"[AUTH] Password changed confirmation email caught: {e}")

    return {
        "status": "success",
        "message": "Your password has been successfully updated. You can now log in with your new password."
    }


# =============================================================================
# RESEND OTP
# =============================================================================
@router.post("/resend-otp")
def resend_otp(req: ResendOTPRequest, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()

    # Check 60-second cooldown
    recent_cutoff = datetime.utcnow() - timedelta(seconds=60)
    recent_request = (
        db.query(PasswordReset)
        .filter(PasswordReset.email == email_clean, PasswordReset.created_at >= recent_cutoff)
        .first()
    )
    if recent_request:
        elapsed = (datetime.utcnow() - recent_request.created_at).total_seconds()
        remaining = max(1, int(60 - elapsed))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {remaining} seconds before requesting a new code."
        )

    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        return {
            "status": "success",
            "message": "If this email is registered, a new verification code has been dispatched."
        }

    # Invalidate previous records
    db.query(PasswordReset).filter(
        PasswordReset.email == email_clean,
        PasswordReset.is_used == False
    ).update({"is_used": True})
    db.commit()

    otp = f"{secrets.randbelow(900000) + 100000}"
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    reset_record = PasswordReset(
        email=email_clean,
        otp=otp,
        reset_token=reset_token,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        attempts=0,
        is_used=False
    )
    db.add(reset_record)
    db.commit()

    EmailService.send_password_reset_otp_email(
        db=db,
        email=email_clean,
        user_name=user.name,
        otp=otp,
        expires_minutes=15
    )

    return {
        "status": "success",
        "message": "A new 6-digit verification code has been sent to your email."
    }


# =============================================================================
# CURRENT USER PROFILE
# =============================================================================
@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile_data = {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_date": current_user.created_date,
        "last_login_at": current_user.last_login_at,
    }

    if current_user.role == "job_seeker":
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.user_id).first()
        if candidate:
            profile_data["candidate_id"] = candidate.candidate_id
            profile_data["phone"] = candidate.phone
            profile_data["location"] = candidate.location
            profile_data["education"] = candidate.education
            profile_data["experience"] = candidate.experience
            profile_data["profile_details"] = candidate.profile_details
            profile_data["skills"] = [s.skill_name for s in candidate.skills]
            profile_data["has_resume"] = len(candidate.resumes) > 0
    elif current_user.role == "recruiter":
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.user_id).first()
        if recruiter:
            profile_data["recruiter_id"] = recruiter.recruiter_id
            profile_data["designation"] = recruiter.designation
            profile_data["company_name"] = recruiter.company.company_name if recruiter.company else "Unknown Company"
            profile_data["company_id"] = recruiter.company_id

    return profile_data
