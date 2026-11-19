import re
import json
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.core.config import settings

# =============================================================================
# GEMINI AI SYSTEM PROMPT: PROJECT-AWARE CAREER INTELLIGENCE + CHATGPT-LIKE CONVERSATION
# =============================================================================
BASE_SYSTEM_INSTRUCTION = """You are the intelligent, empathetic, and highly capable AI Assistant integrated within SkillSphere – a modern career, job intelligence, and recruitment platform.

CORE TWO-TIER INTELLIGENCE (PRIORITIZE SKILLSPHERE ASSISTANCE):

1. SKILLSPHERE PLATFORM & CAREER INTELLIGENCE (HIGHEST PRIORITY):
   - When a user asks about jobs, internships, application status, assessments, proctoring, resume matching, or their current stage, ALWAYS provide precise, helpful, and platform-specific guidance.
   - Reference their verified real-time database record provided below for profile completeness, resume status, active applications, and assessment scores.
   - NEVER invent or hallucinate user progress, application stages, test scores, or interview dates.
   - Explain portal processes clearly:
     * Jobs & Internships: Explain how to browse the Jobs section, review the explainable 0-100% AI skill match score, view prerequisites & stipend, and click Apply Now (1-click apply).
     * Technical Assessments: Explain the 20-question MCQ format, 25-minute live timer, 60% passing mark (12/20 correct), single sitting, and automatic promotion to the ATS Interview round upon passing.
     * AI Camera Proctoring: Explain the 3-strike policy (Strike 1 Yellow warning, Strike 2 Orange final warning, Strike 3 Red auto-submission) and camera permission setup.
     * Career & Learning: For Python, DSA, interview preparation, and coding roadmaps, give structured, beginner-friendly paths and tie them directly to technical assessment and interview readiness.

2. NATURAL CONVERSATIONAL AI (ChatGPT Mode):
   - Respond naturally, warmly, and playfully to casual greetings, humor, jokes, and everyday chats ("Hi", "Hello", "Ki haal aa veere?", "How are you?", "Suggest thriller movies", "Tell me a joke").
   - Do NOT force every casual conversation into portal functionality or repeat a robotic introduction.
   - Show genuine human empathy when someone expresses stress or frustration ("aj mood off hai", "samajh nahi aa raha").

3. MULTILINGUAL & CASUAL TEXTING MASTERY:
   - Flawlessly understand and mirror whatever language or dialect the user uses:
     * English / Broken English / Typos -> Clear, friendly, encouraging English.
     * Hindi (Devanagari or Romanized/Hinglish like "kya scene hai", "kaunsi stage", "mera status") -> Conversational Hinglish or Hindi.
     * Punjabi (Gurmukhi or Romanized Punjabi like "ki haal aa veere", "mainu samajh ni aa reha", "hun ki hovega") -> Warm, friendly Punjabi or Punjabi-English mix ("Veere", "Paji", "Chardi kala").
   - Never criticize grammar, spelling errors, or abbreviations.

4. CONVERSATIONAL CONTINUITY:
   - Preserve conversational context across multi-turn exchanges ("uske baad?", "and then?", "why?", "kaise?", "what about that?", "haan bata").
"""


