import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Search,
  Filter,
  Download,
  Eye,
  X,
  Clock,
  User,
  CheckCircle2,
  XCircle,
  Briefcase,
  Calendar,
  RefreshCw,
  Camera,
  Layers
} from 'lucide-react';
import { assessmentAPI } from '../services/api';
import { useToast } from '../context/ToastContext';

export default function RecruiterProctoringDashboard({ recruiterJobs = [] }) {
  const { showToast } = useToast();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAssessmentForTimeline, setSelectedAssessmentForTimeline] = useState(null);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [timelineLoading, setTimelineLoading] = useState(false);

  useEffect(() => {
    fetchProctoringReports();
  }, [selectedJob, selectedRisk]);

  const fetchProctoringReports = async () => {
    setLoading(true);
    try {
      const params = {};
      if (selectedJob) params.job_id = selectedJob;
      if (selectedRisk !== 'all') params.risk_level = selectedRisk;
      const res = await assessmentAPI.getProctoringReports(params);
      setReports(res.data || []);
    } catch (err) {
      console.error('Failed to load proctoring reports:', err);
      showToast('Failed to load proctoring reports.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenTimeline = async (assessment) => {
    setSelectedAssessmentForTimeline(assessment);
    setTimelineLoading(true);
    try {
      const res = await assessmentAPI.getAssessmentProctoringEvents(assessment.assessment_id);
      setTimelineEvents(res.data || []);
    } catch (err) {
      console.error('Failed to load proctoring timeline:', err);
      showToast('Could not load proctoring timeline events.', 'error');
    } finally {
      setTimelineLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (!reports.length) {
      showToast('No proctoring records available to export.', 'warning');
      return;
    }

    const headers = [
      'Assessment ID',
      'Candidate Name',
      'Candidate Email',
      'Job Title',
      'Test Title',
      'Status',
      'Score',
      'Percentage',
      'Violations Count',
      'Strikes (Max 3)',
      'Risk Classification',
      'Auto-Submitted Violation',
      'Auto-Submission Reason',
      'Started At',
      'Completed At'
    ];

    const rows = filteredReports.map((r) => [
      r.assessment_id,
      `"${r.candidate_name || ''}"`,
      `"${r.candidate_email || ''}"`,
      `"${r.job_title || ''}"`,
      `"${r.title || ''}"`,
      `"${r.status || ''}"`,
      r.score ?? 'N/A',
      r.percentage !== null && r.percentage !== undefined ? `${r.percentage}%` : 'N/A',
      r.violation_count || 0,
      r.strikes || 0,
      `"${r.risk_level || ''}"`,
      r.auto_submitted_proctoring ? 'YES' : 'NO',
      `"${(r.proctoring_submission_reason || '').replace(/"/g, '""')}"`,
      r.started_at ? new Date(r.started_at).toLocaleString() : 'N/A',
      r.completed_at ? new Date(r.completed_at).toLocaleString() : 'N/A'
    ]);

    const csvContent = [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `SkillSphere_Proctoring_Report_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Proctoring report exported successfully.', 'success');
  };

  // Filter by search query
  const filteredReports = reports.filter((r) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      r.candidate_name?.toLowerCase().includes(q) ||
      r.candidate_email?.toLowerCase().includes(q) ||
      r.title?.toLowerCase().includes(q) ||
      r.job_title?.toLowerCase().includes(q)
    );
  });

  // Calculate metrics
  const totalMonitored = reports.length;
  const cleanCount = reports.filter((r) => r.risk_level === 'Clean').length;
  const warningCount = reports.filter((r) => r.risk_level === 'Warning').length;
  const terminatedCount = reports.filter((r) => r.risk_level === 'Terminated').length;

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
            AI Proctoring & Examination Monitoring
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time computer vision telemetry, MediaPipe face tracking, and three-strike violation audits.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchProctoringReports}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 flex items-center gap-2 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleExportCSV}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-black font-bold flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition-all"
          >
            <Download className="w-3.5 h-3.5 text-black" />
            Export Audit Log
          </button>
        </div>
      </div>

      {/* Telemetry Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 font-medium block mb-1">Total Exam Sessions</span>
          <span className="text-2xl font-black text-white">{totalMonitored}</span>
        </div>
        <div className="p-4 rounded-xl glass-card border border-emerald-500/20 bg-emerald-500/5">
          <span className="text-xs text-emerald-300 font-medium block mb-1 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Clean Sessions (0 Strikes)
          </span>
          <span className="text-2xl font-black text-emerald-400">{cleanCount}</span>
        </div>
        <div className="p-4 rounded-xl glass-card border border-amber-500/20 bg-amber-500/5">
          <span className="text-xs text-amber-300 font-medium block mb-1 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Warnings Issued (1-2 Strikes)
          </span>
          <span className="text-2xl font-black text-amber-400">{warningCount}</span>
        </div>
        <div className="p-4 rounded-xl glass-card border border-rose-500/20 bg-rose-500/5">
          <span className="text-xs text-rose-300 font-medium block mb-1 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" /> Auto-Submitted (Strike 3)
          </span>
          <span className="text-2xl font-black text-rose-400">{terminatedCount}</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl glass-panel border border-white/10 flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Job Filter */}
          <select
            value={selectedJob}
            onChange={(e) => setSelectedJob(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl glass-input bg-dark-850 border border-white/10 text-white focus:outline-none focus:border-cyan-400"
          >
            <option value="">All Job Roles</option>
            {recruiterJobs.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                {j.title}
              </option>
            ))}
          </select>

          {/* Risk Level Filter */}
          <select
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl glass-input bg-dark-850 border border-white/10 text-white focus:outline-none focus:border-cyan-400"
          >
            <option value="all">All Risk Levels</option>
            <option value="clean">Clean (0 Violations)</option>
            <option value="warning">Warning (1-2 Violations)</option>
            <option value="terminated">Terminated (Strike 3)</option>
          </select>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search candidate name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl text-xs glass-input bg-dark-850 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
          />
        </div>
      </div>

      {/* Reports Table */}
      <div className="rounded-2xl glass-card border border-white/10 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400">
            <div className="w-8 h-8 border-3 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-xs">Loading proctoring records...</p>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-white mb-1">No proctoring records match filters</h3>
            <p className="text-xs">Adjust search keywords or filters to inspect candidates.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-white/5 border-b border-white/10 text-slate-400 uppercase tracking-wider font-semibold text-[10px]">
                <tr>
                  <th className="px-5 py-3.5">Candidate</th>
                  <th className="px-5 py-3.5">Job & Assessment</th>
                  <th className="px-5 py-3.5 text-center">Violations</th>
                  <th className="px-5 py-3.5 text-center">Strikes</th>
                  <th className="px-5 py-3.5 text-center">Status & Risk</th>
                  <th className="px-5 py-3.5 text-center">Score</th>
                  <th className="px-5 py-3.5">Timestamps</th>
                  <th className="px-5 py-3.5 text-right">Audit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {filteredReports.map((r) => {
                  const isTerminated = r.status === 'terminated_proctoring' || r.auto_submitted_proctoring || r.strikes >= 3;
                  const isWarning = !isTerminated && r.strikes > 0;
                  const isClean = !isTerminated && r.strikes === 0;

                  return (
                    <tr key={r.assessment_id} className="hover:bg-white/5 transition-colors">
                      <td className="px-5 py-4">
                        <div className="font-semibold text-white">{r.candidate_name}</div>
                        <div className="text-[11px] text-slate-400">{r.candidate_email}</div>
                      </td>

                      <td className="px-5 py-4">
                        <div className="font-medium text-slate-200">{r.job_title}</div>
                        <div className="text-[11px] text-slate-400">{r.title}</div>
                      </td>

                      <td className="px-5 py-4 text-center">
                        <span className="font-mono font-bold text-white text-xs">
                          {r.violation_count || 0}
                        </span>
                        {r.violations_breakdown && Object.keys(r.violations_breakdown).length > 0 && (
                          <div className="text-[10px] text-slate-500 mt-0.5">
                            {Object.entries(r.violations_breakdown)
                              .map(([type, count]) => `${type.replace(/_/g, ' ')}: ${count}`)
                              .slice(0, 2)
                              .join(' • ')}
                          </div>
                        )}
                      </td>

                      <td className="px-5 py-4 text-center">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                            isTerminated
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                              : isWarning
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          }`}
                        >
                          {r.strikes || 0} / 3
                        </span>
                      </td>

                      <td className="px-5 py-4 text-center">
                        {isTerminated ? (
                          <div>
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-400 border border-rose-500/30">
                              <ShieldAlert className="w-3 h-3" /> Terminated (Auto-Submitted)
                            </span>
                            {r.proctoring_submission_reason && (
                              <p className="text-[10px] text-rose-300/80 mt-1 max-w-xs truncate mx-auto" title={r.proctoring_submission_reason}>
                                {r.proctoring_submission_reason}
                              </p>
                            )}
                          </div>
                        ) : isWarning ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-amber-500/20 text-amber-400 border border-amber-500/30">
                            <AlertTriangle className="w-3 h-3" /> Warning Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            <ShieldCheck className="w-3 h-3" /> Clean Record
                          </span>
                        )}
                      </td>

                      <td className="px-5 py-4 text-center">
                        {r.score !== null && r.score !== undefined ? (
                          <div>
                            <span className="font-bold text-white">{r.score}/20</span>
                            <span className="text-[10px] text-slate-400 block">({r.percentage}%)</span>
                          </div>
                        ) : (
                          <span className="text-slate-500 text-xs">—</span>
                        )}
                      </td>

                      <td className="px-5 py-4 text-[11px] text-slate-400">
                        <div>Start: {r.started_at ? new Date(r.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}</div>
                        <div>End: {r.completed_at ? new Date(r.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'In progress'}</div>
                      </td>

                      <td className="px-5 py-4 text-right">
                        <button
                          onClick={() => handleOpenTimeline(r)}
                          className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-cyan-500/10 border border-white/10 hover:border-cyan-500/30 text-slate-300 hover:text-cyan-300 font-semibold text-xs flex items-center gap-1.5 ml-auto transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" /> Timeline
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Violation Timeline Audit Modal */}
      {selectedAssessmentForTimeline && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card max-w-2xl w-full p-6 border border-cyan-500/30 shadow-2xl max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-cyan-400" />
                  Proctoring Violation Audit Log
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Candidate: <strong className="text-white">{selectedAssessmentForTimeline.candidate_name}</strong> •{' '}
                  {selectedAssessmentForTimeline.title}
                </p>
              </div>
              <button
                onClick={() => setSelectedAssessmentForTimeline(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              {timelineLoading ? (
                <div className="p-8 text-center text-slate-400">
                  <div className="w-6 h-6 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto mb-2" />
                  <p className="text-xs">Loading violation events...</p>
                </div>
              ) : timelineEvents.length === 0 ? (
                <div className="p-8 text-center text-slate-400">
                  <ShieldCheck className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-white">Clean Examination Session</p>
                  <p className="text-xs text-slate-400">No proctoring violations recorded for this candidate.</p>
                </div>
              ) : (
                timelineEvents.map((ev, idx) => (
                  <div
                    key={ev.event_id || idx}
                    className={`p-3.5 rounded-xl border flex items-start gap-3 ${
                      ev.strike_number === 3
                        ? 'bg-rose-500/10 border-rose-500/30'
                        : 'bg-white/5 border-white/10'
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 font-bold text-xs ${
                        ev.strike_number === 3
                          ? 'bg-rose-500 text-white'
                          : 'bg-amber-500/20 text-amber-400'
                      }`}
                    >
                      {ev.strike_number || idx + 1}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-xs text-white uppercase tracking-wider">
                          {ev.event_type.replace(/_/g, ' ')}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {ev.created_at ? new Date(ev.created_at).toLocaleTimeString() : 'N/A'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1">{ev.details}</p>
                      {ev.strike_number === 3 && (
                        <div className="mt-2 text-[10px] text-rose-300 font-bold flex items-center gap-1">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          Auto-Submission Trigger: Assessment terminated at this violation.
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="pt-4 border-t border-white/10 flex justify-end">
              <button
                onClick={() => setSelectedAssessmentForTimeline(null)}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-semibold transition-colors"
              >
                Close Audit Log
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
