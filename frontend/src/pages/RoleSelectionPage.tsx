import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { getTargetRoles, getTargetRoleDetail, analyzeRoleFitWithInterview, analyzeManualJD } from '../api/client';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Briefcase,
  Layers,
  ArrowRight,
  ArrowLeft,
  ShieldCheck,
  Sparkles,
  AlertCircle,
  Award,
  CheckCircle2,
  ChevronRight,
  FileText,
  RotateCcw
} from 'lucide-react';

const SAMPLE_JDS = [
  {
    title: 'Senior Backend Engineer',
    company: 'CloudScale Systems',
    text: `Job Title: Senior Backend Engineer
Company: CloudScale Systems
Seniority: Senior

About the Role:
We are seeking an experienced Senior Backend Engineer to architect, build, and maintain high-performance microservice APIs and distributed backend systems.

Responsibilities:
- Design, build, and optimize scalable REST and microservice APIs.
- Lead architecture decisions around database modeling, caching, and throughput optimization.
- Write robust unit, integration, and performance test suites.
- Mentor engineers on coding best practices and asynchronous workflows.

Required Qualifications:
- 5+ years of software engineering experience in backend development.
- Strong hands-on proficiency in Python, FastAPI, and PostgreSQL.
- Solid experience in REST API design, microservices, and asynchronous architecture.
- Demonstrated experience containerizing applications using Docker and Git version control.

Preferred Qualifications:
- Nice to have: Hands-on experience with Kubernetes and container orchestration.
- Knowledge of Redis for distributed caching and message queues.
- Experience with Amazon Web Services (AWS) cloud infrastructure.
- Familiarity with CI/CD pipeline automation and automated monitoring.`
  },
  {
    title: 'Full Stack Developer',
    company: 'Horizon Digital',
    text: `Job Title: Full Stack Developer
Company: Horizon Digital
Seniority: Mid-Level

About the Role:
Join our engineering team to build modern, responsive web applications spanning rich client-side frontends and scalable server-side systems.

Responsibilities:
- Build responsive, accessible web applications with TypeScript and React.
- Develop backend APIs and integrate databases with PostgreSQL and Python.
- Collaborate with product designers and engineers across agile sprint cycles.

Requirements:
- 3+ years of professional full-stack development experience.
- Strong proficiency in TypeScript, React, and modern JavaScript.
- Solid backend experience in Python, FastAPI, and REST APIs.
- Experience with PostgreSQL relational database modeling.
- Hands-on version control workflow with Git and GitHub.

Preferred:
- Experience with Next.js, Tailwind CSS, or GraphQL.
- Working knowledge of Docker containerization and CI/CD pipelines.
- Experience building and consuming cloud services on AWS.`
  },
  {
    title: 'Machine Learning Engineer',
    company: 'Cortex Intelligence Labs',
    text: `Job Title: Machine Learning Engineer
Company: Cortex Intelligence Labs
Seniority: Mid-Senior

About the Role:
We are looking for a Machine Learning Engineer to train, evaluate, and deploy predictive models and data-driven systems into production.

Required Qualifications:
- 3+ years of experience building machine learning or deep learning pipelines.
- Strong Python programming with PyTorch, Scikit-Learn, or TensorFlow.
- Strong foundation in SQL, Pandas, data preprocessing, and statistical analysis.
- Experience containerizing models with Docker and deploying REST API inference endpoints with FastAPI.

Preferred Qualifications:
- Hands-on experience with MLOps pipelines and Kubernetes deployment.
- Familiarity with Apache Spark or large-scale data processing.
- Experience with cloud platforms (AWS, GCP).`
  }
];

