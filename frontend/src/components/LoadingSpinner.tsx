import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  submessage?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Processing...',
  submessage = 'Analyzing document and matching taxonomies...'
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
      <h3 className="text-base font-bold text-slate-900 mb-1">{message}</h3>
      <p className="text-xs text-slate-500 max-w-sm">{submessage}</p>
    </div>
  );
};
