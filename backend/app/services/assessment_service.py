import uuid
import json
import random
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status

from app.models.models import (
    Assessment, AssessmentQuestion, Candidate, Job, Application, User,
    Recruiter, RecruiterQuestion, AssessmentTemplate
)
from app.services.question_bank import QUESTION_BANK
from app.services.email_service import EmailService

def utc_now():
    return datetime.utcnow()

def is_expired(dt: Optional[datetime]) -> bool:
    if not dt:
        return False
    if dt.tzinfo is not None:
        return datetime.now(timezone.utc) > dt
    return datetime.utcnow() > dt

class AssessmentService:

    # ================= 1. RECRUITER QUESTION MANAGEMENT =================

    @staticmethod
    def create_recruiter_question(db: Session, recruiter_id: int, data: Dict[str, Any]) -> RecruiterQuestion:
        """
        Creates a custom technical question authored by the recruiter.
        Validates:
        - Exactly 4 MCQ options.
        - Exactly one designated correct answer contained in the options.
        """
        options = data.get("options", [])
        if len(options) != 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A question must contain exactly 4 options."
            )

        correct_answer = data.get("correct_answer")
        if not correct_answer or correct_answer not in options:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The correct answer must exactly match one of the four provided options."
            )

        question = RecruiterQuestion(
            recruiter_id=recruiter_id,
            job_id=data.get("job_id"),
            technology=data.get("technology", "General").strip(),
            difficulty=data.get("difficulty", "intermediate").lower(),
            question_text=data.get("question_text", "").strip(),
            options=json.dumps(options),
            correct_answer=correct_answer,
            explanation=data.get("explanation", "").strip() if data.get("explanation") else None,
            created_at=utc_now(),
            updated_at=utc_now()
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def update_recruiter_question(
        db: Session, 
        question_id: int, 
        recruiter_id: int, 
        data: Dict[str, Any], 
        is_admin: bool = False
    ) -> RecruiterQuestion:
        """
        Updates an existing recruiter technical question with RBAC enforcement.
        """
        question = db.query(RecruiterQuestion).filter(RecruiterQuestion.question_id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found.")

        if not is_admin and question.recruiter_id != recruiter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You can only modify questions created by your recruiter account."
            )

        if "options" in data and data["options"] is not None:
            options = data["options"]
            if len(options) != 4:
                raise HTTPException(status_code=400, detail="A question must contain exactly 4 options.")
            question.options = json.dumps(options)

            if "correct_answer" in data and data["correct_answer"]:
                if data["correct_answer"] not in options:
                    raise HTTPException(status_code=400, detail="The correct answer must match one of the options.")
                question.correct_answer = data["correct_answer"]
        elif "correct_answer" in data and data["correct_answer"]:
            current_options = json.loads(question.options)
            if data["correct_answer"] not in current_options:
                raise HTTPException(status_code=400, detail="The correct answer must match one of the current options.")
            question.correct_answer = data["correct_answer"]

        if "technology" in data and data["technology"]:
            question.technology = data["technology"].strip()
        if "difficulty" in data and data["difficulty"]:
            question.difficulty = data["difficulty"].lower()
        if "question_text" in data and data["question_text"]:
            question.question_text = data["question_text"].strip()
        if "explanation" in data:
            question.explanation = data["explanation"].strip() if data["explanation"] else None
        if "job_id" in data:
            question.job_id = data["job_id"]

        question.updated_at = utc_now()
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def delete_recruiter_question(
        db: Session, 
        question_id: int, 
        recruiter_id: int, 
        is_admin: bool = False
    ) -> bool:
        """
        Deletes a question owned by the recruiter or by an admin.
        """
        question = db.query(RecruiterQuestion).filter(RecruiterQuestion.question_id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found.")

        if not is_admin and question.recruiter_id != recruiter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You can only delete questions created by your recruiter account."
            )

        db.delete(question)
        db.commit()
        return True

    @staticmethod
    def get_recruiter_questions(
        db: Session,
        recruiter_id: Optional[int] = None,
        job_id: Optional[int] = None,
        technology: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches questions matching optional filters.
        """
        query = db.query(RecruiterQuestion)
        if recruiter_id:
            query = query.filter(RecruiterQuestion.recruiter_id == recruiter_id)
        if job_id:
            query = query.filter((RecruiterQuestion.job_id == job_id) | (RecruiterQuestion.job_id == None))
        if technology and technology.lower() != "all":
            query = query.filter(func.lower(RecruiterQuestion.technology) == technology.lower())
        if difficulty and difficulty.lower() != "all":
            query = query.filter(func.lower(RecruiterQuestion.difficulty) == difficulty.lower())
        if search:
            query = query.filter(RecruiterQuestion.question_text.ilike(f"%{search}%"))

        questions = query.order_by(desc(RecruiterQuestion.created_at)).all()
        results = []
        for q in questions:
            results.append({
                "question_id": q.question_id,
                "recruiter_id": q.recruiter_id,
                "job_id": q.job_id,
                "job_title": q.job.title if q.job else "General Bank",
                "technology": q.technology,
                "difficulty": q.difficulty,
                "question_text": q.question_text,
                "options": json.loads(q.options),
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "created_at": q.created_at,
                "updated_at": q.updated_at
            })
        return results

    @staticmethod
    def import_library_questions(
        db: Session, 
        recruiter_id: int, 
        technology: str, 
        count: int = 20, 
        job_id: Optional[int] = None
    ) -> List[RecruiterQuestion]:
        """
        Imports curated questions from the built-in QUESTION_BANK library into the recruiter's custom question bank.
        """
        tech_key = technology.lower().replace(" ", "_")
        target_pool = []
        if tech_key in QUESTION_BANK:
            target_pool = QUESTION_BANK[tech_key]
        else:
            # Fallback scan all categories
            for k, pool in QUESTION_BANK.items():
                if tech_key in k or k in tech_key:
                    target_pool = pool
                    break
            if not target_pool:
                target_pool = QUESTION_BANK.get("python", [])

        # Avoid duplicate imports
        existing_texts = set(
            q[0] for q in db.query(RecruiterQuestion.question_text)
            .filter(RecruiterQuestion.recruiter_id == recruiter_id).all()
        )

        imported = []
        for item in target_pool[:count]:
            if item["question"] not in existing_texts:
                q_obj = RecruiterQuestion(
                    recruiter_id=recruiter_id,
                    job_id=job_id,
                    technology=technology.title(),
                    difficulty=item.get("difficulty", "intermediate"),
                    question_text=item["question"],
                    options=json.dumps(item["options"]),
                    correct_answer=item["correct_answer"],
                    explanation=item.get("explanation"),
                    created_at=utc_now(),
                    updated_at=utc_now()
                )
                db.add(q_obj)
                imported.append(q_obj)
                existing_texts.add(item["question"])

        db.commit()
        # Return all matching questions now available in the recruiter's question bank
        all_qs = db.query(RecruiterQuestion).filter(
            RecruiterQuestion.recruiter_id == recruiter_id,
            func.lower(RecruiterQuestion.technology) == technology.lower()
        ).limit(count).all()
        return all_qs

    # ================= 2. ASSESSMENT TEMPLATES (RECRUITER CONTROLLED) =================

    @staticmethod
    def create_assessment_template(
        db: Session, 
        recruiter_id: int, 
        data: Dict[str, Any]
    ) -> AssessmentTemplate:
        """
        Creates an assessment template for a job posting.
        Can be saved as 'draft' or 'published'.
        When published, strictly validates that exactly 20 questions are chosen.
        """
        job_id = data.get("job_id")
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job opening not found.")

        question_ids = data.get("question_ids", [])
        status_val = data.get("status", "draft").lower()

        if status_val == "published" and len(question_ids) != 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A published technical assessment must contain exactly 20 questions. You currently have {len(question_ids)} questions selected."
            )

        template = AssessmentTemplate(
            recruiter_id=recruiter_id,
            job_id=job_id,
            title=data.get("title", f"{job.title} Technical Evaluation").strip(),
            tech_stack=data.get("tech_stack", "Full Stack Engineering").strip(),
            duration_minutes=data.get("duration_minutes", 25),
            passing_percentage=data.get("passing_percentage", 60.0),
            status=status_val,
            question_ids=json.dumps(question_ids),
            created_at=utc_now(),
            updated_at=utc_now()
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        # If published, automatically assign to any existing shortlisted candidates for this job
        if status_val == "published":
            AssessmentService.auto_assign_published_template_to_shortlisted(db, template)

        return template

    @staticmethod
    def update_assessment_template(
        db: Session, 
        template_id: int, 
        recruiter_id: int, 
        data: Dict[str, Any], 
        is_admin: bool = False
    ) -> AssessmentTemplate:
        """
        Updates an assessment template (e.g. adding questions to a draft, updating duration, publishing).
        """
        template = db.query(AssessmentTemplate).filter(AssessmentTemplate.template_id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found.")

        if not is_admin and template.recruiter_id != recruiter_id:
            raise HTTPException(status_code=403, detail="Unauthorized to edit this assessment template.")

        if "question_ids" in data and data["question_ids"] is not None:
            q_ids = data["question_ids"]
            if data.get("status") == "published" and len(q_ids) != 20:
                raise HTTPException(status_code=400, detail="Published assessments must have exactly 20 questions.")
            template.question_ids = json.dumps(q_ids)

        if "status" in data and data["status"]:
            new_status = data["status"].lower()
            if new_status == "published":
                current_q_ids = json.loads(template.question_ids)
                if len(current_q_ids) != 20:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot publish: You must select exactly 20 questions (currently {len(current_q_ids)})."
                    )
            template.status = new_status

        if "title" in data and data["title"]:
            template.title = data["title"].strip()
        if "tech_stack" in data and data["tech_stack"]:
            template.tech_stack = data["tech_stack"].strip()
        if "duration_minutes" in data and data["duration_minutes"] is not None:
            template.duration_minutes = int(data["duration_minutes"])
        if "passing_percentage" in data and data["passing_percentage"] is not None:
            template.passing_percentage = float(data["passing_percentage"])

        template.updated_at = utc_now()
        db.commit()
        db.refresh(template)

        if template.status == "published":
            AssessmentService.auto_assign_published_template_to_shortlisted(db, template)

        return template

    @staticmethod
    def publish_assessment_template(
        db: Session, 
        template_id: int, 
        recruiter_id: int, 
        is_admin: bool = False
    ) -> AssessmentTemplate:
        """
        Validates and transitions an assessment template from draft to published.
        """
        template = db.query(AssessmentTemplate).filter(AssessmentTemplate.template_id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found.")

        if not is_admin and template.recruiter_id != recruiter_id:
            raise HTTPException(status_code=403, detail="Unauthorized to publish this assessment template.")

        q_ids = json.loads(template.question_ids) if template.question_ids else []
        if len(q_ids) != 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Assessment must contain exactly 20 questions before publishing. Currently has {len(q_ids)}."
            )

        template.status = "published"
        template.updated_at = utc_now()
        db.commit()
        db.refresh(template)

        # Automatically assign to any pending shortlisted candidates for this job
        AssessmentService.auto_assign_published_template_to_shortlisted(db, template)

        return template

    @staticmethod
    def delete_assessment_template(
        db: Session, 
        template_id: int, 
        recruiter_id: int, 
        is_admin: bool = False
    ) -> bool:
        """
        Deletes an assessment template.
        """
        template = db.query(AssessmentTemplate).filter(AssessmentTemplate.template_id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found.")

        if not is_admin and template.recruiter_id != recruiter_id:
            raise HTTPException(status_code=403, detail="Unauthorized to delete this assessment template.")

        db.delete(template)
        db.commit()
        return True

    @staticmethod
    def get_assessment_templates(
        db: Session,
        recruiter_id: Optional[int] = None,
        job_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches recruiter assessment templates.
        """
        query = db.query(AssessmentTemplate)
        if recruiter_id:
            query = query.filter(AssessmentTemplate.recruiter_id == recruiter_id)
        if job_id:
            query = query.filter(AssessmentTemplate.job_id == job_id)
        if status_filter and status_filter.lower() != "all":
            query = query.filter(AssessmentTemplate.status == status_filter.lower())

        templates = query.order_by(desc(AssessmentTemplate.created_at)).all()
        results = []
        for t in templates:
            q_ids = json.loads(t.question_ids) if t.question_ids else []
            company_name = t.job.recruiter.company.company_name if t.job and t.job.recruiter and t.job.recruiter.company else "TechNova Labs"
            results.append({
                "template_id": t.template_id,
                "recruiter_id": t.recruiter_id,
                "job_id": t.job_id,
                "job_title": t.job.title if t.job else "Job Opening",
                "company_name": company_name,
                "title": t.title,
                "tech_stack": t.tech_stack,
                "duration_minutes": t.duration_minutes,
                "passing_percentage": t.passing_percentage,
                "status": t.status,
                "question_ids": q_ids,
                "questions_count": len(q_ids),
                "created_at": t.created_at,
                "updated_at": t.updated_at
            })
        return results

    @staticmethod
    def auto_assign_published_template_to_shortlisted(db: Session, template: AssessmentTemplate):
        """
        When a template is published, automatically generates tests for any candidate who is
        shortlisted for this job but has not yet received their assessment.
        """
        shortlisted_apps = db.query(Application).filter(
            Application.job_id == template.job_id,
            Application.status == "Shortlisted"
        ).all()

        for app in shortlisted_apps:
            # Check if candidate already has an assessment for this job
            existing = db.query(Assessment).filter(
                Assessment.candidate_id == app.candidate_id,
                Assessment.job_id == template.job_id
            ).first()
            if not existing:
                try:
                    AssessmentService.generate_assessment_from_template(
                        db=db,
                        candidate=app.candidate,
                        job=app.job,
                        template=template,
                        application_id=app.application_id
                    )
                except Exception as e:
                    print(f"Notice auto-assigning assessment: {e}")

    # ================= 3. CANDIDATE ASSESSMENT INSTANTIATION =================

    @classmethod
    def generate_assessment_from_template(
        cls, 
        db: Session, 
        candidate: Candidate, 
        job: Job, 
        template: AssessmentTemplate,
        application_id: Optional[int] = None
    ) -> Assessment:
        """
        Instantiates a unique candidate assessment strictly using the recruiter's published 20 questions.
        - Randomizes question sequence.
        - Randomizes 4-option orders without altering the correct answer string.
        - Generates secure candidate-only access token.
        - Dispatches invitation email.
        """
        # Check existing
        existing = db.query(Assessment).filter(
            Assessment.candidate_id == candidate.candidate_id,
            Assessment.job_id == job.job_id
        ).first()
        if existing:
            return existing

        q_ids = json.loads(template.question_ids) if template.question_ids else []
        questions_pool = db.query(RecruiterQuestion).filter(RecruiterQuestion.question_id.in_(q_ids)).all()

        # If some questions were missing or template is slightly short, supplement from recruiter's pool or library
        if len(questions_pool) < 20:
            all_recruiter_qs = db.query(RecruiterQuestion).filter(
                RecruiterQuestion.recruiter_id == template.recruiter_id
            ).all()
            for q in all_recruiter_qs:
                if q not in questions_pool:
                    questions_pool.append(q)
                if len(questions_pool) == 20:
                    break

        # If still under 20, import required library questions
        if len(questions_pool) < 20:
            needed = 20 - len(questions_pool)
            imported = cls.import_library_questions(db, template.recruiter_id, template.tech_stack, count=needed, job_id=job.job_id)
            questions_pool.extend(imported)

        selected_20 = list(questions_pool[:20])
        # Randomize question presentation order for this candidate
        random.shuffle(selected_20)

        test_token = f"test_{uuid.uuid4().hex}"

        assessment = Assessment(
            template_id=template.template_id,
            application_id=application_id,
            candidate_id=candidate.candidate_id,
            job_id=job.job_id,
            test_token=test_token,
            title=template.title,
            tech_stack=template.tech_stack,
            total_questions=20,
            time_limit_minutes=template.duration_minutes,
            passing_percentage=template.passing_percentage,
            status="pending",
            created_at=utc_now()
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        # Instantiate the 20 questions with randomized option sequence
        for idx, rq in enumerate(selected_20):
            raw_options = json.loads(rq.options)
            shuffled_options = list(raw_options)
            random.shuffle(shuffled_options)

            q_obj = AssessmentQuestion(
                assessment_id=assessment.assessment_id,
                question_text=rq.question_text,
                skill_category=rq.technology,
                difficulty=rq.difficulty,
                options=json.dumps(shuffled_options),
                correct_answer=rq.correct_answer,
                explanation=rq.explanation or "",
                order_index=idx + 1
            )
            db.add(q_obj)

        db.commit()
        db.refresh(assessment)

        # Send Invitation Email
        test_link = f"http://localhost:5173/assessment/{test_token}"
        try:
            EmailService.send_test_invitation_email(
                db=db,
                candidate=candidate,
                job=job,
                test_link=test_link,
                time_limit=template.duration_minutes
            )
        except Exception as e:
            print(f"Notice: Failed to dispatch invitation email: {e}")

        return assessment

    @classmethod
    def generate_assessment(
        cls, 
        db: Session, 
        candidate: Candidate, 
        job: Job, 
        application_id: Optional[int] = None,
        time_limit_minutes: Optional[int] = None
    ) -> Assessment:
        """
        Main entry point for candidate assessment generation:
        Looks for the recruiter's published AssessmentTemplate for this job.
        If recruiter has not created one yet, initializes 20 recruiter-approved questions from the library
        and creates a published template for this job under the recruiter's ownership.
        """
        # 1. Check existing candidate assessment
        existing = db.query(Assessment).filter(
            Assessment.candidate_id == candidate.candidate_id,
            Assessment.job_id == job.job_id
        ).first()
        if existing:
            return existing

        # 2. Look for published assessment template for this job
        template = db.query(AssessmentTemplate).filter(
            AssessmentTemplate.job_id == job.job_id,
            AssessmentTemplate.status == "published"
        ).first()

        if not template:
            # Check for draft template
            template = db.query(AssessmentTemplate).filter(
                AssessmentTemplate.job_id == job.job_id
            ).first()

        if not template:
            # Seed a default recruiter assessment template for this job so recruiter immediately controls it
            recruiter_id = job.recruiter_id
            tech = "Full Stack Engineering"
            if job.skills:
                tech = job.skills[0].skill_name

            # Import 20 questions into recruiter's question bank
            imported_qs = cls.import_library_questions(db, recruiter_id=recruiter_id, technology=tech, count=20, job_id=job.job_id)
            q_ids = [q.question_id for q in imported_qs]

            template = AssessmentTemplate(
                recruiter_id=recruiter_id,
                job_id=job.job_id,
                title=f"{job.title} Technical Evaluation",
                tech_stack=tech,
                duration_minutes=time_limit_minutes or 25,
                passing_percentage=60.0,
                status="published",
                question_ids=json.dumps(q_ids),
                created_at=utc_now(),
                updated_at=utc_now()
            )
            db.add(template)
            db.commit()
            db.refresh(template)

        return cls.generate_assessment_from_template(
            db=db,
            candidate=candidate,
            job=job,
            template=template,
            application_id=application_id
        )

    # ================= 4. CANDIDATE TEST TAKING & GRADING =================

    @staticmethod
    def get_assessment_for_candidate(db: Session, token: str, user: User) -> Dict[str, Any]:
        """
        Fetches test data for the candidate. Strictly hides correct answers and explanations.
        Enforces candidate authentication & RBAC.
        """
        assessment = db.query(Assessment).filter(Assessment.test_token == token).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found or invalid test token.")

        if user.role == "job_seeker":
            candidate = db.query(Candidate).filter(Candidate.user_id == user.user_id).first()
            if not candidate or assessment.candidate_id != candidate.candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized: You can only access technical assessments assigned to your candidate account."
                )

        # Check deadline expiry
        if assessment.status not in ["completed", "terminated_proctoring"]:
            if is_expired(assessment.expires_at):
                assessment.status = "expired"
                db.commit()
                db.refresh(assessment)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This assessment link has expired. Please contact the recruiter for a new assessment link."
                )

        if assessment.status == "expired":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This assessment link has expired. Please contact the recruiter for a new assessment link."
            )

        if assessment.status == "completed":
            return {
                "assessment_id": assessment.assessment_id,
                "test_token": assessment.test_token,
                "title": assessment.title,
                "description": getattr(assessment, "description", None),
                "tech_stack": assessment.tech_stack,
                "status": "completed",
                "score": assessment.score,
                "percentage": assessment.percentage,
                "passed": assessment.passed,
                "total_questions": assessment.total_questions,
                "completed_at": assessment.completed_at,
                "expires_at": assessment.expires_at,
                "message": "This assessment has already been submitted and evaluated."
            }
        if assessment.status == "terminated_proctoring":
            return {
                "assessment_id": assessment.assessment_id,
                "test_token": assessment.test_token,
                "title": assessment.title,
                "description": getattr(assessment, "description", None),
                "status": "terminated_proctoring",
                "violation_count": getattr(assessment, "violation_count", 3) or 3,
                "auto_submitted_proctoring": True,
                "proctoring_submission_reason": getattr(assessment, "proctoring_submission_reason", "Terminated due to 3 proctoring strikes"),
                "score": assessment.score,
                "percentage": assessment.percentage,
                "expires_at": assessment.expires_at,
                "message": "This assessment was terminated due to proctoring violations."
            }
   
        questions_payload = []
        for q in assessment.questions:
            questions_payload.append({
                "question_id": q.question_id,
                "order_index": q.order_index,
                "question_text": q.question_text,
                "skill_category": q.skill_category,
                "difficulty": q.difficulty,
                "options": json.loads(q.options)
            })

        company_name = assessment.job.recruiter.company.company_name if assessment.job and assessment.job.recruiter and assessment.job.recruiter.company else "Company"

        return {
            "assessment_id": assessment.assessment_id,
            "test_token": assessment.test_token,
            "title": assessment.title,
            "description": getattr(assessment, "description", None),
            "tech_stack": assessment.tech_stack,
            "job_id": assessment.job_id,
            "job_title": assessment.job.title if assessment.job else "Technical Assessment",
            "company_name": company_name,
            "total_questions": assessment.total_questions,
            "time_limit_minutes": assessment.time_limit_minutes,
            "status": assessment.status,
            "started_at": assessment.started_at,
            "expires_at": assessment.expires_at,
            "questions": questions_payload
        }

    @staticmethod
    def submit_and_evaluate(
        db: Session, 
        assessment_id: int, 
        submitted_answers: Dict[str, str], 
        user: User
    ) -> Dict[str, Any]:
        """
        Evaluates answers, scores out of 20, updates application status based on configured
        passing percentage, and dispatches confirmation email.
        """
        assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found.")

        if user.role == "job_seeker":
            candidate = db.query(Candidate).filter(Candidate.user_id == user.user_id).first()
            if not candidate or assessment.candidate_id != candidate.candidate_id:
                raise HTTPException(status_code=403, detail="Unauthorized access to this assessment.")

        if assessment.status == "terminated_proctoring":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This assessment was terminated due to proctoring violations and cannot be submitted."
            )

        if assessment.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This assessment has already been completed and submitted. Duplicate submissions are prevented."
            )

        if assessment.status != "completed" and assessment.status != "terminated_proctoring":
            if is_expired(assessment.expires_at):
                assessment.status = "expired"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This assessment link has expired and can no longer be submitted."
                )

        if assessment.status == "expired":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This assessment link has expired and can no longer be submitted."
            )

        correct_count = 0
        breakdown = []

        for q in assessment.questions:
            user_chosen = submitted_answers.get(str(q.question_id)) or submitted_answers.get(q.question_id)
            is_correct = (user_chosen == q.correct_answer)
            if is_correct:
                correct_count += 1

            breakdown.append({
                "question_id": q.question_id,
                "order_index": q.order_index,
                "question_text": q.question_text,
                "skill_category": q.skill_category,
                "difficulty": q.difficulty,
                "options": json.loads(q.options),
                "candidate_answer": user_chosen,
                "correct_answer": q.correct_answer,
                "is_correct": is_correct,
                "explanation": q.explanation
            })

        total = assessment.total_questions or 20
        percentage = round((correct_count / total) * 100.0, 1)

        pass_mark = assessment.passing_percentage if assessment.passing_percentage is not None else 60.0
        passed = percentage >= pass_mark

        assessment.score = float(correct_count)
        assessment.percentage = percentage
        assessment.passed = passed
        assessment.correct_answers_count = correct_count
        assessment.incorrect_answers_count = total - correct_count
        assessment.status = "completed"
        assessment.completed_at = utc_now()
        assessment.candidate_answers = json.dumps(breakdown)

        # Update candidate Application status
        app_record = None
        if assessment.application_id:
            app_record = db.query(Application).filter(Application.application_id == assessment.application_id).first()
        if not app_record:
            app_record = db.query(Application).filter(
                Application.candidate_id == assessment.candidate_id,
                Application.job_id == assessment.job_id
            ).first()

        if app_record:
            if passed:
                app_record.status = "Interview"
            else:
                app_record.status = "Under Review"

        db.commit()
        db.refresh(assessment)

        # Send Submission & Results Confirmation Email
        try:
            EmailService.send_submission_confirmation_email(
                db=db,
                candidate=assessment.candidate,
                job=assessment.job,
                score=assessment.score,
                total=total,
                percentage=percentage,
                passed=passed
            )
        except Exception as e:
            print(f"Notice: Failed to dispatch confirmation email: {e}")

        return {
            "assessment_id": assessment.assessment_id,
            "title": assessment.title,
            "status": "completed",
            "score": assessment.score,
            "total_questions": total,
            "percentage": percentage,
            "passed": passed,
            "passing_percentage": pass_mark,
            "correct_answers_count": correct_count,
            "incorrect_answers_count": total - correct_count,
            "completed_at": assessment.completed_at,
            "breakdown": breakdown
        }

    @staticmethod
    def get_assessment_results(db: Session, assessment_id: int) -> Dict[str, Any]:
        """
        Fetches detailed evaluation results including question-by-question breakdown.
        """
        assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found.")

        breakdown = json.loads(assessment.candidate_answers) if assessment.candidate_answers else []
        company_name = assessment.job.recruiter.company.company_name if assessment.job.recruiter and assessment.job.recruiter.company else "Company"

        return {
            "assessment_id": assessment.assessment_id,
            "candidate_id": assessment.candidate_id,
            "candidate_name": assessment.candidate.user.name if assessment.candidate and assessment.candidate.user else "Candidate",
            "candidate_email": assessment.candidate.user.email if assessment.candidate and assessment.candidate.user else "",
            "job_id": assessment.job_id,
            "job_title": assessment.job.title,
            "company_name": company_name,
            "title": assessment.title,
            "tech_stack": assessment.tech_stack,
            "status": assessment.status,
            "score": assessment.score,
            "total_questions": assessment.total_questions,
            "percentage": assessment.percentage,
            "passed": assessment.passed,
            "passing_percentage": assessment.passing_percentage or 60.0,
            "correct_answers_count": assessment.correct_answers_count,
            "incorrect_answers_count": assessment.incorrect_answers_count,
            "started_at": assessment.started_at,
            "completed_at": assessment.completed_at,
            "breakdown": breakdown
        }

    # ================= 5. RECRUITER & ADMIN TELEMETRY =================

    @staticmethod
    def get_recruiter_stats(db: Session, recruiter_id: int) -> Dict[str, Any]:
        """
        Calculates recruiter-specific assessment statistics.
        """
        total_questions = db.query(RecruiterQuestion).filter(RecruiterQuestion.recruiter_id == recruiter_id).count()
        published_count = db.query(AssessmentTemplate).filter(
            AssessmentTemplate.recruiter_id == recruiter_id,
            AssessmentTemplate.status == "published"
        ).count()
        draft_count = db.query(AssessmentTemplate).filter(
            AssessmentTemplate.recruiter_id == recruiter_id,
            AssessmentTemplate.status == "draft"
        ).count()

        # Assessments for recruiter's jobs
        recruiter_job_ids = [j.job_id for j in db.query(Job.job_id).filter(Job.recruiter_id == recruiter_id).all()]
        assessments = db.query(Assessment).filter(Assessment.job_id.in_(recruiter_job_ids)).all() if recruiter_job_ids else []

        completed = [a for a in assessments if a.status == "completed"]
        passed = [a for a in completed if a.passed is True]
        avg_score = 0.0
        if completed:
            scores = [a.percentage for a in completed if a.percentage is not None]
            if scores:
                avg_score = round(sum(scores) / len(scores), 1)

        return {
            "total_questions": total_questions,
            "published_assessments": published_count,
            "draft_assessments": draft_count,
            "total_candidates_tested": len(assessments),
            "tests_completed": len(completed),
            "tests_passed": len(passed),
            "average_score": avg_score
        }

    @staticmethod
    def get_admin_stats(db: Session) -> Dict[str, Any]:
        """
        Global platform-wide assessment telemetry for administrators.
        """
        total_questions = db.query(RecruiterQuestion).count()
        total_templates = db.query(AssessmentTemplate).count()
        published_templates = db.query(AssessmentTemplate).filter(AssessmentTemplate.status == "published").count()
        draft_templates = db.query(AssessmentTemplate).filter(AssessmentTemplate.status == "draft").count()

        all_assessments = db.query(Assessment).all()
        completed = [a for a in all_assessments if a.status == "completed"]
        passed = [a for a in completed if a.passed is True]

        avg_score = 0.0
        if completed:
            scores = [a.percentage for a in completed if a.percentage is not None]
            if scores:
                avg_score = round(sum(scores) / len(scores), 1)

        # Job-wise breakdown
        jobs = db.query(Job).all()
        job_stats = []
        for j in jobs:
            t = db.query(AssessmentTemplate).filter(AssessmentTemplate.job_id == j.job_id).first()
            j_assessments = [a for a in all_assessments if a.job_id == j.job_id]
            job_stats.append({
                "job_id": j.job_id,
                "title": j.title,
                "recruiter_name": j.recruiter.user.name if j.recruiter and j.recruiter.user else "Recruiter",
                "company_name": j.recruiter.company.company_name if j.recruiter and j.recruiter.company else "Company",
                "template_status": t.status if t else "not_created",
                "duration_minutes": t.duration_minutes if t else 25,
                "total_tested": len(j_assessments),
                "completed": len([a for a in j_assessments if a.status == "completed"]),
                "passed": len([a for a in j_assessments if a.passed is True])
            })

        return {
            "total_questions": total_questions,
            "total_templates": total_templates,
            "published_templates": published_templates,
            "draft_templates": draft_templates,
            "total_assessments": len(all_assessments),
            "completed_assessments": len(completed),
            "passed_assessments": len(passed),
            "average_score": avg_score,
            "job_statistics": job_stats
        }
