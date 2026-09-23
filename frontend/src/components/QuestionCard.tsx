import React from 'react';
import { InterviewQuestion } from '../types';
import { HelpCircle, Code, Users, Zap, Compass } from 'lucide-react';

interface QuestionCardProps {
  question: InterviewQuestion;
  index: number;
  total: number;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({ question, index, total }) => {
  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'technical':
        return { label: 'Technical Depth', icon: <Code className="w-3.5 h-3.5 mr-1" />, color: 'bg-blue-50 text-blue-700 border-blue-200' };
      case 'project_based':
        return { label: 'Project Architecture', icon: <Zap className="w-3.5 h-3.5 mr-1" />, color: 'bg-purple-50 text-purple-700 border-purple-200' };
      case 'scenario':
        return { label: 'System Design Scenario', icon: <Compass className="w-3.5 h-3.5 mr-1" />, color: 'bg-emerald-50 text-emerald-700 border-emerald-200' };
      case 'gap_probing':
        return { label: 'Gap Probing', icon: <HelpCircle className="w-3.5 h-3.5 mr-1" />, color: 'bg-amber-50 text-amber-700 border-amber-200' };
      case 'behavioral':
      default:
        return { label: 'Behavioral & Ownership', icon: <Users className="w-3.5 h-3.5 mr-1" />, color: 'bg-slate-100 text-slate-700 border-slate-200' };
    }
  };

  const badge = getTypeBadge(question.type);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6 mb-4">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold text-slate-400">
            QUESTION {index + 1} OF {total}
          </span>
          <span className={`inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-full border ${badge.color}`}>
            {badge.icon}
            {badge.label}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600 capitalize">
            {question.difficulty}
          </span>
        </div>
      </div>

      <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-relaxed mb-3">
        {question.question_text}
      </h3>

      {question.resume_evidence && (
        <div className="mb-4 bg-slate-50 border border-slate-100 rounded-lg p-3 text-xs text-slate-600">
          <span className="font-semibold text-slate-700">Resume Grounding: </span>
          <span>{question.resume_evidence}</span>
        </div>
      )}

      {question.skill_focus.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100">
          <span className="text-xs text-slate-400 mr-1">Skills tested:</span>
          {question.skill_focus.map((skill, i) => (
            <span key={i} className="text-xs font-medium px-2 py-0.5 rounded bg-blue-50 text-blue-700">
              {skill}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
