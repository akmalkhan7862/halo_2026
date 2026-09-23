import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { createJobDescription, runAnalysis } from '../api/client';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  FileText,
  Link,
  Upload,
  ArrowRight,
  AlertCircle,
  Sparkles,
  CheckCircle2,
  Building,
  Briefcase
} from 'lucide-react';

export const JobDescriptionPage: React.FC = () => {
  const { resume, jd, setJd, setAnalysis, setStep } = useApp();
  const [activeTab, setActiveTab] = useState<'text' | 'url' | 'file'>('text');
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [rawText, setRawText] = useState('');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const createdJd = await createJobDescription({
        title,
        company,
        rawText: activeTab === 'text' ? rawText : undefined,
        url: activeTab === 'url' ? url : undefined,
        file: activeTab === 'file' && file ? file : undefined,
      });

      setJd(createdJd);

      // Trigger analysis immediately
      if (resume) {
        const analysisResult = await runAnalysis({
          resumeId: resume.id,
          jobDescriptionId: createdJd.id,
          targetRole: title || createdJd.title,
        });
        setAnalysis(analysisResult);
        setStep('analysis');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to parse Job Description');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSampleJD = () => {
    setTitle('Senior Backend Developer');
    setCompany('CloudWave Technologies');
    setActiveTab('text');
    setRawText(`CloudWave Technologies is hiring a Senior Backend Developer.

About the Role:
We are looking for an experienced Senior Backend Developer to join our core platform engineering team.
You will architect, build, and deploy mission-critical microservices and database pipelines.

Requirements:
* 4+ years of professional software engineering experience.
* Proficiency in Python and FastAPI (or modern Python web framework).
* Strong relational database expertise with PostgreSQL and complex SQL queries.
* Hands-on experience with Docker, containerization, and automated CI/CD workflows.
* Familiarity with version control using Git.

Preferred Qualifications:
* Experience with Kubernetes container orchestration.
* Knowledge of Amazon Web Services (AWS) cloud architecture.
* Understanding of System Design for scalable distributed services.
* Experience with caching layers such as Redis.

Responsibilities:
* Design scalable REST APIs and high-throughput background processing services.
* Collaborate closely with product managers and frontend teams.
* Conduct architecture reviews and mentor junior developers.`);
  };

  const parsed = jd?.parsed_json;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Step 2: Provide Job Description
        </h2>
        <p className="mt-2 text-sm text-slate-600 max-w-xl mx-auto">
          Specify the target role requirements. The platform classifies mandatory vs preferred skills,
          detects required years of experience, and evaluates candidate alignment.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start text-rose-800 text-xs">
          <AlertCircle className="w-5 h-5 mr-2 shrink-0 text-rose-600" />
          <div>
            <span className="font-bold">Error: </span>
            {error}
          </div>
        </div>
      )}

      {loading ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
          <LoadingSpinner
            message="Analyzing Job Description & Computing Match Engine..."
            submessage="Performing 5-way skill gap classification (Matched, Weak, Missing, Transferable, Extra) and calculating explainable subscores."
          />
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
          <div className="flex items-center justify-between pb-4 border-b border-slate-200 mb-6">
            <div className="flex space-x-1 bg-slate-100 p-1 rounded-xl">
              <button
                type="button"
                onClick={() => setActiveTab('text')}
                className={`flex items-center text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'text' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <FileText className="w-3.5 h-3.5 mr-1.5" />
                Paste Text
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('url')}
                className={`flex items-center text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'url' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Link className="w-3.5 h-3.5 mr-1.5" />
                Job Posting URL
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('file')}
                className={`flex items-center text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'file' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Upload className="w-3.5 h-3.5 mr-1.5" />
                Upload Document
              </button>
            </div>

            <button
              type="button"
              onClick={handleLoadSampleJD}
              className="bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-xs px-3.5 py-1.5 rounded-lg transition-colors flex items-center"
            >
              <Sparkles className="w-3.5 h-3.5 mr-1 text-blue-600" />
              Load Sample JD
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Target Job Title (Optional)
                </label>
                <div className="relative">
                  <Briefcase className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Senior Backend Developer"
                    className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Company Name (Optional)
                </label>
                <div className="relative">
                  <Building className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="e.g. CloudWave Technologies"
                    className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {activeTab === 'text' && (
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Job Description Text
                </label>
                <textarea
                  required
                  rows={10}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Paste the full job posting requirements, responsibilities, and qualifications here..."
                  className="w-full p-3 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-slate-800 leading-relaxed"
                />
              </div>
            )}

            {activeTab === 'url' && (
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Job Posting URL
                </label>
                <input
                  type="url"
                  required
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://jobs.example.com/posting/12345"
                  className="w-full p-2.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  The server will fetch and clean page content. Note: Pages requiring login or heavy JS may not be accessible.
                </p>
              </div>
            )}

            {activeTab === 'file' && (
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Upload Job Description Document
                </label>
                <input
                  type="file"
                  required
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => e.target.files && setFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
            )}

            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setStep('upload')}
                className="text-xs font-medium text-slate-600 hover:text-slate-900"
              >
                Back to Resume
              </button>

              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-6 py-2.5 rounded-xl shadow-md transition-all flex items-center"
              >
                <span>Run Gap Analysis & Compute Scores</span>
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
