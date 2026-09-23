import React from 'react';
import { useApp, Step } from '../context/AppContext';
import { FileText, Target, BarChart3, MessageSquare, Award, Check } from 'lucide-react';

interface StepItem {
  id: Step;
  label: string;
  sublabel: string;
  icon: React.ElementType;
}

const STEPS: StepItem[] = [
  { id: 'upload', label: '1. Resume Upload', sublabel: 'PDF / Word extraction', icon: FileText },
  { id: 'role', label: '2. Target Role', sublabel: 'ESCO & O*NET profiles', icon: Target },
  { id: 'analysis', label: '3. Skill Gap Analysis', sublabel: 'Explainable match fit', icon: BarChart3 },
  { id: 'interview', label: '4. Mock Interview', sublabel: '7-10 resume-grounded Qs', icon: MessageSquare },
  { id: 'report', label: '5. Final Report & Roadmap', sublabel: 'Action plan & PDF report', icon: Award },
];

export const Stepper: React.FC = () => {
  const { step, setStep, resume, analysis, interview } = useApp();

  const isStepEnabled = (s: Step): boolean => {
    if (s === 'upload') return true;
    if (s === 'role') return !!resume;
    if (s === 'analysis') return !!analysis;
    if (s === 'interview') return !!interview;
    if (s === 'report') return !!analysis;
    return false;
  };

  const currentIdx = STEPS.findIndex((item) => item.id === step);

  return (
    <nav aria-label="Progress" className="bg-white border-b border-slate-200 py-3 px-4 sm:px-8">
      <ol className="max-w-7xl mx-auto flex items-center justify-between overflow-x-auto space-x-2 sm:space-x-4">
        {STEPS.map((s, idx) => {
          const Icon = s.icon;
          const isActive = s.id === step;
          const isCompleted = idx < currentIdx;
          const enabled = isStepEnabled(s.id);

          return (
            <li key={s.id} className="flex-1 min-w-[170px]">
              <button
                disabled={!enabled}
                onClick={() => enabled && setStep(s.id)}
                className={`w-full text-left p-2.5 rounded-lg border transition-all flex items-center space-x-3 ${
                  isActive
                    ? 'border-blue-600 bg-blue-50/70 text-blue-900 shadow-sm'
                    : isCompleted
                    ? 'border-emerald-300 bg-emerald-50/40 text-emerald-900 hover:bg-emerald-50'
                    : enabled
                    ? 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                    : 'border-slate-100 bg-white text-slate-400 cursor-not-allowed opacity-60'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : isCompleted
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  {isCompleted ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                </div>
                <div className="overflow-hidden">
                  <div className="text-xs font-bold truncate leading-snug">{s.label}</div>
                  <div className="text-[11px] text-slate-500 truncate">{s.sublabel}</div>
                </div>
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
