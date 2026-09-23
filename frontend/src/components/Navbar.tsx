import React from 'react';
import { useApp } from '../context/AppContext';
import { Briefcase, RotateCcw, ShieldCheck, Target, FileText } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { resetAll } = useApp();

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={resetAll}>
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">
              Resume Intelligence & Mock Interview
            </h1>
            <p className="text-xs text-slate-500">
              Deterministic Taxonomies (ESCO / O*NET) • Dynamic AI Interviews • No Manual JD
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5 mr-1" />
            12 Curated ESCO & O*NET Roles
          </span>

          <button
            onClick={resetAll}
            className="flex items-center text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-md transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
            New Session
          </button>
        </div>
      </div>
    </header>
  );
};
