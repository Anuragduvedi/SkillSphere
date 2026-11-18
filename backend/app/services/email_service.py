from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models.models import EmailNotification, Candidate, Job

class EmailService:
    @staticmethod
    def send_shortlisting_email(
        db: Session,
        candidate: Candidate,
        job: Job,
        match_score: Optional[float] = None,
        test_link: Optional[str] = None,
        match_percentage: Optional[float] = None,
        reasons: Optional[Any] = None
    ) -> Optional[EmailNotification]:
        try:
            score = match_score if match_score is not None else (match_percentage if match_percentage is not None else 75.0)
            link = test_link or "/assessment"
            name = candidate.user.name if candidate.user else "Candidate"
            email = candidate.user.email if candidate.user else "candidate@example.com"
            company_name = job.recruiter.company.company_name if job.recruiter and job.recruiter.company else "SkillSphere Partner"

            subject = f"Congratulations! You've Been Shortlisted for {job.title} at {company_name}"
            body_html = f"""
            <div style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; padding: 30px; border-radius: 12px;">
                <div style="border-bottom: 2px solid #00f5ff; padding-bottom: 12px; margin-bottom: 20px;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Skill<span style="color: #00f5ff;">Sphere</span> AI Screening</h1>
                </div>
                <h2 style="color: #10b981;">Candidate Shortlisting Notice</h2>
                <p>Dear <strong>{name}</strong>,</p>
                <p>We are delighted to inform you that your resume and profile matched <strong>{score}%</strong> against the prerequisites for <strong>{job.title}</strong> at <strong>{company_name}</strong>.</p>
                <div style="background-color: #151d32; padding: 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;">
                    <p style="margin: 0 0 8px 0;"><strong>Role:</strong> {job.title}</p>
                    <p style="margin: 0 0 8px 0;"><strong>Company:</strong> {company_name}</p>
                    <p style="margin: 0 0 8px 0;"><strong>AI Requirement Fit:</strong> <span style="color: #10b981; font-weight: bold;">{score}% (Passed 70% Threshold)</span></p>
                    <p style="margin: 0;"><strong>Status:</strong> Automatically Shortlisted</p>
                </div>
                <p>As part of our automated technical screening process, you have been invited to complete a customized <strong>20-Question Technical Assessment</strong> tailored specifically to your background.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background: linear-gradient(135deg, #00f5ff, #6366f1); color: #000000; font-weight: bold; padding: 14px 28px; text-decoration: none; border-radius: 8px; display: inline-block;">
                        Launch Technical Assessment &rarr;
                    </a>
                </div>
                <p style="color: #94a3b8; font-size: 13px;">Please complete the test in a single sitting. The timer begins when you click start.</p>
            </div>
            """

            notification = EmailNotification(
                recipient_email=email,
                recipient_name=name,
                subject=subject,
                body_html=body_html,
                email_type="shortlisting",
                status="Sent",
                candidate_id=candidate.candidate_id,
                job_id=job.job_id
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            print(f"[EMAIL SERVICE] Shortlisting email dispatched to {email} for job {job.title}")
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Failed to dispatch shortlisting email: {e}")
            return None

    @staticmethod
    def send_test_invitation_email(
        db: Session,
        candidate: Candidate,
        job: Optional[Job],
        test_link: str,
        time_limit: int = 25,
        title: Optional[str] = None
    ) -> Optional[EmailNotification]:
        try:
            name = candidate.user.name if candidate.user else "Candidate"
            email = candidate.user.email if candidate.user else "candidate@example.com"
            job_title = job.title if job else (title or "Technical Assessment")
            company_name = job.recruiter.company.company_name if job and job.recruiter and job.recruiter.company else "SkillSphere Partner"

            subject = f"Action Required: SkillSphere Technical Assessment for {job_title}"
            body_html = f"""
            <div style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; padding: 30px; border-radius: 12px;">
                <div style="border-bottom: 2px solid #a855f7; padding-bottom: 12px; margin-bottom: 20px;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Skill<span style="color: #00f5ff;">Sphere</span> Assessment System</h1>
                </div>
                <h2 style="color: #a855f7;">Technical Assessment Invitation</h2>
                <p>Dear <strong>{name}</strong>,</p>
                <p>Your technical evaluation for the <strong>{job_title}</strong> position at <strong>{company_name}</strong> is now live.</p>
                <div style="background-color: #151d32; padding: 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;">
                    <p style="margin: 0 0 6px 0;">• <strong>Total Questions:</strong> 20 Multiple-Choice Questions (MCQs)</p>
                    <p style="margin: 0 0 6px 0;">• <strong>Time Limit:</strong> {time_limit} Minutes (Auto-submits on expiration)</p>
                    <p style="margin: 0 0 6px 0;">• <strong>Coverage:</strong> Core technologies, frameworks, and architecture relevant to your profile</p>
                    <p style="margin: 0;">• <strong>Attempt Policy:</strong> Single Attempt Only</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{test_link}" style="background: linear-gradient(135deg, #a855f7, #00f5ff); color: #ffffff; font-weight: bold; padding: 14px 28px; text-decoration: none; border-radius: 8px; display: inline-block;">
                        Access Your Assessment &rarr;
                    </a>
                </div>
                <p style="color: #94a3b8; font-size: 13px;">If you face any issues, please copy and paste this link into your browser: {test_link}</p>
            </div>
            """

            notification = EmailNotification(
                recipient_email=email,
                recipient_name=name,
                subject=subject,
                body_html=body_html,
                email_type="test_invitation",
                status="Sent",
                candidate_id=candidate.candidate_id,
                job_id=job.job_id if job else None
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            print(f"[EMAIL SERVICE] Assessment invitation dispatched to {email}")
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Failed to dispatch test invitation email: {e}")
            return None

    @staticmethod
    def send_submission_confirmation_email(
        db: Session,
        candidate: Candidate,
        job: Optional[Job],
        score: float,
        total: int,
        percentage: float,
        passed: bool
    ) -> Optional[EmailNotification]:
        try:
            name = candidate.user.name if candidate.user else "Candidate"
            email = candidate.user.email if candidate.user else "candidate@example.com"
            job_title = job.title if job else "Technical Assessment"
            company_name = job.recruiter.company.company_name if job and job.recruiter and job.recruiter.company else "SkillSphere Partner"

            status_text = "Passed" if passed else "Completed"
            status_color = "#10b981" if passed else "#f59e0b"

            subject = f"Assessment Submitted: {job_title} – {status_text} ({percentage}%)"
            body_html = f"""
            <div style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; padding: 30px; border-radius: 12px;">
                <div style="border-bottom: 2px solid #10b981; padding-bottom: 12px; margin-bottom: 20px;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Skill<span style="color: #00f5ff;">Sphere</span> Assessment System</h1>
                </div>
                <h2 style="color: {status_color};">Technical Assessment Results Recorded</h2>
                <p>Dear <strong>{name}</strong>,</p>
                <p>Thank you for completing your technical assessment for <strong>{job_title}</strong> at <strong>{company_name}</strong>.</p>
                <div style="background-color: #151d32; padding: 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;">
                    <p style="margin: 0 0 8px 0;"><strong>Score:</strong> <span style="font-size: 18px; font-weight: bold; color: {status_color};">{score} / {total} ({percentage}%)</span></p>
                    <p style="margin: 0 0 8px 0;"><strong>Evaluation Outcome:</strong> <span style="color: {status_color}; font-weight: bold;">{status_text}</span></p>
                    <p style="margin: 0;"><strong>Application Status:</strong> {'Updated to Interview Priority' if passed else 'Under Final Recruiter Review'}</p>
                </div>
                <p style="color: #cbd5e1;">Your test score and comprehensive question breakdown have been securely registered with the hiring team.</p>
            </div>
            """

            notification = EmailNotification(
                recipient_email=email,
                recipient_name=name,
                subject=subject,
                body_html=body_html,
                email_type="assessment_result",
                status="Sent",
                candidate_id=candidate.candidate_id,
                job_id=job.job_id if job else None
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            print(f"[EMAIL SERVICE] Assessment results email dispatched to {email}: {score}/{total} ({percentage}%)")
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Failed to dispatch submission confirmation email: {e}")
            return None
