import React from 'react';
import { CareerRoadmap, PersonalizedRoadmap } from '../types';
import {
  Sparkles,
  BookOpen,
  FolderGit2,
  Award,
  Crosshair,
  Clock,
  ArrowUpRight,
  CheckCircle2,
  Calendar,
  ExternalLink,
  Target,
  Lightbulb,
  FileText
} from 'lucide-react';

interface RoadmapCardProps {
  roadmap: CareerRoadmap;
  personalizedRoadmap?: PersonalizedRoadmap;
}

export const RoadmapCard: React.FC<RoadmapCardProps> = ({ roadmap, personalizedRoadmap }) => {
  const learningRoadmap = personalizedRoadmap?.learning_roadmap;
  const prioritySkills = learningRoadmap?.priority_skills || [];
  const suggestedSequence = learningRoadmap?.suggested_sequence || [];
  const generalAdvice = learningRoadmap?.general_advice || [];

  return (
    <div className="space-y-8">
      {/* PART 2: Personalized Learning Roadmap for Missing/Weak Skills */}
      {prioritySkills.length > 0 && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-blue-300 block mb-1">
                  Personalized Growth Blueprint • {personalizedRoadmap?.display_name || 'Target Role'}
                </span>
                <h3 className="text-xl font-black tracking-tight flex items-center">
                  <Target className="w-5 h-5 text-amber-400 mr-2" />
                  Priority Skill Development & Concrete Project Tasks
                </h3>
              </div>
              <span className="hidden sm:inline-flex text-xs bg-blue-500/20 text-blue-200 border border-blue-400/30 px-3 py-1.5 rounded-full font-bold">
                {prioritySkills.length} Core Priority Gaps
              </span>
            </div>
            <p className="text-xs text-blue-200 mt-2 max-w-3xl leading-relaxed">
              Actionable learning plan specifically focused on bridging your critical missing and weak skills.
              Every task is feasible and tailored to extend your existing projects so you can demonstrate real production outcomes.
            </p>
          </div>

          {/* Priority Skill Cards */}
          <div className="grid grid-cols-1 gap-5">
            {prioritySkills.map((p, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:border-indigo-300 transition-all space-y-4"
              >
                {/* Header */}
                <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
                  <div className="flex items-center space-x-3">
                    <span className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-700 font-black text-sm flex items-center justify-center border border-indigo-200">
                      #{idx + 1}
                    </span>
                    <div>
                      <h4 className="text-lg font-black text-slate-900">{p.skill}</h4>
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                        High-Leverage Target Competency
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="inline-flex items-center text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
                      <Clock className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
                      {p.estimated_effort}
                    </span>
                  </div>
                </div>

                {/* Why It Matters */}
                <div className="bg-slate-50/70 border border-slate-100 p-3.5 rounded-xl text-xs">
                  <span className="font-bold text-slate-800 uppercase tracking-wider text-[10px] block mb-1">
                    Why This Matters for {personalizedRoadmap?.display_name || 'This Role'}:
                  </span>
                  <p className="text-slate-700 leading-relaxed">{p.why_it_matters}</p>
                </div>

                {/* Hands-On Project Task */}
                <div className="bg-indigo-50/50 border border-indigo-100 p-4 rounded-xl text-xs space-y-1.5">
                  <span className="font-bold text-indigo-950 flex items-center">
                    <FolderGit2 className="w-4 h-4 text-indigo-600 mr-1.5" />
                    Hands-On Project Task (Portfolio Extension)
                  </span>
                  <p className="text-slate-800 leading-relaxed font-medium">
                    {p.project_task}
                  </p>
                </div>

                {/* Success Criteria & Resources */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                  {/* Success Criteria */}
                  <div className="bg-emerald-50/30 border border-emerald-100/80 p-3.5 rounded-xl text-xs">
                    <span className="font-bold text-emerald-950 block mb-2 text-[11px] uppercase tracking-wider">
                      Measurable Success Criteria:
                    </span>
                    <ul className="space-y-1.5 text-emerald-900">
                      {p.success_criteria.map((crit, cIdx) => (
                        <li key={cIdx} className="flex items-start">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mr-2 shrink-0 mt-0.5" />
                          <span className="leading-snug">{crit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Curated Resources */}
                  <div className="bg-blue-50/30 border border-blue-100/80 p-3.5 rounded-xl text-xs">
                    <span className="font-bold text-blue-950 block mb-2 text-[11px] uppercase tracking-wider">
                      Recommended Learning Resources:
                    </span>
                    <div className="space-y-2">
                      {p.resources.map((res, rIdx) => (
                        <a
                          key={rIdx}
                          href={res.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-between p-2 rounded-lg bg-white border border-blue-200 hover:border-blue-400 hover:shadow-xs transition-all text-blue-900 font-medium group"
                        >
                          <span className="flex items-center truncate mr-2">
                            <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 mr-2 shrink-0">
                              {res.type}
                            </span>
                            <span className="truncate group-hover:text-blue-600">{res.title}</span>
                          </span>
                          <ExternalLink className="w-3.5 h-3.5 text-blue-400 group-hover:text-blue-600 shrink-0" />
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Suggested Timeline Sequence */}
          {suggestedSequence.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
              <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center">
                <Calendar className="w-4 h-4 text-indigo-600 mr-2" />
                Suggested Timeline & Implementation Sequence
              </h4>
              <div className="space-y-2.5">
                {suggestedSequence.map((seq, sIdx) => (
                  <div
                    key={sIdx}
                    className="flex items-start space-x-3 p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs"
                  >
                    <span className="font-mono font-bold text-indigo-600 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded text-[11px] shrink-0">
                      Phase {sIdx + 1}
                    </span>
                    <span className="text-slate-800 font-medium leading-relaxed">{seq}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* High-Level General Advice */}
          {generalAdvice.length > 0 && (
            <div className="bg-amber-50/50 rounded-2xl border border-amber-200/80 p-6 shadow-sm space-y-3">
              <h4 className="text-sm font-bold text-amber-950 uppercase tracking-wider flex items-center">
                <Lightbulb className="w-4 h-4 text-amber-600 mr-2" />
                Strategic Preparation Principles
              </h4>
              <ul className="space-y-2 text-xs text-amber-950">
                {generalAdvice.map((adv, aIdx) => (
                  <li key={aIdx} className="flex items-start">
                    <span className="font-bold text-amber-600 mr-2">•</span>
                    <span className="leading-relaxed">{adv}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Immediate Resume Tweaks */}
      {roadmap.immediate_resume_improvements.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
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
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3 text-blue-900">
            <BookOpen className="w-4 h-4 text-blue-600 mr-2" />
            Supplemental Technical Topics
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

      {/* Recommended Portfolio Projects */}
      {roadmap.project_suggestions.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h4 className="font-bold text-slate-900 text-sm flex items-center mb-3 text-purple-900">
            <FolderGit2 className="w-4 h-4 text-purple-600 mr-2" />
            Additional Standalone Architecture Projects
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
    </div>
  );
};
