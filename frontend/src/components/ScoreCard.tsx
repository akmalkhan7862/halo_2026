import React, { useState } from 'react';
import { ComponentScore } from '../types';
import { ChevronDown, ChevronUp, AlertCircle, CheckCircle2 } from 'lucide-react';

interface ScoreCardProps {
  title: string;
  scoreData: ComponentScore;
  icon?: React.ReactNode;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ title, scoreData, icon }) => {
  const [expanded, setExpanded] = useState(false);
  const score = Math.round(scoreData.score);

  const getScoreColor = (val: number) => {
    if (val >= 80) return 'text-emerald-600 border-emerald-500 bg-emerald-50';
    if (val >= 60) return 'text-blue-600 border-blue-500 bg-blue-50';
    if (val >= 45) return 'text-amber-600 border-amber-500 bg-amber-50';
    return 'text-rose-600 border-rose-500 bg-rose-50';
  };

  const getProgressBg = (val: number) => {
    if (val >= 80) return 'bg-emerald-500';
    if (val >= 60) return 'bg-blue-500';
    if (val >= 45) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden hover:border-slate-300 transition-all">
      <div className="p-4 sm:p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2.5">
            {icon && <span className="text-slate-500">{icon}</span>}
            <h3 className="font-semibold text-slate-900 text-sm">{title}</h3>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
            Weight: {Math.round(scoreData.weight * 100)}%
          </span>
        </div>

        <div className="flex items-baseline justify-between mb-2">
          <span className="text-3xl font-extrabold text-slate-900">{score}</span>
          <span className="text-xs text-slate-400 font-medium">/ 100 max</span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-slate-100 rounded-full h-2 mb-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${getProgressBg(score)}`}
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center justify-between w-full text-xs font-medium text-slate-500 hover:text-slate-800 pt-2 border-t border-slate-100"
        >
          <span>{expanded ? 'Hide explainability breakdown' : 'Why this score? View breakdown'}</span>
          {expanded ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
        </button>
      </div>

      {expanded && (
        <div className="bg-slate-50 p-4 border-t border-slate-100 text-xs space-y-3">
          <div>
            <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">
              Scoring Factors:
            </span>
            <ul className="mt-1.5 space-y-1.5">
              {scoreData.breakdown.map((item, i) => (
                <li key={i} className="flex items-start justify-between bg-white p-2 rounded border border-slate-200/70">
                  <span className="text-slate-700 leading-snug mr-2">{item.reason}</span>
                  <span
                    className={`font-mono font-bold px-1.5 py-0.5 rounded text-[11px] shrink-0 ${
                      item.impact.startsWith('+')
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}
                  >
                    {item.impact}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {scoreData.recommendations.length > 0 && (
            <div>
              <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">
                Recommended Actions:
              </span>
              <ul className="mt-1 space-y-1">
                {scoreData.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start text-slate-600">
                    <span className="text-blue-500 mr-1.5">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
