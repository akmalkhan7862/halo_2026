import React from 'react';
import { useApp } from '../context/AppContext';
import {
  FileText,
  Target,
  BarChart3,
  MessageSquare,
  Award,
  ArrowRight,
  ShieldCheck,
  Zap,
  CheckCircle2
} from 'lucide-react';

export const HomePage: React.FC = () => {
  const { setStep } = useApp();

  return (
    <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8 space-y-12">
      <div className="text-center space-y-4">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
          <ShieldCheck className="w-3.5 h-3.5 mr-1.5" />
          Production-Ready Architecture
        </span>
        <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
          Resume Intelligence & <br />
          <span className="text-blue-600">Dynamic Mock Interview</span> Platform
        </h1>
        <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Bridge the gap between your resume and target job requirements with deterministic ESCO/O*NET
          taxonomies, explainable 5-factor scoring, and dynamic AI mock interviews.
        </p>

        <div className="pt-4 flex justify-center">
          <button
            onClick={() => setStep('upload')}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm px-8 py-3.5 rounded-xl shadow-lg transition-all flex items-center"
          >
            <span>Start Resume Evaluation</span>
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base mb-2">
            Deterministic Extraction & Taxonomies
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Extracts skills, experience, and projects using PyMuPDF, python-docx, and spaCy.
            Maps all entities to canonical ESCO and O*NET IDs with evidence citations.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-4">
            <BarChart3 className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base mb-2">
            Explainable 5-Factor Match Engine
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            No black-box percentages. Receive itemized positive and negative point breakdowns
            across Skill Coverage, Experience, Project Depth, Keywords, and Seniority.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
            <MessageSquare className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base mb-2">
            Dynamic, Resume-Grounded Interviews
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            7–10 rigorous technical and scenario questions generated dynamically from your actual
            resume and identified JD gaps. Receive instant feedback and adaptive follow-ups.
          </p>
        </div>
      </div>
    </div>
  );
};
