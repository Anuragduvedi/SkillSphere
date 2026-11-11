import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { 
  Sparkles, 
  ArrowRight, 
  Loader2, 
  Lock, 
  Mail, 
  UserCheck, 
  Briefcase, 
  ShieldCheck 
} from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      showToast('Please fill in both email and password.', 'warning');
      return;
    }

    setLoading(true);
    try {
      const user = await login(email, password);
      showToast(`Welcome back, ${user.name}!`, 'success');
      
      // Navigate to role appropriate dashboard
      if (user.role === 'recruiter') {
        navigate('/recruiter');
      } else if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
      const detail = err.response?.data?.detail || 'Invalid email or password.';
      showToast(detail, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
  };

  return (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center p-4 relative overflow-hidden">
      
      {/* Background Neon Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-12 rounded-3xl glass-panel border border-white/20 shadow-2xl shadow-cyan-950/40 overflow-hidden relative z-10">
        
        {/* Left Side: Brand Visual Info */}
        <div className="lg:col-span-5 p-8 md:p-10 bg-gradient-to-br from-cyan-950/40 via-dark-850 to-purple-950/40 border-b lg:border-b-0 lg:border-r border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-8">
              <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400" />
              </div>
              <span className="font-heading font-extrabold text-xl text-white">
                Skill<span className="text-cyan-400">Sphere</span>
              </span>
            </div>

            <h2 className="text-2xl font-bold font-heading text-white mb-3">
              Career & Job Intelligence Portal
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed mb-6">
              Sign in to manage resume OCR parses, evaluate explainable role match scores, or manage candidate ATS pipelines.
            </p>

            {/* Demo Quick Logins */}
            <div className="space-y-3">
              <p className="text-[11px] uppercase tracking-wider font-semibold text-cyan-400">
                1-Click Evaluator Demo Accounts:
              </p>
              
              <button
                type="button"
                onClick={() => handleQuickLogin('candidate@skillsphere.com', 'password123')}
                className="w-full text-left p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-slate-300 hover:text-white flex items-center justify-between transition-colors"
              >
                <span className="flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-cyan-400" />
                  <span>Job Seeker: <strong>Alex Rivera</strong></span>
                </span>
                <span className="text-[10px] text-cyan-300 font-mono">Fill</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('recruiter@skillsphere.com', 'password123')}
                className="w-full text-left p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-slate-300 hover:text-white flex items-center justify-between transition-colors"
              >
                <span className="flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-purple-400" />
                  <span>Recruiter: <strong>Sarah Jenkins</strong></span>
                </span>
                <span className="text-[10px] text-purple-300 font-mono">Fill</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('admin@skillsphere.com', 'password123')}
                className="w-full text-left p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-slate-300 hover:text-white flex items-center justify-between transition-colors"
              >
                <span className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Admin: <strong>Elena Rostova</strong></span>
                </span>
                <span className="text-[10px] text-emerald-300 font-mono">Fill</span>
              </button>
            </div>
          </div>

          <div className="pt-6 text-[11px] text-slate-500">
            Protected by bcrypt hashing & JWT stateless authentication.
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="lg:col-span-7 p-8 md:p-12 flex flex-col justify-center">
          <div className="mb-6">
            <h3 className="text-2xl font-bold font-heading text-white">Sign In</h3>
            <p className="text-xs text-slate-400 mt-1">Enter your credentials to access your portal session</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl glass-input"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl glass-input"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/25 hover:brightness-110 flex items-center justify-center gap-2 transition-all"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              Sign In to SkillSphere
            </button>
          </form>

          <p className="text-center text-xs text-slate-400 mt-6">
            Don't have an account yet?{' '}
            <Link to="/register" className="text-cyan-400 hover:text-cyan-300 font-semibold underline">
              Create an account
            </Link>
          </p>
        </div>

      </div>

    </div>
  );
}
