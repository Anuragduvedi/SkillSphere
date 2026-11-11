import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Briefcase, 
  User, 
  LogOut, 
  ShieldCheck, 
  FileText, 
  Layers, 
  Menu, 
  X,
  Compass,
  Sparkles
} from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-40 w-full backdrop-blur-xl bg-dark-900/70 border-b border-white/10 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-600 to-purple-600 p-[1px] shadow-neon-cyan/20 group-hover:shadow-neon-cyan transition-all duration-300">
              <div className="w-full h-full bg-dark-900 rounded-xl flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400 group-hover:rotate-12 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-extrabold tracking-tight font-heading text-white">
                  Skill<span className="text-cyan-400">Sphere</span>
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                  v2.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block tracking-wider uppercase font-medium">Career Intelligence Portal</p>
            </div>
          </Link>

          {/* Center Navigation Links */}
          <div className="hidden md:flex items-center gap-1">
            <Link
              to="/jobs"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive('/jobs')
                  ? 'text-cyan-300 bg-white/5 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-white/5'
              }`}
            >
              Explore Openings
            </Link>

            {user?.role === 'job_seeker' && (
              <>
                <Link
                  to="/dashboard"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive('/dashboard')
                      ? 'text-cyan-300 bg-white/5 border border-cyan-500/30'
                      : 'text-slate-300 hover:text-white hover:bg-white/5'
                  }`}
                >
                  Candidate Portal
                </Link>
              </>
            )}

            {user?.role === 'recruiter' && (
              <Link
                to="/recruiter"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive('/recruiter')
                    ? 'text-purple-300 bg-white/5 border border-purple-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                }`}
              >
                Recruiter ATS
              </Link>
            )}

            {user?.role === 'admin' && (
              <Link
                to="/admin"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive('/admin')
                    ? 'text-emerald-300 bg-white/5 border border-emerald-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                }`}
              >
                Admin Center
              </Link>
            )}
          </div>

          {/* Right User Actions */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3 pl-3 border-l border-white/10">
                <div className="flex flex-col text-right">
                  <span className="text-sm font-semibold text-white truncate max-w-[140px]">{user.name}</span>
                  <span className="text-[11px] capitalize text-slate-400 font-mono flex items-center justify-end gap-1">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      user.role === 'admin' ? 'bg-emerald-400' : user.role === 'recruiter' ? 'bg-purple-400' : 'bg-cyan-400'
                    }`} />
                    {user.role.replace('_', ' ')}
                  </span>
                </div>
                
                <button
                  onClick={handleLogout}
                  title="Sign Out"
                  className="p-2.5 rounded-xl border border-white/10 bg-white/5 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 hover:bg-rose-500/10 transition-all"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-all"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-xl text-sm font-semibold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 hover:brightness-110 transition-all"
                >
                  Join Portal
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu trigger */}
          <div className="flex md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg bg-white/5 border border-white/10 text-slate-300"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-white/10 bg-dark-900/95 backdrop-blur-2xl px-4 py-6 space-y-4">
          <Link
            to="/jobs"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-slate-300 hover:text-white"
          >
            Explore Jobs
          </Link>
          {user?.role === 'job_seeker' && (
            <Link
              to="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-cyan-400 hover:text-cyan-300"
            >
              Candidate Portal
            </Link>
          )}
          {user?.role === 'recruiter' && (
            <Link
              to="/recruiter"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-purple-400 hover:text-purple-300"
            >
              Recruiter ATS
            </Link>
          )}
          {user?.role === 'admin' && (
            <Link
              to="/admin"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-emerald-400 hover:text-emerald-300"
            >
              Admin Dashboard
            </Link>
          )}
          {user ? (
            <div className="pt-4 border-t border-white/10 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-white">{user.name}</p>
                <p className="text-xs text-slate-400">{user.role}</p>
              </div>
              <button
                onClick={() => { setMobileMenuOpen(false); handleLogout(); }}
                className="px-3 py-1.5 rounded-lg text-xs bg-rose-500/20 text-rose-300 border border-rose-500/30"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="pt-4 border-t border-white/10 flex gap-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2 text-sm bg-white/5 rounded-lg"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2 text-sm bg-cyan-500 text-black font-semibold rounded-lg"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
}
