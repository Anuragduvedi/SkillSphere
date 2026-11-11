import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Upload, 
  Search, 
  Filter, 
  Briefcase, 
  Building2, 
  MapPin, 
  DollarSign, 
  CheckCircle2, 
  Clock, 
  FileText, 
  Edit3, 
  Plus, 
  X, 
  ArrowRight, 
  Trash2, 
  Loader2,
  ChevronRight,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import { jobsAPI, resumeAPI, applicationsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import RadialGauge from '../components/RadialGauge';
import StatusBadge from '../components/StatusBadge';
import ResumeUploadModal from '../components/ResumeUploadModal';
import MatchAnalysisModal from '../components/MatchAnalysisModal';
import JobDetailsModal from '../components/JobDetailsModal';

export default function JobSeekerDashboard() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState('jobs'); // 'jobs', 'applications', 'profile'
  
  // Jobs state & filters
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [skillFilter, setSkillFilter] = useState('');
  
  // Applications state
  const [applications, setApplications] = useState([]);
  const [loadingApps, setLoadingApps] = useState(false);

  // Candidate Profile state
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);

  // Modals state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedJobForDetails, setSelectedJobForDetails] = useState(null);
  const [selectedJobForAnalysis, setSelectedJobForAnalysis] = useState(null);

  useEffect(() => {
    fetchProfile();
    fetchJobs();
    fetchApplications();
  }, []);

  const fetchProfile = async () => {
    setLoadingProfile(true);
    try {
      const res = await resumeAPI.getProfile();
      setProfile(res.data);
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoadingProfile(false);
    }
  };

  const fetchJobs = async () => {
    setLoadingJobs(true);
    try {
      const params = {};
      if (keyword) params.keyword = keyword;
      if (locationFilter) params.location = locationFilter;
      if (typeFilter) params.job_type = typeFilter;
      if (skillFilter) params.skill = skillFilter;

      const res = await jobsAPI.list(params);
      setJobs(res.data);
    } catch (err) {
      console.error('Error fetching jobs:', err);
      showToast('Failed to load job listings.', 'error');
    } finally {
      setLoadingJobs(false);
    }
  };

  const fetchApplications = async () => {
    setLoadingApps(true);
    try {
      const res = await applicationsAPI.list();
      setApplications(res.data);
    } catch (err) {
      console.error('Error fetching applications:', err);
    } finally {
      setLoadingApps(false);
    }
  };

  const handleWithdraw = async (applicationId) => {
    if (!window.confirm('Are you sure you want to withdraw this application?')) return;
    try {
      await applicationsAPI.withdraw(applicationId);
      showToast('Application successfully withdrawn.', 'info');
      fetchApplications();
      fetchJobs();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Withdrawal failed.';
      showToast(detail, 'error');
    }
  };

  const handleJobApplied = (jobId) => {
    fetchJobs();
    fetchApplications();
  };

  const handleProfileUpdated = () => {
    fetchProfile();
    fetchJobs();
  };

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      
      {/* ================= PROFILE OVERVIEW HERO CARD ================= */}
      <div className="p-6 md:p-8 rounded-3xl glass-panel border border-white/15 mb-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          
          {/* Candidate Info */}
          <div className="flex items-start sm:items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center font-extrabold text-2xl text-white shadow-lg shadow-cyan-500/25 flex-shrink-0">
              {profile?.name ? profile.name.slice(0, 2).toUpperCase() : 'CV'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold font-heading text-white">{profile?.name || user?.name}</h1>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  Candidate Profile
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 flex flex-wrap items-center gap-3">
                <span>{profile?.email || user?.email}</span>
                {profile?.phone && <span>• {profile.phone}</span>}
                {profile?.location && <span>• {profile.location}</span>}
              </p>

              {/* Candidate Skills Pill Matrix */}
              <div className="flex flex-wrap items-center gap-1.5 mt-3">
                {profile?.skills && profile.skills.length > 0 ? (
                  profile.skills.slice(0, 7).map((s) => (
                    <span
                      key={s}
                      className="px-2.5 py-0.5 rounded-md text-[11px] font-medium bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
                    >
                      {s}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-amber-400 flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" /> No skills indexed. Upload your resume to extract skills!
                  </span>
                )}
                {profile?.skills && profile.skills.length > 7 && (
                  <span className="text-xs text-slate-400">+{profile.skills.length - 7} more</span>
                )}
              </div>
            </div>
          </div>

          {/* Action: Upload / Re-extract Resume */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              onClick={() => setIsUploadOpen(true)}
              className="px-5 py-3 rounded-xl font-bold text-xs bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/25 hover:brightness-110 flex items-center justify-center gap-2 transition-all"
            >
              <Upload className="w-4 h-4" />
              {profile?.resumes && profile.resumes.length > 0 ? 'Upload / Re-Scan Resume (OCR)' : 'Upload Resume & Extract Data'}
            </button>
          </div>

        </div>
      </div>

      {/* ================= TABS NAVIGATION ================= */}
      <div className="flex border-b border-white/10 mb-8 space-x-2">
        <button
          onClick={() => setActiveTab('jobs')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'jobs'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Briefcase className="w-4 h-4" />
          Job Matrix & Match AI ({jobs.length})
        </button>

        <button
          onClick={() => setActiveTab('applications')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'applications'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Clock className="w-4 h-4" />
          Application Tracker ({applications.length})
        </button>

        <button
          onClick={() => setActiveTab('profile')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'profile'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Edit3 className="w-4 h-4" />
          Profile & OCR Credentials
        </button>
      </div>

      {/* ================= TAB 1: JOB MATRIX ================= */}
      {activeTab === 'jobs' && (
        <div className="space-y-6">
          
          {/* Multi-Parameter Filter Matrix */}
          <div className="p-4 rounded-2xl glass-card border border-white/10">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              
              {/* Keyword Search */}
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="Keyword, role, technology..."
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl glass-input"
                />
              </div>

              {/* Location Filter */}
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                  placeholder="City, state, or Remote..."
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl glass-input"
                />
              </div>

              {/* Job Type Dropdown */}
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl glass-input bg-dark-850"
              >
                <option value="">All Job Types</option>
                <option value="Full-time">Full-time</option>
                <option value="Remote">Remote</option>
                <option value="Contract">Contract</option>
                <option value="Part-time">Part-time</option>
              </select>

              {/* Required Skill */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={skillFilter}
                  onChange={(e) => setSkillFilter(e.target.value)}
                  placeholder="Skill (e.g. React, Docker)"
                  className="w-full px-3 py-2 text-xs rounded-xl glass-input"
                />
                <button
                  onClick={fetchJobs}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400 transition-colors flex-shrink-0"
                >
                  Filter
                </button>
              </div>

            </div>
          </div>

          {/* Job Cards Grid */}
          {loadingJobs ? (
            <div className="py-20 text-center space-y-3">
              <Loader2 className="w-10 h-10 text-cyan-400 animate-spin mx-auto" />
              <p className="text-xs text-slate-400">Loading opening matrix and calculating candidate match vectors...</p>
            </div>
          ) : jobs.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card">
              <Briefcase className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No openings found</h3>
              <p className="text-xs text-slate-400">Try adjusting your keyword or location filters.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {jobs.map((job) => (
                <div
                  key={job.job_id}
                  className="p-6 rounded-2xl glass-card border border-white/10 flex flex-col justify-between group hover:border-cyan-500/40"
                >
                  <div>
                    {/* Header */}
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors">
                          {job.title}
                        </h3>
                        <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                          <span className="flex items-center gap-1 text-slate-200">
                            <Building2 className="w-3.5 h-3.5 text-cyan-400" /> {job.company_name}
                          </span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3.5 h-3.5 text-purple-400" /> {job.location}
                          </span>
                        </div>
                      </div>

                      {/* Dynamic Match Score Meter */}
                      {job.match_score !== null && job.match_score !== undefined && (
                        <div 
                          onClick={() => setSelectedJobForAnalysis(job)}
                          className="cursor-pointer hover:scale-105 transition-transform"
                          title="Click for full breakdown"
                        >
                          <RadialGauge score={job.match_score} size={64} strokeWidth={6} />
                        </div>
                      )}
                    </div>

                    {/* Metadata tags */}
                    <div className="flex flex-wrap items-center gap-2 mb-3 text-xs">
                      <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-slate-300">
                        {job.job_type}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-slate-300">
                        Exp: {job.experience}
                      </span>
                      {job.salary_range && (
                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-medium">
                          {job.salary_range}
                        </span>
                      )}
                    </div>

                    {/* Description preview */}
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">
                      {job.description}
                    </p>

                    {/* Skills pills */}
                    <div className="flex flex-wrap gap-1.5 mb-5">
                      {job.skills.map((s) => (
                        <span
                          key={s}
                          className="px-2.5 py-0.5 rounded-md text-[11px] font-medium bg-white/5 text-slate-300 border border-white/10"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Actions Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <button
                      onClick={() => setSelectedJobForDetails(job)}
                      className="text-xs font-semibold text-slate-400 hover:text-white flex items-center gap-1"
                    >
                      View Details &rarr;
                    </button>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setSelectedJobForAnalysis(job)}
                        className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-cyan-300 flex items-center gap-1 transition-colors"
                      >
                        <Sparkles className="w-3.5 h-3.5" /> Gap Analysis
                      </button>

                      {job.user_has_applied ? (
                        <span className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Applied
                        </span>
                      ) : (
                        <button
                          onClick={() => setSelectedJobForDetails(job)}
                          className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-500/20 hover:brightness-110 transition-all"
                        >
                          Apply Now
                        </button>
                      )}
                    </div>
                  </div>

                </div>
              ))}
            </div>
          )}

        </div>
      )}

      {/* ================= TAB 2: APPLICATIONS TRACKER ================= */}
      {activeTab === 'applications' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold font-heading text-white">Application Workflow Tracker</h2>
              <p className="text-xs text-slate-400">Track interview progress, recruiter review stages, and status progression</p>
            </div>
            <button
              onClick={fetchApplications}
              className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-slate-300 border border-white/10"
            >
              Refresh Status
            </button>
          </div>

          {loadingApps ? (
            <div className="py-20 text-center space-y-3">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
              <p className="text-xs text-slate-400">Loading your submitted applications...</p>
            </div>
          ) : applications.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card">
              <Clock className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No active applications</h3>
              <p className="text-xs text-slate-400 mb-4">You have not submitted any applications yet.</p>
              <button
                onClick={() => setActiveTab('jobs')}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400 transition-colors"
              >
                Browse Available Jobs
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {applications.map((app) => (
                <div
                  key={app.application_id}
                  className="p-6 rounded-2xl glass-card border border-white/10 flex flex-col lg:flex-row lg:items-center justify-between gap-6"
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-bold text-white">{app.job_title}</h3>
                      <StatusBadge status={app.status} />
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
                      <span className="flex items-center gap-1.5 text-slate-200">
                        <Building2 className="w-3.5 h-3.5 text-cyan-400" /> {app.company_name}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-purple-400" /> {app.location}
                      </span>
                      <span>•</span>
                      <span>Applied on {new Date(app.application_date).toLocaleDateString()}</span>
                    </div>

                    {/* Progress Stepper */}
                    <div className="pt-2">
                      <div className="flex items-center gap-1 sm:gap-2 max-w-lg">
                        {['Applied', 'Under Review', 'Shortlisted', 'Interview', 'Selected'].map((step, idx) => {
                          const stepsOrder = ['Applied', 'Under Review', 'Shortlisted', 'Interview', 'Selected'];
                          const currentIdx = stepsOrder.indexOf(app.status);
                          const isComplete = currentIdx >= idx;
                          const isCurrent = app.status === step;

                          if (app.status === 'Rejected') {
                            return null;
                          }

                          return (
                            <React.Fragment key={step}>
                              <div className="flex flex-col items-center">
                                <div
                                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                                    isComplete
                                      ? 'bg-cyan-500 text-black shadow-neon-cyan/40 shadow-sm'
                                      : 'bg-white/10 text-slate-500'
                                  }`}
                                >
                                  {isComplete ? '✓' : idx + 1}
                                </div>
                                <span className={`text-[9px] mt-1 text-center whitespace-nowrap hidden sm:block ${
                                  isCurrent ? 'text-cyan-300 font-bold' : 'text-slate-500'
                                }`}>
                                  {step}
                                </span>
                              </div>
                              {idx < 4 && (
                                <div className={`flex-1 h-0.5 ${currentIdx > idx ? 'bg-cyan-500' : 'bg-white/10'}`} />
                              )}
                            </React.Fragment>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                  {/* Right: Match Score & Withdraw */}
                  <div className="flex items-center gap-5 justify-between lg:justify-end border-t lg:border-t-0 pt-4 lg:pt-0 border-white/10">
                    {app.match_score && (
                      <div className="text-right">
                        <span className="text-[10px] uppercase text-slate-400 block font-medium">Match Score</span>
                        <span className="text-xl font-bold font-heading text-emerald-400">{app.match_score}%</span>
                      </div>
                    )}

                    {['Applied', 'Under Review'].includes(app.status) && (
                      <button
                        onClick={() => handleWithdraw(app.application_id)}
                        className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 transition-colors"
                      >
                        Withdraw Application
                      </button>
                    )}
                  </div>

                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ================= TAB 3: CANDIDATE PROFILE & CREDENTIALS ================= */}
      {activeTab === 'profile' && (
        <div className="space-y-6">
          <div className="p-6 md:p-8 rounded-3xl glass-card border border-white/10">
            <h2 className="text-xl font-bold font-heading text-white mb-2">Candidate Profile & Credentials</h2>
            <p className="text-xs text-slate-400 mb-6">
              These details are extracted by OCR when you upload a resume, and used by the matching engine to compute your fit for each job.
            </p>

            <div className="space-y-6">
              
              {/* Contact info grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                  <span className="text-xs text-slate-400 block mb-1">Full Name</span>
                  <span className="text-sm font-semibold text-white">{profile?.name}</span>
                </div>
                <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                  <span className="text-xs text-slate-400 block mb-1">Email Address</span>
                  <span className="text-sm font-semibold text-white">{profile?.email}</span>
                </div>
                <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                  <span className="text-xs text-slate-400 block mb-1">Phone Number</span>
                  <span className="text-sm font-semibold text-white">{profile?.phone || 'Not provided'}</span>
                </div>
                <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                  <span className="text-xs text-slate-400 block mb-1">Current Location</span>
                  <span className="text-sm font-semibold text-white">{profile?.location || 'San Francisco, CA'}</span>
                </div>
              </div>

              {/* Education & Experience */}
              <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                <span className="text-xs text-slate-400 block mb-1">Education Credentials</span>
                <p className="text-sm text-slate-200">{profile?.education || 'Bachelor of Science in Computer Science'}</p>
              </div>

              <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                <span className="text-xs text-slate-400 block mb-1">Industry Experience Summary</span>
                <p className="text-sm text-slate-200">{profile?.experience || '3+ years developing web applications and APIs'}</p>
              </div>

              {/* Skills Tags */}
              <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                <span className="text-xs text-slate-400 block mb-2">Verified Skill Competencies ({profile?.skills?.length || 0})</span>
                <div className="flex flex-wrap gap-2">
                  {profile?.skills && profile.skills.map((s) => (
                    <span
                      key={s}
                      className="px-3 py-1 rounded-lg text-xs font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Uploaded Resumes History */}
              <div className="p-4 rounded-xl bg-dark-900/60 border border-white/5">
                <span className="text-xs text-slate-400 block mb-2">Uploaded Resume Records</span>
                {profile?.resumes && profile.resumes.length > 0 ? (
                  <div className="space-y-2">
                    {profile.resumes.map((r) => (
                      <div key={r.resume_id} className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/5 text-xs">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-cyan-400" />
                          <span className="font-semibold text-white">{r.file_name}</span>
                          <span className="text-slate-500">• {new Date(r.upload_date).toLocaleDateString()}</span>
                        </div>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold text-[10px]">
                          {r.processing_status}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">No resume documents uploaded yet.</p>
                )}
              </div>

              <button
                onClick={() => setIsUploadOpen(true)}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400 transition-colors flex items-center gap-2"
              >
                <Upload className="w-4 h-4" /> Open Resume Upload & OCR Tool
              </button>

            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      <ResumeUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onProfileUpdated={handleProfileUpdated}
      />

      <JobDetailsModal
        isOpen={Boolean(selectedJobForDetails)}
        onClose={() => setSelectedJobForDetails(null)}
        job={selectedJobForDetails}
        onOpenMatchAnalysis={(j) => setSelectedJobForAnalysis(j)}
        onApplied={handleJobApplied}
      />

      <MatchAnalysisModal
        isOpen={Boolean(selectedJobForAnalysis)}
        onClose={() => setSelectedJobForAnalysis(null)}
        job={selectedJobForAnalysis}
        onApplied={handleJobApplied}
      />

    </div>
  );
}