class ChatbotService:
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect whether the user is typing in Punjabi, Hindi/Hinglish, or English.
        """
        lower = text.lower()

        # Check Punjabi Gurmukhi script
        if any('\u0A00' <= char <= '\u0A7F' for char in text):
            return "punjabi"

        # Check Hindi Devanagari script
        if any('\u0900' <= char <= '\u097F' for char in text):
            return "hindi"

        # Instant Punjabi triggers
        punjabi_triggers = [
            "ki haal", "haal aa", "veere", "kitti c", "ki hovega", "daso ki", "mainu samajh",
            "ki banya", "mainu help", "help chahidi", "sat sri akal", "sasrikal", "chardi kala",
            "kida veere", "kive ho", "kivein ho", "othe", "ithe", "sohna", "changa", "haanji",
            "kithe", "dass", "dasso", "kariye", "kitta", "hove", "hovega"
        ]
        if any(pt in lower for pt in punjabi_triggers):
            return "punjabi"

        # Check Punjabi Romanized keywords
        punjabi_keywords = [
            "kitti", "kitta", "hovega", "hovegi", "hove", "daso", "dasso",
            "kida", "kidan", "kive", "kivein", "tussi", "mainu", "mera", "meri",
            "ki", "hun", "karda", "kardi", "paji", "paaji", "veere", "bai",
            "gal", "das", "kariye", "dass", "karange", "chahidi", "chahida", "reha"
        ]
        punjabi_matches = sum(1 for kw in punjabi_keywords if re.search(r'\b' + kw + r'\b', lower))
        if punjabi_matches >= 2:
            return "punjabi"

        # Comprehensive Hindi / Hinglish keywords (including casual texting, progress, & questions)
        hindi_keywords = [
            "kya", "kab", "kaise", "kahan", "kyun", "kis", "mera", "meri", "mere",
            "mujhe", "mujhko", "yaar", "bhai", "hai", "hain", "tha", "thi",
            "raha", "rahi", "hoga", "hogi", "batao", "bataiye", "bata", "btao", "karna", "karo",
            "uske", "baad", "ab", "kuch", "nahi", "nhi", "ho", "gaya", "gya", "chahiye",
            "samajh", "aaya", "theek", "shukriya", "dhanyawad", "kripya", "haan", "ha",
            "bolo", "bata do", "kaise kare", "lagta hai", "bataye", "kr rha",
            "seekhni", "seekhna", "seekhe", "seekhu", "dimag", "kharab", "scene", "pareshan", "suno",
            "karein", "karenge", "shuru", "main", "kaunsi", "konsi", "stage", "par", "hoon", "hu",
            "maine", "kitne", "kitna", "kiye", "kiya", "karun", "agla", "aage", "step", "taiyari",
            "pehle", "aata", "aate", "aati", "padhna", "naukri"
        ]
        hindi_matches = sum(1 for kw in hindi_keywords if re.search(r'\b' + kw + r'\b', lower))
        if hindi_matches >= 1:
            return "hinglish"

        return "english"

    @staticmethod
    def get_response(
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None,
        user_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate contextual AI response using Gemini if key is configured,
        or fall back seamlessly to our intelligent native knowledge engine.
        """
        clean_msg = message.strip()
        if not clean_msg:
            return {
                "reply": "Hey! 👋 I am your SkillSphere AI Career Assistant. How can I help you today with your applications, assessments, interview preparation, or account progress?",
                "provider": "skillsphere_assistant",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        api_key = (settings.GEMINI_API_KEY or "").strip()

        # Try Google Gemini API if configured
        if api_key:
            try:
                reply = ChatbotService._call_gemini_api(api_key, clean_msg, history, user_data)
                if reply:
                    return {
                        "reply": reply,
                        "provider": "gemini",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
            except Exception as e:
                print(f"[SkillSphere Chatbot] Gemini call exception: {e}. Running native engine.")

        # Native Intelligent Project-Aware Engine
        reply = ChatbotService._generate_native_response(clean_msg, history, context, user_data)
        return {
            "reply": reply,
            "provider": "skillsphere_assistant",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # =========================================================================
    # GEMINI API MULTITURN INTEGRATION
    # =========================================================================
    @staticmethod
    def _call_gemini_api(
        api_key: str,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        model = settings.GEMINI_MODEL or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        # Inject verified real-time database record if authenticated
        system_content = BASE_SYSTEM_INSTRUCTION
        if user_data and user_data.get("authenticated"):
            candidate_info = user_data.get("candidate", {})
            system_content += f"""\n
VERIFIED REAL-TIME CANDIDATE RECORD FOR THIS USER:
- Name: {user_data.get('name')}
- Email: {user_data.get('email')}
- Role: {user_data.get('role')}
- Profile Completeness: {candidate_info.get('profile_percentage', 0)}%
- Resume Uploaded: {candidate_info.get('resume_uploaded', False)} (Total Resumes: {candidate_info.get('resumes_count', 0)})
- Missing Profile Details: {', '.join(candidate_info.get('missing_fields', [])) or 'None (Profile 100% Complete)'}
- Extracted Skills: {', '.join(candidate_info.get('skills', [])) or 'No skills recorded'}
- Active Applications ({candidate_info.get('applications_count', 0)}): {json.dumps(candidate_info.get('applications', []), indent=2)}
- Assessments ({candidate_info.get('completed_assessments_count', 0)} Completed, {candidate_info.get('pending_assessments_count', 0)} Pending): {json.dumps(candidate_info.get('assessments', []), indent=2)}

STRICT RULE: Reference this verified record whenever the user asks about their stage, application status, assessments, or next steps. Quote exact numbers and never invent or assume data.
"""

        # Build clean alternating history for Gemini multiturn
        contents = []
        if history:
            last_role = None
            for turn in history[-10:]:
                raw_role = turn.get("role", "")
                role = "user" if raw_role in ["user", "candidate"] else "model"
                text = str(turn.get("content", "")).strip()
                if not text:
                    continue
                if role == "user" and text == message.strip():
                    continue
                if role == last_role and contents:
                    contents[-1]["parts"][0]["text"] += f"\n{text}"
                else:
                    contents.append({
                        "role": role,
                        "parts": [{"text": text[:2000]}]
                    })
                    last_role = role

        if contents and contents[-1]["role"] == "user":
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. Please continue!"}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": message[:2500]}]
        })

        payload = {
            "systemInstruction": {
                "parts": [{"text": system_content}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1200,
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
                print(f"[SkillSphere Chatbot] Gemini HTTP {resp.status_code}: {resp.text[:200]}")
                return None

        return None

    # =========================================================================
    # NATIVE INTELLIGENT PROJECT-AWARE CONVERSATIONAL ENGINE
    # =========================================================================
    @staticmethod
    def _generate_native_response(
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None,
        user_data: Optional[Dict[str, Any]] = None
    ) -> str:
        lang = ChatbotService.detect_language(message)
        lower = message.lower().strip()

        # ---------------------------------------------------------------------
        # 1. CONVERSATION CONTEXT & MULTI-TURN FOLLOW-UPS
        # ---------------------------------------------------------------------
        is_follow_up = any(re.search(r'\b' + phrase + r'\b', lower) for phrase in [
            "uske baad", "iske baad", "then what", "ab kya", "aur fir", "aur aage",
            "what next", "next step", "after that", "after this", "fir kya", "hun ki",
            "usde baad", "kya hoga", "kya karna hai", "agla step", "then?", "continue",
            "haan bata", "aur bata", "aage", "aur?", "why?", "kaise?", "what about that"
        ])

        if history and len(history) > 0:
            history_text = " ".join([turn.get("content", "").lower() for turn in history[-8:]])
            last_bot_msg = ""
            for turn in reversed(history):
                if turn.get("role") in ["model", "assistant"]:
                    last_bot_msg = turn.get("content", "").lower()
                    break

            # Follow-up in Interview Prep / Python Discussion
            if "interview" in history_text or "python developer" in history_text:
                if any(w in lower for w in ["python developer", "python dev", "backend", "developer", "data science"]):
                    if lang in ["hindi", "hinglish"]:
                        return (
                            "Nice! Python Developer role ke liye typically 3 core areas check hote hain: "
                            "Python Fundamentals, OOP & Data Structures, aur Web Frameworks (FastAPI/Django).\n\n"
                            "Aap Python basics mein comfortable hain, ya hum core fundamentals se shuru karein? 🐍"
                        )
                    else:
                        return (
                            "Great! For a Python Developer role, interviews typically focus on core fundamentals, "
                            "OOP & data structures, and backend frameworks (FastAPI/Django).\n\n"
                            "Are you comfortable with Python basics, or should we start with the fundamentals?"
                        )
                elif any(w in lower for w in ["basics aate", "know basics", "aate hain", "comfortable", "fundamentals done", "basics theek"]):
                    if lang in ["hindi", "hinglish"]:
                        return (
                            "Perfect! Phir seedha intermediate topics cover karte hain:\n\n"
                            "- **OOP Concepts:** Inheritance, Polymorphism, Encapsulation\n"
                            "- **Python Specials:** Decorators, Generators, Context Managers (`with`)\n"
                            "- **Data Structures & Time Complexity:** Lists vs Dicts vs Sets, Big-O\n\n"
                            "Chalo ek quick question try karein? Batao, Python mein `is` aur `==` ke beech kya farak hota hai? 🎯"
                        )
                    else:
                        return (
                            "Perfect! Then let's focus on intermediate OOP, DSA patterns, and core interview concepts:\n\n"
                            "- **OOP:** Classes, Inheritance, Polymorphism\n"
                            "- **Python Deep Dive:** Decorators, Generators, Context Managers\n"
                            "- **Complexity:** Lists vs Dicts hash lookups, Big-O\n\n"
                            "Ready for a quick question? What is the difference between `is` and `==` in Python? 🎯"
                        )
                elif any(w in lower for w in ["haan bata", "sure", "continue", "pucho", "batao", "yes", "go ahead", "aur bata", "aage", "next"]):
                    if lang in ["hindi", "hinglish"]:
                        return (
                            "Bilkul! `==` value check karta hai (jaise `[1, 2] == [1, 2]` -> True), jabki `is` memory reference / identity check karta hai (`id(a) == id(b)`).\n\n"
                            "Chalo next question: Python mein mutable default arguments (jaise `def add(item, lst=[]):`) kyu dangerous hote hain aur inhe fix kaise karte hain? Batao! 🐍"
                        )
                    else:
                        return (
                            "Spot on! `==` checks equality of values, while `is` verifies object identity (memory address in RAM).\n\n"
                            "Next question: Why is using a mutable default argument like `def add_item(val, bag=[]):` problematic in Python, and how do you properly fix it? 🐍"
                        )

            # Follow-up on Job / Internship Application
            if is_follow_up and ("job" in last_bot_msg or "apply" in last_bot_msg or "internship" in last_bot_msg):
                if lang == "punjabi":
                    return (
                        "Job apply karan to baad tuhada resume recruiter kol review layi jaavega. "
                        "Je tuhade skills job naal match hunde ne, taan tuhade dashboard te **20-Question Technical Assessment** da invite aavega! "
                        "Test clear karan (60%+) to baad agla step **Interview** da hunda hai."
                    )
                elif lang in ["hindi", "hinglish"]:
                    return (
                        "Job/Internship apply karne ke baad recruiter aapka profile aur match score review karta hai. "
                        "Shortlist hone par aapko **20-Question Technical Assessment** ka invite dashboard aur email par milta hai. "
                        "Test clear (60%+) karne ke baad aapka application sidha **Interview round** ke liye advance ho jata hai!"
                    )
                else:
                    return (
                        "After applying, the hiring recruiter evaluates your profile and explainable match score. "
                        "If shortlisted, you receive an invitation to take a **20-Question Technical Assessment**. "
                        "Scoring 60% or higher automatically advances your application to the **Interview stage**!"
                    )

            # Follow-up on Assessment / Test
            if is_follow_up and ("assessment" in last_bot_msg or "test" in last_bot_msg or "exam" in last_bot_msg):
                if lang == "punjabi":
                    return (
                        "Assessment submit karan to baad tuhada score turant calculate ho janda hai. "
                        "Je tussi 60% (12/20) ya us to vadh score karde ho, taan tuhada application sidha **Interview priority** vich chala janda hai!"
                    )
                elif lang in ["hindi", "hinglish"]:
                    return (
                        "Assessment complete hone ke baad system turant score calculate karta hai. "
                        "Agar aap 60% (12/20) ya usse zyada score karte hain, toh aap qualify ho jate hain aur recruiter team aapse **Interview** ke liye coordinate karegi!"
                    )
                else:
                    return (
                        "Once submitted, your assessment is graded instantly. "
                        "If you score 60% or above (12/20 correct), your profile is automatically elevated to **Interview Priority**!"
                    )

        # ---------------------------------------------------------------------
        # 2. INTENT: USER PROGRESS & STAGE INQUIRIES (PRIORITY 1)
        # ---------------------------------------------------------------------
        # Triggers covering "Main kaunsi stage par hoon?", "Meri application ka status", "Next step", "Kitne assessments"
        is_stage_query = any(w in lower for w in [
            "kaunsi stage", "konsi stage", "kidi stage", "what stage", "current stage", "my stage",
            "kis stage", "kahan tak pahucha", "stage par hoon", "stage pe hu", "kedi stage"
        ])
        is_application_query = any(w in lower for w in [
            "meri application", "application ka kya status", "application status", "meriyaan application",
            "my application", "applied jobs", "application ka status", "kya status hai", "status kya hai"
        ])
        is_assessment_count_query = any(w in lower for w in [
            "kitne assessment", "kitne test", "assessments complete", "completed assessment",
            "completed assessments", "test result", "mera score", "kitne test diye", "kitne assessment diye"
        ])
        is_next_step_query = any(w in lower for w in [
            "mera next step", "mera agla step", "what is my next step", "what should i do next",
            "ab aage kya", "agla step kya", "next step kya", "where do i stand", "ab kya karun"
        ])
        is_general_status = any(w in lower for w in [
            "mera status", "my status", "meri progress", "profile complete", "profile completion",
            "resume status", "hun ki hovega", "ki hoya"
        ])

        if is_stage_query or is_application_query or is_assessment_count_query or is_next_step_query or is_general_status:
            return ChatbotService._handle_user_progress_and_stage(
                lower=lower,
                lang=lang,
                user_data=user_data,
                is_stage_query=is_stage_query,
                is_application_query=is_application_query,
                is_assessment_count_query=is_assessment_count_query,
                is_next_step_query=is_next_step_query
            )

        # ---------------------------------------------------------------------
        # 3. INTENT: INTERNSHIP & JOB GUIDANCE (PRIORITY 2)
        # ---------------------------------------------------------------------
        is_job_query = any(w in lower for w in [
            "internship", "internships", "internship ke liye", "internship apply",
            "apply for job", "job apply", "how to apply", "apply kaise", "apply karun",
            "apply kive", "job kaise milegi", "naukri", "job openings", "browse jobs",
            "eligibility check", "apply karne ka", "apply kaise kare"
        ])

        if is_job_query:
            return ChatbotService._handle_job_and_internship_guidance(lang)

        # ---------------------------------------------------------------------
        # 4. INTENT: ASSESSMENT & PROCTORING GUIDANCE (PRIORITY 3)
        # ---------------------------------------------------------------------
        is_assessment_query = any(w in lower for w in [
            "assessment pending", "test pending", "pending hai", "assessment format", "test format",
            "passing score", "passing mark", "pass marks", "passing criteria", "passing percentage",
            "technical assessment", "technical assessments", "20 question", "20 questions",
            "how do assessments work", "how do the 20-question", "assessment details", "test details",
            "proctor", "proctoring", "strike", "3 strike", "three strike", "violation", "camera",
            "webcam", "video feed", "black screen", "face not detected"
        ])

        if is_assessment_query:
            return ChatbotService._handle_assessment_guidance(lower, lang, user_data)

        # ---------------------------------------------------------------------
        # 4B. INTENT: CONFUSION & TROUBLESHOOTING / FRUSTRATION
        # ---------------------------------------------------------------------
        is_frustration_query = any(w in lower for w in [
            "nahi ho raha", "nahi ho rha", "complete nahi ho rha", "complete nahi ho raha",
            "shuru nahi ho raha", "start nahi ho raha", "problem aa rahi", "mushkil aa rahi"
        ])
        is_confusion_query = any(w in lower for w in [
            "mainu samajh ni", "samajh ni aa reha", "samajh nahi aa raha", "kuch samajh nhi",
            "samajh nahi aara", "help chahidi", "confused hu"
        ])

        if is_frustration_query or is_confusion_query:
            return ChatbotService._handle_frustration_and_confusion(lower, lang)

        # ---------------------------------------------------------------------
        # 5. INTENT: CAREER & LEARNING ASSISTANCE (PRIORITY 4)
        # ---------------------------------------------------------------------
        is_career_query = any(w in lower for w in [
            "python seekhni", "learn python", "python sikhna", "python kaise", "python roadmap",
            "python developer", "dsa", "data structures", "algorithms", "coding seekhni",
            "programming seekhni", "interview preparation", "interview ki taiyari",
            "interview prepare", "preparing for an interview", "kal mera interview"
        ])

        if is_career_query:
            return ChatbotService._handle_career_and_learning(lower, lang)

        # ---------------------------------------------------------------------
        # 6. INTENT: CASUAL GREETINGS & DAILY LIFE CHAT
        # ---------------------------------------------------------------------
        is_greeting = any(re.search(r'\b' + w + r'\b', lower) for w in [
            "hello", "hi", "hey", "heyy", "heyyy", "kida", "kidan", "kive", "kive ho",
            "ki haal", "haal aa", "veere", "kya scene", "kya chal raha", "whats up",
            "what's up", "how are you", "how r u", "kaise ho", "kaisa hai", "sat sri akal",
            "sasrikal", "namaste", "pranam"
        ])
        is_casual_chitchat = any(w in lower for w in [
            "what u doing", "what are you doing", "bro kya kr rha", "kya kar rahe ho",
            "kuch khaas nahi", "same old", "bore ho raha", "boring lag raha"
        ])

        if is_greeting or is_casual_chitchat:
            return ChatbotService._handle_greetings_and_casual(lower, lang)

        # ---------------------------------------------------------------------
        # 7. INTENT: ENTERTAINMENT, HUMOR & GENERAL CONCEPTS
        # ---------------------------------------------------------------------
        is_movie_query = any(w in lower for w in [
            "thriller movie", "thriller movies", "suggest movies", "movie suggest",
            "recommend movies", "best movies", "kuch movie"
        ])
        is_joke_query = any(w in lower for w in [
            "tell me a joke", "koi joke", "joke sunao", "joke batao", "funny joke"
        ])
        is_humor_praise = any(w in lower for w in [
            "funny bro", "you're funny", "you are funny", "has mat", "mast tha", "hasi aa gayi"
        ]) or lower.startswith("haha") or lower.startswith("lol") or lower.startswith("lmao")
        is_mood_query = any(w in lower for w in [
            "mood off", "dimag kharab", "dimagh kharab", "sad hu", "feeling sad",
            "feeling down", "tension ho rahi", "pareshan hu", "gussa aa raha"
        ])
        is_ai_concept = any(w in lower for w in [
            "artificial intelligence", "what is ai", "explain ai", "machine learning", "what is ml"
        ])
        is_capabilities_query = any(w in lower for w in [
            "what can you do", "kya kar sakte ho", "who are you", "who made you", "capabilities", "tum kya ho"
        ])

        if is_movie_query or is_joke_query or is_humor_praise or is_mood_query or is_ai_concept or is_capabilities_query:
            return ChatbotService._handle_entertainment_and_humor(lower, lang)

        # ---------------------------------------------------------------------
        # 8. DEFAULT BALANCED PROJECT-AWARE FALLBACK
        # ---------------------------------------------------------------------
        return ChatbotService._format_project_aware_fallback(lang)

    # =========================================================================
    # DEDICATED INTENT HANDLERS
    # =========================================================================

    @staticmethod
    def _handle_user_progress_and_stage(
        lower: str,
        lang: str,
        user_data: Optional[Dict[str, Any]],
        is_stage_query: bool,
        is_application_query: bool,
        is_assessment_count_query: bool,
        is_next_step_query: bool
    ) -> str:
        """
        Produce verified user stage, application status, assessment count, and next steps strictly from DB.
        """
        # Case A: Guest / Unauthenticated
        if not user_data or not user_data.get("authenticated"):
            if is_application_query:
                if lang == "punjabi":
                    return (
                        "🔒 **Tussi haley login nahi kita hoya.**\n\n"
                        "Apniyan job ya internship applications da live status vekhan layi kripya pehla **Sign In** karo!"
                    )
                elif lang in ["hindi", "hinglish"]:
                    return (
                        "🔒 **Aap abhi logged in nahi hain.**\n\n"
                        "Apni submitted job ya internship applications ka live status dekhne ke liye kripya pehle **Sign In / Log In** karein. "
                        "Login karne ke baad main aapke real records turant display kar dunga!"
                    )
                else:
                    return (
                        "🔒 **You are currently browsing as a guest.**\n\n"
                        "Please **Sign In** to view the live status of your submitted job and internship applications."
                    )

            if is_assessment_count_query:
                if lang in ["hindi", "hinglish"]:
                    return (
                        "🔒 **Aap abhi logged in nahi hain.**\n\n"
                        "Apne completed assessments aur test scores dekhne ke liye kripya pehle **Sign In** karein."
                    )
                else:
                    return (
                        "🔒 **You are currently browsing as a guest.**\n\n"
                        "Please **Sign In** to view your completed technical assessments, scores, and pending test invitations."
                    )

            # Stage / General Progress for Guest
            if lang in ["hindi", "hinglish"]:
                return (
                    "🔒 **Aap abhi logged in nahi hain.** (Browsing as Guest)\n\n"
                    "Apna real-time profile, job application status aur stage track karne ke liye pehle **Sign In** karein.\n\n"
                    "**SkillSphere par Candidate Journey 4 Stages mein hoti hai:**\n"
                    "1. **Stage 1 (Profile & Resume):** Resume upload karke AI se skills aur details auto-populate karein.\n"
                    "2. **Stage 2 (Job & Internship Discovery):** AI Match Scores (0-100%) ke sath open positions par 1-click apply karein.\n"
                    "3. **Stage 3 (20-Question Technical Assessment):** 25-minute online test complete karein (60% passing criteria).\n"
                    "4. **Stage 4 (Interview & Selection):** Recruiter ke sath direct interview coordinate karein.\n\n"
                    "Login karne ke baad main aapke actual database record se aapki exact stage aur next steps turant bata dunga!"
                )
            elif lang == "punjabi":
                return (
                    "🔒 **Tussi haley login nahi kita hoya.** (Guest Mode)\n\n"
                    "Apna personal stage, application status, te pending tests dekhn layi pehla **Sign In** karo!\n\n"
                    "SkillSphere te 4 stages hundiyan ne: Profile Setup ➔ Job Apply ➔ 20-Question Assessment ➔ Interview Priority."
                )
            else:
                return (
                    "🔒 **You are currently browsing as a guest.**\n\n"
                    "Please **Sign In** to view your verified platform progress, completed assessments, and next steps.\n\n"
                    "**SkillSphere Candidate Journey Overview:**\n"
                    "1. **Stage 1 (Profile & Resume):** Upload your resume to extract skills.\n"
                    "2. **Stage 2 (Applications):** Apply with 1 click based on AI match scores.\n"
                    "3. **Stage 3 (Assessments):** Complete timed 20-question technical tests (60% pass threshold).\n"
                    "4. **Stage 4 (Interview):** Advance automatically to interview shortlisting upon passing."
                )

        # Case B: Authenticated Candidate / Student
        cand = user_data.get("candidate", {})
        name = user_data.get("name", "Student")
        profile_pct = cand.get("profile_percentage", 0)
        missing_fields = cand.get("missing_fields", [])
        resumes_count = cand.get("resumes_count", 0)
        apps = cand.get("applications", [])
        tests = cand.get("assessments", [])

        completed_tests = [t for t in tests if t.get("status") == "completed" or t.get("score") is not None]
        pending_tests = [t for t in tests if t.get("status") in ["pending", "assigned", "in_progress"] and not t.get("passed")]
        passed_tests = [t for t in tests if t.get("passed")]

        # Determine true current stage from verified DB evidence
        if resumes_count == 0 or profile_pct < 50:
            stage_num = 1
            stage_name = "Stage 1: Profile & Resume Setup 📄"
            rec_next_step = "Pehle apna Resume (PDF/Image) upload karein taaki AI aapke skills extract kare aur profile completion 100% ho sake."
            rec_next_step_en = "Upload your resume (PDF/Image) to populate your skills and reach 100% profile completeness."
        elif len(apps) == 0:
            stage_num = 2
            stage_name = "Stage 2: Job & Internship Applications 💼"
            rec_next_step = "Aapka profile ready hai! Ab Jobs tab mein jakar high match score wali roles par Apply Now button par click karein."
            rec_next_step_en = "Your profile is ready! Visit the Jobs tab to explore matching roles and click Apply Now."
        elif len(pending_tests) > 0:
            stage_num = 3
            stage_name = "Stage 3: Technical Assessment Stage 📝"
            pending_title = pending_tests[0].get("title", "Technical Assessment")
            rec_next_step = f"Aapka '{pending_title}' assessment pending hai! Ise 25-minute timer mein complete karein aur 60%+ score karke Interview unlock karein."
            rec_next_step_en = f"You have a pending assessment ('{pending_title}'). Complete it within the 25-minute window with 60%+ to unlock Interview Priority."
        elif len(passed_tests) > 0 or any(a.get("status") == "interview" for a in apps):
            stage_num = 4
            stage_name = "Stage 4: Interview & Priority Hiring 🎉"
            rec_next_step = "Badhai ho! Aap assessment qualify kar chuke hain aur Interview Priority mein hain. Recruiter team contact karegi, tab tak core frameworks revise karein."
            rec_next_step_en = "Congratulations! You have qualified your assessment and reached Interview Priority. The hiring team will coordinate interview scheduling."
        else:
            stage_num = 2
            stage_name = "Stage 2: Application Review in Progress ⏳"
            rec_next_step = "Aapki submitted applications recruiter review mein hain. Shortlist hone par dashboard par 20-question assessment invite aayega."
            rec_next_step_en = "Your applications are under recruiter review. Shortlisted candidates receive an automated 20-question test invitation."

        # Sub-Case 1: Specific Assessment Count Inquiry
        if is_assessment_count_query:
            if lang in ["hindi", "hinglish"]:
                lines = [
                    f"👋 **{name}, aapke technical assessments ka verified database record:**\n",
                    f"- **Total Completed Assessments:** **{len(completed_tests)}**",
                    f"- **Total Pending Assessments:** **{len(pending_tests)}**\n"
                ]
                if completed_tests:
                    lines.append("📝 **Completed Assessment Results:**")
                    for t in completed_tests[:5]:
                        score_str = f"{t.get('score')}/20 ({t.get('percentage')}%)" if t.get('score') is not None else "Graded"
                        outcome = "✅ Passed (Interview Qualified)" if t.get("passed") else "⚠️ Completed (Score below 60%)"
                        lines.append(f"- **{t.get('title')}** | Score: `{score_str}` | Result: **{outcome}**")
                else:
                    lines.append("- Abhi aapke account par **0 completed assessments** hain.")

                if pending_tests:
                    lines.append("\n⏳ **Pending Assessment Action:**")
                    for t in pending_tests[:3]:
                        lines.append(f"- **{t.get('title')}** (Time limit: {t.get('time_limit', 25)} mins, 20 MCQs)")
                    lines.append("👉 *Next Step:* Dashboard ya Assessments page se **Start Assessment** par click karein!")
                return "\n".join(lines)
            else:
                lines = [
                    f"👋 **{name}, here is your verified technical assessment breakdown:**\n",
                    f"- **Completed Assessments:** **{len(completed_tests)}**",
                    f"- **Pending Assessments:** **{len(pending_tests)}**\n"
                ]
                if completed_tests:
                    lines.append("📝 **Completed Assessment Details:**")
                    for t in completed_tests[:5]:
                        score_str = f"{t.get('score')}/20 ({t.get('percentage')}%)" if t.get('score') is not None else "Graded"
                        outcome = "✅ Passed (Interview Priority)" if t.get("passed") else "⚠️ Completed (Below 60%)"
                        lines.append(f"- **{t.get('title')}** | Score: `{score_str}` | Outcome: **{outcome}**")
                else:
                    lines.append("- You currently have **0 completed assessments** registered.")

                if pending_tests:
                    lines.append("\n⏳ **Pending Tests:**")
                    for t in pending_tests[:3]:
                        lines.append(f"- **{t.get('title')}** ({t.get('time_limit', 25)} mins, 20 MCQs)")
                    lines.append("👉 *Next Step:* Click **Start Assessment** from your Dashboard.")
                return "\n".join(lines)

        # Sub-Case 2: Specific Applications Status Inquiry
        if is_application_query:
            if lang in ["hindi", "hinglish"]:
                lines = [
                    f"📁 **{name}, aapki active job & internship applications ka live status:**\n",
                    f"- **Total Applications Submitted:** **{len(apps)}**\n"
                ]
                if apps:
                    for a in apps[:6]:
                        stage_label = a.get("status", "Applied")
                        lines.append(f"- **{a.get('job_title')}** at **{a.get('company')}**")
                        lines.append(f"  Current Status: `{stage_label}` | Applied On: {a.get('date', 'Recent')}")
                    lines.append(f"\n👉 *Next Step:* {rec_next_step}")
                else:
                    lines.append("- Aapne abhi tak kisi job ya internship ke liye apply nahi kiya hai.")
                    lines.append("👉 *Next Step:* **Jobs** tab par jakar matching roles explore karein aur **Apply Now** karein!")
                return "\n".join(lines)
            else:
                lines = [
                    f"📁 **{name}, here is the live status of your applications:**\n",
                    f"- **Total Applications:** **{len(apps)}**\n"
                ]
                if apps:
                    for a in apps[:6]:
                        lines.append(f"- **{a.get('job_title')}** at **{a.get('company')}**")
                        lines.append(f"  Pipeline Status: `{a.get('status', 'Applied')}` | Submitted: {a.get('date', 'Recent')}")
                    lines.append(f"\n👉 *Recommended Action:* {rec_next_step_en}")
                else:
                    lines.append("- You have not submitted any job or internship applications yet.")
                    lines.append("👉 *Next Action:* Visit the **Jobs** tab to explore positions aligned with your skills.")
                return "\n".join(lines)

        # Sub-Case 3: Current Stage Inquiry ("Main kaunsi stage par hoon?")
        if is_stage_query:
            if lang in ["hindi", "hinglish"]:
                return (
                    f"🎯 **{name}, aap abhi {stage_name} par hain!**\n\n"
                    f"📊 **Aapka Verified Journey Breakdown:**\n"
                    f"- **Profile Completion:** `{profile_pct}%` ({resumes_count} resume uploaded)\n"
                    f"- **Missing Details:** {', '.join(missing_fields) if missing_fields else 'None (100% Complete)'}\n"
                    f"- **Job/Internship Applications:** `{len(apps)}` active\n"
                    f"- **Assessments:** `{len(completed_tests)}` Completed, `{len(pending_tests)}` Pending\n\n"
                    f"👉 **Aapke Liye Recommended Next Step:**\n{rec_next_step}"
                )
            elif lang == "punjabi":
                return (
                    f"🎯 **{name}, tussi haley {stage_name} te ho!**\n\n"
                    f"📊 **Tuhada Live Record:**\n"
                    f"- **Profile:** `{profile_pct}%` complete\n"
                    f"- **Applications:** `{len(apps)}` job apply kitian ne\n"
                    f"- **Assessments:** `{len(completed_tests)}` complete, `{len(pending_tests)}` pending\n\n"
                    f"👉 **Agla Step:** {rec_next_step}"
                )
            else:
                return (
                    f"🎯 **{name}, you are currently at {stage_name}!**\n\n"
                    f"📊 **Verified Platform Evidence:**\n"
                    f"- **Profile Completion:** `{profile_pct}%` ({resumes_count} resume on file)\n"
                    f"- **Missing Fields:** {', '.join(missing_fields) if missing_fields else 'None'}\n"
                    f"- **Applications:** `{len(apps)}` submitted\n"
                    f"- **Assessments:** `{len(completed_tests)}` Completed, `{len(pending_tests)}` Pending\n\n"
                    f"👉 **Recommended Next Action:**\n{rec_next_step_en}"
                )

        # Sub-Case 4: Next Step Inquiry ("Mera next step kya hai?")
        if is_next_step_query:
            if lang in ["hindi", "hinglish"]:
                return (
                    f"🎯 **{name}, aapke liye current recommended next step ye hai:**\n\n"
                    f"👉 **{rec_next_step}**\n\n"
                    f"📌 *Context:* Aap abhi **{stage_name}** par hain (Profile: {profile_pct}%, Applications: {len(apps)}, Assessments: {len(completed_tests)} completed, {len(pending_tests)} pending)."
                )
            else:
                return (
                    f"🎯 **{name}, your prioritized next step is:**\n\n"
                    f"👉 **{rec_next_step_en}**\n\n"
                    f"📌 *Current Status:* You are in **{stage_name}** (Profile: {profile_pct}%, Applications: {len(apps)}, Assessments: {len(completed_tests)} completed, {len(pending_tests)} pending)."
                )

        # General status overview fallback
        return ChatbotService._format_user_journey_response(lang, user_data)

    @staticmethod
    def _handle_job_and_internship_guidance(lang: str) -> str:
        """
        Explain how to browse jobs/internships, inspect AI match scores, and apply.
        """
        if lang in ["hindi", "hinglish"]:
            return (
                "💼 **SkillSphere par Jobs & Internships ke liye Apply karne ka asaan tareeka:**\n\n"
                "1. **Jobs Section Explore Karein:** Top navigation bar mein **Jobs** tab par click karein. Wahan full-time jobs aur internships listed hain.\n"
                "2. **AI Skill Match Score (0-100%):** Har job card par aapka real-time Match Score display hota hai. Ye batata hai ki aapke skills job description se kitne match karte hain (matched skills vs missing skills).\n"
                "3. **Role & Eligibility Review:** Job card par click karke stipend/salary, job location, required tech stack aur responsibilities check karein.\n"
                "4. **1-Click Apply Now:** **Apply Now** button par click karein. Aapka verified resume turant hiring recruiter ke portal par review ke liye submit ho jata hai.\n"
                "5. **Agla Step (Assessment Invite):** Recruiter review ke baad qualified candidates ko **20-Question Technical Assessment** ka invite dashboard aur email par milta hai!\n\n"
                "Aap kis role (e.g. Python Developer, React Frontend, Data Science) ki internship dhoondh rahe hain? Main aur specific help kar sakta hoon!"
            )
        elif lang == "punjabi":
            return (
                "💼 **SkillSphere te Jobs & Internships Apply karan da tareeka:**\n\n"
                "1. Navigation bar vich **Jobs** tab te jaao.\n"
                "2. Othe saari open tech positions te internships nazar aavangiyan, naal hi tuhada **AI Match Score (0-100%)** dikhega.\n"
                "3. Job card te click karke required skills, role details te stipend review karo.\n"
                "4. **Apply Now** button te click karo — tuhada resume recruiter kol review layi chala javega.\n"
                "5. Review karan to baad dashboard te **20-Question Technical Assessment** da link aavega!"
            )
        else:
            return (
                "💼 **How to Find and Apply for Jobs & Internships on SkillSphere:**\n\n"
                "1. **Navigate to Jobs:** Click on the **Jobs** tab in the top navigation bar to explore full-time and internship openings.\n"
                "2. **Inspect Explainable Match Scores:** Each listing shows your explainable **AI Match Score (0-100%)** with matched vs missing skill tags.\n"
                "3. **Check Prerequisites & Stipend:** Click any card to view detailed responsibilities, tech stack, and salary/stipend range.\n"
                "4. **1-Click Application:** Click **Apply Now**. Your profile and uploaded resume are instantly submitted to the hiring manager.\n"
                "5. **Next Step:** Once screened, candidates receive an invitation for a customized **20-Question Technical Assessment**!\n\n"
                "What role are you targeting (e.g. Python, Full Stack, Data Science)? I can guide you further!"
            )

    @staticmethod
    def _handle_assessment_guidance(lower: str, lang: str, user_data: Optional[Dict[str, Any]]) -> str:
        """
        Explain assessment structure, pass marks (60%), proctoring 3-strike rules, and camera troubleshooting.
        """
        # Camera / Hardware troubleshooting
        if any(w in lower for w in ["camera", "webcam", "black screen", "face not detected", "permission"]):
            if lang in ["hindi", "hinglish"]:
                return (
                    "📷 **Camera Setup & Troubleshooting Tips:**\n\n"
                    "1. **Camera Permission dein:** Browser ke address bar mein lock/camera icon par click karke Camera ko **Allow** karein.\n"
                    "2. **Good Lighting:** Achhi front lighting mein baithein taaki AI aapka chehra clearly detect kar sake.\n"
                    "3. **Background Apps Band Karein:** Zoom, Google Meet ya Teams jaise apps band karein jo camera lock kar sakti hain.\n"
                    "4. **Page Reload:** Permission Allow karne ke baad test page refresh karein."
                )
            else:
                return (
                    "📷 **Camera Setup & Troubleshooting Guide:**\n\n"
                    "1. **Grant Permission:** Click the camera icon in your browser address bar and set Camera to **Allow**.\n"
                    "2. **Centering & Lighting:** Keep your face centered with sufficient front lighting.\n"
                    "3. **Close Conflicting Apps:** Quit apps like Zoom, Teams, or Skype holding camera locks.\n"
                    "4. **Refresh:** Reload the test page after allowing permissions."
                )

        # Proctoring 3-strike rules
        if any(w in lower for w in ["proctor", "strike", "violation", "cheat", "rule", "auto submit"]):
            if lang in ["hindi", "hinglish"]:
                return (
                    "🛡️ **SkillSphere AI Camera Proctoring & 3-Strike Policy:**\n\n"
                    "- **Strike 1 (Yellow Alert):** Pehli bar violation hone par warning alert milta hai (jaise camera se hatna ya multiple faces).\n"
                    "- **Strike 2 (Orange Final Warning):** Final warning — sirf 1 violation baki rehti hai.\n"
                    "- **Strike 3 (Red Auto-Submission):** Test immediately auto-submit ho jata hai, existing answers lock ho jaate hain aur recruiter ko telemetry notification chala jata hai.\n\n"
                    "💡 *Important Tips:* Browser tab switch na karein, phone use na karein, aur camera frame mein bane rahein."
                )
            else:
                return (
                    "🛡️ **SkillSphere AI Camera Proctoring & Three-Strike System:**\n\n"
                    "- **Strike 1 (Yellow Alert):** First violation warning alert.\n"
                    "- **Strike 2 (Orange Final Warning):** Critical notice — 1 strike remaining before termination.\n"
                    "- **Strike 3 (Red Auto-Submission):** Exam terminates immediately, submitted answers lock, and telemetry is sent to hiring managers.\n\n"
                    "💡 *Guidelines:* Stay centered in camera, do not switch browser tabs, and do not use secondary devices."
                )

        # General Assessment rules & passing criteria
        if lang in ["hindi", "hinglish"]:
            return (
                "📝 **SkillSphere 20-Question Technical Assessment Guidelines:**\n\n"
                "1. **Format:** Exactly **20 Multiple-Choice Questions (MCQs)** tailored to the role's required tech stack.\n"
                "2. **Time Limit:** **25 Minutes** live countdown timer (auto-submits when timer expires).\n"
                "3. **Passing Benchmark:** **60% (yani 12/20 correct answers)** qualify karne ke liye zaroori hain.\n"
                "4. **Automatic Advancement:** 60%+ score karte hi aapka application sidha **Interview Priority** par chala jata hai!\n"
                "5. **Proctoring:** Single attempt test, AI face monitoring aur 3-strike violation policy.\n\n"
                "Agar aapke dashboard par assessment pending hai, toh aap wahan se directly test shuru kar sakte hain!"
            )
        else:
            return (
                "📝 **SkillSphere 20-Question Technical Assessment Overview:**\n\n"
                "1. **Format:** Exactly **20 technical multiple-choice questions** customized to the job tech stack.\n"
                "2. **Time Limit:** **25-minute countdown timer** with instant scoring upon submission.\n"
                "3. **Passing Threshold:** **60% (at least 12/20 correct)** is required to pass.\n"
                "4. **Interview Advancement:** Passing with 60%+ automatically upgrades your status to **Interview Priority** in the recruiter ATS.\n"
                "5. **Proctoring Rules:** Single focused sitting with AI camera tracking and 3-strike policy.\n\n"
                "Visit your Dashboard or Assessments tab to launch any assigned tests!"
            )

    @staticmethod
    def _handle_frustration_and_confusion(lower: str, lang: str) -> str:
        """
        Empathetically help users who are confused or facing assessment / camera issues.
        """
        # Assessment or camera frustration
        if any(w in lower for w in ["assessment", "test", "camera", "complete", "shuru", "start", "nahi ho", "problem"]):
            if lang == "punjabi":
                return (
                    "Koi gal nahi veere, bilkul tension na lo! Main poori help karda haan. 😊\n\n"
                    "Dasso ki dikkat aa rahi hai:\n"
                    "- **Camera / Webcam:** Browser address bar vich camera icon te click karke **Allow** karo te page refresh karo.\n"
                    "- **Assessment:** 20 questions, 25 minute timer hunda hai, tab switch bilkul na karo.\n"
                    "- **Lighting:** Kamre vich lighting theek rakho taaki chehra saaf dikhe.\n\n"
                    "Dasso kis step te issue aa reha hai, main solve karda haan!"
                )
            elif lang in ["hindi", "hinglish"]:
                return (
                    "Arrey tension bilkul mat lo bro! Main aapki poori madad karunga. 😊\n\n"
                    "Bataiye kis step par problem aa rahi hai:\n"
                    "- **Camera Permission:** Browser ke address bar mein lock/camera icon par click karke Camera ko **Allow** karein aur page reload/refresh karein.\n"
                    "- **Background Apps:** Zoom ya Teams jaise apps band karein jo camera lock kar sakti hain.\n"
                    "- **3-Strike Safety:** Relax hokar test dein, 25 minutes ka timer hai aur single sitting test hai.\n\n"
                    "Aapko kis screen par issue aa raha hai? Khul ke batao, main help kar dunga!"
                )
            else:
                return (
                    "Don't worry at all! I'm here to help you get this resolved. 😊\n\n"
                    "Here are quick fixes for common assessment issues:\n"
                    "- **Camera Permission:** Click the camera icon in your browser address bar and set Camera to **Allow**, then refresh.\n"
                    "- **Conflicts:** Close conflicting video apps (Zoom, Teams) that may lock your webcam.\n"
                    "- **Assessment Window:** Complete the 20 questions in one sitting without switching tabs.\n\n"
                    "Let me know what error or screen you are stuck on!"
                )

        # General confusion
        if lang == "punjabi":
            return (
                "Koi gal nahi veere, aaraam naal saans lo! 😊 Sab theek ho jayega. "
                "Mainu aaraam naal dasso ki kis cheez vich confusion ho rahi hai — career/jobs baare, koi technical topic hai, ya bas overall sab mixed up lag reha hai? "
                "Main step-by-step clear kar dinda haan!"
            )
        elif lang in ["hindi", "hinglish"]:
            return (
                "Arey relax bro, bilkul tension mat lo! 😊 Main hoon na. "
                "Aaram se batao kis cheez mein confusion ho rahi hai — career ya jobs ko lekar, koi coding/tech topic hai, ya bas life mein sab thoda overwhelming lag raha hai? "
                "Step-by-step sab theek kar denge!"
            )
        else:
            return (
                "Hey, take a deep breath! 😊 No stress at all. "
                "Tell me what's confusing you — is it career/job related, a technical concept, or just feeling a bit overwhelmed today? "
                "Break it down for me, and we'll tackle it together step-by-step!"
            )

    @staticmethod
    def _handle_career_and_learning(lower: str, lang: str) -> str:
        """
        Provide structured beginner-friendly career and coding roadmaps linked to SkillSphere assessments.
        """
        # Python Learning Roadmap
        if "python" in lower:
            if lang in ["hindi", "hinglish"]:
                return (
                    "Python seekhna ek **bohot hi smart aur high-value decision** hai bro! 🐍 Ye clean aur beginner-friendly hai, aur Web Backend (FastAPI/Django), AI/Data Science, aur Automation sabhi jagah use hoti hai.\n\n"
                    "**Aapka 4-Step Practical Career Roadmap:**\n"
                    "1. **Core Fundamentals (Week 1-2):** Variables, Data Types (`list`, `dict`, `set`, `tuple`), conditions, loops (`for`, `while`), aur functions.\n"
                    "2. **OOP & Problem Solving (Week 3):** Classes, Objects, Inheritance, Decorators, Exception Handling — ye production code aur SkillSphere assessments ke liye zaroori hain.\n"
                    "3. **Hands-on Mini Projects (Week 4):** CLI Task Manager, Weather API fetcher, ya Web Scraper (`BeautifulSoup`). Projects banane se concepts pakke hote hain!\n"
                    "4. **Pick a Specialty (Week 5+):**\n"
                    "   - *Web Backend:* FastAPI ya Django + PostgreSQL\n"
                    "   - *AI / Data Science:* Pandas, NumPy, Scikit-Learn\n"
                    "   - *DSA for Coding Rounds:* Lists, HashMaps, Two Pointers, Stacks, Trees\n\n"
                    "💡 **SkillSphere Connection:** SkillSphere ke technical assessments mein Python ke 20 MCQs aate hain (syntax, OOP, list comprehensions). Pass hone ke liye 60% zaroori hai.\n\n"
                    "Aap bilkul zero se start kar rahe hain ya thoda syntax pehle se aata hai? Bataiye, main tailored practice questions de sakta hoon!"
                )
            elif lang == "punjabi":
                return (
                    "Python sikhna bohot vadiya decision hai veere! 🐍 Eh bohot asaan te powerful language hai jo Web Dev, AI, te Data Science vich use hundi hai.\n\n"
                    "**Step-by-step Roadmap:**\n"
                    "1. **Basics:** Variables, loops, functions, lists te dictionaries.\n"
                    "2. **OOP:** Classes te objects.\n"
                    "3. **Projects:** Chhote projects banao jaise calculator ya web scraper.\n"
                    "4. **Specialization:** Web development (FastAPI/Django) ya Data Science (Pandas/NumPy).\n\n"
                    "Ki tussi bilkul scratch to shuru kar rahe ho ya pehla thoda coding aandi hai?"
                )
            else:
                return (
                    "Learning Python is one of the best career decisions you can make! 🐍 It has clean syntax and powers backends, AI/ML, and automation.\n\n"
                    "**Your 4-Stage Roadmap:**\n"
                    "1. **Core Basics (Weeks 1-2):** Syntax, control flow (`if`/`else`), loops (`for`/`while`), data structures (`list`, `dict`, `set`), and functions.\n"
                    "2. **OOP & Architecture (Week 3):** Classes, inheritance, decorators, and exception handling.\n"
                    "3. **Hands-on Projects (Week 4):** CLI task manager, weather API app, or web scraper using `BeautifulSoup`.\n"
                    "4. **Choose Your Domain (Week 5+):**\n"
                    "   - *Web Backend:* FastAPI or Django with PostgreSQL\n"
                    "   - *Data Science & AI:* NumPy, Pandas, Scikit-learn\n"
                    "   - *DSA for Coding Rounds:* HashMaps, Two Pointers, Binary Search, Trees\n\n"
                    "💡 **SkillSphere Connection:** Python fundamentals and OOP form a major part of SkillSphere's 20-question assessments (60% passing mark to unlock interviews).\n\n"
                    "Are you starting from absolute scratch or do you already know some coding?"
                )

        # General Interview Prep
        if "interview" in lower:
            if lang in ["hindi", "hinglish"]:
                return (
                    "Nice! 🎯 Technical interview preparation ke liye yahan solid strategy hai:\n\n"
                    "1. **Projects Walkthrough:** Apne resume ke projects ke architecture aur apni responsibility ko clearly explain karna seekhein (STAR method: Situation, Task, Action, Result).\n"
                    "2. **Core Fundamentals:** Framework (FastAPI, React, Django) aur language fundamentals revise karein.\n"
                    "3. **Coding & Problem Solving:** Data structures (Arrays, HashMaps, Strings) ke common patterns practice karein.\n\n"
                    "Aap kis role ke liye interview prepare kar rahe hain? Bataiye, hum targeted mock questions cover kar sakte hain!"
                )
            else:
                return (
                    "Nice! 🎯 Here is a high-impact technical interview preparation strategy:\n\n"
                    "1. **Projects Walkthrough:** Be prepared to explain technical decisions and architecture in your resume using the STAR method.\n"
                    "2. **Core Fundamentals:** Solidify framework mechanisms (FastAPI, React, Django) and language quirks.\n"
                    "3. **DSA Patterns:** Practice HashMaps, Two Pointers, and recursion.\n\n"
                    "Which role are you preparing for? Let's practice targeted mock questions!"
                )

        return (
            "Career growth aur tech learning ke liye continuous practice zaroori hai! "
            "Aap coding, Python, DSA, ya interview prep mein se kis cheez par focus karna chahte hain? Batao, main targeted guidance provide karunga!"
        )

    @staticmethod
    def _handle_greetings_and_casual(lower: str, lang: str) -> str:
        """
        Handle casual greetings and friendly everyday chit-chat naturally without spamming SkillSphere.
        """
        if any(w in lower for w in ["what u doing", "what are you doing", "bro kya kr rha", "kya kar rahe ho"]):
            if lang == "punjabi":
                return "Bas veere, tuhade naal chat kar reha haan te fresh vibes share kar reha haan! 😄 Tussi dasso, ki chal reha aaj?"
            elif lang in ["hindi", "hinglish"]:
                return "Bas yahan baitha tumhare saath chat kar raha hoon! 😄 Tum batao, kya chal raha hai? Kuch interesting kaam ya aalsi din?"
            else:
                return "Just hanging out right here, ready to chat with you! 😄 What about you? Working on something cool or just chilling?"

        if any(w in lower for w in ["bore ho raha", "bore ho rha", "boring lag raha"]):
            if lang in ["hindi", "hinglish"]:
                return "Arey yaar 😂 Kuch interesting karte hain! Movies pasand hain ya random interesting facts sunne hain? Ya phir koi coding challenge try karein?"
            elif lang == "punjabi":
                return "Arey veere 😂 Bore hon di lod nahi! Kujh interesting karde aan — koi movie recommend karaan ya koi fun fact sunna hai?"
            else:
                return "Haha don't be bored! 😂 Let's do something fun — do you want thriller movie recommendations, mind-blowing facts, or a coding challenge?"

        if any(w in lower for w in ["kuch khaas nahi", "same old", "kuch nhi yaar"]):
            if lang in ["hindi", "hinglish"]:
                return "Haha, same old routine? 😅 College ya office mein busy tha aaj? Batao, ab kya plan hai?"
            else:
                return "Haha, same old routine? 😅 Busy with work or study today? What's the plan for the rest of the day?"

        # Casual greetings
        if lang == "punjabi":
            return "Sat Sri Akal veere! 🙏 Main bilkul chardi kala vich! Tussi sunao, ki haal-chaal aa tuhada? Sab theek-thaak chal reha?"
        elif lang in ["hindi", "hinglish"]:
            if any(w in lower for w in ["bro", "bhai", "yaar"]):
                return "Heyyy bro! 😄 Main bilkul mast hoon! Tum sunao, kaisa chal raha hai aaj ka din? Sab badhiya?"
            return "Heyyy! 😄 Main badhiya hoon, aap sunao! Kaisa chal raha hai aaj ka din? Kya haal-chaal?"
        else:
            return "Heyyy! 😄 I'm doing great, thanks for asking! What's up with you? How's your day going so far?"

    @staticmethod
    def _handle_entertainment_and_humor(lower: str, lang: str) -> str:
        """
        Handle movies, jokes, humor, mood venting, and AI concepts.
        """
        # Thriller movies
        if any(w in lower for w in ["movie", "movies", "thriller"]):
            if lang in ["hindi", "hinglish"]:
                return (
                    "Yeh rahe kuch absolute top-tier thriller movies jo aapko end tak screen se bandh kar rakhengi! 🍿🎬\n\n"
                    "1. **Inception (2010):** Christopher Nolan ka mind-bending dream-heist masterpiece. Har layer par suspense!\n"
                    "2. **Shutter Island (2010):** Leonardo DiCaprio ek mysterious psychiatric facility investigate karta hai — plot twist legendary hai!\n"
                    "3. **Andhadhun (2018):** Ayushmann Khurrana as a blind pianist who witnesses a murder. Har 10 minute mein naya shock!\n"
                    "4. **Drishyam (1 & 2):** Ajay Devgn as a family man outsmarting the entire police force. Pure suspense.\n"
                    "5. **Gone Girl (2014):** Psychological thriller with one of the most brilliant mid-movie twists ever filmed.\n\n"
                    "Tumhe Hollywood mind-benders zyada pasand hain ya Bollywood crime suspense? Batao, aur specific gems suggest kar dunga!"
                )
            else:
                return (
                    "Here are some top-tier thriller movies that will keep your heart racing from start to finish! 🍿🎬\n\n"
                    "1. **Inception (2010):** A dream-heist mind-bender directed by Christopher Nolan with incredible stakes and visuals.\n"
                    "2. **Shutter Island (2010):** A US Marshal investigates a disappearance at a psychiatric hospital on an isolated island. Legendary twist!\n"
                    "3. **Gone Girl (2014):** A chilling psychological thriller about a husband whose wife mysteriously vanishes.\n"
                    "4. **Prisoners (2013):** Hugh Jackman and Jake Gyllenhaal in a dark, gritty, and relentlessly intense mystery.\n"
                    "5. **Andhadhun (2018):** A brilliant dark-comedy suspense thriller about a pianist who pretends to be blind.\n\n"
                    "Do you prefer psychological mind-benders, crime mysteries, or action thrillers? Let me know!"
                )

        # Jokes
        if any(w in lower for w in ["joke"]):
            if lang in ["hindi", "hinglish", "punjabi"]:
                return (
                    "Ek programmer grocery store gaya. 🛒\n"
                    "Uski biwi ne bola: '1 bread le aana, aur agar dukan par eggs hon toh 10 le aana.'\n\n"
                    "Programmer 10 bread le kar ghar wapas aaya! 🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞\n"
                    "Biwi ne gusse mein pucha: 'Tum 10 bread kyun laye?!'\n"
                    "Programmer: 'Kyunki dukan par eggs the!' 😂🥚\n\n"
                    "Haha! Ek aur sunna hai ya koi aur baat karein?"
                )
            else:
                return (
                    "Why do programmers prefer dark mode? 🕶️\n\n"
                    "Because light attracts bugs! 🐛😂\n\n"
                    "Want another tech joke, or should we talk about something else?"
                )

        # Humor praise
        if any(w in lower for w in ["funny bro", "you're funny", "you are funny", "has mat"]) or lower.startswith("haha") or lower.startswith("lol"):
            return "Haha glad I could make you smile! 😂 Life's too short for dry robotic answers anyway. What else is on your mind today?"

        # Mood off / stress
        if any(w in lower for w in ["mood off", "dimag kharab", "sad hu", "feeling down", "tension"]):
            if lang in ["hindi", "hinglish"]:
                return (
                    "Arey yaar, kya hua? Mood off kyun hai? 🫂 Kabhi kabhi din sach mein heavy aur annoying nikal jata hai. "
                    "Tension mat lo, agar dil halka karna hai toh batao kya baat hui, main sun raha hoon! Ya phir mood refresh karne ke liye koi light baat karein?"
                )
            else:
                return (
                    "Oh no, I'm sorry to hear that! 🫂 What happened? Some days can be truly draining or stressful. "
                    "If you want to vent or talk through whatever is bothering you, I'm right here to listen. Or if you'd rather distract yourself with something fun, let me know!"
                )

        # AI Concept
        if any(w in lower for w in ["artificial intelligence", "what is ai", "explain ai"]):
            if lang in ["hindi", "hinglish"]:
                return (
                    "**Artificial Intelligence (AI)** basically computers aur machines ko insano ki tarah sochna, seekhna aur decision lena sikhane ki science hai! 🤖💡\n\n"
                    "Normal software wahi karta hai jo programmer ne line-by-line code kiya ho. Lekin AI systems **data aur patterns** ko analyse karke khud seekhte hain (Machine Learning aur Neural Networks ke zariye).\n\n"
                    "**Everyday Examples:**\n"
                    "- **Conversational AI / LLMs:** Jaise ChatGPT ya main, jo natural bhasha samajh ke chat karte hain.\n"
                    "- **Recommendations:** YouTube, Netflix aur Spotify jo predict karte hain aapko kya pasand aayega.\n"
                    "- **Computer Vision:** Smartphone ka Face Unlock aur Tesla jaisi self-driving cars.\n\n"
                    "Simple shabdon mein: AI machines ko 'smart' banata hai taaki wo complex problems solve kar sakein!"
                )
            else:
                return (
                    "**Artificial Intelligence (AI)** is the branch of computer science focused on building smart systems capable of performing tasks that typically require human intelligence! 🤖💡\n\n"
                    "Instead of just following hardcoded instructions, modern AI systems learn patterns directly from data using **Machine Learning** and **Deep Learning** (neural networks).\n\n"
                    "**Everyday Examples:**\n"
                    "- **Conversational AI / LLMs:** Understanding context, nuance, and responding naturally.\n"
                    "- **Predictive Algorithms:** Powering Netflix, Spotify, and YouTube.\n"
                    "- **Computer Vision:** Face ID on smartphones and autonomous vehicles."
                )

        # Capabilities
        if lang in ["hindi", "hinglish"]:
            return (
                "Main SkillSphere ka intelligent AI Career Assistant hoon! 😄 Aap mujhse in sabhi cheezon par help le sakte hain:\n\n"
                "- 🎯 **SkillSphere Support:** Aapka current stage, application status, 20-question assessments, aur proctoring rules\n"
                "- 💼 **Jobs & Internships:** Open roles discover karna, AI match score check karna, aur 1-click apply karna\n"
                "- 💻 **Career & Coding:** Python seekhna, DSA roadmap, aur technical interview preparation\n"
                "- 💬 **Casual Baatcheet:** Din kaisa raha, mood refresh karna, jokes, ya thriller movie recommendations!\n\n"
                "Aap kya discuss karna chahte hain?"
            )
        else:
            return (
                "I am your SkillSphere AI Career Assistant! 😄 Here's how I can help:\n\n"
                "- 🎯 **SkillSphere Progress:** Check your current stage, applications, and 20-question assessment results\n"
                "- 💼 **Jobs & Internships:** Discover roles, check explainable AI match scores, and apply with 1 click\n"
                "- 💻 **Career & Code:** Python roadmaps, DSA essentials, and interview preparation\n"
                "- 💬 **Casual Chat:** Chat about your day, jokes, and movie recommendations!\n\n"
                "What would you like to explore today?"
            )

    @staticmethod
    def _format_project_aware_fallback(lang: str) -> str:
        """
        Balanced fallback that politely introduces SkillSphere support without sounding like an advertisement.
        """
        if lang in ["hindi", "hinglish"]:
            return (
                "Main SkillSphere ka AI Assistant hoon! 😄 Aap mujhse in vishayon par poochh sakte hain:\n\n"
                "- 🎯 **Aapka Status:** 'Main kaunsi stage par hoon?' ya 'Meri application ka kya status hai?'\n"
                "- 💼 **Jobs/Internships:** 'Internship ke liye kaise apply karun?'\n"
                "- 📝 **Assessments:** '20-question test ke rules kya hain?' ya 'Kitne assessments complete kiye?'\n"
                "- 💻 **Career & Learning:** 'Bro mujhe Python seekhni hai' ya 'Interview prep kaise karun?'\n\n"
                "Aap kis baare mein janna chahte hain? Khul ke batayein!"
            )
        elif lang == "punjabi":
            return (
                "Main SkillSphere da AI Career Assistant haan veere! 😄 Tussi mainu kujh vi puchh sakde ho:\n\n"
                "- 🎯 **Tuhada Status:** 'Main kedi stage te haan?' ya 'Application da ki status hai?'\n"
                "- 💼 **Jobs & Internships:** 'Job ya internship layi apply kiven kariye?'\n"
                "- 📝 **Assessments:** '20-question assessment de rules te 60% passing criteria'\n"
                "- 💻 **Learning:** 'Python kiven sikhiye' ya interview preparation\n\n"
                "Dasso veere, kis cheez vich help chahidi hai?"
            )
        else:
            return (
                "I am your SkillSphere AI Career Assistant! 😄 Here is how I can assist you:\n\n"
                "- 🎯 **Your Stage & Status:** 'What stage am I in?' or 'What is my application status?'\n"
                "- 💼 **Jobs & Internships:** 'How can I apply for an internship?'\n"
                "- 📝 **Assessments:** 20-question test format, 25-minute timer, and 60% passing criteria\n"
                "- 💻 **Career & Learning:** Python roadmaps, DSA guidance, and interview prep\n\n"
                "Feel free to ask in English, Hindi, Punjabi, or Hinglish!"
            )

    @staticmethod
    def _format_user_journey_response(lang: str, user_data: Optional[Dict[str, Any]]) -> str:
        """
        Detailed user journey formatter strictly using verified records.
        """
        if not user_data or not user_data.get("authenticated"):
            return ChatbotService._handle_user_progress_and_stage(
                lower="stage", lang=lang, user_data=user_data,
                is_stage_query=True, is_application_query=False,
                is_assessment_count_query=False, is_next_step_query=False
            )

        name = user_data.get("name", "Student")
        cand = user_data.get("candidate", {})
        profile_pct = cand.get("profile_percentage", 0)
        missing_fields = cand.get("missing_fields", [])
        apps = cand.get("applications", [])
        tests = cand.get("assessments", [])
        completed_tests = [t for t in tests if t.get("status") == "completed" or t.get("score") is not None]
        pending_tests = [t for t in tests if t.get("status") in ["pending", "assigned", "in_progress"] and not t.get("passed")]

        if lang in ["hindi", "hinglish"]:
            lines = [
                f"👋 **Namaste {name}! Yeh raha aapke SkillSphere Career Journey ka live status:**\n",
                f"- **Profile Completion:** `{profile_pct}%` ({'100% Complete' if not missing_fields else f'Missing: {', '.join(missing_fields)}'})",
                f"- **Job & Internship Applications:** `{len(apps)}` submitted",
                f"- **Assessments:** `{len(completed_tests)}` Completed, `{len(pending_tests)}` Pending\n"
            ]
            if apps:
                lines.append("📁 **Aapki Submitted Applications:**")
                for a in apps[:4]:
                    lines.append(f"- **{a.get('job_title')}** at {a.get('company')} (Status: `{a.get('status')}`)")
            if pending_tests:
                lines.append(f"\n⏳ **Pending Assessment:** '{pending_tests[0].get('title')}' — 25 minute timer, 60% passing mark.")
            return "\n".join(lines)
        else:
            lines = [
                f"👋 **Hello {name}! Here is your verified SkillSphere Career Journey:**\n",
                f"- **Profile Completion:** `{profile_pct}%` ({'100% Complete' if not missing_fields else f'Missing: {', '.join(missing_fields)}'})",
                f"- **Applications:** `{len(apps)}` submitted",
                f"- **Assessments:** `{len(completed_tests)}` Completed, `{len(pending_tests)}` Pending\n"
            ]
            if apps:
                lines.append("📁 **Your Active Applications:**")
                for a in apps[:4]:
                    lines.append(f"- **{a.get('job_title')}** at {a.get('company')} (Status: `{a.get('status')}`)")
            if pending_tests:
                lines.append(f"\n⏳ **Pending Assessment:** '{pending_tests[0].get('title')}' — 25 minutes, 60% pass threshold.")
            return "\n".join(lines)
