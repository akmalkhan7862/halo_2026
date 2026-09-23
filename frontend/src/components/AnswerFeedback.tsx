import React from 'react';
import { AnswerEvaluation } from '../types';
import { CheckCircle2, AlertCircle, Sparkles, MessageCircleQuestion } from 'lucide-react';

interface AnswerFeedbackProps {
  evaluation: AnswerEvaluation;
}

export const AnswerFeedback: React.FC<AnswerFeedbackProps> = ({ evaluation }) => {
  const getVerdictStyle = (v: string) => {
    switch (v) {
      case 'exceptional':
        return 'bg-emerald-50 text-emerald-800 border-emerald-300';
      case 'good':
        return 'bg-blue-50 text-blue-800 border-blue-300';
      case 'adequate':
        return 'bg-amber-50 text-amber-800 border-amber-300';
      default:
        return 'bg-rose-50 text-rose-800 border-rose-300';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6 mb-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
        <div>
          <h4 className="font-bold text-slate-900 text-sm sm:text-base flex items-center">
            <Sparkles className="w-4 h-4 text-blue-600 mr-2" />
            AI Interviewer Evaluation
          </h4>
          <span className="text-xs text-slate-500">
            Assessed on accuracy, depth, concrete examples, and communication clarity
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <span
            className={`text-xs font-bold uppercase px-2.5 py-1 rounded-full border ${getVerdictStyle(
              evaluation.verdict
            )}`}
          >
            {evaluation.verdict}
          </span>
          <div className="text-right">
            <span className="text-2xl font-black text-slate-900">{evaluation.score}</span>
            <span className="text-xs text-slate-400 font-medium">/100</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mb-4">
        {evaluation.strengths.length > 0 && (
          <div className="bg-emerald-50/50 border border-emerald-100 rounded-lg p-3">
            <span className="font-bold text-emerald-900 flex items-center mb-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mr-1" />
              Observed Strengths
            </span>
            <ul className="space-y-1 text-emerald-800">
              {evaluation.strengths.map((str, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="mr-1.5">•</span>
                  <span>{str}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {evaluation.weaknesses.length > 0 && (
          <div className="bg-amber-50/50 border border-amber-100 rounded-lg p-3">
            <span className="font-bold text-amber-900 flex items-center mb-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600 mr-1" />
              Areas of Weakness
            </span>
            <ul className="space-y-1 text-amber-800">
              {evaluation.weaknesses.map((w, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="mr-1.5">•</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {evaluation.missing_points.length > 0 && (
        <div className="bg-slate-50 border border-slate-200/70 rounded-lg p-3 text-xs mb-4">
          <span className="font-bold text-slate-700">Missing Key Points:</span>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {evaluation.missing_points.map((pt, idx) => (
              <span key={idx} className="bg-white border border-slate-200 px-2 py-0.5 rounded text-slate-700">
                {pt}
              </span>
            ))}
          </div>
        </div>
      )}

      {evaluation.suggested_improvement && (
        <div className="bg-blue-50/60 border border-blue-100 rounded-lg p-3 text-xs text-blue-950 mb-3">
          <span className="font-bold text-blue-900">Coaching Advice: </span>
          <span>{evaluation.suggested_improvement}</span>
        </div>
      )}

      {evaluation.follow_up_question && (
        <div className="bg-indigo-50/60 border border-indigo-200 rounded-lg p-3 text-xs text-indigo-950">
          <span className="font-bold text-indigo-900 flex items-center mb-1">
            <MessageCircleQuestion className="w-4 h-4 text-indigo-600 mr-1.5" />
            Adaptive Follow-Up Question:
          </span>
          <p className="italic font-medium text-indigo-900">{evaluation.follow_up_question}</p>
        </div>
      )}
    </div>
  );
};
