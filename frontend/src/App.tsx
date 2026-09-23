import React from 'react';
import { useApp } from './context/AppContext';
import { Navbar } from './components/Navbar';
import { Stepper } from './components/Stepper';
import { ResumeUploadPage } from './pages/ResumeUploadPage';
import { RoleSelectionPage } from './pages/RoleSelectionPage';
import { AnalysisViewPage } from './pages/AnalysisViewPage';
import { MockInterviewPage } from './pages/MockInterviewPage';
import { FinalReportPage } from './pages/FinalReportPage';

export const App: React.FC = () => {
  const { step } = useApp();

  const renderCurrentStep = () => {
    switch (step) {
      case 'upload':
        return <ResumeUploadPage />;
      case 'role':
        return <RoleSelectionPage />;
      case 'analysis':
        return <AnalysisViewPage />;
      case 'interview':
        return <MockInterviewPage />;
      case 'report':
        return <FinalReportPage />;
      default:
        return <ResumeUploadPage />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <Stepper />

      <main className="flex-1 pb-16">
        {renderCurrentStep()}
      </main>

      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <p>Resume Intelligence Platform • Official ESCO & O*NET Taxonomy Integration • No Manual JD Required</p>
      </footer>
    </div>
  );
};

export default App;
