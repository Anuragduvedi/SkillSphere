import React, { useState } from 'react';
import { 
  X, 
  Building2, 
  MapPin, 
  Briefcase, 
  DollarSign, 
  Clock, 
  CheckCircle2, 
  ArrowRight, 
  Loader2, 
  Sparkles,
  Zap
} from 'lucide-react';
import { applicationsAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import RadialGauge from './RadialGauge';
import confetti from 'canvas-confetti';

export default function JobDetailsModal({ isOpen, onClose, job, onOpenMatchAnalysis, onApplied }) {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [coverNote, setCoverNote] = useState('');
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(job?.user_has_applied || false);

  if (!isOpen || !job) return null;

  const handleApply = async () => {
    if (!user) {
      showToast('Please sign in as a job seeker to apply.', 'warning');
      return;
    }
    if (user.role !== 'job_seeker') {
      showToast('Only job seekers can submit job applications.', 'warning');
      return;
    }

    setApplying(true);
    try {
      await applicationsAPI.apply(job.job_id, { cover_note: coverNote });
      setApplied(true);
      showToast(`Application successfully submitted for ${job.title}!`, 'success');
      
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch (e) {}

      if (onApplied) onApplied(job.job_id);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Application failed.';
      showToast(detail, 'error');
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-3xl bg-dark-850/95 border border-white/20 rounded-2xl shadow-2xl shadow-cyan-950/40 p-6 md:p-8 my-8 text-slate-100 max-h-[90vh] overflow-y-auto">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6 pb-6 border-b border-white/10">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold mb-3">
              <Zap className="w-3.5 h-3.5 text-cyan-400" /> Active Opening
            </div>
            <h2 className="text-2xl font-bold font-heading text-white">{job.title}</h2>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-2">
              <span className="flex items-center gap-1.5 font-medium text-slate-200">
                <Building2 className="w-4 h-4 text-cyan-400" /> {job.company_name}
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-purple-400" /> {job.location}
              </span>
              <span className="flex items-center gap-1.5">
                <Briefcase className="w-4 h-4 text-emerald-400" /> {job.job_type}
              </span>
              {job.salary_range && (
                <span className="flex items-center gap-1.5 text-cyan-300 font-semibold">
                  <DollarSign className="w-4 h-4 text-cyan-400" /> {job.salary_range}
                </span>
              )}
            </div>
          </div>

          {user?.role === 'job_seeker' && job.match_score !== null && job.match_score !== undefined && (
            <div className="flex items-center gap-3 p-3 rounded-2xl bg-white/5 border border-white/10">
              <RadialGauge score={job.match_score} size={68} strokeWidth={6} />
              <button
                onClick={() => {
                  onClose();
                  onOpenMatchAnalysis(job);
                }}
                className="text-xs text-cyan-400 hover:text-cyan-300 underline font-medium"
              >
                Deep Match Breakdown &rarr;
              </button>
            </div>
          )}
        </div>

        {/* Experience & Requirements metadata bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-dark-900/60 border border-white/5 mb-6 text-xs">
          <div>
            <span className="text-slate-400 block mb-0.5">Experience Level</span>
            <span className="font-semibold text-white">{job.experience}</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Total Applicants</span>
            <span className="font-semibold text-white">{job.applicant_count} candidates</span>
          </div>
          <div>
            <span className="text-slate-400 block mb-0.5">Application Status</span>
            <span className={`font-semibold ${applied ? 'text-emerald-400' : 'text-slate-300'}`}>
              {applied ? 'Applied' : 'Not Applied'}
            </span>
          </div>
        </div>

        {/* Required Skills */}
        <div className="mb-6">
          <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-300 mb-2">Required Core Competencies</h4>
          <div className="flex flex-wrap gap-2">
            {job.skills && job.skills.length > 0 ? (
              job.skills.map((s) => (
                <span
                  key={s}
                  className="px-3 py-1 rounded-lg text-xs font-semibold bg-white/5 border border-white/10 text-cyan-300"
                >
                  {s}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500">General software development competencies</span>
            )}
          </div>
        </div>

        {/* Job Description */}
        <div className="mb-6">
          <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-300 mb-2">Role Overview & Responsibilities</h4>
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 text-sm text-slate-300 leading-relaxed whitespace-pre-line">
            {job.description}
          </div>
        </div>

        {/* Cover Note Section (if applying) */}
        {!applied && user?.role === 'job_seeker' && (
          <div className="mb-6">
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Brief Introduction or Note to Recruiter (Optional)
            </label>
            <textarea
              rows={2}
              value={coverNote}
              onChange={(e) => setCoverNote(e.target.value)}
              placeholder="Highlight why your skills make you a high-value match for this team..."
              className="w-full px-3 py-2 text-xs rounded-xl glass-input"
            />
          </div>
        )}

        {/* Actions Footer */}
        <div className="flex items-center justify-between pt-6 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
          >
            Close
          </button>

          <div className="flex items-center gap-3">
            {user?.role === 'job_seeker' && (
              <button
                onClick={() => {
                  onClose();
                  onOpenMatchAnalysis(job);
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-cyan-300 transition-colors"
              >
                Analyze Match Score
              </button>
            )}

            {applied ? (
              <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                <CheckCircle2 className="w-4 h-4" /> Application Submitted
              </div>
            ) : (
              <button
                disabled={applying}
                onClick={handleApply}
                className="px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/30 hover:brightness-110 flex items-center gap-2 transition-all"
              >
                {applying ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                Submit Application
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
