import re
import json
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings

SYSTEM_INSTRUCTION = """You are the official AI Assistant for SkillSphere – an advanced AI-Powered Career & Job Portal featuring automated OCR Resume Parsing, Explainable Skill Matching, Customizable 20-Question Technical Assessments, and Real-Time MediaPipe Camera Proctoring.

SkillSphere Platform Overview:
- Job Seekers / Candidates:
  - Can browse tech jobs with real-time match scores (0-100%) and clear breakdown of matched vs missing skills.
  - Upload resumes (PDF, PNG, JPG) with OCR entity extraction that automatically pulls skills, experience, education, and contact details.
  - Complete customized 20-question technical assessments linked to job applications.
  - Track application statuses in real-time.
- 20-Question Technical Assessments:
  - Each assessment consists of exactly 20 technical questions (Beginner, Intermediate, Advanced).
  - Default time limit is 25 minutes with a countdown timer.
  - Passing score is 60% (12 out of 20 correct answers).
  - Passing candidates automatically advance to the 'Interview' stage in the ATS pipeline.
  - Instant automated grading with full question-by-question explanations.
- AI Camera Proctoring System & Three-Strike Policy:
  - Candidates must grant camera permissions before starting the test.
  - Continuous live computer vision monitoring (Face presence, Looking away, Multiple faces, Mobile phone / unauthorized device detection, Window blur / Tab switching, Exiting full-screen).
  - STRIKE 1 (Yellow Warning): Detected violation notification; 2 strikes remaining.
  - STRIKE 2 (Orange Final Warning): Final warning alert; 1 strike remaining before termination.
  - STRIKE 3 (Red Auto-Submission): Test immediately terminates; timer stops; all answered questions are saved; assessment marked as 'terminated_proctoring' and submitted automatically to hiring recruiters.
- Recruiters & Admins:
  - Recruiter Question Bank: Create, edit, search, filter, and manage custom technical questions.
  - Assessment Templates: Build customizable 20-question test templates and associate them with jobs.
  - ATS Kanban Board: Drag-and-drop candidates through stages (Applied, Screening, Interview, Offered, Hired, Rejected).
  - Proctoring & Exam Monitoring Dashboard: Review candidate violation counts, strike history timeline, and telemetry reports.

Guidelines:
- Be friendly, professional, concise, and structured.
- Use bullet points and clear markdown formatting.
- If a candidate has camera or technical issues, give step-by-step troubleshooting instructions.
- Never reveal test answers or correct solutions for active assessment questions.
"""

# Fallback knowledge base topics
FALLBACK_RESPONSES = {
    "proctoring": (
        "### 🛡️ SkillSphere AI Camera Proctoring & Three-Strike System\n\n"
        "Our proctoring system ensures fair and secure assessments for all candidates:\n\n"
        "- **What is Monitored:**\n"
        "  - **Face Detection:** Your face must remain centered and clearly visible in the camera frame.\n"
        "  - **Looking Away:** Prolonged glances away from the screen trigger a warning.\n"
        "  - **Multiple Faces:** No other individuals are permitted in the camera frame.\n"
        "  - **Mobile Phones / Devices:** Detecting a phone or unauthorized device records a strike.\n"
        "  - **Tab Switching & Fullscreen:** Leaving fullscreen or switching browser tabs is strictly prohibited.\n\n"
        "- **The Three-Strike Rule:**\n"
        "  - **Strike 1 (Yellow Alert):** First violation warning with reason recorded.\n"
        "  - **Strike 2 (Orange Alert):** Final warning — only 1 strike remaining before termination.\n"
        "  - **Strike 3 (Red Termination):** Test immediately auto-submits. All current answers are saved, answers are locked, and your recruiter is notified."
    ),
    "camera": (
        "### 📷 Camera Setup & Troubleshooting\n\n"
        "To ensure a smooth proctored exam experience:\n\n"
        "1. **Allow Permissions:** Click the camera icon in your browser's address bar and set Camera to **Allow**.\n"
        "2. **Good Lighting:** Sit in a well-lit room facing your light source (avoid harsh backlighting).\n"
        "3. **Stay in Frame:** Keep your head and shoulders visible within the camera viewfinder.\n"
        "4. **Close Other Apps:** Close apps like Zoom, Teams, or Skype that might hold exclusive camera locks.\n"
        "5. **Refresh Page:** If your camera does not initialize, refresh the page and allow camera access when prompted."
    ),
    "assessment": (
        "### 📝 20-Question Technical Assessments\n\n"
        "- **Format:** Exactly 20 multiple-choice questions tailored to the job's tech stack.\n"
        "- **Time Limit:** 25 minutes (countdown timer is visible at the top).\n"
        "- **Passing Threshold:** 60% (12 out of 20 questions correct).\n"
        "- **Automated Progression:** Scoring 60%+ automatically transitions your application to the **Interview** stage.\n"
        "- **Review & Explanations:** After submitting or upon test completion, you receive an in-depth breakdown of every question with explanations."
    ),
    "resume": (
        "### 📄 Resume Upload & OCR Skill Extraction\n\n"
        "- **Supported Formats:** PDF, PNG, JPG (up to 10MB).\n"
        "- **Smart OCR:** Our backend extracts your candidate name, email, phone, education, experience, and technical skills.\n"
        "- **Match Score:** SkillSphere calculates an explainable 0-100% match score against every job posting, highlighting matched and missing skills."
    ),
    "recruiter": (
        "### 💼 Recruiter Management Features\n\n"
        "- **Question Bank:** Add and manage custom technical questions across Beginner, Intermediate, and Advanced tiers.\n"
        "- **Assessment Templates:** Configure customized 20-question screening templates for any job opening.\n"
        "- **ATS Kanban Board:** Track applicants from Applied to Screening, Interview, and Hired stages.\n"
        "- **Proctoring Telemetry:** Inspect candidate proctoring violation logs, strike counts, and camera activity timestamps."
    )
}

