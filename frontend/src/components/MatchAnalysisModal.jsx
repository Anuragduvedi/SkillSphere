import React, { useState, useEffect } from 'react';
import { 
  X, 
  CheckCircle2, 
  AlertTriangle, 
  Sparkles, 
  ArrowRight, 
  Loader2, 
  Building2, 
  MapPin, 
  Briefcase,
  Download
} from 'lucide-react';
import RadialGauge from './RadialGauge';
import { resumeAPI, applicationsAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import { generateResumeAnalysisReport } from '../services/reportGenerator';
import confetti from 'canvas-confetti';

export default function MatchAnalysisModal({ isOpen, onClose, job, onApplied }) {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    if (isOpen && job) {
      setApplied(job.user_has_applied || false);
      fetchAnalysis();
    }
  }, [isOpen, job]);

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const res = await resumeAPI.analyze(job.job_id);
      setAnalysis(res.data);
    } catch (err) {
      console.error('Error fetching match analysis:', err);
      showToast('Could not calculate match analysis.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!user) {
      showToast('Please sign in as a job seeker to submit an application.', 'warning');
      return;
    }
    setApplying(true);
    try {
      await applicationsAPI.apply(job.job_id);
      setApplied(true);
      showToast(`Application successfully submitted to ${job.title}!`, 'success');
      
      // Celebrate with confetti
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch (e) {}

      if (onApplied) onApplied(job.job_id);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Application submission failed.';
      showToast(detail, 'error');
    } finally {
      setApplying(false);
    }
  };

  if (!isOpen || !job) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-2xl bg-dark-850/95 border border-white/20 rounded-2xl shadow-2xl shadow-cyan-950/40 p-6 md:p-8 my-8 text-slate-100">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold font-heading text-white">AI Skill Matching Intelligence</h2>
            <p className="text-xs text-slate-400">Deep gap analysis comparing candidate profile vs job requirements</p>
          </div>
        </div>

        {/* Job Summary Banner */}
        <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-white">{job.title}</h3>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-1">
              <span className="flex items-center gap-1.5"><Building2 className="w-3.5 h-3.5 text-cyan-400" /> {job.company_name}</span>
              <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-purple-400" /> {job.location}</span>
              <span className="flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5 text-emerald-400" /> {job.job_type}</span>
            </div>
          </div>

          {!loading && analysis && (
            <div className="flex-shrink-0">
              <RadialGauge score={analysis.match_score} size={84} />
            </div>
          )}
        </div>

        {/* Content */}
        {loading ? (
          <div className="py-16 text-center space-y-4">
            <Loader2 className="w-10 h-10 text-cyan-400 animate-spin mx-auto" />
            <p className="text-xs text-slate-400">Evaluating multi-dimensional skill vectors...</p>
          </div>
        ) : analysis ? (
          <div className="space-y-6">
            
            {/* Skills Breakdown Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              {/* Matched Skills */}
              <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
                <div className="flex items-center gap-2 mb-3 text-emerald-400 font-semibold text-xs uppercase tracking-wider">
                  <CheckCircle2 className="w-4 h-4" />
                  Matched Competencies ({analysis.matched_skills.length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {analysis.matched_skills.length > 0 ? (
                    analysis.matched_skills.map((s) => (
                      <span
                        key={s}
                        className="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                      >
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500">None detected in profile</span>
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30">
                <div className="flex items-center gap-2 mb-3 text-amber-400 font-semibold text-xs uppercase tracking-wider">
                  <AlertTriangle className="w-4 h-4" />
                  Skill Gaps to Address ({analysis.missing_skills.length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {analysis.missing_skills.length > 0 ? (
                    analysis.missing_skills.map((s) => (
                      <span
                        key={s}
                        className="px-2.5 py-1 rounded-md text-xs font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      >
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-emerald-400 font-medium">100% Core Requirements Met!</span>
                  )}
                </div>
              </div>

            </div>

            {/* Explainable Recommendations */}
            <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30">
              <h4 className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Explainable Recommendation
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                {analysis.recommendations}
              </p>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-white/10">
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={() => generateResumeAnalysisReport(analysis, user?.name)}
                  className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-cyan-300 flex items-center gap-1.5 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Export PDF Report
                </button>
              </div>

              {applied ? (
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 w-full sm:w-auto justify-center">
                  <CheckCircle2 className="w-4 h-4" /> Application Submitted
                </div>
              ) : (
                <button
                  disabled={applying}
                  onClick={handleApply}
                  className="px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/30 hover:brightness-110 flex items-center justify-center gap-2 transition-all w-full sm:w-auto"
                >
                  {applying ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                  Submit Application Now
                </button>
              )}
            </div>

          </div>
        ) : null}

      </div>
    </div>
  );
}
