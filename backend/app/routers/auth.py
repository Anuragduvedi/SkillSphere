from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Candidate, Recruiter, Company
from app.schemas.schemas import UserRegister, UserLogin, Token, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Hash password
    hashed_pwd = get_password_hash(user_in.password)

    # Create User record
    db_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hashed_pwd,
        role=user_in.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Auto-create related role profile
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
        company_name = user_in.company_name or f"{user_in.name}'s Enterprise"
        company = db.query(Company).filter(Company.company_name == company_name).first()
        if not company:
            company = Company(
                company_name=company_name,
                description=f"Innovating technology solutions at {company_name}",
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

    # Generate JWT
    access_token = create_access_token(data={"sub": str(db_user.user_id), "role": db_user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
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

    access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

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
