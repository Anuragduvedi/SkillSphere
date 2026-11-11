import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { UserCheck, Briefcase, ShieldCheck, Zap, ChevronUp, ChevronDown } from 'lucide-react';

export default function DemoRoleSwitcher() {
  const { user, login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(true);

  const switchPersona = async (email, password, route, name) => {
    try {
      await login(email, password);
      showToast(`Switched persona to: ${name}`, 'info');
      navigate(route);
      setCollapsed(true);
    } catch (err) {
      showToast('Could not switch persona.', 'error');
    }
  };

  return (
    <div className="fixed bottom-6 left-6 z-50">
      <div className="rounded-2xl glass-panel border border-cyan-500/40 shadow-2xl shadow-cyan-950/60 p-2.5 backdrop-blur-2xl transition-all duration-300">
        
        {/* Toggle bar */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-2 px-2.5 py-1 text-xs font-bold text-white hover:text-cyan-300 transition-colors"
        >
          <Zap className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="hidden sm:inline">Demo Persona Switcher</span>
          <span className="sm:hidden">Persona</span>
          <span className="px-1.5 py-0.5 rounded bg-white/10 text-[10px] text-cyan-300 font-mono">
            {user ? user.role.replace('_', ' ') : 'Guest'}
          </span>
          {collapsed ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {/* Expanded options */}
        {!collapsed && (
          <div className="mt-2.5 pt-2.5 border-t border-white/10 space-y-1.5 animate-in fade-in slide-in-from-bottom-2 duration-200">
            <button
              onClick={() => switchPersona('candidate@skillsphere.com', 'password123', '/dashboard', 'Alex Rivera (Candidate)')}
              className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                user?.role === 'job_seeker'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold'
                  : 'text-slate-300 hover:text-white hover:bg-white/5'
              }`}
            >
              <span className="flex items-center gap-2">
                <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
                <span>Alex Rivera (Candidate)</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono">/dashboard</span>
            </button>

            <button
              onClick={() => switchPersona('recruiter@skillsphere.com', 'password123', '/recruiter', 'Sarah Jenkins (Recruiter)')}
              className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                user?.role === 'recruiter'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold'
                  : 'text-slate-300 hover:text-white hover:bg-white/5'
              }`}
            >
              <span className="flex items-center gap-2">
                <Briefcase className="w-3.5 h-3.5 text-purple-400" />
                <span>Sarah Jenkins (Recruiter)</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono">/recruiter</span>
            </button>

            <button
              onClick={() => switchPersona('admin@skillsphere.com', 'password123', '/admin', 'Elena Rostova (Admin)')}
              className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                user?.role === 'admin'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold'
                  : 'text-slate-300 hover:text-white hover:bg-white/5'
              }`}
            >
              <span className="flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Elena Rostova (Admin)</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono">/admin</span>
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
