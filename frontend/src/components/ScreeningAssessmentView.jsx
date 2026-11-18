import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  Sparkles,
  Users,
  CheckCircle2,
  XCircle,
  Clock,
  Mail,
  Send,
  Eye,
  Award,
  AlertTriangle,
  ChevronRight,
  ExternalLink,
  RefreshCw,
  FileText,
  Search,
  Filter,
  Layers,
  ChevronDown,
  Building2,
  Briefcase,
  Copy,
  Check
} from 'lucide-react';
import { screeningAPI, jobsAPI, assessmentAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import RadialGauge from './RadialGauge';

export default function ScreeningAssessmentView() {
  const { showToast } = useToast();

  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [screeningData, setScreeningData] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [emails, setEmails] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [runningAutoScreen, setRunningAutoScreen] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState('shortlisted'); // 'shortlisted', 'rejected', 'emails'
  
  // Inspection Modals
  const [inspectAssessmentId, setInspectAssessmentId] = useState(null);
  const [inspectAssessmentData, setInspectAssessmentData] = useState(null);
  const [loadingInspection, setLoadingInspection] = useState(false);

  const [previewEmail, setPreviewEmail] = useState(null);
  const [copiedToken, setCopiedToken] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedJobId) {
      loadJobScreening(selectedJobId);
    }
  }, [selectedJobId]);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [jobsRes, statsRes, emailRes] = await Promise.all([
        jobsAPI.list(),
        screeningAPI.getStats(),
        screeningAPI.getEmails(),
      ]);

      const jobsList = jobsRes.data || [];
      setJobs(jobsList);
      setTelemetry(statsRes.data);
      setEmails(emailRes.data || []);

      if (jobsList.length > 0) {
        setSelectedJobId(jobsList[0].job_id);
      }
    } catch (err) {
      console.error('Error loading screening data:', err);
      showToast('Failed to load screening engine telemetry.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadJobScreening = async (jobId) => {
    try {
      const res = await screeningAPI.getCandidatesForJob(jobId);
      setScreeningData(res.data);
    } catch (err) {
      console.error('Error loading candidates for job:', err);
      showToast('Failed to calculate candidate match vectors.', 'error');
    }
  };

  const handleRunAutoShortlist = async () => {
    if (!selectedJobId) return;
    setRunningAutoScreen(true);
    try {
      const res = await screeningAPI.autoShortlist(selectedJobId);
      showToast(res.data.message || 'Auto-screening complete! Tests generated & invitations emailed.', 'success');
      // Refresh candidates, stats and email log
      await loadJobScreening(selectedJobId);
      const [statsRes, emailRes] = await Promise.all([
        screeningAPI.getStats(),
        screeningAPI.getEmails(),
      ]);
      setTelemetry(statsRes.data);
      setEmails(emailRes.data || []);
    } catch (err) {
      console.error('Auto-shortlist error:', err);
      showToast(err.response?.data?.detail || 'Failed to execute auto-shortlisting.', 'error');
    } finally {
      setRunningAutoScreen(false);
    }
  };

  const handleGenerateCandidateTest = async (candidateId) => {
    try {
      const res = await screeningAPI.generateTest(candidateId, selectedJobId);
      showToast('20-Question assessment generated and assigned to candidate!', 'success');
      await loadJobScreening(selectedJobId);
    } catch (err) {
      console.error('Failed to generate test for candidate:', err);
      showToast(err.response?.data?.detail || 'Failed to generate assessment for candidate.', 'error');
    }
  };

  const handleInspectAssessment = async (assessmentId) => {
    setInspectAssessmentId(assessmentId);
    setLoadingInspection(true);
    try {
      const res = await assessmentAPI.getResults(assessmentId);
      setInspectAssessmentData(res.data);
    } catch (err) {
      console.error('Error fetching assessment breakdown:', err);
      showToast('Could not load assessment details.', 'error');
    } finally {
      setLoadingInspection(false);
    }
  };

  const handleCopyLink = (token) => {
    const url = `${window.location.origin}/assessment/${token}`;
    navigator.clipboard.writeText(url);
    setCopiedToken(token);
    showToast('Assessment URL copied to clipboard!', 'info');
    setTimeout(() => setCopiedToken(null), 2500);
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto" />
        <p className="text-slate-400 text-sm">Evaluating candidate resumes & technical assessment matrices...</p>
      </div>
    );
  }

  const selectedJob = jobs.find((j) => j.job_id === Number(selectedJobId));

  return (
    <div className="space-y-8">
      {/* ================= TELEMETRY STATS GRID ================= */}
      {telemetry && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="glass-card p-4 rounded-2xl border-white/10 text-center">
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block mb-1">
              Total Applicants
            </span>
            <span className="text-2xl font-black text-white">{telemetry.total_applicants}</span>
            <span className="text-[10px] text-slate-500 block mt-0.5">Across all roles</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-emerald-500/30 bg-emerald-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-emerald-400 font-semibold block mb-1">
              Shortlisted (&ge; 70%)
            </span>
            <span className="text-2xl font-black text-emerald-400">{telemetry.shortlisted_count}</span>
            <span className="text-[10px] text-emerald-500/80 block mt-0.5">Auto-qualified</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-rose-500/30 bg-rose-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-rose-400 font-semibold block mb-1">
              Below 70% Cutoff
            </span>
            <span className="text-2xl font-black text-rose-400">{telemetry.rejected_count}</span>
            <span className="text-[10px] text-rose-500/80 block mt-0.5">Screening rejected</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-amber-500/30 bg-amber-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-amber-400 font-semibold block mb-1">
              Tests Pending
            </span>
            <span className="text-2xl font-black text-amber-400">{telemetry.pending_tests}</span>
            <span className="text-[10px] text-amber-500/80 block mt-0.5">Awaiting candidate</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-cyan-500/30 bg-cyan-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-cyan-400 font-semibold block mb-1">
              Tests Completed
            </span>
            <span className="text-2xl font-black text-cyan-400">{telemetry.assessments_completed}</span>
            <span className="text-[10px] text-cyan-500/80 block mt-0.5">{telemetry.passed_tests} Passed</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-purple-500/30 bg-purple-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-purple-400 font-semibold block mb-1">
              Avg Test Score
            </span>
            <span className="text-2xl font-black text-purple-400">{telemetry.average_assessment_score}%</span>
            <span className="text-[10px] text-purple-500/80 block mt-0.5">Evaluation accuracy</span>
          </div>
        </div>
      )}

      {/* ================= JOB SELECTOR & AUTO-SHORTLIST ACTION HERO ================= */}
      <div className="glass-card p-6 rounded-3xl border border-white/10 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 blur-[120px] pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <BrainCircuit className="w-5 h-5" />
              </span>
              <h2 className="text-xl font-black text-white font-heading">
                AI Candidate Screening & Technical Assessment Engine
              </h2>
            </div>
            
            <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
              Dynamically compares candidates against job requirements across skills (50%), experience (25%), education (15%), and role alignment (10%). Candidates scoring <strong className="text-cyan-300">&ge; 70%</strong> are automatically shortlisted with 20-question technical tests generated and emailed.
            </p>

            {/* Job Selector Dropdown */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <span className="text-xs text-slate-400 font-semibold">Active Position:</span>
              <select
                value={selectedJobId || ''}
                onChange={(e) => setSelectedJobId(Number(e.target.value))}
                className="bg-dark-800/80 border border-white/20 text-white rounded-xl px-3.5 py-2 text-xs font-semibold focus:outline-none focus:border-cyan-400"
              >
                {jobs.map((j) => (
                  <option key={j.job_id} value={j.job_id}>
                    {j.title} ({j.company_name})
                  </option>
                ))}
              </select>

              {selectedJob && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  {selectedJob.skills.slice(0, 4).map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded text-[10px] bg-white/10 text-slate-300">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Trigger Auto-Screening Button */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              disabled={runningAutoScreen}
              onClick={handleRunAutoShortlist}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 text-white font-bold text-xs shadow-xl shadow-cyan-500/20 hover:brightness-110 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {runningAutoScreen ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Screening & Generating Tests...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Batch Auto-Shortlist (&ge;70%)</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ================= SUB-NAVIGATION TABS ================= */}
      <div className="flex items-center justify-between border-b border-white/10">
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveSubTab('shortlisted')}
            className={`pb-3 px-3 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeSubTab === 'shortlisted'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Shortlisted Candidates</span>
            <span className="px-2 py-0.5 rounded-full text-xs bg-emerald-500/20 text-emerald-300">
              {screeningData?.shortlisted_candidates?.length || 0}
            </span>
          </button>

          <button
            onClick={() => setActiveSubTab('rejected')}
            className={`pb-3 px-3 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeSubTab === 'rejected'
                ? 'border-rose-400 text-rose-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <XCircle className="w-4 h-4" />
            <span>Below 70% Cutoff</span>
            <span className="px-2 py-0.5 rounded-full text-xs bg-rose-500/20 text-rose-300">
              {screeningData?.rejected_candidates?.length || 0}
            </span>
          </button>

          <button
            onClick={() => setActiveSubTab('emails')}
            className={`pb-3 px-3 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeSubTab === 'emails'
                ? 'border-cyan-400 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Mail className="w-4 h-4" />
            <span>Email Audit Trail</span>
            <span className="px-2 py-0.5 rounded-full text-xs bg-cyan-500/20 text-cyan-300">
              {emails.length}
            </span>
          </button>
        </div>

        <button
          onClick={() => {
            loadInitialData();
            if (selectedJobId) loadJobScreening(selectedJobId);
          }}
          className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1.5 pb-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* ================= TAB 1: SHORTLISTED CANDIDATES (>= 70%) ================= */}
      {activeSubTab === 'shortlisted' && (
        <div className="space-y-4">
          {!screeningData?.shortlisted_candidates || screeningData.shortlisted_candidates.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <CheckCircle2 className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No shortlisted candidates yet</h3>
              <p className="text-xs text-slate-400 mb-4">
                Click "Run Batch Auto-Shortlist" to evaluate applicants and generate technical assessments.
              </p>
            </div>
          ) : (
            screeningData.shortlisted_candidates.map((cand) => (
              <div
                key={cand.candidate_id}
                className="p-6 rounded-2xl glass-card border border-emerald-500/20 hover:border-emerald-500/40 transition-all flex flex-col lg:flex-row lg:items-center justify-between gap-6"
              >
                {/* Left: Info & Breakdown */}
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-bold text-white">{cand.name}</h3>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                      Shortlisted (&ge; 70%)
                    </span>
                    <span className="text-xs text-slate-400">{cand.email}</span>
                  </div>

                  {/* Reasons Box */}
                  <div className="p-3.5 rounded-xl bg-black/30 border border-white/5 space-y-1 text-xs text-slate-300">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 block mb-1">
                      Explainable AI Match Reasons:
                    </span>
                    {cand.reasons.map((r, rIdx) => (
                      <div key={rIdx} className="flex items-start gap-2">
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span className="leading-snug">{r}</span>
                      </div>
                    ))}
                  </div>

                  {/* Skills & Experience */}
                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
                    {cand.experience && (
                      <span className="flex items-center gap-1 text-slate-300">
                        <Briefcase className="w-3.5 h-3.5 text-cyan-400" /> {cand.experience}
                      </span>
                    )}
                    {cand.education && (
                      <span className="flex items-center gap-1 text-slate-300">
                        <Award className="w-3.5 h-3.5 text-purple-400" /> {cand.education}
                      </span>
                    )}
                  </div>

                  {/* Matched Skills Chips */}
                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="text-[11px] text-slate-400 font-semibold mr-1">Matched:</span>
                    {cand.matched_skills.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Right: Score Meter & Assessment Status */}
                <div className="flex flex-col sm:flex-row items-center gap-6 justify-between lg:justify-end border-t lg:border-t-0 pt-4 lg:pt-0 border-white/10">
                  <div className="text-center">
                    <RadialGauge score={cand.match_score} size={70} strokeWidth={6} />
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider mt-1 block">Fit Score</span>
                  </div>

                  {/* Assessment Actions */}
                  <div className="space-y-2 text-right">
                    {cand.assessment ? (
                      <div>
                        {cand.assessment.status === 'completed' ? (
                          <div className="space-y-1.5">
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Score: {cand.assessment.score}/20 ({cand.assessment.percentage}%)
                            </span>
                            <div>
                              <button
                                onClick={() => handleInspectAssessment(cand.assessment.assessment_id)}
                                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center gap-1.5 ml-auto"
                              >
                                <Eye className="w-3.5 h-3.5" /> Inspect 20 Qs Answers
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                              <Clock className="w-3.5 h-3.5" /> Test Assigned (Pending)
                            </span>
                            <div className="flex items-center gap-2 justify-end">
                              <button
                                onClick={() => handleCopyLink(cand.assessment.test_token)}
                                className="px-3 py-1.5 rounded-xl text-xs font-medium bg-white/10 hover:bg-white/20 text-slate-300 flex items-center gap-1"
                                title="Copy Candidate Test Link"
                              >
                                {copiedToken === cand.assessment.test_token ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                                <span>Link</span>
                              </button>
                              <a
                                href={`/assessment/${cand.assessment.test_token}`}
                                target="_blank"
                                rel="noreferrer"
                                className="px-3 py-1.5 rounded-xl text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black flex items-center gap-1 shadow-md shadow-cyan-500/20"
                              >
                                <span>Simulate</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => handleGenerateCandidateTest(cand.candidate_id)}
                        className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400 transition-colors shadow-lg shadow-cyan-500/20"
                      >
                        Generate 20-Q Test
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* ================= TAB 2: REJECTED CANDIDATES (< 70%) ================= */}
      {activeSubTab === 'rejected' && (
        <div className="space-y-4">
          {!screeningData?.rejected_candidates || screeningData.rejected_candidates.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No rejected candidates</h3>
              <p className="text-xs text-slate-400">All evaluated applicants met or surpassed the 70% threshold.</p>
            </div>
          ) : (
            screeningData.rejected_candidates.map((cand) => (
              <div
                key={cand.candidate_id}
                className="p-6 rounded-2xl glass-card border border-rose-500/20 hover:border-rose-500/40 transition-all flex flex-col lg:flex-row lg:items-center justify-between gap-6"
              >
                {/* Left: Info & Rejection Reasons */}
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-bold text-white">{cand.name}</h3>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/15 text-rose-300 border border-rose-500/30">
                      Below Cutoff ({cand.match_score}%)
                    </span>
                    <span className="text-xs text-slate-400">{cand.email}</span>
                  </div>

                  {/* Deficits Box */}
                  <div className="p-3.5 rounded-xl bg-black/30 border border-white/5 space-y-1 text-xs text-slate-300">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-rose-400 block mb-1">
                      Screening Gap Analysis:
                    </span>
                    {cand.reasons.map((r, rIdx) => (
                      <div key={rIdx} className="flex items-start gap-2">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                        <span className="leading-snug">{r}</span>
                      </div>
                    ))}
                  </div>

                  {/* Missing Skills */}
                  {cand.missing_skills.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[11px] text-slate-400 font-semibold mr-1">Missing Proficiencies:</span>
                      {cand.missing_skills.map((s) => (
                        <span
                          key={s}
                          className="px-2 py-0.5 rounded text-[11px] font-medium bg-rose-500/15 text-rose-300 border border-rose-500/30"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Right: Score Gauge & Manual Action */}
                <div className="flex flex-col sm:flex-row items-center gap-6 justify-between lg:justify-end border-t lg:border-t-0 pt-4 lg:pt-0 border-white/10">
                  <div className="text-center">
                    <RadialGauge score={cand.match_score} size={70} strokeWidth={6} />
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider mt-1 block">Score &lt; 70%</span>
                  </div>

                  <div className="text-right">
                    <span className="text-xs text-slate-500 block mb-2">Automated test withheld</span>
                    <button
                      onClick={async () => {
                        try {
                          await screeningAPI.generateTest(cand.candidate_id, selectedJobId);
                          showToast('Manual override: Technical assessment generated!', 'success');
                          loadJobScreening(selectedJobId);
                        } catch (err) {
                          showToast('Could not generate assessment.', 'error');
                        }
                      }}
                      className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/20 text-slate-300 transition-colors"
                    >
                      Override: Generate Test
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* ================= TAB 3: EMAIL AUDIT TRAIL ================= */}
      {activeSubTab === 'emails' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Automated Dispatch Log</h3>
              <p className="text-xs text-slate-400">Immutable ledger of screening invites, shortlisting notices, and assessment evaluations</p>
            </div>
            <span className="text-xs text-slate-400">{emails.length} notifications logged</span>
          </div>

          {emails.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <Mail className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No emails logged yet</h3>
              <p className="text-xs text-slate-400">Dispatches appear automatically when candidates are shortlisted or complete tests.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {emails.map((e) => (
                <div
                  key={e.email_id}
                  className="p-4 rounded-xl glass-card border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="flex items-start gap-3">
                    <span className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mt-0.5">
                      <Mail className="w-4 h-4" />
                    </span>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="font-bold text-sm text-white">{e.subject}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          e.email_type === 'shortlisting' ? 'bg-emerald-500/20 text-emerald-300' :
                          e.email_type === 'test_invitation' ? 'bg-cyan-500/20 text-cyan-300' :
                          'bg-purple-500/20 text-purple-300'
                        }`}>
                          {e.email_type.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400">
                        Recipient: <strong className="text-slate-200">{e.recipient_name}</strong> ({e.recipient_email}) • Sent {new Date(e.sent_date).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => setPreviewEmail(e)}
                    className="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs text-slate-200 font-semibold transition-colors flex items-center gap-1.5 self-end md:self-auto"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View Email HTML</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ================= MODAL: INSPECT ASSESSMENT BREAKDOWN ================= */}
      {inspectAssessmentId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card p-6 md:p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-white/10 shadow-2xl rounded-3xl">
            {loadingInspection || !inspectAssessmentData ? (
              <div className="py-20 text-center">
                <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto mb-3" />
                <p className="text-xs text-slate-400">Loading candidate answer sheet...</p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex items-start justify-between gap-4 pb-4 border-b border-white/10">
                  <div>
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Candidate Test Evaluation</span>
                    <h3 className="text-2xl font-black text-white">{inspectAssessmentData.candidate_name}</h3>
                    <p className="text-xs text-slate-400 mt-1">
                      {inspectAssessmentData.title} • {inspectAssessmentData.job_title}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <span className="text-xs text-slate-400 block font-semibold">Final Score</span>
                      <span className={`text-2xl font-black ${inspectAssessmentData.passed ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {inspectAssessmentData.score}/{inspectAssessmentData.total_questions} ({inspectAssessmentData.percentage}%)
                      </span>
                    </div>
                    <button
                      onClick={() => setInspectAssessmentId(null)}
                      className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-slate-400 hover:text-white"
                    >
                      <XCircle className="w-6 h-6" />
                    </button>
                  </div>
                </div>

                {/* 20 Questions Breakdown */}
                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-white flex items-center gap-2">
                    <FileText className="w-4 h-4 text-cyan-400" />
                    Question-by-Question Evaluation ({inspectAssessmentData.breakdown?.length || 0} Questions):
                  </h4>

                  {(inspectAssessmentData.breakdown || []).map((q, qIdx) => (
                    <div
                      key={q.question_id || qIdx}
                      className={`p-4 rounded-xl border text-xs ${
                        q.is_correct ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-rose-500/5 border-rose-500/20'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`mt-0.5 p-1 rounded-full ${q.is_correct ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                          {q.is_correct ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-white mb-2">
                            Q{qIdx + 1}: {q.question_text}
                          </p>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
                            <div className={`p-2 rounded-lg border ${q.is_correct ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'}`}>
                              <span className="font-semibold block text-[10px]">Candidate Answer:</span>
                              <span>{q.candidate_answer || '(Unanswered)'}</span>
                            </div>
                            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                              <span className="font-semibold block text-[10px]">Correct Answer:</span>
                              <span>{q.correct_answer}</span>
                            </div>
                          </div>

                          {q.explanation && (
                            <p className="text-[11px] text-slate-400 bg-black/30 p-2 rounded border border-white/5 font-mono">
                              {q.explanation}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex justify-end pt-4 border-t border-white/10">
                  <button
                    onClick={() => setInspectAssessmentId(null)}
                    className="px-6 py-2.5 rounded-xl bg-cyan-500 text-black font-bold text-xs"
                  >
                    Close Inspection
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ================= MODAL: PREVIEW EMAIL HTML ================= */}
      {previewEmail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card p-6 md:p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-white/10 shadow-2xl rounded-3xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-4">
              <div>
                <span className="text-xs uppercase font-bold text-cyan-400 tracking-wider">Email Dispatch Preview</span>
                <h3 className="text-lg font-bold text-white">{previewEmail.subject}</h3>
                <p className="text-xs text-slate-400">To: {previewEmail.recipient_name} ({previewEmail.recipient_email})</p>
              </div>
              <button
                onClick={() => setPreviewEmail(null)}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-400 hover:text-white"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            {/* Rendered HTML Box */}
            <div
              className="bg-slate-900 rounded-2xl p-6 border border-white/10 text-slate-200 overflow-x-auto text-sm"
              dangerouslySetInnerHTML={{ __html: previewEmail.body_html }}
            />

            <div className="flex justify-end pt-4 mt-4 border-t border-white/10">
              <button
                onClick={() => setPreviewEmail(null)}
                className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
