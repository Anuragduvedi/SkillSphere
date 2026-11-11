import React, { useState, useEffect } from 'react';
import { 
  Briefcase, 
  Search, 
  MapPin, 
  Building2, 
  Sparkles, 
  Loader2, 
  ArrowRight, 
  CheckCircle2, 
  Filter 
} from 'lucide-react';
import { jobsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import RadialGauge from '../components/RadialGauge';
import JobDetailsModal from '../components/JobDetailsModal';
import MatchAnalysisModal from '../components/MatchAnalysisModal';

export default function JobDetailsPage() {
  const { user } = useAuth();
  
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [jobType, setJobType] = useState('');
  const [skill, setSkill] = useState('');

  const [selectedJob, setSelectedJob] = useState(null);
  const [analysisJob, setAnalysisJob] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = {};
      if (keyword) params.keyword = keyword;
      if (location) params.location = location;
      if (jobType) params.job_type = jobType;
      if (skill) params.skill = skill;

      const res = await jobsAPI.list(params);
      setJobs(res.data);
    } catch (err) {
      console.error('Failed to load jobs', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="mb-8 text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
          <Briefcase className="w-3.5 h-3.5 text-cyan-400" /> Live Career Matrix
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold font-heading text-white">
          Explore Frontier Tech Openings
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Discover vetted engineering, AI, and design openings matched directly against candidate skill vectors.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-2xl glass-card border border-white/10 mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Keyword or title..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl glass-input"
            />
          </div>

          <div className="relative">
            <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Location or Remote..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl glass-input"
            />
          </div>

          <select
            value={jobType}
            onChange={(e) => setJobType(e.target.value)}
            className="w-full px-3 py-2 text-xs rounded-xl glass-input bg-dark-850"
          >
            <option value="">All Job Types</option>
            <option value="Full-time">Full-time</option>
            <option value="Remote">Remote</option>
            <option value="Contract">Contract</option>
            <option value="Part-time">Part-time</option>
          </select>

          <div className="flex gap-2">
            <input
              type="text"
              value={skill}
              onChange={(e) => setSkill(e.target.value)}
              placeholder="Skill (e.g. React, Python)"
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

      {/* Jobs Grid */}
      {loading ? (
        <div className="py-20 text-center space-y-3">
          <Loader2 className="w-10 h-10 text-cyan-400 animate-spin mx-auto" />
          <p className="text-xs text-slate-400">Loading opening matrix...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="p-12 text-center rounded-2xl glass-card">
          <Briefcase className="w-12 h-12 text-slate-500 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No openings found</h3>
          <p className="text-xs text-slate-400">Try adjusting your search criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {jobs.map((job) => (
            <div
              key={job.job_id}
              className="p-6 rounded-2xl glass-card border border-white/10 flex flex-col justify-between group hover:border-cyan-500/40"
            >
              <div>
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

                  {job.match_score !== null && job.match_score !== undefined && (
                    <div 
                      onClick={() => setAnalysisJob(job)}
                      className="cursor-pointer hover:scale-105 transition-transform"
                      title="Click for full breakdown"
                    >
                      <RadialGauge score={job.match_score} size={64} strokeWidth={6} />
                    </div>
                  )}
                </div>

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

                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">
                  {job.description}
                </p>

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

              <div className="flex items-center justify-between pt-4 border-t border-white/10">
                <button
                  onClick={() => setSelectedJob(job)}
                  className="text-xs font-semibold text-slate-400 hover:text-white flex items-center gap-1"
                >
                  View Details &rarr;
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setAnalysisJob(job)}
                    className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-cyan-300 flex items-center gap-1 transition-colors"
                  >
                    <Sparkles className="w-3.5 h-3.5" /> Match AI
                  </button>

                  <button
                    onClick={() => setSelectedJob(job)}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-500/20 hover:brightness-110 transition-all"
                  >
                    Apply Now
                  </button>
                </div>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      <JobDetailsModal
        isOpen={Boolean(selectedJob)}
        onClose={() => setSelectedJob(null)}
        job={selectedJob}
        onOpenMatchAnalysis={(j) => setAnalysisJob(j)}
        onApplied={() => fetchJobs()}
      />

      <MatchAnalysisModal
        isOpen={Boolean(analysisJob)}
        onClose={() => setAnalysisJob(null)}
        job={analysisJob}
        onApplied={() => fetchJobs()}
      />

    </div>
  );
}
