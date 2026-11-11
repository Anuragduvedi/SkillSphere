import re
from typing import List, Dict, Tuple, Any

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
