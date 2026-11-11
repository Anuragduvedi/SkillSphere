import React, { useState, useEffect } from 'react';
import { 
  Briefcase, 
  Users, 
  CheckCircle2, 
  Clock, 
  Building2, 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Layers, 
  Table, 
  Edit, 
  Trash2, 
  Eye, 
  Sparkles, 
  Loader2, 
  X,
  MapPin,
  DollarSign,
  ChevronDown
} from 'lucide-react';
import { recruiterAPI, jobsAPI, applicationsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import RadialGauge from '../components/RadialGauge';
import StatusBadge from '../components/StatusBadge';

const ATS_STAGES = ['Applied', 'Under Review', 'Shortlisted', 'Interview', 'Selected', 'Rejected'];

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState('kanban'); // 'kanban', 'table', 'jobs', 'company'
  
  // Data state
  const [stats, setStats] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [recruiterJobs, setRecruiterJobs] = useState([]);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedJobFilter, setSelectedJobFilter] = useState('');
  const [searchCandidate, setSearchCandidate] = useState('');
  const [skillFilter, setSkillFilter] = useState('');

  // Modals
  const [isPostJobOpen, setIsPostJobOpen] = useState(false);
  const [selectedApplicant, setSelectedApplicant] = useState(null);

  // New Job Form State
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobLocation, setJobLocation] = useState('Remote');
  const [jobExperience, setJobExperience] = useState('2-4 years');
  const [jobType, setJobType] = useState('Full-time');
  const [jobSalary, setJobSalary] = useState('$120,000 - $150,000');
  const [jobSkillsList, setJobSkillsList] = useState(['React', 'TypeScript', 'Node.js']);
  const [skillInput, setSkillInput] = useState('');
  const [submittingJob, setSubmittingJob] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, appsRes, jobsRes, compRes] = await Promise.all([
        recruiterAPI.getStats(),
        recruiterAPI.getApplicants(),
        jobsAPI.list({ recruiter_id: user?.recruiter_id, status: 'all' }),
        recruiterAPI.getCompany().catch(() => ({ data: null })),
      ]);

      setStats(statsRes.data);
      setApplicants(appsRes.data);
      setRecruiterJobs(jobsRes.data);
      if (compRes.data) setCompany(compRes.data);
    } catch (err) {
      console.error('Error loading recruiter dashboard data:', err);
      showToast('Failed to load ATS data.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (applicationId, newStatus) => {
    try {
      await applicationsAPI.updateStatus(applicationId, newStatus);
      showToast(`Applicant stage moved to: ${newStatus}`, 'success');
      
      // Update local state smoothly
      setApplicants((prev) =>
        prev.map((a) => (a.application_id === applicationId ? { ...a, status: newStatus } : a))
      );
      if (selectedApplicant?.application_id === applicationId) {
        setSelectedApplicant((prev) => ({ ...prev, status: newStatus }));
      }
      
      // Refresh stats
      const statsRes = await recruiterAPI.getStats();
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to update applicant status:', err);
      showToast('Could not update applicant stage.', 'error');
    }
  };

  const handleExportCsv = async () => {
    try {
      const res = await recruiterAPI.exportCsv(selectedJobFilter || undefined);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `skillsphere_applicants_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      showToast('Applicants CSV exported successfully!', 'success');
    } catch (err) {
      console.error('CSV Export failed:', err);
      showToast('Failed to export CSV.', 'error');
    }
  };

  const handleAddSkillTag = (e) => {
    e.preventDefault();
    const clean = skillInput.trim();
    if (clean && !jobSkillsList.includes(clean)) {
      setJobSkillsList([...jobSkillsList, clean]);
      setSkillInput('');
    }
  };

  const handleRemoveSkillTag = (tag) => {
    setJobSkillsList(jobSkillsList.filter((s) => s !== tag));
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    if (!jobTitle || !jobDescription || !jobLocation) {
      showToast('Please fill in all mandatory job fields.', 'warning');
      return;
    }

    setSubmittingJob(true);
    try {
      await jobsAPI.create({
        title: jobTitle,
        description: jobDescription,
        location: jobLocation,
        experience: jobExperience,
        job_type: jobType,
        salary_range: jobSalary,
        skills: jobSkillsList,
      });

      showToast(`Job posting "${jobTitle}" published successfully!`, 'success');
      setIsPostJobOpen(false);
      // Reset form
      setJobTitle('');
      setJobDescription('');
      loadDashboardData();
    } catch (err) {
      console.error('Create job error:', err);
      showToast('Failed to publish job opening.', 'error');
    } finally {
      setSubmittingJob(false);
    }
  };

  const handleToggleJobStatus = async (jobId, currentStatus) => {
    const newStatus = currentStatus === 'active' ? 'closed' : 'active';
    try {
      await jobsAPI.update(jobId, { status: newStatus });
      showToast(`Job status updated to ${newStatus}.`, 'success');
      loadDashboardData();
    } catch (err) {
      showToast('Failed to update job status.', 'error');
    }
  };

  // Filtered applicants
  const filteredApplicants = applicants.filter((a) => {
    if (selectedJobFilter && a.job_id.toString() !== selectedJobFilter) return false;
    if (searchCandidate) {
      const q = searchCandidate.toLowerCase();
      const matchName = a.candidate_name?.toLowerCase().includes(q);
      const matchEmail = a.candidate_email?.toLowerCase().includes(q);
      if (!matchName && !matchEmail) return false;
    }
    if (skillFilter) {
      const q = skillFilter.toLowerCase();
      if (!a.candidate_skills?.some((s) => s.toLowerCase().includes(q))) return false;
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      
      {/* Top Header & Metrics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-2">
            <Building2 className="w-3.5 h-3.5 text-purple-400" />
            <span>{company?.company_name || 'Enterprise Recruiter Portal'}</span>
          </div>
          <h1 className="text-3xl font-extrabold font-heading text-white">
            Applicant Tracking System (ATS)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Review OCR-extracted candidate profiles, match vector scores, and transition hiring pipelines.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCsv}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 border border-white/15 text-slate-200 flex items-center gap-2 transition-colors"
          >
            <Download className="w-4 h-4 text-cyan-400" /> Export CSV
          </button>

          <button
            onClick={() => setIsPostJobOpen(true)}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-600/25 hover:brightness-110 flex items-center gap-2 transition-all"
          >
            <Plus className="w-4 h-4" /> Post a New Opening
          </button>
        </div>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 font-medium block mb-1">Active Job Postings</span>
          <span className="text-3xl font-extrabold font-heading text-white">{stats?.active_jobs || 0}</span>
        </div>
        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 font-medium block mb-1">Total Candidates</span>
          <span className="text-3xl font-extrabold font-heading text-cyan-400">{stats?.total_applicants || 0}</span>
        </div>
        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 font-medium block mb-1">Shortlisted for Review</span>
          <span className="text-3xl font-extrabold font-heading text-amber-400">{stats?.shortlisted || 0}</span>
        </div>
        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 font-medium block mb-1">In Active Interviews</span>
          <span className="text-3xl font-extrabold font-heading text-emerald-400">{stats?.interviews || 0}</span>
        </div>
      </div>

      {/* View Switcher Tabs & Filters */}
      <div className="p-4 rounded-2xl glass-panel border border-white/10 mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Left Tabs */}
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('kanban')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'kanban'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Layers className="w-4 h-4" /> Kanban Pipeline
          </button>

          <button
            onClick={() => setActiveTab('table')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'table'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Table className="w-4 h-4" /> Table View ({filteredApplicants.length})
          </button>

          <button
            onClick={() => setActiveTab('jobs')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'jobs'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Briefcase className="w-4 h-4" /> My Openings ({recruiterJobs.length})
          </button>
        </div>

        {/* Right Search & Job Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedJobFilter}
            onChange={(e) => setSelectedJobFilter(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-xl glass-input bg-dark-850"
          >
            <option value="">All Job Roles</option>
            {recruiterJobs.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                {j.title}
              </option>
            ))}
          </select>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchCandidate}
              onChange={(e) => setSearchCandidate(e.target.value)}
              placeholder="Search candidate..."
              className="pl-8 pr-3 py-1.5 text-xs rounded-xl glass-input w-40 sm:w-48"
            />
          </div>

          <input
            type="text"
            value={skillFilter}
            onChange={(e) => setSkillFilter(e.target.value)}
            placeholder="Skill (e.g. React)"
            className="px-3 py-1.5 text-xs rounded-xl glass-input w-28 sm:w-36"
          />
        </div>

      </div>

      {/* ================= VIEW 1: KANBAN BOARD PIPELINE ================= */}
      {activeTab === 'kanban' && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 overflow-x-auto pb-6">
          {ATS_STAGES.map((stage) => {
            const stageApps = filteredApplicants.filter((a) => a.status === stage);
            
            return (
              <div
                key={stage}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.currentTarget.classList.add('border-purple-500', 'bg-purple-950/20');
                }}
                onDragLeave={(e) => {
                  e.currentTarget.classList.remove('border-purple-500', 'bg-purple-950/20');
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.currentTarget.classList.remove('border-purple-500', 'bg-purple-950/20');
                  const appIdStr = e.dataTransfer.getData('applicationId');
                  if (appIdStr) {
                    handleStatusChange(Number(appIdStr), stage);
                  }
                }}
                className="bg-dark-850/80 rounded-2xl border border-white/10 p-3 min-w-[220px] flex flex-col max-h-[750px] transition-colors"
              >
                {/* Stage Header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-purple-400" />
                    <span className="text-xs font-bold text-white uppercase tracking-wider">{stage}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-white/10 text-slate-300">
                    {stageApps.length}
                  </span>
                </div>

                {/* Cards Container */}
                <div className="space-y-3 overflow-y-auto flex-1 pr-1">
                  {stageApps.map((app) => (
                    <div
                      key={app.application_id}
                      draggable="true"
                      onDragStart={(e) => {
                        e.dataTransfer.setData('applicationId', app.application_id.toString());
                        e.currentTarget.classList.add('opacity-50');
                      }}
                      onDragEnd={(e) => {
                        e.currentTarget.classList.remove('opacity-50');
                      }}
                      className="p-3.5 rounded-xl glass-card border border-white/10 hover:border-purple-500/50 cursor-grab active:cursor-grabbing space-y-2.5 transition-all shadow-md group"
                      onClick={() => setSelectedApplicant(app)}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h4 className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                            {app.candidate_name}
                          </h4>
                          <p className="text-[10px] text-slate-400 line-clamp-1">{app.job_title}</p>
                        </div>
                        {app.match_score && (
                          <span className="text-[10px] font-bold text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                            {Math.round(app.match_score)}%
                          </span>
                        )}
                      </div>

                      {/* Skills preview */}
                      <div className="flex flex-wrap gap-1">
                        {app.candidate_skills.slice(0, 3).map((s) => (
                          <span key={s} className="px-1.5 py-0.5 rounded text-[9px] bg-white/5 text-slate-300">
                            {s}
                          </span>
                        ))}
                      </div>

                      {/* Stage Changer Dropdown & Drag Hint */}
                      <div className="pt-2 border-t border-white/5 flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
                        <span className="text-[9px] text-slate-500">Drag or select:</span>
                        <select
                          value={app.status}
                          onChange={(e) => handleStatusChange(app.application_id, e.target.value)}
                          className="text-[10px] py-0.5 px-1.5 rounded bg-dark-900 border border-white/15 text-slate-200"
                        >
                          {ATS_STAGES.map((s) => (
                            <option key={s} value={s}>{s}</option>
                          ))}
                        </select>
                      </div>

                    </div>
                  ))}

                  {stageApps.length === 0 && (
                    <div className="py-10 text-center border-2 border-dashed border-white/5 rounded-xl text-[11px] text-slate-500">
                      Drop candidate here
                    </div>
                  )}
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* ================= VIEW 2: APPLICANTS TABLE ================= */}
      {activeTab === 'table' && (
        <div className="rounded-2xl glass-card border border-white/10 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-dark-850/90 border-b border-white/10 text-slate-400 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3.5 px-4">Candidate</th>
                  <th className="py-3.5 px-4">Role Applied</th>
                  <th className="py-3.5 px-4 text-center">Match Score</th>
                  <th className="py-3.5 px-4">Experience</th>
                  <th className="py-3.5 px-4">Verified Skills</th>
                  <th className="py-3.5 px-4">Current Stage</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {filteredApplicants.map((app) => (
                  <tr key={app.application_id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-white">{app.candidate_name}</div>
                      <div className="text-[11px] text-slate-400">{app.candidate_email}</div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-200">
                      {app.job_title}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {app.match_score ? (
                        <span className="inline-flex items-center gap-1 font-bold font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                          {app.match_score}%
                        </span>
                      ) : (
                        <span className="text-slate-500">N/A</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      {app.candidate_experience || 'Not specified'}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {app.candidate_skills.slice(0, 4).map((s) => (
                          <span key={s} className="px-2 py-0.5 rounded text-[10px] bg-white/5 border border-white/10 text-cyan-300">
                            {s}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedApplicant(app)}
                        className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white border border-white/10"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ================= VIEW 3: MANAGE JOB OPENINGS ================= */}
      {activeTab === 'jobs' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-bold font-heading text-white">Your Posted Openings</h2>
            <button
              onClick={() => setIsPostJobOpen(true)}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400"
            >
              + Create Opening
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recruiterJobs.map((j) => (
              <div key={j.job_id} className="p-5 rounded-2xl glass-card border border-white/10 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-base font-bold text-white">{j.title}</h3>
                    <p className="text-xs text-slate-400">{j.location} • {j.job_type}</p>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    j.status === 'active' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-500/20 text-slate-400'
                  }`}>
                    {j.status}
                  </span>
                </div>

                <div className="flex flex-wrap gap-1">
                  {j.skills.map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded text-[10px] bg-white/5 text-slate-300">
                      {s}
                    </span>
                  ))}
                </div>

                <div className="pt-3 border-t border-white/10 flex items-center justify-between text-xs">
                  <span className="text-slate-400">{j.applicant_count} Applicants</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleToggleJobStatus(j.job_id, j.status)}
                      className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300"
                    >
                      {j.status === 'active' ? 'Close Opening' : 'Reactivate'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= MODAL: CREATE JOB OPENING ================= */}
      {isPostJobOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
          <div className="relative w-full max-w-2xl bg-dark-850/95 border border-white/20 rounded-2xl shadow-2xl p-6 md:p-8 my-8 text-slate-100 max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsPostJobOpen(false)}
              className="absolute top-5 right-5 p-2 rounded-xl bg-white/5 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="text-xl font-bold font-heading text-white mb-1">Post a New Job Opening</h2>
            <p className="text-xs text-slate-400 mb-6">Published jobs are instantly available to job seekers and indexed by the matching engine.</p>

            <form onSubmit={handleCreateJob} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Job Title</label>
                <input
                  type="text"
                  required
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g. Senior Backend Engineer"
                  className="w-full px-3 py-2 text-xs rounded-xl glass-input"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Location</label>
                  <input
                    type="text"
                    required
                    value={jobLocation}
                    onChange={(e) => setJobLocation(e.target.value)}
                    placeholder="Remote / City"
                    className="w-full px-3 py-2 text-xs rounded-xl glass-input"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Job Type</label>
                  <select
                    value={jobType}
                    onChange={(e) => setJobType(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl glass-input bg-dark-850"
                  >
                    <option value="Full-time">Full-time</option>
                    <option value="Remote">Remote</option>
                    <option value="Contract">Contract</option>
                    <option value="Part-time">Part-time</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Experience</label>
                  <input
                    type="text"
                    required
                    value={jobExperience}
                    onChange={(e) => setJobExperience(e.target.value)}
                    placeholder="e.g. 3-5 years"
                    className="w-full px-3 py-2 text-xs rounded-xl glass-input"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Salary Range</label>
                <input
                  type="text"
                  value={jobSalary}
                  onChange={(e) => setJobSalary(e.target.value)}
                  placeholder="e.g. $130,000 - $160,000"
                  className="w-full px-3 py-2 text-xs rounded-xl glass-input"
                />
              </div>

              {/* Skills Tag Input */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Required Competencies</label>
                <div className="flex flex-wrap gap-1.5 mb-2 p-2 rounded-xl bg-dark-900/60 border border-white/10">
                  {jobSkillsList.map((s) => (
                    <span key={s} className="px-2.5 py-1 rounded-md text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1">
                      {s}
                      <button type="button" onClick={() => handleRemoveSkillTag(s)}><X className="w-3 h-3" /></button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    placeholder="Add required skill (e.g. Docker, Python)..."
                    className="flex-1 px-3 py-1.5 text-xs rounded-xl glass-input"
                  />
                  <button
                    type="button"
                    onClick={handleAddSkillTag}
                    className="px-3 py-1.5 rounded-xl bg-white/10 text-xs font-medium text-white"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Role Description & Responsibilities</label>
                <textarea
                  rows={4}
                  required
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Describe key responsibilities, deliverables, team culture, and requirements..."
                  className="w-full px-3 py-2 text-xs rounded-xl glass-input"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setIsPostJobOpen(false)}
                  className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingJob}
                  className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-600/30 hover:brightness-110 flex items-center gap-2"
                >
                  {submittingJob ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                  Publish Opening
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= DRAWER: INSPECT CANDIDATE ================= */}
      {selectedApplicant && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="relative w-full max-w-xl bg-dark-850/95 border border-white/20 rounded-2xl shadow-2xl p-6 md:p-8 text-slate-100 max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedApplicant(null)}
              className="absolute top-5 right-5 p-2 rounded-xl bg-white/5 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-xl font-bold text-white shadow-lg">
                {selectedApplicant.candidate_name?.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <h3 className="text-xl font-bold font-heading text-white">{selectedApplicant.candidate_name}</h3>
                <p className="text-xs text-slate-400">{selectedApplicant.candidate_email} • {selectedApplicant.candidate_phone || 'No phone'}</p>
                <p className="text-xs text-cyan-300 mt-0.5">Applied for: {selectedApplicant.job_title}</p>
              </div>
            </div>

            {/* Match score & stage bar */}
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 mb-6 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400 block mb-1">Current ATS Stage</span>
                <select
                  value={selectedApplicant.status}
                  onChange={(e) => handleStatusChange(selectedApplicant.application_id, e.target.value)}
                  className="px-3 py-1 text-xs rounded-lg bg-dark-900 border border-white/20 text-white font-semibold"
                >
                  {ATS_STAGES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {selectedApplicant.match_score && (
                <div className="text-right">
                  <span className="text-[10px] uppercase text-slate-400 block">Match Score</span>
                  <span className="text-2xl font-bold font-heading text-emerald-400">
                    {selectedApplicant.match_score}%
                  </span>
                </div>
              )}
            </div>

            {/* Candidate Experience */}
            <div className="space-y-4 text-xs mb-6">
              <div className="p-3.5 rounded-xl bg-dark-900/60 border border-white/5">
                <span className="text-slate-400 block mb-1 font-medium">Candidate Experience Summary</span>
                <p className="text-slate-200">{selectedApplicant.candidate_experience || '3 years full-stack experience'}</p>
              </div>

              {selectedApplicant.cover_note && (
                <div className="p-3.5 rounded-xl bg-dark-900/60 border border-white/5">
                  <span className="text-slate-400 block mb-1 font-medium">Applicant Cover Note</span>
                  <p className="text-slate-200">{selectedApplicant.cover_note}</p>
                </div>
              )}

              {/* Skills */}
              <div className="p-3.5 rounded-xl bg-dark-900/60 border border-white/5">
                <span className="text-slate-400 block mb-2 font-medium">Extracted Candidate Skills</span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedApplicant.candidate_skills?.map((s) => (
                    <span key={s} className="px-2.5 py-0.5 rounded-md text-[11px] bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-white/10">
              <button
                onClick={() => setSelectedApplicant(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/15 text-white"
              >
                Close Profile
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
