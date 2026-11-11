import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowLeft } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4 text-center">
      <div className="max-w-md p-8 rounded-3xl glass-panel border border-white/10 space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
          <Sparkles className="w-6 h-6" />
        </div>
        <h1 className="text-4xl font-extrabold font-heading text-white">404</h1>
        <h2 className="text-lg font-bold text-slate-200">Sector Not Found</h2>
        <p className="text-xs text-slate-400">
          The career coordinate or dashboard page you requested does not exist or has been relocated.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Return to SkillSphere Portal
        </Link>
      </div>
    </div>
  );
}
