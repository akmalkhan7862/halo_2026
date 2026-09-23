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
      {/* Profile & Score Snapshot */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Resume & Role Fit Score */}
        <div className="bg-gradient-to-br from-slate-900 to-blue-950 text-white rounded-2xl p-6 shadow-md flex flex-col justify-between">
          <div>
            <div className="text-xs uppercase font-bold text-blue-300 tracking-wider mb-1">
              Resume & Role Fit
            </div>
            <div className="text-5xl font-black">{overall}/100</div>
            <div className="text-xs text-blue-200 mt-2">
              Canonical match across skills, experience, projects, keywords, and seniority.
            </div>
          </div>

          <div className="pt-4 border-t border-blue-800/60 mt-4 flex justify-between text-xs text-blue-200">
            <span>Readiness:</span>
            <span className="font-bold uppercase text-white">
              {report.analysis.gap_summary.overall_readiness}
            </span>
          </div>
        </div>

        {/* Mock Interview Score */}
        <div className="bg-gradient-to-br from-indigo-900 to-purple-950 text-white rounded-2xl p-6 shadow-md flex flex-col justify-between">
          <div>
            <div className="text-xs uppercase font-bold text-indigo-300 tracking-wider mb-1">
              Mock Interview Performance
            </div>
            <div className="text-5xl font-black">
              {report.interview_performance?.answered_count
                ? `${report.interview_performance.overall_interview_score}/100`
                : `${interviewSession?.overall_score || 0}/100`}
            </div>
            <div className="text-xs text-indigo-200 mt-2">
              Weighted average across technical accuracy, relevance, completeness, structure, and communication.
            </div>
          </div>

          <div className="pt-4 border-t border-indigo-800/60 mt-4 flex justify-between text-xs text-indigo-200">
            <span>Questions Evaluated:</span>
            <span className="font-bold text-white">
              {report.interview_performance?.answered_count || 0} / {report.interview_performance?.question_count || 8}
            </span>
          </div>
        </div>

        {/* Candidate & Target Role Snapshot */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h4 className="font-bold text-slate-900 text-sm flex items-center mb-2">
              <UserCheck className="w-4 h-4 text-emerald-600 mr-2" />
              Candidate & Target Role
            </h4>
            <div className="space-y-2 text-xs text-slate-600">
              <div>
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Target Role:</span>
                <span className="font-semibold text-slate-900">{target.title}</span>
                <span className="text-[11px] text-slate-500 block capitalize">{target.seniority} Level • {target.domain.replace('_', ' ')}</span>
              </div>
              <div className="pt-1 border-t border-slate-100">
                <span className="text-slate-400 font-bold uppercase text-[10px] block">Candidate:</span>
                <span className="font-medium text-slate-800">{candidate.contact?.name || 'Verified Candidate'}</span>
                <span className="text-slate-500 block">{candidate.skills_count} Skills • {candidate.projects_count} Projects • {candidate.experience_count} Roles</span>
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

        {scores.overall_breakdown && scores.overall_breakdown.length > 0 && (
          <div className="mt-5 pt-4 border-t border-slate-100">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2.5">
              Key Scoring Drivers & Blocker Analysis:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {scores.overall_breakdown.map((b, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-slate-700 mr-2 font-medium">{b.reason}</span>
                  <span className={`font-mono font-bold px-2 py-0.5 rounded text-[11px] shrink-0 border ${b.impact.startsWith('+') ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'}`}>
                    {b.impact}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Mock Interview Performance Assessment (Derived strictly from actual answers) */}
      {report.interview_performance && report.interview_performance.answered_count > 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">
                Simulated Assessment • Evidence-Based
              </span>
              <h3 className="text-xl font-black text-slate-900 flex items-center mt-0.5">
                <Award className="w-5 h-5 text-amber-500 mr-2" />
                Mock Interview Performance Assessment
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Score computed strictly from evaluated answers across 5 weighted dimensions (not inflated by resume fit).
              </p>
            </div>

            <div className="flex items-center space-x-3 bg-indigo-50/60 border border-indigo-100 px-4 py-2.5 rounded-2xl">
              <div className="text-right">
                <span className="text-[10px] font-bold text-indigo-700 uppercase block">Interview Score</span>
                <span className="text-3xl font-black text-indigo-950">
                  {report.interview_performance.overall_interview_score}
                </span>
                <span className="text-xs text-indigo-600 font-semibold">/100</span>
              </div>
              <div className="text-xs text-indigo-800 border-l border-indigo-200 pl-3">
                <span className="font-bold block">
                  {report.interview_performance.answered_count} of {report.interview_performance.question_count} Answered
                </span>
                <span className="text-[11px] text-indigo-600">
                  {report.interview_performance.overall_interview_score >= 70 ? 'Competency Verified' : 'Practice Recommended'}
                </span>
              </div>
            </div>
          </div>

          {/* 5 Interview Dimensions */}
          <div>
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-3">
              Weighted Dimension Breakdown:
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/70">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Technical Accuracy (35%)</span>
                <div className="text-xl font-extrabold text-slate-900 mt-1">
                  {report.interview_performance.dimension_scores.technical_accuracy}/100
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/70">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Relevance (20%)</span>
                <div className="text-xl font-extrabold text-slate-900 mt-1">
                  {report.interview_performance.dimension_scores.relevance}/100
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/70">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Completeness (20%)</span>
                <div className="text-xl font-extrabold text-slate-900 mt-1">
                  {report.interview_performance.dimension_scores.completeness}/100
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/70">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Structure & Clarity (15%)</span>
                <div className="text-xl font-extrabold text-slate-900 mt-1">
                  {report.interview_performance.dimension_scores.structure_and_clarity}/100
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/70">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Communication (10%)</span>
                <div className="text-xl font-extrabold text-slate-900 mt-1">
                  {report.interview_performance.dimension_scores.communication}/100
                </div>
              </div>
            </div>
          </div>

          {/* Answer Quality Distribution */}
          <div className="flex flex-wrap items-center gap-2 pt-1 pb-1">
            <span className="text-xs font-bold text-slate-500 uppercase mr-1">Answer Quality Distribution:</span>
            <span className="px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
              Strong: {report.interview_performance.score_distribution.strong || 0}
            </span>
            <span className="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-xs font-semibold">
              Good: {report.interview_performance.score_distribution.good || 0}
            </span>
            <span className="px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold">
              Moderate: {report.interview_performance.score_distribution.moderate || 0}
            </span>
            <span className="px-2.5 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
              Weak: {report.interview_performance.score_distribution.weak || 0}
            </span>
          </div>

          {/* Key Strengths & Weaknesses Grids */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="bg-emerald-50/50 border border-emerald-100 p-4 rounded-xl">
              <span className="font-bold text-emerald-900 flex items-center mb-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 mr-1.5" />
                Demonstrated Interview Strengths
              </span>
              <ul className="space-y-1.5 text-emerald-800">
                {report.interview_performance.key_strengths.map((s, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="mr-1.5">•</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-amber-50/50 border border-amber-100 p-4 rounded-xl">
              <span className="font-bold text-amber-900 flex items-center mb-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 mr-1.5" />
                Observed Gaps in Answers
              </span>
              <ul className="space-y-1.5 text-amber-800">
                {report.interview_performance.key_weaknesses.map((w, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="mr-1.5">•</span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Actionable Recommendations from Interview */}
          {report.interview_performance.recommendations.length > 0 && (
            <div className="bg-blue-50/40 border border-blue-100 p-4 rounded-xl text-xs space-y-2">
              <span className="font-bold text-blue-950 flex items-center">
                <Sparkles className="w-4 h-4 text-blue-600 mr-1.5" />
                Interview Coaching Recommendations for {target.title}
              </span>
              <ul className="space-y-1 text-blue-900">
                {report.interview_performance.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-blue-500 mr-1.5">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Communication Feedback */}
          {report.interview_performance.communication_feedback && (
            <div className="bg-slate-50 border border-slate-200/80 p-4 rounded-xl text-xs space-y-2">
              <span className="font-bold text-slate-800 uppercase tracking-wider text-[11px] block">
                Technical Communication & Articulation Feedback:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div>
                  <span className="font-semibold text-slate-700 block mb-1">Observed Clarity:</span>
                  <ul className="space-y-1 text-slate-600">
                    {report.interview_performance.communication_feedback.strengths.map((cs, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-emerald-500 mr-1.5">•</span>
                        <span>{cs}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <span className="font-semibold text-slate-700 block mb-1">Articulation Refinement:</span>
                  <ul className="space-y-1 text-slate-600">
                    {report.interview_performance.communication_feedback.improvements.map((ci, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-amber-500 mr-1.5">•</span>
                        <span>{ci}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : interviewSession && interviewSession.summary_feedback ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
            <h3 className="font-bold text-slate-900 text-base flex items-center">
              <Award className="w-5 h-5 text-amber-500 mr-2" />
              Mock Interview Performance Recap
            </h3>
            <span className="text-xs font-bold uppercase px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              Score: {interviewSession.overall_score || 0}/100
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
      ) : null}

      {/* Dynamic Personalized Career Roadmap */}
      <div>
        <div className="flex items-center space-x-2 mb-4">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-black text-slate-900 tracking-tight">
            Personalized Career Growth Roadmap
          </h3>
        </div>
        <RoadmapCard
          roadmap={report.roadmap}
          personalizedRoadmap={report.learning_roadmap || report.analysis?.learning_roadmap}
        />
      </div>
    </div>
  );
};
