import re
from typing import List, Dict, Tuple, Any, Optional

def normalize_skill(skill: str) -> str:
    """Normalize skill name for fuzzy matching (e.g., 'React.js' -> 'react', 'Node.js' -> 'node')"""
    s = skill.lower().strip()
    s = re.sub(r'[\.\-\s_]', '', s)
    if s == "reactjs":
        return "react"
    if s == "nodejs":
        return "node"
    if s == "vuejs":
        return "vue"
    if s == "golang":
        return "go"
    if s == "postgresql":
        return "postgres"
    if s == "k8s":
        return "kubernetes"
    return s

def extract_years_of_experience(exp_text: Optional[str]) -> float:
    """Extract numeric years of experience from strings like '3-5 years', '2+ yrs', 'Fresher', '4 years'"""
    if not exp_text:
        return 0.0
    text = exp_text.lower()
    if "fresher" in text or "entry" in text or "intern" in text:
        return 0.5
    # Look for patterns like "3-5", "3+", "4 years", "5 yrs"
    range_match = re.search(r'(\d+)\s*[-–to]\s*(\d+)', text)
    if range_match:
        return float(range_match.group(1))
    single_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\+|\s*years?|\s*yrs?)', text)
    if single_match:
        return float(single_match.group(1))
    number_match = re.search(r'\b(\d+)\b', text)
    if number_match:
        return float(number_match.group(1))
    return 1.0

