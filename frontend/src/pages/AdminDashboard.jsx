import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Users, 
  Briefcase, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  Trash2, 
  Power, 
  TrendingUp, 
  Activity, 
  Loader2, 
  Search,
  Layers,
  Database
} from 'lucide-react';
import { adminAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function AdminDashboard() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState('analytics'); // 'analytics', 'users', 'jobs'
  const [analytics, setAnalytics] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [jobsList, setJobsList] = useState([]);
  const [loading, setLoading] = useState(true);

  const [userSearch, setUserSearch] = useState('');
  const [jobSearch, setJobSearch] = useState('');

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [analyticsRes, usersRes, jobsRes] = await Promise.all([
        adminAPI.getAnalytics(),
        adminAPI.getUsers(),
        adminAPI.getJobs(),
      ]);

      setAnalytics(analyticsRes.data);
      setUsersList(usersRes.data);
      setJobsList(jobsRes.data);
    } catch (err) {
      console.error('Error fetching admin data:', err);
      showToast('Failed to load admin telemetry.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId) => {
    try {
      const res = await adminAPI.toggleUserStatus(userId);
      showToast(res.data.message, 'success');
      setUsersList((prev) =>
        prev.map((u) => (u.user_id === userId ? { ...u, is_active: res.data.is_active } : u))
      );
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to toggle status.';
      showToast(detail, 'error');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to permanently delete this user account?')) return;
    try {
      await adminAPI.deleteUser(userId);
      showToast('User deleted successfully.', 'info');
      setUsersList((prev) => prev.filter((u) => u.user_id !== userId));
      loadAdminData();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Deletion failed.';
      showToast(detail, 'error');
    }
  };

  const handleModerateJob = async (jobId) => {
    try {
      const res = await adminAPI.moderateJob(jobId);
      showToast(res.data.message, 'success');
      setJobsList((prev) =>
        prev.map((j) => (j.job_id === jobId ? { ...j, status: res.data.status } : j))
      );
    } catch (err) {
      showToast('Moderation action failed.', 'error');
    }
  };

  const filteredUsers = usersList.filter((u) => {
    if (!userSearch) return true;
    const q = userSearch.toLowerCase();
    return u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q) || u.role.includes(q);
  });

  const filteredJobs = jobsList.filter((j) => {
    if (!jobSearch) return true;
    const q = jobSearch.toLowerCase();
    return j.title.toLowerCase().includes(q) || j.company_name?.toLowerCase().includes(q);
  });

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold mb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> System Superadmin Portal
          </div>
          <h1 className="text-3xl font-extrabold font-heading text-white">Platform Governance & Telemetry</h1>
          <p className="text-xs text-slate-400 mt-1">Global user lifecycle oversight, job moderation, and OCR match telemetry</p>
        </div>

        <button
          onClick={loadAdminData}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-slate-300 border border-white/15"
        >
          Refresh Telemetry
        </button>
      </div>

      {/* Analytics Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 block mb-1">Registered Users</span>
          <span className="text-3xl font-extrabold font-heading text-white">{analytics?.total_users || 0}</span>
          <div className="text-[11px] text-cyan-400 mt-1">
            {analytics?.total_candidates || 0} Candidates • {analytics?.total_recruiters || 0} Recruiters
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 block mb-1">Platform Jobs</span>
          <span className="text-3xl font-extrabold font-heading text-cyan-400">{analytics?.total_jobs || 0}</span>
          <div className="text-[11px] text-emerald-400 mt-1">
            {analytics?.active_jobs || 0} Active / Moderated
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 block mb-1">Applications Handled</span>
          <span className="text-3xl font-extrabold font-heading text-purple-400">{analytics?.total_applications || 0}</span>
          <div className="text-[11px] text-slate-400 mt-1">
            {analytics?.total_resumes_processed || 0} Resumes Processed
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-white/10">
          <span className="text-xs text-slate-400 block mb-1">Avg AI Match Score</span>
          <span className="text-3xl font-extrabold font-heading text-emerald-400">
            {analytics?.average_match_score || 0}%
          </span>
          <div className="text-[11px] text-slate-400 mt-1">Across all role matrices</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10 mb-8 space-x-2">
        <button
          onClick={() => setActiveTab('analytics')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'analytics' ? 'border-emerald-400 text-emerald-300' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Activity className="w-4 h-4" /> Platform Telemetry
        </button>

        <button
          onClick={() => setActiveTab('users')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'users' ? 'border-emerald-400 text-emerald-300' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Users className="w-4 h-4" /> User Management ({usersList.length})
        </button>

        <button
          onClick={() => setActiveTab('jobs')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'jobs' ? 'border-emerald-400 text-emerald-300' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Briefcase className="w-4 h-4" /> Job Moderation ({jobsList.length})
        </button>
      </div>

      {/* ================= TAB 1: PLATFORM TELEMETRY ================= */}
      {activeTab === 'analytics' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Status Breakdown */}
          <div className="p-6 rounded-2xl glass-card border border-white/10 space-y-4">
            <h3 className="text-base font-bold font-heading text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" /> Applications by Status Stage
            </h3>
            
            <div className="space-y-3">
              {analytics?.status_distribution && Object.entries(analytics.status_distribution).map(([stage, count]) => (
                <div key={stage} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5">
                  <span className="text-xs font-semibold text-slate-300">{stage}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-cyan-400">{count} applications</span>
                    <div className="w-24 bg-white/10 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-cyan-500 h-full rounded-full"
                        style={{ width: `${Math.min(100, (count / (analytics.total_applications || 1)) * 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Jobs by Type */}
          <div className="p-6 rounded-2xl glass-card border border-white/10 space-y-4">
            <h3 className="text-base font-bold font-heading text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" /> Openings by Work Arrangement
            </h3>

            <div className="space-y-3">
              {analytics?.jobs_by_type && Object.entries(analytics.jobs_by_type).map(([jType, count]) => (
                <div key={jType} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5">
                  <span className="text-xs font-semibold text-slate-300">{jType}</span>
                  <span className="text-xs font-mono font-bold text-purple-400">{count} openings</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {/* ================= TAB 2: USERS MANAGEMENT ================= */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          <div className="relative max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={userSearch}
              onChange={(e) => setUserSearch(e.target.value)}
              placeholder="Search user by name, email, or role..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl glass-input"
            />
          </div>

          <div className="rounded-2xl glass-card border border-white/10 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-dark-850/90 border-b border-white/10 text-slate-400 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4">Account Status</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-4 text-right">Moderation Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {filteredUsers.map((u) => (
                  <tr key={u.user_id} className="hover:bg-white/[0.02]">
                    <td className="py-3 px-4">
                      <div className="font-bold text-white">{u.name}</div>
                      <div className="text-[11px] text-slate-400">{u.email}</div>
                    </td>
                    <td className="py-3 px-4 capitalize">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        u.role === 'admin' ? 'bg-emerald-500/20 text-emerald-300' :
                        u.role === 'recruiter' ? 'bg-purple-500/20 text-purple-300' : 'bg-cyan-500/20 text-cyan-300'
                      }`}>
                        {u.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        u.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${u.is_active ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        {u.is_active ? 'Active' : 'Deactivated'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {new Date(u.created_date).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {u.user_id !== user?.user_id && (
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleToggleUserStatus(u.user_id)}
                            className={`p-1.5 rounded-lg border text-xs ${
                              u.is_active
                                ? 'bg-amber-500/10 text-amber-400 border-amber-500/20 hover:bg-amber-500/20'
                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
                            }`}
                            title={u.is_active ? 'Deactivate Account' : 'Reactivate Account'}
                          >
                            <Power className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteUser(u.user_id)}
                            className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20"
                            title="Delete User Permanently"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ================= TAB 3: JOBS MODERATION ================= */}
      {activeTab === 'jobs' && (
        <div className="space-y-4">
          <div className="relative max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={jobSearch}
              onChange={(e) => setJobSearch(e.target.value)}
              placeholder="Search job opening or company..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl glass-input"
            />
          </div>

          <div className="rounded-2xl glass-card border border-white/10 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-dark-850/90 border-b border-white/10 text-slate-400 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Recruiter</th>
                  <th className="py-3 px-4">Applicants</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Moderation Toggle</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {filteredJobs.map((j) => (
                  <tr key={j.job_id} className="hover:bg-white/[0.02]">
                    <td className="py-3 px-4 font-bold text-white">{j.title}</td>
                    <td className="py-3 px-4">{j.company_name}</td>
                    <td className="py-3 px-4 text-slate-400">{j.recruiter_name}</td>
                    <td className="py-3 px-4 font-mono text-cyan-400">{j.applicant_count} candidates</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        j.status === 'active' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {j.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleModerateJob(j.job_id)}
                        className="px-3 py-1 rounded-lg text-xs bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10"
                      >
                        {j.status === 'active' ? 'Disable / Close' : 'Reopen Job'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}
