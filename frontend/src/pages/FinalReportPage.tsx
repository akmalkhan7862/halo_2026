import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { getFinalReport, getReportDownloadUrl } from '../api/client';
import { RoadmapCard } from '../components/RoadmapCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Download,
  Award,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  FileText,
  UserCheck,
  Target
} from 'lucide-react';

export const FinalReportPage: React.FC = () => {
  const { analysis, report, setReport, resetAll } = useApp();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!report && analysis) {
      setLoading(true);
      getFinalReport(analysis.id)
        .then((data) => setReport(data))
        .catch((err) => console.error('Failed to load final report:', err))
        .finally(() => setLoading(false));
    }
  }, [analysis, report, setReport]);

  if (loading || !report) {
    return (
      <div className="max-w-4xl mx-auto py-16">
        <LoadingSpinner
          message="Synthesizing Consolidated Intelligence Report & Roadmap..."
          submessage="Integrating candidate profile, skill match provenance, interview evaluations, and targeted learning path."
        />
      </div>
    );
  }

  const scores = report.analysis.scores;
  const overall = Math.round(scores.overall_score);
  const candidate = report.candidate_profile;
  const target = report.target_job;
  const interviewSession = report.interview_session;

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Top Banner & PDF Download */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">
            Step 5 of 5 • Final Assessment
          </span>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Interview Readiness & Career Roadmap Report
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Target Role: <span className="font-semibold text-slate-800">{target.title}</span> •
            Generated: {report.generated_at.slice(0, 10)}
          </p>
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <a
            href={getReportDownloadUrl(report.analysis_id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 md:flex-initial bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-5 py-3 rounded-xl shadow-md transition-all flex items-center justify-center"
          >
            <Download className="w-4 h-4 mr-2" />
            <span>Download Official PDF Report</span>
          </a>

          <button
            onClick={resetAll}
            className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs p-3 rounded-xl transition-colors"
            title="Start New Session"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Profile & Score Snapshot */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Overall Score */}
        <div className="bg-gradient-to-br from-blue-900 to-indigo-950 text-white rounded-2xl p-6 shadow-md flex flex-col justify-between">
          <div>
            <div className="text-xs uppercase font-bold text-blue-300 tracking-wider mb-1">
              Overall Job Match
            </div>
            <div className="text-5xl font-black">{overall}/100</div>
            <div className="text-xs text-blue-200 mt-2">
              Weighted composite across skill match, experience, projects, keywords, and seniority.
            </div>
          </div>

          <div className="pt-4 border-t border-blue-800/60 mt-4 flex justify-between text-xs text-blue-200">
            <span>Readiness:</span>
            <span className="font-bold uppercase text-white">
              {report.analysis.gap_summary.overall_readiness}
            </span>
          </div>
        </div>

        {/* Candidate Snapshot */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3">
              <UserCheck className="w-4 h-4 text-emerald-600 mr-2" />
              Candidate Profile
            </h4>
            <div className="space-y-2 text-xs text-slate-600">
              <div>
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Name:</span>
                <span className="font-semibold text-slate-800">{candidate.contact?.name || 'Verified Candidate'}</span>
              </div>
              <div>
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Email:</span>
                <span>{candidate.contact?.email || 'N/A'}</span>
              </div>
              <div>
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Extracted Metrics:</span>
                <span>{candidate.skills_count} Skills • {candidate.projects_count} Projects • {candidate.experience_count} Roles</span>
              </div>
            </div>
          </div>
        </div>

        {/* Target Job Snapshot */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3">
              <Target className="w-4 h-4 text-blue-600 mr-2" />
              Target Position
            </h4>
            <div className="space-y-2 text-xs text-slate-600">
              <div>
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Title:</span>
                <span className="font-semibold text-slate-800">{target.title}</span>
              </div>
              <div>
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Company:</span>
                <span>{target.company || 'Industry Benchmark'}</span>
              </div>
              <div>
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Level & Domain:</span>
                <span className="capitalize">{target.seniority} Level • {target.domain.replace('_', ' ')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subscores Overview */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h3 className="font-bold text-slate-900 text-sm mb-4 uppercase tracking-wider">
          Explainable Assessment Breakdown
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Skill Match (35%)</span>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{Math.round(scores.skill_match_score.score)}/100</div>
          </div>
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Experience (20%)</span>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{Math.round(scores.experience_score.score)}/100</div>
          </div>
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Projects (20%)</span>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{Math.round(scores.project_score.score)}/100</div>
          </div>
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Keywords (15%)</span>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{Math.round(scores.keyword_score.score)}/100</div>
          </div>
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Seniority (10%)</span>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{Math.round(scores.seniority_score.score)}/100</div>
          </div>
        </div>
      </div>

      {/* Mock Interview Summary (if available) */}
      {interviewSession && interviewSession.summary_feedback && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
            <h3 className="font-bold text-slate-900 text-base flex items-center">
              <Award className="w-5 h-5 text-amber-500 mr-2" />
              Mock Interview Performance Recap
            </h3>
            <span className="text-xs font-bold uppercase px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              Score: {interviewSession.overall_score || 80}/100
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="bg-emerald-50/40 border border-emerald-100 p-3.5 rounded-xl">
              <span className="font-bold text-emerald-900 block mb-1">Key Interview Strengths:</span>
              <ul className="space-y-1 text-emerald-800">
                {(interviewSession.summary_feedback.key_strengths || []).map((s: string, idx: number) => (
                  <li key={idx}>• {s}</li>
                ))}
              </ul>
            </div>

            <div className="bg-amber-50/40 border border-amber-100 p-3.5 rounded-xl">
              <span className="font-bold text-amber-900 block mb-1">Areas to Sharpen:</span>
              <ul className="space-y-1 text-amber-800">
                {(interviewSession.summary_feedback.areas_to_improve || []).map((w: string, idx: number) => (
                  <li key={idx}>• {w}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Dynamic Personalized Career Roadmap */}
      <div>
        <div className="flex items-center space-x-2 mb-4">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-black text-slate-900 tracking-tight">
            Personalized Career Growth Roadmap
          </h3>
        </div>
        <RoadmapCard roadmap={report.roadmap} />
      </div>
    </div>
  );
};
