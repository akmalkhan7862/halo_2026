import React, { createContext, useContext, useState } from 'react';
import {
  ResumeRecord,
  JDRecord,
  AnalysisRecord,
  InterviewSessionRecord,
  FinalReportRecord
} from '../types';

export type Step = 'upload' | 'role' | 'analysis' | 'interview' | 'report';

interface AppContextType {
  step: Step;
  setStep: (step: Step) => void;
  selectedRoleKey: string;
  setSelectedRoleKey: (key: string) => void;
  resume: ResumeRecord | null;
  setResume: (resume: ResumeRecord | null) => void;
  jd: JDRecord | null;
  setJd: (jd: JDRecord | null) => void;
  analysis: AnalysisRecord | null;
  setAnalysis: (analysis: AnalysisRecord | null) => void;
  interview: InterviewSessionRecord | null;
  setInterview: (interview: InterviewSessionRecord | null) => void;
  report: FinalReportRecord | null;
  setReport: (report: FinalReportRecord | null) => void;
  resetAll: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [step, setStep] = useState<Step>('upload');
  const [selectedRoleKey, setSelectedRoleKey] = useState<string>('backend_developer');
  const [resume, setResume] = useState<ResumeRecord | null>(null);
  const [jd, setJd] = useState<JDRecord | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisRecord | null>(null);
  const [interview, setInterview] = useState<InterviewSessionRecord | null>(null);
  const [report, setReport] = useState<FinalReportRecord | null>(null);

  const resetAll = () => {
    setStep('upload');
    setSelectedRoleKey('backend_developer');
    setResume(null);
    setJd(null);
    setAnalysis(null);
    setInterview(null);
    setReport(null);
  };

  return (
    <AppContext.Provider
      value={{
        step,
        setStep,
        selectedRoleKey,
        setSelectedRoleKey,
        resume,
        setResume,
        jd,
        setJd,
        analysis,
        setAnalysis,
        interview,
        setInterview,
        report,
        setReport,
        resetAll,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