class MatchingService:
    @staticmethod
    def calculate_match(candidate_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        """
        Calculates explainable resume-to-job matching score and returns:
        - match_score: float (0.0 to 100.0)
        - matched_skills: List[str]
        - missing_skills: List[str]
        - recommendations: str
        """
        if not required_skills:
            return {
                "match_score": 100.0,
                "matched_skills": candidate_skills,
                "missing_skills": [],
                "recommendations": "This position has no strict mandatory skill requirements. Your profile meets all criteria."
            }

        norm_candidate_skills = {normalize_skill(s): s for s in candidate_skills}
        matched_skills = []
        missing_skills = []

        for req in required_skills:
            norm_req = normalize_skill(req)
            if norm_req in norm_candidate_skills:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        # Base score on required skills
        matched_count = len(matched_skills)
        total_required = len(required_skills)
        base_percentage = (matched_count / total_required) * 100.0

        # Bonus for depth of candidate skills (max +5% if candidate has extra skills)
        bonus = 0.0
        if len(candidate_skills) > matched_count:
            bonus = min(5.0, (len(candidate_skills) - matched_count) * 1.0)

        match_score = round(min(100.0, base_percentage + bonus), 1)

        # Generate explainable recommendations
        if match_score >= 85.0:
            recommendations = (
                f"Outstanding match ({match_score}%)! Your core competencies align directly with "
                f"the mandatory prerequisites. You possess {matched_count} of {total_required} required proficiencies. "
                "Recommended action: Submit your application directly to recruiter priority queue."
            )
        elif match_score >= 60.0:
            missing_str = ", ".join(missing_skills[:3])
            recommendations = (
                f"Promising match ({match_score}%). You meet the primary qualifications ({matched_count}/{total_required}), "
                f"with slight gaps in: {missing_str}. "
                "Highlighting relevant coursework, portfolio repositories, or adjacent architectural experience will strengthen your interview prospect."
            )
        else:
            missing_str = ", ".join(missing_skills[:4])
            recommendations = (
                f"Emerging match ({match_score}%). This position heavily relies on: {missing_str}. "
                "We recommend reviewing these specific core concepts or exploring companion junior/mid-level openings."
            )

        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations
        }

    @staticmethod
    def calculate_comprehensive_match(candidate: Any, job: Any) -> Dict[str, Any]:
        """
        AI-Based Screening Candidate-to-Job Matching Engine:
        Analyzes:
        1. Technical Skills & Technologies (50% weight)
        2. Relevant Experience (25% weight)
        3. Educational Qualifications (15% weight)
        4. Job-Specific Requirements & Resume Keyword Fit (10% weight)

        Returns match percentage, breakdown components, shortlist status (>= 70%),
        and structured reasons for matching/not matching.
        """
        # 1. Extract Candidate Skills
        candidate_skills_raw = []
        if hasattr(candidate, "skills"):
            for s in candidate.skills:
                candidate_skills_raw.append(s.skill_name if hasattr(s, "skill_name") else str(s))
        elif isinstance(candidate, dict):
            candidate_skills_raw = candidate.get("skills", [])

        # Candidate Education & Experience & Resume Text
        candidate_edu = getattr(candidate, "education", "") or ""
        candidate_exp = getattr(candidate, "experience", "") or ""
        candidate_details = getattr(candidate, "profile_details", "") or ""
        resume_text = ""
        if hasattr(candidate, "resumes") and candidate.resumes:
            for r in candidate.resumes:
                if getattr(r, "extracted_text", None):
                    resume_text += " " + r.extracted_text

        combined_candidate_text = f"{candidate_edu} {candidate_exp} {candidate_details} {resume_text}".lower()

        # 2. Extract Job Requirements
        job_skills_raw = []
        if hasattr(job, "skills"):
            for s in job.skills:
                job_skills_raw.append(s.skill_name if hasattr(s, "skill_name") else str(s))
        elif isinstance(job, dict):
            job_skills_raw = job.get("skills", [])

        job_exp_req = getattr(job, "experience", "1-3 years") or "1-3 years"
        job_desc = (getattr(job, "description", "") or "").lower()
        job_title = (getattr(job, "title", "") or "").lower()

        reasons: List[str] = []

        # --- COMPONENT 1: Technical Skills Matching (50 Points Max) ---
        norm_candidate_skills = {normalize_skill(s): s for s in candidate_skills_raw}
        matched_skills = []
        missing_skills = []

        for req in job_skills_raw:
            norm_req = normalize_skill(req)
            if norm_req in norm_candidate_skills or norm_req in combined_candidate_text:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        if job_skills_raw:
            skills_ratio = len(matched_skills) / len(job_skills_raw)
            skills_score = skills_ratio * 50.0
            # Extra skill bonus (up to 5 points) if candidate has additional relevant tech skills
            extra_skills_count = max(0, len(candidate_skills_raw) - len(matched_skills))
            skills_score = min(50.0, skills_score + min(5.0, extra_skills_count * 0.8))
        else:
            skills_score = 50.0

        if matched_skills:
            reasons.append(f"Technical Skills: Aligned on {len(matched_skills)}/{len(job_skills_raw)} required proficiencies ({', '.join(matched_skills[:4])}).")
        if missing_skills:
            reasons.append(f"Skill Deficits: Missing prerequisite technologies: {', '.join(missing_skills[:3])}.")

        # --- COMPONENT 2: Relevant Experience Matching (25 Points Max) ---
        job_min_exp = extract_years_of_experience(job_exp_req)
        cand_years = extract_years_of_experience(candidate_exp)
        if cand_years == 0.0 and resume_text:
            cand_years = extract_years_of_experience(resume_text)

        if job_min_exp <= 0.5:
            # Entry level / Fresher job
            exp_score = 25.0
            reasons.append(f"Experience: Entry-level position; profile background meets prerequisites.")
        elif cand_years >= job_min_exp:
            exp_score = 25.0
            reasons.append(f"Experience: Candidate provides ~{cand_years:.1f} yrs experience, exceeding required {job_exp_req}.")
        elif cand_years >= (job_min_exp * 0.6):
            exp_score = 17.5
            reasons.append(f"Experience: Candidate has ~{cand_years:.1f} yrs experience, partially matching requirement ({job_exp_req}).")
        else:
            exp_score = 8.0
            reasons.append(f"Experience: Candidate ~{cand_years:.1f} yrs experience is below the expected {job_exp_req}.")

        # --- COMPONENT 3: Educational Qualifications (15 Points Max) ---
        higher_ed_keywords = ["b.tech", "btech", "m.tech", "mtech", "b.e", "computer science", "bca", "mca", "bachelor", "master", "bsc", "msc", "phd", "degree", "diploma"]
        has_tech_degree = any(k in candidate_edu.lower() or k in combined_candidate_text for k in higher_ed_keywords)

        if has_tech_degree:
            edu_score = 15.0
            reasons.append("Education: Verified Bachelor/Master degree in STEM/Computer Science or technical discipline.")
        elif candidate_edu.strip():
            edu_score = 10.0
            reasons.append(f"Education: Candidate holds educational qualification: {candidate_edu[:40]}.")
        else:
            edu_score = 6.0
            reasons.append("Education: Limited educational degree credentials listed in profile.")

        # --- COMPONENT 4: Job-Specific Requirements & Resume Keyword Fit (10 Points Max) ---
        role_keywords = set(re.findall(r'[a-zA-Z]{4,}', job_title + " " + job_desc[:250]))
        overlap_count = 0
        for kw in role_keywords:
            if kw in combined_candidate_text:
                overlap_count += 1

        keyword_fit = min(1.0, overlap_count / max(5, len(role_keywords)))
        alignment_score = keyword_fit * 10.0
        if keyword_fit >= 0.5:
            reasons.append("Project & Role Fit: High contextual overlap with job description responsibilities.")
        else:
            reasons.append("Project & Role Fit: Moderate domain context alignment with job requirements.")

        # Total Score
        total_score = round(skills_score + exp_score + edu_score + alignment_score, 1)
        total_score = min(100.0, max(10.0, total_score))

        # Automatic Shortlisting Threshold: 70% or above
        is_shortlisted = total_score >= 70.0
        if is_shortlisted:
            reasons.insert(0, f"Passed Screening: Candidate achieved {total_score}%, meeting or surpassing the 70.0% benchmark for automatic shortlisting.")
        else:
            reasons.insert(0, f"Screening Incomplete: Candidate achieved {total_score}%, falling below the 70.0% benchmark for automatic shortlisting.")

        return {
            "match_score": total_score,
            "is_shortlisted": is_shortlisted,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "breakdown": {
                "technical_skills": round(skills_score, 1),
                "experience": round(exp_score, 1),
                "education": round(edu_score, 1),
                "role_alignment": round(alignment_score, 1)
            },
            "reasons": reasons
        }

