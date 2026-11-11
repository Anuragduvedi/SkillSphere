import React from 'react';
import { Sparkles, Heart, Terminal, Database, Cpu, ShieldAlert } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-dark-900/90 backdrop-blur-md pt-12 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          {/* Col 1 */}
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-cyan-400" />
              </div>
              <span className="font-heading font-bold text-lg text-white">
                Skill<span className="text-cyan-400">Sphere</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              Enterprise career intelligence & hiring platform driven by OCR resume extraction and deep skill gap analytics.
            </p>
          </div>

          {/* Col 2 */}
          <div className="space-y-3">
            <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-300">Platform Features</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><span className="hover:text-cyan-400 transition-colors cursor-pointer">Optical Character Recognition</span></li>
              <li><span className="hover:text-cyan-400 transition-colors cursor-pointer">Explainable Skill Matching</span></li>
              <li><span className="hover:text-cyan-400 transition-colors cursor-pointer">ATS Kanban Pipeline</span></li>
              <li><span className="hover:text-cyan-400 transition-colors cursor-pointer">Role-Based Access Control</span></li>
            </ul>
          </div>

          {/* Col 3 */}
          <div className="space-y-3">
            <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-300">Architecture Specs</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="flex items-center gap-2"><Cpu className="w-3.5 h-3.5 text-cyan-400" /> Python FastAPI + SQLAlchemy</li>
              <li className="flex items-center gap-2"><Terminal className="w-3.5 h-3.5 text-purple-400" /> React 18 + Vite + Tailwind</li>
              <li className="flex items-center gap-2"><Database className="w-3.5 h-3.5 text-emerald-400" /> PostgreSQL / SQLite Normalized</li>
              <li className="flex items-center gap-2"><Sparkles className="w-3.5 h-3.5 text-amber-400" /> GSAP & Framer Motion</li>
            </ul>
          </div>

          {/* Col 4 */}
          <div className="space-y-3">
            <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-300">Candidate Quick Guide</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload your PDF, JPG, or PNG resume (max 10MB). Review the OCR-extracted skills and experience, then test your profile against real job openings with immediate explainable match scores.
            </p>
          </div>

        </div>

        <div className="border-t border-white/5 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <div>
            &copy; 2026 SkillSphere Career Portal. Built for Full-Stack Engineering Assessment.
          </div>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              API Online & Synced
            </span>
          </div>
        </div>

      </div>
    </footer>
  );
}
