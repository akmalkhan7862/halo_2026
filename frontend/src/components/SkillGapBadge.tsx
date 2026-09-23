import React, { useState } from 'react';
import { SkillClassificationItem } from '../types';
import { CheckCircle2, AlertTriangle, XCircle, ArrowRightLeft, ChevronDown } from 'lucide-react';

interface SkillGapBadgeProps {
  item: SkillClassificationItem;
}

export const SkillGapBadge: React.FC<SkillGapBadgeProps> = ({ item }) => {
  const [showCitation, setShowCitation] = useState(false);

  const getStyle = () => {
    switch (item.status) {
      case 'MATCHED':
        return {
          bg: 'bg-emerald-50 hover:bg-emerald-100/70 border-emerald-200 text-emerald-800',
          icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mr-1.5 shrink-0" />,
          label: 'Matched'
        };
      case 'WEAK':
        return {
          bg: 'bg-amber-50 hover:bg-amber-100/70 border-amber-200 text-amber-800',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600 mr-1.5 shrink-0" />,
          label: 'Weak Evidence'
        };
      case 'RELATED_PARTIAL':
        return {
          bg: 'bg-indigo-50 hover:bg-indigo-100/70 border-indigo-200 text-indigo-800',
          icon: <ArrowRightLeft className="w-3.5 h-3.5 text-indigo-600 mr-1.5 shrink-0" />,
          label: 'Transferable'
        };
      case 'MISSING':
      default:
        return {
          bg: 'bg-rose-50 hover:bg-rose-100/70 border-rose-200 text-rose-800',
          icon: <XCircle className="w-3.5 h-3.5 text-rose-600 mr-1.5 shrink-0" />,
          label: 'Missing'
        };
    }
  };

  const style = getStyle();

  return (
    <div className="flex flex-col mb-1.5">
      <div
        onClick={() => setShowCitation(!showCitation)}
        className={`inline-flex items-center justify-between px-3 py-1.5 rounded-lg border text-xs font-medium cursor-pointer transition-colors ${style.bg}`}
      >
        <div className="flex items-center min-w-0 mr-2">
          {style.icon}
          <span className="font-semibold truncate">{item.canonical_skill}</span>
          {item.importance === 'preferred' && (
            <span className="ml-1.5 text-[10px] text-slate-500 italic shrink-0">(Preferred)</span>
          )}
        </div>

        <div className="flex items-center space-x-1 shrink-0">
          <span className="text-[10px] uppercase font-bold tracking-wider opacity-75">
            {style.label}
          </span>
          <ChevronDown
            className={`w-3.5 h-3.5 transition-transform ${showCitation ? 'rotate-180' : ''}`}
          />
        </div>
      </div>

      {showCitation && (
        <div className="mt-1 ml-2 pl-3 border-l-2 border-slate-300 py-1 text-xs text-slate-600 bg-white p-2 rounded shadow-xs">
          <p className="font-medium text-slate-800">{item.reason}</p>
          {item.evidence_citation && (
            <p className="mt-1 text-[11px] text-slate-500 italic bg-slate-50 p-1.5 rounded border border-slate-100">
              <span className="font-semibold text-slate-700">Resume Evidence:</span> "{item.evidence_citation}"
            </p>
          )}
        </div>
      )}
    </div>
  );
};
