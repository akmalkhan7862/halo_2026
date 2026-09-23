import React, { useState, useEffect } from 'react';
import {
  getTargetRoles,
  uploadResume,
  getResume,
  analyzeResumeAgainstRoles
} from '../api/client';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Briefcase,
  Upload,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowRightLeft,
  Sparkles,
  FileCheck,
  Award,
  Layers,
  ChevronRight,
  TrendingUp,
  AlertCircle
} from 'lucide-react';

export const RoleAnalysisPage: React.FC = () => {
  const [roles, setRoles] = useState<any[]>([]);
  const [selectedRoleKey, setSelectedRoleKey] = useState<string>('backend_developer');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [candidateName, setCandidateName] = useState<string>('');
  const [extractedSkills, setExtractedSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [singleResult, setSingleResult] = useState<any | null>(null);
  const [multiResult, setMultiResult] = useState<any | null>(null);

  // Load target roles on mount
  useEffect(() => {
    getTargetRoles()
      .then((data) => {
        setRoles(data);
        if (data.length > 0 && !selectedRoleKey) {
          setSelectedRoleKey(data[0].role_key);
        }
      })
      .catch((err) => {
        console.error('Failed to load target roles:', err);
        setError('Could not connect to backend to load target roles.');
      });
  }, []);

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    setSingleResult(null);
    setMultiResult(null);

    try {
      const res = await uploadResume(file, false);
      setResumeId(res.resume_id);
      const detail = await getResume(res.resume_id);
      const name = detail.parsed_json?.contact?.name || 'Verified Candidate';
      setCandidateName(name);

      const skills = (detail.parsed_json?.skills || []).map((s: any) => s.canonical_skill);
      setExtractedSkills(skills);
    } catch (err: any) {
      setError(err.message || 'Failed to upload and parse resume.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSampleResume = async () => {
    const sampleText = `Alex Morgan
alex.morgan@example.com | (555) 234-5678 | San Francisco, CA | github.com/alexmorgan | linkedin.com/in/alexmorgan

PROFESSIONAL SUMMARY
Results-driven Software Engineer with 4 years of hands-on experience building high-throughput backend APIs, microservices, and distributed data pipelines.

TECHNICAL SKILLS
Languages: Python, TypeScript, SQL
Frameworks: FastAPI, Flask, Pydantic, SQLAlchemy
Databases: PostgreSQL, Redis, MySQL
Cloud & DevOps: Docker, Git, CI/CD, AWS

WORK EXPERIENCE
Software Engineer | Apex Cloud Systems (Jan 2022 - Present)
* Developed REST APIs using FastAPI and PostgreSQL supporting over 50,000 daily active users.
* Optimized database indexing and async queries, reducing p95 API response times by 38%.
* Architected automated CI/CD deployment pipelines using Docker and GitHub Actions.

Junior Developer | NovaTech Labs (Jun 2020 - Dec 2021)
* Maintained backend Flask microservices and integrated third-party payment gateways.
* Implemented unit and integration test suites achieving 85% code coverage.

KEY PROJECTS
Distributed Task Streamer
Engineered a resilient event streaming worker using Python, Redis, and Docker. Handled 10,000 tasks/sec with zero job loss.

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley (2020) | GPA: 3.8`;

    const blob = new Blob([sampleText], { type: 'application/pdf' });
    const file = new File([blob], 'alex_morgan_resume.pdf', { type: 'application/pdf' });
    setResumeFile(file);
    await handleFileUpload(file);
  };

  const handleRunAnalysis = async () => {
    if (!resumeId) return;
    setAnalyzing(true);
    setError(null);

    try {
      const data = await analyzeResumeAgainstRoles(resumeId, selectedRoleKey);
      if (selectedRoleKey === 'all') {
        setMultiResult(data);
        setSingleResult(null);
      } else {
        setSingleResult(data.role_analysis);
        setMultiResult(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to analyze resume against target roles.');
    } finally {
      setAnalyzing(false);
    }
  };

  const renderSingleRoleResult = (res: any) => {
    const gap = res.gap_summary;

    return (
      <div className="space-y-6 mt-6 animate-fadeIn">
        {/* Fit Score & Readiness Banner */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                Official Taxonomy Alignment
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold capitalize">
                {res.seniority} Level • {res.domain.replace('_', ' ')}
              </span>
            </div>
            <h3 className="text-2xl font-black text-slate-900 tracking-tight">
              {res.display_name} Fit Evaluation
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-xl">
              Target role skills loaded directly from ESCO & O*NET standards. Zero manual JD required.
            </p>
          </div>

          <div className="flex items-center space-x-4 bg-slate-50 p-4 rounded-xl border border-slate-100">
            <div className="text-right">
              <div className="text-[10px] uppercase font-bold text-slate-400">Taxonomy Fit Score</div>
              <div className="text-4xl font-black text-slate-900">{Math.round(res.fit_score)}%</div>
            </div>
            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white text-xs ${
              res.fit_score >= 75 ? 'bg-emerald-600' : res.fit_score >= 50 ? 'bg-amber-500' : 'bg-rose-500'
            }`}>
              {gap.overall_readiness.toUpperCase()}
            </div>
          </div>
        </div>

        {/* Narrative Summary */}
        <div className="bg-blue-50/60 border border-blue-200 rounded-2xl p-5 text-xs text-blue-950 leading-relaxed shadow-xs">
          <span className="font-bold text-blue-900 text-sm block mb-1">Taxonomy Gap Summary:</span>
          <p>{gap.narrative_summary}</p>

          {gap.critical_missing_skills.length > 0 && (
            <div className="mt-3 pt-2 border-t border-blue-200/60 flex flex-wrap items-center gap-1.5">
              <span className="font-semibold text-blue-900">Critical Gaps to Close:</span>
              {gap.critical_missing_skills.map((s: string, idx: number) => (
                <span key={idx} className="bg-white px-2 py-0.5 rounded text-rose-700 font-bold border border-rose-200 text-[11px]">
                  {s}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* 4-Way Skill Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Matched */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-100 mb-3">
              <span className="font-bold text-xs text-slate-900 flex items-center">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 mr-1.5" />
                Matched ({res.matched_skills.length})
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.5 rounded">
                Verified
              </span>
            </div>
            <div className="space-y-1.5">
              {res.matched_skills.map((s: any, idx: number) => (
                <div key={idx} className="bg-emerald-50/70 border border-emerald-200 rounded-lg p-2 text-xs">
                  <span className="font-bold text-emerald-900 block">{s.canonical_skill}</span>
                  <span className="text-[11px] text-slate-500 italic block mt-0.5 line-clamp-2">
                    {s.evidence_citation}
                  </span>
                </div>
              ))}
              {res.matched_skills.length === 0 && (
                <p className="text-xs text-slate-400 italic">No direct matches</p>
              )}
            </div>
          </div>

          {/* Missing */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-100 mb-3">
              <span className="font-bold text-xs text-slate-900 flex items-center">
                <XCircle className="w-4 h-4 text-rose-600 mr-1.5" />
                Missing ({res.missing_skills.length})
              </span>
              <span className="text-[10px] bg-rose-100 text-rose-800 font-bold px-1.5 py-0.5 rounded">
                Gaps
              </span>
            </div>
            <div className="space-y-1.5">
              {res.missing_skills.map((s: any, idx: number) => (
                <div key={idx} className="bg-rose-50/70 border border-rose-200 rounded-lg p-2 text-xs">
                  <span className="font-bold text-rose-900 block">{s.canonical_skill}</span>
                  <span className="text-[10px] text-rose-600 uppercase font-semibold">
                    {s.importance} requirement
                  </span>
                </div>
              ))}
              {res.missing_skills.length === 0 && (
                <p className="text-xs text-slate-400 italic">No missing requirements</p>
              )}
            </div>
          </div>

          {/* Weak / Transferable */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-100 mb-3">
              <span className="font-bold text-xs text-slate-900 flex items-center">
                <ArrowRightLeft className="w-4 h-4 text-indigo-600 mr-1.5" />
                Weak / Transferable ({res.weak_skills.length + res.related_partial_skills.length})
              </span>
              <span className="text-[10px] bg-indigo-100 text-indigo-800 font-bold px-1.5 py-0.5 rounded">
                Bridge
              </span>
            </div>
            <div className="space-y-1.5">
              {res.related_partial_skills.map((s: any, idx: number) => (
                <div key={idx} className="bg-indigo-50/70 border border-indigo-200 rounded-lg p-2 text-xs">
                  <span className="font-bold text-indigo-900 block">{s.canonical_skill}</span>
                  <span className="text-[11px] text-indigo-700 block">
                    Bridged by candidate's <b>{s.related_to}</b>
                  </span>
                </div>
              ))}
              {res.weak_skills.map((s: any, idx: number) => (
                <div key={idx} className="bg-amber-50/70 border border-amber-200 rounded-lg p-2 text-xs">
                  <span className="font-bold text-amber-900 block">{s.canonical_skill}</span>
                  <span className="text-[11px] text-slate-500 italic block">
                    Listed only; lacks project proof
                  </span>
                </div>
              ))}
              {res.weak_skills.length === 0 && res.related_partial_skills.length === 0 && (
                <p className="text-xs text-slate-400 italic">None</p>
              )}
            </div>
          </div>

          {/* Extra Skills */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-100 mb-3">
              <span className="font-bold text-xs text-slate-900 flex items-center">
                <Layers className="w-4 h-4 text-slate-600 mr-1.5" />
                Extra Skills ({res.extra_skills.length})
              </span>
              <span className="text-[10px] bg-slate-100 text-slate-700 font-bold px-1.5 py-0.5 rounded">
                Bonus
              </span>
            </div>
            <div className="flex flex-wrap gap-1">
              {res.extra_skills.map((s: string, idx: number) => (
                <span key={idx} className="bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded border border-slate-200">
                  {s}
                </span>
              ))}
              {res.extra_skills.length === 0 && (
                <p className="text-xs text-slate-400 italic">None</p>
              )}
            </div>
          </div>
        </div>

        {/* Quick Wins */}
        {gap.quick_wins.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2.5 flex items-center">
              <Sparkles className="w-4 h-4 text-blue-600 mr-1.5" />
              Actionable Career Advice to Bridge Gaps
            </h4>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {gap.quick_wins.map((win: string, idx: number) => (
                <li key={idx} className="bg-slate-50 p-2.5 rounded-lg border border-slate-100 flex items-start">
                  <span className="text-blue-600 font-bold mr-2">✓</span>
                  <span className="text-slate-700">{win}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderMultiRoleResult = (res: any) => {
    return (
      <div className="space-y-6 mt-6 animate-fadeIn">
        <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-md">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-300">
            Multi-Role Benchmark Analysis
          </span>
          <h3 className="text-2xl font-black mt-1">
            Top Recommended Role: {res.top_recommended_role}
          </h3>
          <p className="text-xs text-blue-200 mt-1">
            Evaluated {res.total_roles_evaluated} curated ESCO/O*NET industry standard roles without manual JD input.
          </p>
        </div>

        <div className="space-y-3">
          {res.role_rankings.map((r: any, idx: number) => (
            <div
              key={r.role_key}
              className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:border-slate-300 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="flex items-center space-x-3">
                <span className="w-7 h-7 rounded-full bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center shrink-0">
                  #{idx + 1}
                </span>
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">{r.display_name}</h4>
                  <div className="flex flex-wrap gap-2 text-[11px] text-slate-500 mt-0.5">
                    <span className="capitalize">{r.seniority} Level</span>
                    <span>•</span>
                    <span className="capitalize">{r.domain.replace('_', ' ')}</span>
                    <span>•</span>
                    <span className="text-emerald-700 font-semibold">{r.matched_skills.length} matched</span>
                    <span>•</span>
                    <span className="text-rose-700 font-semibold">{r.missing_skills.length} missing</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-4 self-end md:self-auto">
                <div className="text-right">
                  <div className="text-2xl font-black text-slate-900">{Math.round(r.fit_score)}%</div>
                  <span className="text-[10px] uppercase font-bold text-slate-400">Match Fit</span>
                </div>
                <button
                  onClick={() => {
                    setSelectedRoleKey(r.role_key);
                    setSingleResult(r);
                    setMultiResult(null);
                  }}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold px-3 py-2 rounded-lg transition-colors flex items-center"
                >
                  <span>View Details</span>
                  <ChevronRight className="w-3.5 h-3.5 ml-1" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
      <div className="text-center space-y-2">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
          <Briefcase className="w-3.5 h-3.5 mr-1.5" />
          No Manual JD Required
        </span>
        <h2 className="text-3xl font-black text-slate-900 tracking-tight">
          Taxonomy Target Role Analysis
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
          Select from 12 preloaded software and data engineering roles derived from official
          <b> ESCO</b> and <b>O*NET</b> taxonomies. Extract your resume skills and instantly discover your match fit.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start text-rose-800 text-xs">
          <AlertCircle className="w-5 h-5 mr-2 shrink-0 text-rose-600" />
          <div>
            <span className="font-bold">Error: </span>
            {error}
          </div>
        </div>
      )}

      {/* Input Controls Panel */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Step A: Resume Upload */}
          <div className="space-y-3">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
              1. Upload Candidate Resume
            </label>

            {!resumeId ? (
              <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center space-y-3">
                <Upload className="w-8 h-8 text-slate-400 mx-auto" />
                <div className="text-xs text-slate-600">
                  Upload a PDF or DOCX resume to extract skills
                </div>
                <div className="flex justify-center gap-2">
                  <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-4 py-2 rounded-lg transition-colors">
                    <span>Select Resume</span>
                    <input
                      type="file"
                      accept=".pdf,.docx"
                      onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
                      className="hidden"
                    />
                  </label>
                  <button
                    onClick={handleLoadSampleResume}
                    className="bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs px-3.5 py-2 rounded-lg transition-colors flex items-center"
                  >
                    <Sparkles className="w-3.5 h-3.5 mr-1 text-blue-600" />
                    Load Sample
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-emerald-50/60 border border-emerald-200 rounded-xl p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileCheck className="w-6 h-6 text-emerald-600" />
                  <div>
                    <h4 className="font-bold text-slate-900 text-xs">{candidateName}</h4>
                    <p className="text-[11px] text-slate-500">
                      {extractedSkills.length} canonical skills extracted with evidence
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setResumeId(null);
                    setSingleResult(null);
                    setMultiResult(null);
                  }}
                  className="text-xs font-semibold text-slate-500 hover:text-slate-800"
                >
                  Change
                </button>
              </div>
            )}
          </div>

          {/* Step B: Target Role Selection */}
          <div className="space-y-3">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
              2. Select Target Taxonomy Role
            </label>

            <div>
              <select
                value={selectedRoleKey}
                onChange={(e) => setSelectedRoleKey(e.target.value)}
                className="w-full p-2.5 text-xs font-medium border border-slate-300 rounded-xl bg-white shadow-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="all">🔍 Compare & Rank Fit Across All 12 Roles</option>
                <optgroup label="Software Engineering">
                  <option value="backend_developer">Backend Developer (ESCO / O*NET 15-1252.00)</option>
                  <option value="frontend_developer">Frontend Developer (ESCO / O*NET 15-1254.00)</option>
                  <option value="full_stack_developer">Full Stack Developer (ESCO / O*NET 15-1252.00)</option>
                  <option value="mobile_developer">Mobile App Developer (ESCO / O*NET 15-1254.00)</option>
                </optgroup>
                <optgroup label="Data & Artificial Intelligence">
                  <option value="data_analyst">Data Analyst (ESCO / O*NET 15-2051.00)</option>
                  <option value="data_engineer">Data Engineer (ESCO / O*NET 15-1243.00)</option>
                  <option value="ml_engineer">Machine Learning Engineer (ESCO / O*NET 15-2051.01)</option>
                </optgroup>
                <optgroup label="Infrastructure, Cloud & Security">
                  <option value="devops_engineer">DevOps Engineer (ESCO / O*NET 15-1244.00)</option>
                  <option value="cloud_solutions_architect">Cloud Solutions Architect (ESCO / O*NET 15-1299.08)</option>
                  <option value="site_reliability_engineer">Site Reliability Engineer (SRE)</option>
                  <option value="cybersecurity_analyst">Cybersecurity Analyst (ESCO / O*NET 15-1212.00)</option>
                  <option value="qa_automation_engineer">QA Automation Engineer (ESCO / O*NET 15-1253.00)</option>
                </optgroup>
              </select>

              <p className="text-[11px] text-slate-500 mt-2">
                Replaces manual Job Descriptions with standardized ESCO / O*NET occupational standards.
              </p>
            </div>

            <div className="pt-2">
              <button
                disabled={!resumeId || analyzing || loading}
                onClick={handleRunAnalysis}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2.5 rounded-xl shadow-md transition-all flex items-center justify-center disabled:opacity-50"
              >
                {analyzing ? (
                  <span>Evaluating Role Alignment...</span>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4 mr-1.5" />
                    <span>Analyze Role Fit (No JD Needed)</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {analyzing && (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
          <LoadingSpinner
            message="Comparing Resume Skills With Canonical Role Standards..."
            submessage="Cross-referencing ESCO & O*NET occupational skills, detecting transferable clusters, and computing explainable fit scores."
          />
        </div>
      )}

      {/* Results View */}
      {singleResult && renderSingleRoleResult(singleResult)}
      {multiResult && renderMultiRoleResult(multiResult)}
    </div>
  );
};
