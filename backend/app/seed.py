import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models.models import (
    User, Candidate, Recruiter, Company, Skill, Job, Resume, Application, ResumeAnalysis
)
from app.core.security import get_password_hash
from app.services.matching_service import MatchingService

def seed_database():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@skillsphere.com").first():
            print("Database already contains seed data. Skipping.")
            return

        print("Seeding initial skills...")
        skill_catalog = [
            "React", "JavaScript", "TypeScript", "Python", "FastAPI", "PostgreSQL",
            "Docker", "Kubernetes", "Node.js", "AWS", "Tailwind CSS", "Next.js",
            "Redis", "MongoDB", "GraphQL", "Machine Learning", "System Design",
            "Git", "REST APIs", "Microservices", "CI/CD", "Linux", "PyTorch"
        ]
        skill_objs = {}
        for s_name in skill_catalog:
            skill = Skill(skill_name=s_name)
            db.add(skill)
            skill_objs[s_name] = skill
        db.commit()

        print("Seeding companies...")
        c1 = Company(
            company_name="TechNova Labs",
            description="Frontier cloud and distributed computing systems enterprise.",
            contact_info="careers@technova.io",
            website="https://technova.io",
            location="San Francisco, CA"
        )
        c2 = Company(
            company_name="Nexus AI Solutions",
            description="Pioneering enterprise LLM intelligence and automated inference pipelines.",
            contact_info="talent@nexusai.dev",
            website="https://nexusai.dev",
            location="Austin, TX"
        )
        c3 = Company(
            company_name="CloudScale Systems",
            description="Hyper-resilient multi-cloud orchestration and observability frameworks.",
            contact_info="hiring@cloudscale.net",
            website="https://cloudscale.net",
            location="Seattle, WA"
        )
        c4 = Company(
            company_name="Starlight Interactive",
            description="Next-generation interactive media, creative technology, and hyper-polished web UI.",
            contact_info="jobs@starlight.co",
            website="https://starlight.co",
            location="New York, NY"
        )
        db.add_all([c1, c2, c3, c4])
        db.commit()

        print("Seeding core users...")
        pwd_hash = get_password_hash("password123")

        # 1. Admin
        admin_user = User(
            name="Elena Rostova",
            email="admin@skillsphere.com",
            password_hash=pwd_hash,
            role="admin",
            is_active=True
        )
        db.add(admin_user)

        # 2. Recruiter
        recruiter_user = User(
            name="Sarah Jenkins",
            email="recruiter@skillsphere.com",
            password_hash=pwd_hash,
            role="recruiter",
            is_active=True
        )
        db.add(recruiter_user)
        db.commit()
        db.refresh(recruiter_user)

        recruiter_profile = Recruiter(
            user_id=recruiter_user.user_id,
            company_id=c1.company_id,
            designation="Director of Technical Talent",
            recruiter_details="Senior Talent Acquisition Lead at TechNova Labs."
        )
        db.add(recruiter_profile)
        db.commit()
        db.refresh(recruiter_profile)

        # 3. Second Recruiter
        recruiter_user_2 = User(
            name="Marcus Vance",
            email="recruiter2@skillsphere.com",
            password_hash=pwd_hash,
            role="recruiter",
            is_active=True
        )
        db.add(recruiter_user_2)
        db.commit()
        db.refresh(recruiter_user_2)

        recruiter_profile_2 = Recruiter(
            user_id=recruiter_user_2.user_id,
            company_id=c2.company_id,
            designation="Head of AI Hiring",
            recruiter_details="Lead Recruiter at Nexus AI Solutions."
        )
        db.add(recruiter_profile_2)
        db.commit()
        db.refresh(recruiter_profile_2)

        # 4. Job Seeker (Alex Rivera)
        seeker_user = User(
            name="Alex Rivera",
            email="candidate@skillsphere.com",
            password_hash=pwd_hash,
            role="job_seeker",
            is_active=True
        )
        db.add(seeker_user)
        db.commit()
        db.refresh(seeker_user)

        candidate_profile = Candidate(
            user_id=seeker_user.user_id,
            phone="+1 (555) 382-9104",
            location="San Francisco, CA (Open to Remote)",
            education="B.S. in Computer Science, University of California, Berkeley",
            experience="3+ years building high-throughput web applications with React, Python, and PostgreSQL.",
            profile_details="Passionate full-stack developer focused on microservices, modern glassmorphic UIs, and cloud backends."
        )
        # Add initial skills
        candidate_profile.skills.extend([
            skill_objs["React"],
            skill_objs["JavaScript"],
            skill_objs["TypeScript"],
            skill_objs["Python"],
            skill_objs["FastAPI"],
            skill_objs["PostgreSQL"],
            skill_objs["Docker"],
            skill_objs["Tailwind CSS"],
            skill_objs["Git"],
            skill_objs["REST APIs"]
        ])
        db.add(candidate_profile)
        db.commit()
        db.refresh(candidate_profile)

        # 5. Candidate Resume
        sample_resume = Resume(
            candidate_id=candidate_profile.candidate_id,
            file_name="Alex_Rivera_Software_Engineer_Resume.pdf",
            file_path="uploads/demo_alex_rivera_resume.pdf",
            file_type=".pdf",
            processing_status="Completed",
            extracted_text=(
                "Alex Rivera\nEmail: candidate@skillsphere.com | Phone: +1 555-382-9104\n"
                "Summary: Full Stack Engineer with 3+ years experience in React, Python FastAPI, PostgreSQL, and Docker.\n"
                "Education: B.S. in Computer Science - UC Berkeley (2023)\n"
                "Skills: React, JavaScript, TypeScript, Python, FastAPI, PostgreSQL, Docker, Git, REST APIs, Tailwind CSS."
            )
        )
        db.add(sample_resume)
        db.commit()
        db.refresh(sample_resume)

        # 6. Additional Candidates for ATS demonstration
        extra_candidates = [
            ("Devon Harris", "devon.h@example.com", "M.S. in AI, Stanford", "4 years ML research", ["Python", "Machine Learning", "PyTorch", "Docker", "AWS", "FastAPI"]),
            ("Sophia Chen", "sophia.c@example.com", "B.Tech in CSE", "2 years Frontend React", ["React", "JavaScript", "TypeScript", "Tailwind CSS", "Next.js", "Git"]),
            ("Liam Patel", "liam.p@example.com", "B.S. Software Eng, MIT", "5 years Cloud DevOps", ["Docker", "Kubernetes", "AWS", "Linux", "CI/CD", "Python", "PostgreSQL"]),
        ]
        cand_objs = []
        for name, email, edu, exp, skills in extra_candidates:
            u = User(name=name, email=email, password_hash=pwd_hash, role="job_seeker", is_active=True)
            db.add(u)
            db.commit()
            db.refresh(u)
            c = Candidate(user_id=u.user_id, phone="+1 (555) 749-2100", location="Remote", education=edu, experience=exp, profile_details="Experienced professional seeking impactful role.")
            for s in skills:
                if s in skill_objs:
                    c.skills.append(skill_objs[s])
            db.add(c)
            db.commit()
            db.refresh(c)
            # Add resume
            res = Resume(
                candidate_id=c.candidate_id,
                file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                file_path=f"uploads/{name.replace(' ', '_').lower()}.pdf",
                file_type=".pdf",
                processing_status="Completed",
                extracted_text=f"{name}\nEducation: {edu}\nExperience: {exp}\nSkills: {', '.join(skills)}"
            )
            db.add(res)
            db.commit()
            db.refresh(res)
            cand_objs.append((c, res))

        print("Seeding job postings...")
        job1 = Job(
            recruiter_id=recruiter_profile.recruiter_id,
            title="Senior Full-Stack Engineer",
            description="We are seeking an ambitious Senior Full-Stack Engineer to architect next-generation distributed web applications. You will spearhead our client dashboard using React and build resilient asynchronous microservices with FastAPI and PostgreSQL.",
            location="San Francisco, CA (Hybrid)",
            experience="3-5 years",
            job_type="Full-time",
            salary_range="$140,000 - $175,000",
            status="active"
        )
        job1.skills.extend([
            skill_objs["React"],
            skill_objs["TypeScript"],
            skill_objs["Python"],
            skill_objs["FastAPI"],
            skill_objs["PostgreSQL"],
            skill_objs["Docker"]
        ])

        job2 = Job(
            recruiter_id=recruiter_profile_2.recruiter_id,
            title="AI & Machine Learning Platform Engineer",
            description="Nexus AI is expanding our core infrastructure team. In this role, you will scale inference latency, build fine-tuning pipelines using PyTorch, and expose low-latency gRPC and REST endpoints.",
            location="Austin, TX / Remote",
            experience="4-6 years",
            job_type="Remote",
            salary_range="$165,000 - $210,000",
            status="active"
        )
        job2.skills.extend([
            skill_objs["Python"],
            skill_objs["Machine Learning"],
            skill_objs["PyTorch"],
            skill_objs["Docker"],
            skill_objs["AWS"],
            skill_objs["FastAPI"]
        ])

        job3 = Job(
            recruiter_id=recruiter_profile.recruiter_id,
            title="Frontend Glassmorphism & UI Architect",
            description="Elevate our client-facing web portals with stunning animations, smooth GSAP transitions, and Tailwind-based glassmorphism design systems. Passion for typography, micro-interactions, and 60fps rendering required.",
            location="Remote",
            experience="2-4 years",
            job_type="Remote",
            salary_range="$120,000 - $150,000",
            status="active"
        )
        job3.skills.extend([
            skill_objs["React"],
            skill_objs["TypeScript"],
            skill_objs["Tailwind CSS"],
            skill_objs["Next.js"],
            skill_objs["JavaScript"]
        ])

        job4 = Job(
            recruiter_id=recruiter_profile.recruiter_id,
            title="Cloud Infrastructure & DevOps Lead",
            description="Lead the architecture of our multi-region Kubernetes clusters on AWS. Implement automated CI/CD pipelines, monitor metrics with Prometheus/Grafana, and optimize database failover topologies.",
            location="Seattle, WA / Remote",
            experience="5+ years",
            job_type="Full-time",
            salary_range="$155,000 - $190,000",
            status="active"
        )
        job4.skills.extend([
            skill_objs["Docker"],
            skill_objs["Kubernetes"],
            skill_objs["AWS"],
            skill_objs["CI/CD"],
            skill_objs["Linux"],
            skill_objs["PostgreSQL"]
        ])

        job5 = Job(
            recruiter_id=recruiter_profile_2.recruiter_id,
            title="Backend Distributed Systems Specialist",
            description="Build resilient high-throughput event processing pipelines with Python and Redis. Design fault-tolerant message queues, cache synchronization, and schema migrations.",
            location="New York, NY",
            experience="3-5 years",
            job_type="Contract",
            salary_range="$80 - $110 / hour",
            status="active"
        )
        job5.skills.extend([
            skill_objs["Python"],
            skill_objs["FastAPI"],
            skill_objs["Redis"],
            skill_objs["PostgreSQL"],
            skill_objs["Microservices"]
        ])

        db.add_all([job1, job2, job3, job4, job5])
        db.commit()

        print("Seeding sample applications & resume analyses...")
        # Alex Rivera applies to job 1
        app1 = Application(
            job_id=job1.job_id,
            candidate_id=candidate_profile.candidate_id,
            resume_id=sample_resume.resume_id,
            status="Under Review",
            cover_note="Excited to contribute to TechNova's high-scale cloud portal with my React and FastAPI background!"
        )
        # Alex Rivera applies to job 3
        app2 = Application(
            job_id=job3.job_id,
            candidate_id=candidate_profile.candidate_id,
            resume_id=sample_resume.resume_id,
            status="Interview",
            cover_note="I specialize in modern UI craftsmanship and design systems with React and Tailwind."
        )
        db.add_all([app1, app2])
        db.commit()

        # Seed Resume Analysis for Alex on Job 1
        c_skills = [s.skill_name for s in candidate_profile.skills]
        j_skills = [s.skill_name for s in job1.skills]
        m_res = MatchingService.calculate_match(c_skills, j_skills)
        analysis1 = ResumeAnalysis(
            resume_id=sample_resume.resume_id,
            job_id=job1.job_id,
            match_score=m_res["match_score"],
            matched_skills=",".join(m_res["matched_skills"]),
            missing_skills=",".join(m_res["missing_skills"]),
            recommendations=m_res["recommendations"]
        )
        db.add(analysis1)

        # Seed Applications for other candidates across ATS columns
        # Devon applies to AI job (job2)
        devon_cand, devon_res = cand_objs[0]
        db.add(Application(
            job_id=job2.job_id,
            candidate_id=devon_cand.candidate_id,
            resume_id=devon_res.resume_id,
            status="Shortlisted",
            cover_note="Deep learning background with PyTorch and production inference experience."
        ))

        # Sophia applies to UI job (job3)
        sophia_cand, sophia_res = cand_objs[1]
        db.add(Application(
            job_id=job3.job_id,
            candidate_id=sophia_cand.candidate_id,
            resume_id=sophia_res.resume_id,
            status="Selected",
            cover_note="Passionate about UI aesthetics, responsive designs, and clean component architecture."
        ))

        # Liam applies to DevOps job (job4)
        liam_cand, liam_res = cand_objs[2]
        db.add(Application(
            job_id=job4.job_id,
            candidate_id=liam_cand.candidate_id,
            resume_id=liam_res.resume_id,
            status="Applied",
            cover_note="5 years orchestrating production Kubernetes on AWS with Terraform."
        ))

        db.commit()
        print("Database seeded successfully with rich demo data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
