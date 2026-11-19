import os
import smtplib
import socket
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from datetime import datetime, timezone, timedelta
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import EmailNotification, Candidate, Job, User

logger = logging.getLogger("skillsphere.email")

# In-memory deduplication cache: {(recipient, email_type): timestamp}
_recent_dispatches: Dict[str, datetime] = {}
DEDUP_WINDOW_SECONDS = 15


class EmailService:
    @staticmethod
    def _is_duplicate(recipient_email: str, email_type: str) -> bool:
        """Check if an identical email was dispatched within DEDUP_WINDOW_SECONDS."""
        key = f"{recipient_email.lower().strip()}:{email_type}"
        now = datetime.now(timezone.utc)
        last_sent = _recent_dispatches.get(key)
        if last_sent:
            if (now - last_sent).total_seconds() < DEDUP_WINDOW_SECONDS:
                return True
        _recent_dispatches[key] = now
        # Clean older keys periodically
        if len(_recent_dispatches) > 200:
            threshold = now - timedelta(seconds=120)
            stale_keys = [k for k, v in _recent_dispatches.items() if v < threshold]
            for k in stale_keys:
                _recent_dispatches.pop(k, None)
        return False

    @staticmethod
    def _send_smtp_email(
        to_email: str,
        recipient_name: str,
        subject: str,
        body_html: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Deliver a real email over SMTP using configured environment variables.
        If SMTP credentials are not yet configured, log the payload safely and return False.
        """
        smtp_host = (settings.SMTP_HOST or "").strip()
        smtp_port = settings.SMTP_PORT or 587
        smtp_user = (settings.SMTP_USER or "").strip()
        smtp_password = (settings.SMTP_PASSWORD or "").strip()
        from_email = (settings.SMTP_FROM_EMAIL or smtp_user or "no-reply@skillsphere.com").strip()
        from_name = (settings.SMTP_FROM_NAME or "SkillSphere Career Portal").strip()

        if not smtp_host:
            print(f"[EMAIL SERVICE] Notice: SMTP_HOST not configured. Email to <{to_email}> with subject '{subject}' was saved to database and ready for live SMTP upon adding credentials to .env.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{from_email}>"
            msg["To"] = f"{recipient_name} <{to_email}>" if recipient_name else to_email
            msg["Date"] = formatdate(localtime=True)
            msg["Message-ID"] = make_msgid(domain="skillsphere.com")

            # Fallback plain text part
            plain_text = text_content or "Please open this email in an HTML-compatible client to view the full SkillSphere notification."
            part_text = MIMEText(plain_text, "plain", "utf-8")
            part_html = MIMEText(body_html, "html", "utf-8")
            msg.attach(part_text)
            msg.attach(part_html)

            # Establish SMTP connection
            if settings.SMTP_SSL or smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
                if settings.SMTP_TLS:
                    server.starttls()

            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)

            server.send_message(msg)
            server.quit()
            print(f"[EMAIL SERVICE] SUCCESS: Real email dispatched via SMTP to {to_email} | Subject: '{subject}'")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL SERVICE] SMTP Auth Error when sending to {to_email}: Check SMTP_USER & SMTP_PASSWORD in .env. ({e})")
            return False
        except (socket.error, smtplib.SMTPException, Exception) as e:
            print(f"[EMAIL SERVICE] SMTP Delivery Failed for {to_email}: {e}")
            return False

    @staticmethod
    def _create_email_frame(title: str, subtitle: str, content_html: str, accent_color: str = "#00f5ff") -> str:
        """Create a consistent, responsive, high-end SkillSphere dark cyberpunk HTML email template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #060913; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #060913; padding: 24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 600px; background-color: #0d1322; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); overflow: hidden; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);" cellspacing="0" cellpadding="0" border="0">
          
          <!-- Header -->
          <tr>
            <td style="padding: 28px 32px; background: linear-gradient(135deg, rgba(0, 245, 255, 0.12), rgba(99, 102, 241, 0.12)); border-bottom: 2px solid {accent_color};">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <span style="font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">Skill<span style="color: {accent_color};">Sphere</span></span>
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #94a3b8; margin-top: 4px;">Career & Job Intelligence Portal</div>
                  </td>
                  <td align="right">
                    <span style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; background-color: rgba(255, 255, 255, 0.08); color: {accent_color}; border: 1px solid rgba(255, 255, 255, 0.12);">Verified Notice</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Banner / Title -->
          <tr>
            <td style="padding: 28px 32px 12px 32px;">
              <h1 style="margin: 0 0 6px 0; font-size: 20px; font-weight: 700; color: #ffffff;">{title}</h1>
              <p style="margin: 0; font-size: 13px; color: #94a3b8;">{subtitle}</p>
            </td>
          </tr>

          <!-- Main Content -->
          <tr>
            <td style="padding: 12px 32px 28px 32px;">
              {content_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 24px 32px; background-color: #090e1a; border-top: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
              <p style="margin: 0 0 8px 0; font-size: 12px; color: #64748b;">
                You received this email because you are a registered user of SkillSphere.
              </p>
              <p style="margin: 0; font-size: 11px; color: #475569;">
                &copy; {datetime.now().year} SkillSphere Platform. All rights reserved. • AI-Powered Talent & Assessment System
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    # =========================================================================
    # EVENT A: USER REGISTRATION WELCOME EMAIL
    # =========================================================================
    @staticmethod
    def send_welcome_email(
        db: Session,
        user: User,
        company_name: Optional[str] = None
    ) -> Optional[EmailNotification]:
        """Send a professional welcome email to newly registered users."""
        if EmailService._is_duplicate(user.email, "welcome"):
            return None

        role_display = "Recruiter" if user.role == "recruiter" else ("Administrator" if user.role == "admin" else "Job Seeker / Candidate")
        accent = "#6366f1" if user.role == "recruiter" else "#00f5ff"

        role_specific_content = ""
        if user.role == "recruiter":
            role_specific_content = f"""
            <div style="background-color: #121829; border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 10px; padding: 18px; margin: 18px 0;">
              <div style="font-weight: 700; color: #a5b4fc; font-size: 13px; margin-bottom: 8px;">💼 Recruiter Next Steps:</div>
              <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li><strong>Company Workspace:</strong> Linked with {company_name or 'your enterprise'}.</li>
                <li><strong>Post Open Positions:</strong> Define tech stacks and required skills.</li>
                <li><strong>Customize 20-Question Assessments:</strong> Assemble automated screening tests with anti-cheat camera proctoring.</li>
                <li><strong>ATS Kanban Board:</strong> Seamlessly move applicants from Applied to Interview and Hired.</li>
              </ul>
            </div>
            """
        else:
            role_specific_content = """
            <div style="background-color: #121829; border: 1px solid rgba(0, 245, 255, 0.25); border-radius: 10px; padding: 18px; margin: 18px 0;">
              <div style="font-weight: 700; color: #67e8f9; font-size: 13px; margin-bottom: 8px;">🚀 Quick Start Guide:</div>
              <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li><strong>Upload Your Resume:</strong> Our OCR engine will automatically extract your technical skills, experience, and education.</li>
                <li><strong>Check Real-Time Match Scores:</strong> See your 0-100% fit score for top industry tech jobs.</li>
                <li><strong>Take Technical Assessments:</strong> Prove your skills with 20-question customized technical evaluations.</li>
                <li><strong>Chat With AI Assistant:</strong> Ask anything in English, Hindi, Punjabi, or Hinglish anytime!</li>
              </ul>
            </div>
            """

        body_content = f"""
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-top: 0;">
          Dear <strong>{user.name}</strong>,
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1;">
          Welcome to <strong>SkillSphere</strong>! Your account has been successfully created and your session is active.
        </p>

        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0b1120; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); margin: 16px 0;">
          <tr>
            <td style="padding: 14px 18px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="font-size: 13px; color: #94a3b8;">
                <tr>
                  <td style="padding-bottom: 6px; width: 130px;"><strong>Registered Email:</strong></td>
                  <td style="color: #ffffff; padding-bottom: 6px;">{user.email}</td>
                </tr>
                <tr>
                  <td style="padding-bottom: 6px;"><strong>Account Type:</strong></td>
                  <td style="color: {accent}; font-weight: 600; padding-bottom: 6px;">{role_display}</td>
                </tr>
                <tr>
                  <td><strong>Registration Date:</strong></td>
                  <td style="color: #ffffff;">{datetime.now(timezone.utc).strftime('%d %B %Y, %I:%M %p UTC')}</td>
                </tr>
              </table>
            </td>
          </tr>
        </table>

        {role_specific_content}

        <p style="font-size: 13px; color: #94a3b8; line-height: 1.6;">
          If you have any questions or need guidance navigating the portal, our AI Chatbot is available 24/7 on your dashboard.
        </p>
        """

        full_html = EmailService._create_email_frame(
            title="Welcome to SkillSphere",
            subtitle=f"Account confirmed for {user.name}",
            content_html=body_content,
            accent_color=accent
        )

        subject = f"Welcome to SkillSphere – Getting Started as a {role_display}"

        notification = EmailNotification(
            recipient_email=user.email,
            recipient_name=user.name,
            subject=subject,
            body_html=full_html,
            email_type="welcome",
            status="Queued",
            sent_date=datetime.utcnow()
        )
        try:
            db.add(notification)
            db.commit()
            db.refresh(notification)

            dispatched = EmailService._send_smtp_email(
                to_email=user.email,
                recipient_name=user.name,
                subject=subject,
                body_html=full_html
            )
            notification.status = "Sent" if dispatched else "Logged"
            db.commit()
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Error recording welcome email: {e}")
            return None

    # =========================================================================
    # EVENT B: LOGIN NOTIFICATION EMAIL
    # =========================================================================
    @staticmethod
    def send_login_notification_email(
        db: Session,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[EmailNotification]:
        """Send an instant security login notification email."""
        if EmailService._is_duplicate(user.email, "login_alert"):
            return None

        login_time_str = datetime.now(timezone.utc).strftime("%d %B %Y at %I:%M %p UTC")
        device_info = user_agent if user_agent else "Standard Web Browser"
        ip_display = ip_address if ip_address else "Client IP Recorded"

        body_content = f"""
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-top: 0;">
          Hello <strong>{user.name}</strong>,
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1;">
          We detected a successful sign-in to your SkillSphere account. Here are the security details of this session:
        </p>

        <div style="background-color: #0b1120; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); padding: 18px; margin: 18px 0;">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="font-size: 13px; color: #94a3b8;">
            <tr>
              <td style="padding-bottom: 8px; width: 120px;"><strong>Date & Time:</strong></td>
              <td style="color: #ffffff; padding-bottom: 8px;">{login_time_str}</td>
            </tr>
            <tr>
              <td style="padding-bottom: 8px;"><strong>IP Address:</strong></td>
              <td style="color: #00f5ff; font-family: monospace; padding-bottom: 8px;">{ip_display}</td>
            </tr>
            <tr>
              <td style="padding-bottom: 4px;"><strong>Device/Browser:</strong></td>
              <td style="color: #ffffff; padding-bottom: 4px; font-size: 12px; word-break: break-all;">{device_info}</td>
            </tr>
          </table>
        </div>

        <div style="background-color: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 14px 18px; margin: 18px 0;">
          <p style="margin: 0; font-size: 13px; color: #fca5a5; line-height: 1.5;">
            <strong>Don't recognize this sign-in?</strong> Someone may have gained unauthorized access to your account. Please reset your password immediately using the Forgot Password feature on the login screen.
          </p>
        </div>
        """

        full_html = EmailService._create_email_frame(
            title="New Sign-In Detected",
            subtitle="Security alert for your SkillSphere session",
            content_html=body_content,
            accent_color="#38bdf8"
        )

        subject = f"Security Alert: New Sign-in to your SkillSphere account ({login_time_str})"

        notification = EmailNotification(
            recipient_email=user.email,
            recipient_name=user.name,
            subject=subject,
            body_html=full_html,
            email_type="login_alert",
            status="Queued",
            sent_date=datetime.utcnow()
        )
        try:
            db.add(notification)
            db.commit()
            db.refresh(notification)

            dispatched = EmailService._send_smtp_email(
                to_email=user.email,
                recipient_name=user.name,
                subject=subject,
                body_html=full_html
            )
            notification.status = "Sent" if dispatched else "Logged"
            db.commit()
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Error recording login alert email: {e}")
            return None

    # =========================================================================
    # EVENT C-1: PASSWORD RESET OTP EMAIL
    # =========================================================================
    @staticmethod
    def send_password_reset_otp_email(
        db: Session,
        email: str,
        user_name: str,
        otp: str,
        expires_minutes: int = 15
    ) -> Optional[EmailNotification]:
        """Send a one-time password (OTP) email for secure password recovery."""
        body_content = f"""
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-top: 0;">
          Hello <strong>{user_name}</strong>,
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1;">
          We received a request to reset your password for your SkillSphere account. Use the following One-Time Password (OTP) to continue:
        </p>

        <!-- Big OTP Display -->
        <div style="text-align: center; margin: 26px 0;">
          <div style="display: inline-block; background: linear-gradient(135deg, rgba(0, 245, 255, 0.15), rgba(99, 102, 241, 0.15)); border: 2px dashed #00f5ff; border-radius: 12px; padding: 18px 36px;">
            <span style="font-family: 'Courier New', monospace; font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #00f5ff;">{otp}</span>
          </div>
          <p style="margin: 8px 0 0 0; font-size: 12px; color: #94a3b8;">
            ⏰ Valid for <strong>{expires_minutes} minutes</strong>. Single use only.
          </p>
        </div>

        <div style="background-color: #0b1120; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); padding: 14px 18px; margin: 18px 0;">
          <p style="margin: 0; font-size: 12px; color: #cbd5e1; line-height: 1.5;">
            🔒 <strong>Security Warning:</strong> Never share this code with anyone. SkillSphere staff will never ask you for your password reset code or password.
          </p>
        </div>

        <p style="font-size: 12px; color: #64748b; line-height: 1.5;">
          If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.
        </p>
        """

        full_html = EmailService._create_email_frame(
            title="Password Reset Verification Code",
            subtitle="One-Time Password (OTP) for account recovery",
            content_html=body_content,
            accent_color="#00f5ff"
        )

        subject = f"Your SkillSphere Password Reset Code: {otp}"

        notification = EmailNotification(
            recipient_email=email,
            recipient_name=user_name,
            subject=subject,
            body_html=full_html,
            email_type="password_reset_otp",
            status="Queued",
            sent_date=datetime.utcnow()
        )
        try:
            db.add(notification)
            db.commit()
            db.refresh(notification)

            dispatched = EmailService._send_smtp_email(
                to_email=email,
                recipient_name=user_name,
                subject=subject,
                body_html=full_html
            )
            notification.status = "Sent" if dispatched else "Logged"
            db.commit()
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Error recording reset OTP email: {e}")
            return None

    # =========================================================================
    # EVENT C-2: PASSWORD RESET CONFIRMATION EMAIL
    # =========================================================================
    @staticmethod
    def send_password_changed_confirmation_email(
        db: Session,
        user: User
    ) -> Optional[EmailNotification]:
        """Send a confirmation notice after successful password reset."""
        change_time_str = datetime.now(timezone.utc).strftime("%d %B %Y at %I:%M %p UTC")

        body_content = f"""
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-top: 0;">
          Hello <strong>{user.name}</strong>,
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1;">
          Your password for your SkillSphere account (<strong>{user.email}</strong>) was successfully reset on <strong>{change_time_str}</strong>.
        </p>

        <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 16px; margin: 18px 0;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #10b981; font-weight: 700; font-size: 14px;">✓ Password Successfully Updated</span>
          </div>
          <p style="margin: 8px 0 0 0; font-size: 12px; color: #a7f3d0; line-height: 1.5;">
            You can now log in to the portal using your newly set password.
          </p>
        </div>

        <div style="background-color: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 14px 18px; margin: 18px 0;">
          <p style="margin: 0; font-size: 12px; color: #fca5a5; line-height: 1.5;">
            <strong>Did not authorize this change?</strong> If you did not change your password, someone may have compromised your account. Contact our emergency support team or re-run the password recovery immediately.
          </p>
        </div>
        """

        full_html = EmailService._create_email_frame(
            title="Password Changed Successfully",
            subtitle="Confirmation of credentials update",
            content_html=body_content,
            accent_color="#10b981"
        )

        subject = "Security Notice: Your SkillSphere Password Has Been Reset"

        notification = EmailNotification(
            recipient_email=user.email,
            recipient_name=user.name,
            subject=subject,
            body_html=full_html,
            email_type="password_changed",
            status="Queued",
            sent_date=datetime.utcnow()
        )
        try:
            db.add(notification)
            db.commit()
            db.refresh(notification)

            dispatched = EmailService._send_smtp_email(
                to_email=user.email,
                recipient_name=user.name,
                subject=subject,
                body_html=full_html
            )
            notification.status = "Sent" if dispatched else "Logged"
            db.commit()
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Error recording password changed email: {e}")
            return None

    # =========================================================================
    # RECRUITER / SCREENING PIPELINE EMAILS (ENHANCED WITH SMTP)
    # =========================================================================
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
                status="Queued",
                sent_date=datetime.utcnow(),
                candidate_id=candidate.candidate_id,
                job_id=job.job_id
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)

            dispatched = EmailService._send_smtp_email(
                to_email=email,
                recipient_name=name,
                subject=subject,
                body_html=body_html
            )
            notification.status = "Sent" if dispatched else "Logged"
            db.commit()
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
                status="Queued",
                sent_date=datetime.utcnow(),
                candidate_id=candidate.candidate_id,
                job_id=job.job_id if job else None
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)

            dispatched = EmailService._send_smtp_email(
                to_email=email,
                recipient_name=name,
                subject=subject,
                body_html=body_html
            )
            notification.status = "Sent" if dispatched else "Logged"
            db.commit()
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
                status="Queued",
                sent_date=datetime.utcnow(),
                candidate_id=candidate.candidate_id,
                job_id=job.job_id if job else None
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)

            dispatched = EmailService._send_smtp_email(
                to_email=email,
                recipient_name=name,
                subject=subject,
                body_html=body_html
            )
            notification.status = "Sent" if dispatched else "Logged"
            db.commit()
            print(f"[EMAIL SERVICE] Assessment results email dispatched to {email}: {score}/{total} ({percentage}%)")
            return notification
        except Exception as e:
            print(f"[EMAIL SERVICE] Notice: Failed to dispatch submission confirmation email: {e}")
            return None
