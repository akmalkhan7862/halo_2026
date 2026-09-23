import React, { useState } from 'react';
import { InterviewQuestion } from '../types';
import { HelpCircle, Code, Users, Zap, Compass, FileCheck, MessageSquare, ListChecks, ChevronDown, ChevronUp } from 'lucide-react';

interface QuestionCardProps {
  question: InterviewQuestion;
  index: number;
  total: number;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({ question, index, total }) => {
  const [showExpected, setShowExpected] = useState(false);

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
        <div className="mb-3 bg-blue-50/60 border border-blue-100 rounded-lg p-3 text-xs text-blue-900 flex items-start space-x-2">
          <FileCheck className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-blue-950">Resume Grounding: </span>
            <span className="text-blue-800">{question.resume_evidence}</span>
          </div>
        </div>
      )}

      {question.follow_up_hint && (
        <div className="mb-3 bg-slate-50 border border-slate-200/80 rounded-lg p-3 text-xs text-slate-700 flex items-start space-x-2">
          <MessageSquare className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-slate-900">Interviewer Probing Hint: </span>
            <span className="text-slate-600">{question.follow_up_hint}</span>
          </div>
        </div>
      )}

      {question.expected_answer_points && question.expected_answer_points.length > 0 && (
        <div className="mb-3">
          <button
            type="button"
            onClick={() => setShowExpected(!showExpected)}
            className="flex items-center text-xs text-slate-500 hover:text-slate-800 font-medium"
          >
            <ListChecks className="w-3.5 h-3.5 mr-1 text-slate-400" />
            <span>{showExpected ? 'Hide expected criteria' : 'View key evaluation points'}</span>
            {showExpected ? <ChevronUp className="w-3.5 h-3.5 ml-1" /> : <ChevronDown className="w-3.5 h-3.5 ml-1" />}
          </button>
          {showExpected && (
            <div className="mt-2 bg-slate-50 border border-slate-100 rounded-lg p-3 text-xs">
              <span className="font-bold text-slate-700 block mb-1">Expected Key Points:</span>
              <ul className="space-y-1 text-slate-600">
                {question.expected_answer_points.map((pt, i) => (
                  <li key={i} className="flex items-start">
                    <span className="text-blue-500 mr-1.5">•</span>
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {question.skill_focus && question.skill_focus.length > 0 && (
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