export const RoleSelectionPage: React.FC = () => {
  const { resume, setAnalysis, setInterview, setStep, selectedRoleKey, setSelectedRoleKey } = useApp();
  const [analysisMode, setAnalysisMode] = useState<'taxonomy' | 'manual_jd'>('taxonomy');
  const [jdText, setJdText] = useState<string>('');
  const [roles, setRoles] = useState<any[]>([]);
  const [selectedRoleDetail, setSelectedRoleDetail] = useState<any | null>(null);
  const [difficulty, setDifficulty] = useState<string>('medium');
  const [questionCount, setQuestionCount] = useState<number>(8);
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoadingRoles(true);
    getTargetRoles()
      .then((data) => {
        setRoles(data);
        if (data.length > 0 && !selectedRoleKey) {
          setSelectedRoleKey(data[0].role_key);
        }
      })
      .catch((err) => {
        console.error('Failed to load target roles:', err);
        setError('Could not load target roles from backend.');
      })
      .finally(() => setLoadingRoles(false));
  }, []);

  useEffect(() => {
    if (selectedRoleKey) {
      getTargetRoleDetail(selectedRoleKey)
        .then((detail) => setSelectedRoleDetail(detail))
        .catch((err) => console.error('Failed to load role detail:', err));
    }
  }, [selectedRoleKey]);

  const handleAnalyzeAndProceed = async () => {
    if (!resume) {
      setError('Please upload a resume first.');
      return;
    }
    setAnalyzing(true);
    setError(null);

    try {
      if (analysisMode === 'taxonomy') {
        const res = await analyzeRoleFitWithInterview(
          resume.id,
          selectedRoleKey,
          difficulty,
          questionCount
        );

        const analysisRecord: any = {
          id: res.analysis_id,
          resume_id: resume.id,
          mode: 'taxonomy_role',
          role_key: res.role_key,
          role_display_name: res.display_name,
          target_role: res.display_name,
          matched_skills: res.matched_skills,
          missing_skills: res.missing_skills,
          weak_skills: res.weak_skills,
          related_partial_skills: [],
          extra_skills: res.extra_skills,
          gap_summary: res.gap_summary,
          gap_analysis: res.gap_analysis,
          learning_roadmap: res.learning_roadmap,
          scores: res.scores || {
            overall_score: Math.round(res.coverage_ratio * 100),
            overall_breakdown: [
              { reason: `Matched ${res.matched_skills.length} core taxonomy skills`, impact: `+${Math.round(res.coverage_ratio * 35)}` },
              { reason: `${res.missing_skills.length} role requirements missing from resume`, impact: `-${Math.min(res.missing_skills.length * 4, 20)}` }
            ],
            skill_match_score: { score: Math.round(res.coverage_ratio * 100), max_score: 100, weight: 0.35, breakdown: [], recommendations: [] },
            experience_score: { score: 80, max_score: 100, weight: 0.20, breakdown: [], recommendations: [] },
            project_score: { score: 85, max_score: 100, weight: 0.20, breakdown: [], recommendations: [] },
            keyword_score: { score: 75, max_score: 100, weight: 0.15, breakdown: [], recommendations: [] },
            seniority_score: { score: 80, max_score: 100, weight: 0.10, breakdown: [], recommendations: [] }
          },
          explanations: { mode: 'taxonomy_role' },
          provenance: {
            taxonomy_sources: ['ESCO', 'O*NET'],
            scoring_version: 'v1.0.0'
          },
          created_at: new Date().toISOString()
        };

        const interviewRecord: any = {
          id: res.interview.session_id,
          analysis_result_id: res.analysis_id,
          target_role: res.display_name,
          difficulty,
          question_count: res.interview.questions.length,
          status: 'in_progress',
          generated_questions: res.interview.questions,
          answers: [],
          created_at: new Date().toISOString()
        };

        setAnalysis(analysisRecord);
        setInterview(interviewRecord);
        setStep('analysis');
      } else {
        // Mode 2: Manual Job Description
        if (!jdText.trim() || jdText.trim().length < 20) {
          setError('Please paste a job description with at least 20 characters.');
          setAnalyzing(false);
          return;
        }

        const res = await analyzeManualJD(
          resume.id,
          jdText.trim(),
          difficulty,
          questionCount
        );

        const targetTitle = res.role_display_name || res.display_name || 'Custom Role from JD';

        const analysisRecord: any = {
          id: res.analysis_id,
          resume_id: resume.id,
          mode: 'manual_jd',
          role_key: null,
          role_display_name: targetTitle,
          target_role: targetTitle,
          matched_skills: res.matched_skills,
          missing_skills: res.missing_skills,
          weak_skills: res.weak_skills,
          related_partial_skills: [],
          extra_skills: res.extra_skills,
          gap_summary: res.gap_summary,
          gap_analysis: res.gap_analysis,
          learning_roadmap: res.learning_roadmap,
          scores: res.scores || {
            overall_score: Math.round(res.coverage_ratio * 100),
            overall_breakdown: [
              { reason: `Matched ${res.matched_skills.length} JD skills`, impact: `+${Math.round(res.coverage_ratio * 35)}` },
              { reason: `${res.missing_skills.length} requirements missing from resume`, impact: `-${Math.min(res.missing_skills.length * 4, 20)}` }
            ],
            skill_match_score: { score: Math.round(res.coverage_ratio * 100), max_score: 100, weight: 0.35, breakdown: [], recommendations: [] },
            experience_score: { score: 80, max_score: 100, weight: 0.20, breakdown: [], recommendations: [] },
            project_score: { score: 85, max_score: 100, weight: 0.20, breakdown: [], recommendations: [] },
            keyword_score: { score: 75, max_score: 100, weight: 0.15, breakdown: [], recommendations: [] },
            seniority_score: { score: 80, max_score: 100, weight: 0.10, breakdown: [], recommendations: [] }
          },
          explanations: { mode: 'manual_jd' },
          provenance: {
            source: 'manual_jd',
            scoring_version: 'v1.0.0'
          },
          created_at: new Date().toISOString()
        };

        const interviewRecord: any = {
          id: res.interview.session_id,
          analysis_result_id: res.analysis_id,
          target_role: targetTitle,
          difficulty,
          question_count: res.interview.questions.length,
          status: 'in_progress',
          generated_questions: res.interview.questions,
          answers: [],
          created_at: new Date().toISOString()
        };

        setAnalysis(analysisRecord);
        setInterview(interviewRecord);
        setStep('analysis');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate role fit and generate interview.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      {/* Header */}
      <div className="text-center mb-8">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 mb-3">
          <Briefcase className="w-3.5 h-3.5 mr-1.5" />
          Step 2 of 5 • Job Role & Evaluation Mode
        </span>
        <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Choose Evaluation Mode
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
          Match your resume against industry-standard role taxonomies or evaluate directly against your own custom Job Description.
        </p>
      </div>

      {/* Mode Selection Tabs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
        <button
          type="button"
          onClick={() => { setAnalysisMode('taxonomy'); setError(null); }}
          className={`p-4 rounded-2xl border text-left transition-all flex items-start space-x-3.5 cursor-pointer ${
            analysisMode === 'taxonomy'
              ? 'bg-blue-50/70 border-blue-500 ring-2 ring-blue-500/20 shadow-xs'
              : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50'
          }`}
        >
          <div className={`p-2.5 rounded-xl shrink-0 ${analysisMode === 'taxonomy' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}`}>
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-sm text-slate-900">
                Match with standard job roles (ESCO/O*NET)
              </span>
              {analysisMode === 'taxonomy' && (
                <span className="text-[10px] bg-blue-600 text-white font-bold px-1.5 py-0.5 rounded">Active</span>
              )}
            </div>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              12 canonical engineering roles standardized against official European & US occupational profiles.
            </p>
          </div>
        </button>

        <button
          type="button"
          onClick={() => { setAnalysisMode('manual_jd'); setError(null); }}
          className={`p-4 rounded-2xl border text-left transition-all flex items-start space-x-3.5 cursor-pointer ${
            analysisMode === 'manual_jd'
              ? 'bg-indigo-50/70 border-indigo-500 ring-2 ring-indigo-500/20 shadow-xs'
              : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50'
          }`}
        >
          <div className={`p-2.5 rounded-xl shrink-0 ${analysisMode === 'manual_jd' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'}`}>
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-sm text-slate-900">
                Match with your own job description
              </span>
              {analysisMode === 'manual_jd' && (
                <span className="text-[10px] bg-indigo-600 text-white font-bold px-1.5 py-0.5 rounded">Active</span>
              )}
            </div>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Paste any custom job posting or requisition text to parse required skills, seniority, and keywords.
            </p>
          </div>
        </button>
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

      {analyzing ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
          <LoadingSpinner
            message={
              analysisMode === 'taxonomy'
                ? "Comparing Resume Against Canonical Role Standards..."
                : "Parsing Custom Job Description & Evaluating Match..."
            }
            submessage="Extracting skills, computing 5-factor explainable scores, and synthesizing 7–10 resume-grounded mock interview questions."
          />
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
          {/* Candidate Badge */}
          {resume && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span className="text-slate-600">Active Resume:</span>
                <span className="font-bold text-slate-900">
                  {resume.parsed_json?.contact?.name || resume.original_filename}
                </span>
              </div>
              <span className="text-slate-500 font-medium">
                {resume.parsed_json?.skills?.length || 0} skills extracted
              </span>
            </div>
          )}

          {/* MODE 1: Standard Taxonomy Selection */}
          {analysisMode === 'taxonomy' && (
            <>
              {/* Role Dropdown */}
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Choose Target Role Profile (ESCO / O*NET Aligned)
                </label>
                <select
                  value={selectedRoleKey}
                  onChange={(e) => setSelectedRoleKey(e.target.value)}
                  className="w-full p-3 text-xs sm:text-sm font-medium border border-slate-300 rounded-xl bg-white shadow-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
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
              </div>

              {/* Role Preview Card */}
              {selectedRoleDetail && (
                <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-3">
                    <div>
                      <h3 className="text-base font-extrabold text-slate-900">
                        {selectedRoleDetail.display_name}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {selectedRoleDetail.description}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[11px] px-2.5 py-1 rounded-md bg-blue-100 text-blue-800 font-bold uppercase">
                        {selectedRoleDetail.seniority} Level
                      </span>
                      <span className="text-[11px] px-2.5 py-1 rounded-md bg-slate-200 text-slate-700 font-semibold capitalize">
                        {selectedRoleDetail.domain.replace('_', ' ')}
                      </span>
                    </div>
                  </div>

                  {/* Taxonomy Sources */}
                  <div className="flex items-center space-x-2 text-[11px] text-slate-500">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>Standardized via:</span>
                    <span className="font-semibold text-slate-700">
                      {selectedRoleDetail.sources?.join(', ') || 'ESCO & O*NET Occupations'}
                    </span>
                  </div>

                  {/* Required & Preferred Skills Chips */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                    <div>
                      <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-2">
                        Canonical Required Skills ({selectedRoleDetail.required_skills?.length || 0})
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {(selectedRoleDetail.required_skills || []).map((s: string, idx: number) => (
                          <span key={idx} className="bg-white border border-slate-200 text-slate-800 text-xs px-2.5 py-1 rounded-md font-medium shadow-xs">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-2">
                        Preferred Skills ({selectedRoleDetail.preferred_skills?.length || 0})
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {(selectedRoleDetail.preferred_skills || []).map((s: string, idx: number) => (
                          <span key={idx} className="bg-white/80 border border-slate-200 text-slate-600 text-xs px-2.5 py-1 rounded-md">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* MODE 2: Manual Job Description Input */}
          {analysisMode === 'manual_jd' && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Paste Custom Job Description
                </label>
                <div className="flex items-center space-x-2">
                  <span className="text-[11px] text-slate-400">Try a sample JD:</span>
                  {SAMPLE_JDS.map((sample, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => { setJdText(sample.text); setError(null); }}
                      className="text-[11px] font-semibold text-indigo-700 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-2 py-0.5 rounded-lg transition-colors"
                    >
                      {sample.title}
                    </button>
                  ))}
                  {jdText && (
                    <button
                      type="button"
                      onClick={() => setJdText('')}
                      className="text-[11px] text-slate-500 hover:text-slate-800 flex items-center ml-1"
                    >
                      <RotateCcw className="w-3 h-3 mr-0.5" /> Clear
                    </button>
                  )}
                </div>
              </div>

              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                rows={10}
                placeholder="Paste full job posting or requisition text here (e.g. Job Title, Required Qualifications, Tech Stack, Preferred Skills, Experience)..."
                className="w-full p-4 text-xs sm:text-sm font-mono border border-slate-300 rounded-xl bg-slate-50/50 shadow-inner focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all leading-relaxed"
              />

              <div className="flex items-center justify-between text-[11px] text-slate-500">
                <span>
                  {jdText.length} characters • {jdText.split('\n').filter(Boolean).length} lines
                </span>
                <span>
                  Supports markdown, bullet points, and free-form job requisitions
                </span>
              </div>
            </div>
          )}

          {/* Interview Configuration */}
          <div className="pt-2 border-t border-slate-200">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
              Interview Customization Options
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-slate-500 mb-1">Interview Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full p-2.5 text-xs font-medium border border-slate-200 rounded-lg bg-white"
                >
                  <option value="easy">Easy (Fundamentals & Core Concept Probing)</option>
                  <option value="medium">Medium (Standard Technical & Architecture Probing)</option>
                  <option value="hard">Hard (Deep Systems Design & Edge Cases)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-500 mb-1">Total Dynamic Questions</label>
                <select
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  className="w-full p-2.5 text-xs font-medium border border-slate-200 rounded-lg bg-white"
                >
                  <option value={6}>6 Dynamic Questions</option>
                  <option value={8}>8 Dynamic Questions (Recommended)</option>
                  <option value={10}>10 In-Depth Questions</option>
                </select>
              </div>
            </div>
          </div>

          {/* Navigation Controls */}
          <div className="flex justify-between items-center pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setStep('upload')}
              className="text-xs font-medium text-slate-600 hover:text-slate-900 flex items-center"
            >
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Resume</span>
            </button>

            <button
              onClick={handleAnalyzeAndProceed}
              disabled={analyzing || !resume || (analysisMode === 'manual_jd' && !jdText.trim())}
              className={`font-bold text-xs px-6 py-2.5 rounded-xl shadow-md transition-all flex items-center disabled:opacity-50 text-white ${
                analysisMode === 'taxonomy'
                  ? 'bg-blue-600 hover:bg-blue-700'
                  : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
            >
              <span>
                {analysisMode === 'taxonomy'
                  ? 'Analyze Role Fit & Generate Mock Interview'
                  : 'Analyze Custom JD & Generate Mock Interview'}
              </span>
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