class ChatbotService:
    @staticmethod
    def get_response(
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response using Google Gemini API if GEMINI_API_KEY is configured.
        Otherwise or on any network/API failure, use intelligent offline knowledge base.
        """
        clean_msg = message.strip()
        if not clean_msg:
            return {
                "reply": "Hello! I am your SkillSphere AI Assistant. How can I help you today with assessments, camera proctoring, or jobs?",
                "provider": "skillsphere_assistant",
                "timestamp": datetime.utcnow().isoformat()
            }

        api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""

        # Attempt Gemini API if key is available
        if api_key:
            try:
                reply = ChatbotService._call_gemini_api(api_key, clean_msg, history)
                if reply:
                    return {
                        "reply": reply,
                        "provider": "gemini",
                        "timestamp": datetime.utcnow().isoformat()
                    }
            except Exception as e:
                # Log without exposing key and fall back gracefully
                print(f"[SkillSphere Chatbot] Gemini API call note: {e}. Falling back to knowledge engine.")

        # Fallback to local intelligent knowledge engine
        reply = ChatbotService._generate_fallback_response(clean_msg, context)
        return {
            "reply": reply,
            "provider": "skillsphere_assistant",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def _call_gemini_api(
        api_key: str,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """
        Direct REST call to Google Gemini Generative Language API.
        NO Vertex AI SDK or GCP project permissions needed!
        """
        model = settings.GEMINI_MODEL or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        contents = []

        # Convert recent conversation history (up to last 6 turns)
        if history:
            for turn in history[-6:]:
                role = "user" if turn.get("role") in ["user", "candidate"] else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": str(turn.get("content", ""))[:1500]}]
                })

        contents.append({
            "role": "user",
            "parts": [{"text": message[:2000]}]
        })

        payload = {
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
                "topP": 0.95
            }
        }

        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
            else:
                print(f"[SkillSphere Chatbot] Gemini responded with status {resp.status_code}: {resp.text[:200]}")
                return None

        return None

    @staticmethod
    def _generate_fallback_response(message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Comprehensive offline contextual SkillSphere Assistant.
        Provides instant, detailed answers matching platform capabilities.
        """
        lower = message.lower()

        # Proctoring & Strike inquiries
        if any(w in lower for w in ["proctor", "strike", "violation", "cheat", "rule", "warning", "terminate", "auto submit", "auto-submit"]):
            return (
                f"{FALLBACK_RESPONSES['proctoring']}\n\n"
                "> 💡 **Tip:** Keep your camera centered, avoid switching browser tabs, and ensure no other persons enter the camera frame during your assessment."
            )

        # Camera & Hardware inquiries
        if any(w in lower for w in ["camera", "webcam", "video", "permission", "black screen", "feed", "hardware"]):
            return (
                f"{FALLBACK_RESPONSES['camera']}\n\n"
                "> 💡 **Tip:** If the camera status dot is green in the test portal, your live feed and MediaPipe face tracking are active."
            )

        # Assessment & Test inquiries
        if any(w in lower for w in ["assessment", "test", "exam", "quiz", "question", "duration", "time limit", "pass", "marks", "score"]):
            return (
                f"{FALLBACK_RESPONSES['assessment']}\n\n"
                "> 💡 **Assessment Structure:** The 20 questions are drawn from the job's assigned technical template with Beginner, Intermediate, and Advanced difficulty levels."
            )

        # Resume & OCR inquiries
        if any(w in lower for w in ["resume", "cv", "upload", "ocr", "parse", "match", "skill score"]):
            return (
                f"{FALLBACK_RESPONSES['resume']}\n\n"
                "> 💡 **Tip:** Upload your resume directly on your candidate dashboard to automatically populate your technical profile."
            )

        # Recruiter inquiries
        if any(w in lower for w in ["recruiter", "hire", "template", "kanban", "create question", "applicant"]):
            return (
                f"{FALLBACK_RESPONSES['recruiter']}\n\n"
                "> 💡 **Tip:** Navigate to the Recruiter Dashboard to create custom technical questions and assemble 20-question test templates."
            )

        # Greetings
        if any(w in lower for w in ["hello", "hi", "hey", "greetings", "good morning", "good evening"]):
            return (
                "👋 **Hello and welcome to SkillSphere!**\n\n"
                "I am your platform assistant. I can help you with:\n"
                "- 📋 **20-Question Technical Assessments** (rules, time limits, scoring)\n"
                "- 🛡️ **AI Camera Proctoring & Three-Strike Rules**\n"
                "- 📷 **Camera Setup & Troubleshooting**\n"
                "- 📄 **Resume OCR & Job Matching**\n"
                "- 💼 **Recruiter Tools & Assessment Management**\n\n"
                "What would you like to know?"
            )

        # Default helpful assistant response
        return (
            "I'm here to help you navigate **SkillSphere**!\n\n"
            "You can ask me about:\n"
            "- **Technical Assessments:** How the 20-question timed tests work and passing criteria (60%).\n"
            "- **Camera Proctoring:** How MediaPipe face tracking and the **Three-Strike Warning System** operate.\n"
            "- **Troubleshooting:** Camera permissions, tab focus, or technical setup.\n"
            "- **Resume Matching:** How our AI OCR engine calculates job fit scores.\n\n"
            "Feel free to ask a specific question!"
        )
