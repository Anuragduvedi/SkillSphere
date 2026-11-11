import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowRight, 
  FileSearch, 
  Cpu, 
  Target, 
  ShieldCheck, 
  CheckCircle2, 
  Building2, 
  Briefcase, 
  MapPin, 
  Zap, 
  Layers, 
  Users,
  Search,
  Star
} from 'lucide-react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { jobsAPI } from '../services/api';
import RadialGauge from '../components/RadialGauge';
import JobDetailsModal from '../components/JobDetailsModal';
import MatchAnalysisModal from '../components/MatchAnalysisModal';

gsap.registerPlugin(ScrollTrigger);

export default function LandingPage() {
  const navigate = useNavigate();
  const heroRef = useRef(null);
  const headlineRef = useRef(null);
  const cardsRef = useRef(null);
  const statsRef = useRef(null);

  const [featuredJobs, setFeaturedJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [analysisJob, setAnalysisJob] = useState(null);

  useEffect(() => {
    // Fetch featured jobs
    const fetchJobs = async () => {
      try {
        const res = await jobsAPI.list();
        setFeaturedJobs(res.data.slice(0, 4));
      } catch (err) {
        console.error('Failed to load featured jobs', err);
      }
    };
    fetchJobs();

    // GSAP Hero Animation
    const ctx = gsap.context(() => {
      gsap.from(headlineRef.current?.children || [], {
        y: 40,
        opacity: 0,
        duration: 0.9,
        stagger: 0.15,
        ease: 'power3.out',
      });

      gsap.from(cardsRef.current?.children || [], {
        scrollTrigger: {
          trigger: cardsRef.current,
          start: 'top 85%',
        },
        y: 50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.2,
        ease: 'power2.out',
      });

      gsap.from(statsRef.current?.children || [], {
        scrollTrigger: {
          trigger: statsRef.current,
          start: 'top 90%',
        },
        scale: 0.85,
        opacity: 0,
        duration: 0.6,
        stagger: 0.15,
        ease: 'back.out(1.5)',
      });
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={heroRef} className="relative min-h-screen bg-dark-900 overflow-hidden text-slate-100">
      
      {/* Background Neon Glowing Orbs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none -translate-y-1/2" />
      <div className="absolute top-1/3 right-10 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-10 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[140px] pointer-events-none" />

      {/* Grid Pattern Overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)',
          backgroundSize: '40px 40px',
        }}
      />

      {/* ================= HERO SECTION ================= */}
      <section className="relative pt-24 pb-20 md:pt-32 md:pb-32 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Text */}
          <div ref={headlineRef} className="lg:col-span-7 space-y-6 text-center lg:text-left">
            
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold backdrop-blur-md shadow-sm">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Next-Generation Career Intelligence & OCR Platform</span>
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold font-heading text-white tracking-tight leading-[1.15]">
              Match Your Skills to <br className="hidden sm:inline" />
              <span className="text-gradient">Dream Roles</span> with <br className="hidden sm:inline" />
              Explainable AI.
            </h1>

            <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto lg:mx-0 leading-relaxed font-normal">
              Extract resume insights instantly via optical character recognition, calculate multi-vector skill match percentages, and track your hiring pipeline through an intuitive ATS.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
              <Link
                to="/jobs"
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-xl shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-[1.02] flex items-center justify-center gap-2 transition-all duration-300"
              >
                Explore Openings <ArrowRight className="w-4 h-4" />
              </Link>

              <Link
                to="/register"
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-semibold text-sm bg-white/5 hover:bg-white/10 border border-white/15 text-slate-200 hover:text-white backdrop-blur-md flex items-center justify-center gap-2 transition-all duration-300"
              >
                Upload Resume & Test OCR
              </Link>
            </div>

            {/* Trust badge */}
            <div className="pt-4 flex items-center justify-center lg:justify-start gap-6 text-xs text-slate-400">
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Multi-page PDF/Image OCR</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Explainable Gap Analysis</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-purple-400" /> Real-time ATS Kanban</span>
            </div>

          </div>

          {/* Right Floating Glass Preview Card */}
          <div className="lg:col-span-5 relative">
            <div className="relative mx-auto max-w-md p-6 rounded-3xl glass-panel border border-white/20 shadow-2xl shadow-cyan-950/40">
              
              {/* Top Card Badge */}
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
                <div className="flex items-center gap-2.5">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  <span className="text-xs font-mono text-slate-400 ml-2">ocr_match_engine.py</span>
                </div>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">
                  92% Match
                </span>
              </div>

              {/* Sample Profile preview */}
              <div className="flex items-center gap-4 mb-5">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg">
                  AR
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">Alex Rivera</h4>
                  <p className="text-xs text-slate-400">Senior Full-Stack Engineer Candidate</p>
                </div>
              </div>

              {/* Radial Score */}
              <div className="flex items-center justify-center p-4 rounded-2xl bg-white/[0.03] border border-white/5 mb-5">
                <RadialGauge score={92} size={110} strokeWidth={9} />
                <div className="ml-5 text-left">
                  <div className="text-xs font-semibold text-emerald-400 mb-1 flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" /> High-Priority Match
                  </div>
                  <p className="text-xs text-slate-300 leading-snug">
                    Profile matches 5 of 6 core requirements for TechNova Labs.
                  </p>
                </div>
              </div>

              {/* Matched Skill Pills */}
              <div className="space-y-2">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">Matched Competencies</span>
                <div className="flex flex-wrap gap-1.5">
                  {['React', 'Python', 'FastAPI', 'PostgreSQL', 'Docker'].map((s) => (
                    <span key={s} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      ✓ {s}
                    </span>
                  ))}
                  <span className="px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    ! Kubernetes
                  </span>
                </div>
              </div>

            </div>

            {/* Floating Decorative Glass Card */}
            <div className="absolute -bottom-6 -left-6 hidden sm:block p-4 rounded-2xl glass-panel border border-cyan-500/30 shadow-xl shadow-cyan-950/40 animate-float-slow">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-cyan-500/20 flex items-center justify-center">
                  <Cpu className="w-4 h-4 text-cyan-400" />
                </div>
                <div>
                  <p className="text-xs font-bold text-white">OCR Parsing Time</p>
                  <p className="text-[11px] text-cyan-300 font-mono">0.42s (Sub-second)</p>
                </div>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ================= LIVE PLATFORM METRICS ================= */}
      <section className="py-12 border-y border-white/10 bg-dark-850/60 backdrop-blur-md">
        <div ref={statsRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="p-4 rounded-2xl glass-card">
            <div className="text-3xl sm:text-4xl font-extrabold font-heading text-white mb-1">100%</div>
            <div className="text-xs text-slate-400 font-medium">Automated OCR Extraction</div>
          </div>
          <div className="p-4 rounded-2xl glass-card">
            <div className="text-3xl sm:text-4xl font-extrabold font-heading text-cyan-400 mb-1">94.8%</div>
            <div className="text-xs text-slate-400 font-medium">Skill Gap Accuracy</div>
          </div>
          <div className="p-4 rounded-2xl glass-card">
            <div className="text-3xl sm:text-4xl font-extrabold font-heading text-purple-400 mb-1">6-Stage</div>
            <div className="text-xs text-slate-400 font-medium">Full ATS Pipeline</div>
          </div>
          <div className="p-4 rounded-2xl glass-card">
            <div className="text-3xl sm:text-4xl font-extrabold font-heading text-emerald-400 mb-1">0ms</div>
            <div className="text-xs text-slate-400 font-medium">Duplicate App Block</div>
          </div>
        </div>
      </section>

      {/* ================= 3-STEP ARCHITECTURE ================= */}
      <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold">
            <Layers className="w-3.5 h-3.5 text-purple-400" /> Pipeline Workflow
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold font-heading text-white">How SkillSphere Powers Careers</h2>
          <p className="text-sm text-slate-400">An integrated end-to-end flow from unstructured document to verified hire.</p>
        </div>

        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Card 1 */}
          <div className="p-8 rounded-3xl glass-card space-y-4 relative group">
            <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
              <FileSearch className="w-7 h-7" />
            </div>
            <div className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider">Step 01</div>
            <h3 className="text-xl font-bold text-white font-heading">Resume OCR & Parsing</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Upload PDF or image resumes up to 10MB. Our backend applies contrast filters, noise reduction, and regex entity extractors to capture contact metadata, degrees, and 150+ tech competencies.
            </p>
          </div>

          {/* Card 2 */}
          <div className="p-8 rounded-3xl glass-card space-y-4 relative group">
            <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
              <Target className="w-7 h-7" />
            </div>
            <div className="text-xs font-mono text-purple-400 font-bold uppercase tracking-wider">Step 02</div>
            <h3 className="text-xl font-bold text-white font-heading">Explainable Skill Matching</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Every job opening is indexed with canonical skills. Candidates receive instant match percentages, explicit breakdowns of matched vs missing proficiencies, and targeted upskilling recommendations.
            </p>
          </div>

          {/* Card 3 */}
          <div className="p-8 rounded-3xl glass-card space-y-4 relative group">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-7 h-7" />
            </div>
            <div className="text-xs font-mono text-emerald-400 font-bold uppercase tracking-wider">Step 03</div>
            <h3 className="text-xl font-bold text-white font-heading">ATS Pipeline & Recruiter Portal</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Recruiters manage candidate progression through Kanban boards and table views. Move applicants across Applied, Review, Interview, and Offer with automated duplicate submission prevention.
            </p>
          </div>

        </div>
      </section>

      {/* ================= FEATURED JOBS PREVIEW ================= */}
      <section className="py-20 bg-dark-850/40 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-12">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold mb-2">
                <Briefcase className="w-3.5 h-3.5 text-cyan-400" /> Live Market Roles
              </div>
              <h2 className="text-3xl font-bold font-heading text-white">Featured Openings</h2>
            </div>
            <Link
              to="/jobs"
              className="text-sm font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5"
            >
              View all openings &rarr;
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {featuredJobs.map((job) => (
              <div
                key={job.job_id}
                className="p-6 rounded-2xl glass-card flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <h3 className="text-lg font-bold text-white">{job.title}</h3>
                      <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                        <span className="flex items-center gap-1"><Building2 className="w-3.5 h-3.5 text-cyan-400" /> {job.company_name}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-purple-400" /> {job.location}</span>
                      </div>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-white/5 border border-white/10 text-cyan-300">
                      {job.job_type}
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
                    {job.description}
                  </p>

                  <div className="flex flex-wrap gap-1.5 mb-5">
                    {job.skills.slice(0, 4).map((s) => (
                      <span key={s} className="px-2.5 py-0.5 rounded-md text-[11px] font-medium bg-white/5 text-slate-300 border border-white/10">
                        {s}
                      </span>
                    ))}
                    {job.skills.length > 4 && (
                      <span className="px-2 py-0.5 rounded-md text-[11px] text-slate-500">
                        +{job.skills.length - 4} more
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <span className="text-xs font-semibold text-slate-300">
                    {job.salary_range || 'Competitive'}
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedJob(job)}
                      className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/15 text-white transition-colors"
                    >
                      View Spec
                    </button>
                    <button
                      onClick={() => setAnalysisJob(job)}
                      className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-500/20 hover:brightness-110 transition-all flex items-center gap-1"
                    >
                      <Sparkles className="w-3.5 h-3.5" /> Analyze Match
                    </button>
                  </div>
                </div>

              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ================= CALL TO ACTION GLASS BANNER ================= */}
      <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative p-10 md:p-16 rounded-3xl glass-panel border border-cyan-500/40 shadow-2xl shadow-cyan-950/50 text-center overflow-hidden">
          <div className="absolute -top-24 -left-24 w-72 h-72 bg-cyan-500/20 rounded-full blur-[80px]" />
          <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-purple-600/20 rounded-full blur-[80px]" />
          
          <div className="relative z-10 max-w-2xl mx-auto space-y-6">
            <h2 className="text-3xl sm:text-5xl font-extrabold font-heading text-white">
              Ready to Accelerate Your <br />
              <span className="text-gradient">Career Trajectory?</span>
            </h2>
            <p className="text-sm sm:text-base text-slate-300">
              Create your candidate profile, experience real-time resume extraction, and unlock explainable role matching in minutes.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
              <Link
                to="/register"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-xl shadow-cyan-500/30 hover:brightness-110 transition-all"
              >
                Get Started for Free
              </Link>
              <Link
                to="/login"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold text-sm bg-white/5 hover:bg-white/10 border border-white/15 text-white"
              >
                Sign In With Demo Accounts
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Modals */}
      <JobDetailsModal
        isOpen={Boolean(selectedJob)}
        onClose={() => setSelectedJob(null)}
        job={selectedJob}
        onOpenMatchAnalysis={(j) => setAnalysisJob(j)}
      />

      <MatchAnalysisModal
        isOpen={Boolean(analysisJob)}
        onClose={() => setAnalysisJob(null)}
        job={analysisJob}
      />

    </div>
  );
}
