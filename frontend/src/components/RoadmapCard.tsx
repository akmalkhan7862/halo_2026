import React from 'react';
import { CareerRoadmap } from '../types';
import {
  Sparkles,
  BookOpen,
  FolderGit2,
  Award,
  Crosshair,
  Clock,
  ArrowUpRight
} from 'lucide-react';

interface RoadmapCardProps {
  roadmap: CareerRoadmap;
}

export const RoadmapCard: React.FC<RoadmapCardProps> = ({ roadmap }) => {
  return (
    <div className="space-y-6">
      {/* Immediate Resume Tweaks */}
      {roadmap.immediate_resume_improvements.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3 text-emerald-800">
            <Sparkles className="w-4 h-4 text-emerald-600 mr-2" />
            Immediate High-Impact Resume Tweaks
          </h4>
          <ul className="space-y-2 text-xs">
            {roadmap.immediate_resume_improvements.map((item, idx) => (
              <li key={idx} className="flex items-start bg-emerald-50/40 p-2.5 rounded-lg border border-emerald-100">
                <span className="font-bold text-emerald-700 mr-2 text-sm shrink-0">#{idx + 1}</span>
                <span className="text-slate-800 leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Short-Term Learning Actions */}
      {roadmap.short_term_learning_actions.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3 text-blue-900">
            <BookOpen className="w-4 h-4 text-blue-600 mr-2" />
            Short-Term Learning Actions
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {roadmap.short_term_learning_actions.map((act, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg p-3 bg-slate-50/50">
                <div className="flex items-center justify-between mb-1.5">
                  <h5 className="font-bold text-slate-900 text-sm">{act.topic}</h5>
                  <span className="flex items-center text-[10px] font-semibold text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                    <Clock className="w-3 h-3 mr-1" />
                    {act.timeframe}
                  </span>
                </div>
                <p className="text-slate-600 mb-2 leading-relaxed">{act.learning_objective}</p>
                {act.recommended_resources.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {act.recommended_resources.map((res, rIdx) => (
                      <span key={rIdx} className="bg-white border border-slate-200 px-1.5 py-0.5 rounded text-[10px] text-blue-700 font-medium">
                        {res}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Project Suggestions */}
      {roadmap.project_suggestions.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3 text-purple-900">
            <FolderGit2 className="w-4 h-4 text-purple-600 mr-2" />
            Portfolio Projects to Bridge Critical Gaps
          </h4>
          <div className="space-y-3 text-xs">
            {roadmap.project_suggestions.map((proj, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg p-3.5 bg-slate-50/40">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <h5 className="font-bold text-slate-900 text-sm">{proj.project_title}</h5>
                  <div className="flex flex-wrap gap-1">
                    {proj.technologies.map((t, tIdx) => (
                      <span key={tIdx} className="bg-purple-100 text-purple-800 font-medium px-2 py-0.5 rounded text-[10px]">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
                <p className="text-slate-700 mb-2 leading-relaxed">{proj.problem_statement}</p>
                <div className="bg-white p-2 rounded border border-slate-200 text-slate-600">
                  <span className="font-semibold text-slate-800">Target Measurable Outcomes: </span>
                  {proj.demonstrated_outcomes.join('; ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Certifications & Interview Focus */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {roadmap.certification_suggestions.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3 text-amber-900">
              <Award className="w-4 h-4 text-amber-600 mr-2" />
              Strategic Certifications
            </h4>
            <ul className="space-y-2 text-xs">
              {roadmap.certification_suggestions.map((c, idx) => (
                <li key={idx} className="border border-slate-200 p-2.5 rounded-lg bg-slate-50/50">
                  <div className="font-bold text-slate-900">{c.certification_name}</div>
                  <div className="text-[11px] text-slate-500 font-medium">{c.issuer}</div>
                  <div className="text-slate-600 mt-1 text-[11px]">{c.relevance}</div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {roadmap.interview_preparation_focus_areas.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3 text-indigo-900">
              <Crosshair className="w-4 h-4 text-indigo-600 mr-2" />
              Interview Preparation Focus Areas
            </h4>
            <ul className="space-y-2 text-xs">
              {roadmap.interview_preparation_focus_areas.map((area, idx) => (
                <li key={idx} className="flex items-start bg-indigo-50/40 p-2.5 rounded-lg border border-indigo-100">
                  <span className="text-indigo-600 font-bold mr-2">•</span>
                  <span className="text-slate-800 leading-relaxed">{area}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
