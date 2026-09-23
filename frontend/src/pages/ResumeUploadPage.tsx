import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { uploadResume, getResume } from '../api/client';
import { LoadingSpinner } from '../components/LoadingSpinner';
import {
  Upload,
  FileCheck,
  AlertCircle,
  ArrowRight,
  Briefcase,
  User,
  GraduationCap,
  Sparkles,
  CheckCircle
} from 'lucide-react';

export const ResumeUploadPage: React.FC = () => {
  const { resume, setResume, setStep } = useApp();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const res = await uploadResume(file, false);
      const detail = await getResume(res.resume_id);
      setResume(detail);
    } catch (err: any) {
      setError(err.message || 'Failed to upload and parse resume.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async () => {
    setLoading(true);
    setError(null);
    try {
      // Create a mock File representing the clean backend fixture
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
      const sampleFile = new File([blob], 'alex_morgan_resume.pdf', { type: 'application/pdf' });
      const res = await uploadResume(sampleFile, false);
      const detail = await getResume(res.resume_id);
      setResume(detail);
    } catch (err: any) {
      setError(err.message || 'Failed to load sample resume.');
    } finally {
      setLoading(false);
    }
  };

  const parsed = resume?.parsed_json;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Step 1: Upload Your Resume
        </h2>
        <p className="mt-2 text-sm text-slate-600 max-w-xl mx-auto">
          Upload your resume in PDF or DOCX format. The system automatically segments sections,
          extracts entities with evidence preservation, and maps skills to canonical ESCO/O*NET taxonomies.
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

      {/* Upload Box */}
      {!resume && (
        <div className="space-y-4">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all bg-white ${
              dragOver ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 hover:border-slate-400'
            }`}
          >
            {loading ? (
              <LoadingSpinner
                message="Extracting Resume Text & Normalizing Taxonomies..."
                submessage="PyMuPDF is cleaning text, spaCy is tagging entities, and ESCO is resolving canonical skills."
              />
            ) : (
              <>
                <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-8 h-8" />
                </div>
                <h3 className="text-base font-bold text-slate-900 mb-1">
                  Drag and drop your resume file here
                </h3>
                <p className="text-xs text-slate-500 mb-4">
                  Supports PDF and DOCX up to 10MB
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                  <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-5 py-2.5 rounded-lg shadow-sm transition-colors">
                    <span>Select Resume File</span>
                    <input
                      type="file"
                      accept=".pdf,.docx"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>

                  <span className="text-xs text-slate-400">or</span>

                  <button
                    type="button"
                    onClick={handleLoadSample}
                    className="bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-xs px-4 py-2.5 rounded-lg transition-colors flex items-center"
                  >
                    <Sparkles className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
                    Load Pre-Built Sample Resume
                  </button>
                </div>

                {file && (
                  <div className="mt-4 p-3 bg-blue-50/70 border border-blue-200 rounded-lg inline-flex items-center text-xs text-blue-900">
                    <FileCheck className="w-4 h-4 mr-2 text-blue-600" />
                    <span className="font-semibold mr-2">{file.name}</span>
                    <span className="text-slate-500">({(file.size / 1024).toFixed(1)} KB)</span>
                  </div>
                )}
              </>
            )}
          </div>

          {file && !loading && (
            <div className="flex justify-end">
              <button
                onClick={handleUpload}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm px-6 py-2.5 rounded-xl shadow-md transition-all flex items-center"
              >
                <span>Parse Resume</span>
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Parsed Resume Preview */}
      {resume && parsed && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
          <div className="flex flex-wrap items-center justify-between pb-4 border-b border-slate-200 gap-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center">
                <CheckCircle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base">
                  {parsed.contact.name || 'Candidate Resume'}
                </h3>
                <p className="text-xs text-slate-500">
                  {resume.original_filename} • Parsed & Canonically Normalized
                </p>
              </div>
            </div>

            <button
              onClick={() => setStep('role')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-5 py-2.5 rounded-lg shadow-sm transition-all flex items-center"
            >
              <span>Next: Select Target Role</span>
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </button>
          </div>

          {/* Contact Details */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs bg-slate-50 p-4 rounded-xl">
            <div>
              <span className="text-slate-400 uppercase font-bold text-[10px]">Email:</span>
              <div className="font-medium text-slate-800">{parsed.contact.email || 'N/A'}</div>
            </div>
            <div>
              <span className="text-slate-400 uppercase font-bold text-[10px]">Phone:</span>
              <div className="font-medium text-slate-800">{parsed.contact.phone || 'N/A'}</div>
            </div>
            <div>
              <span className="text-slate-400 uppercase font-bold text-[10px]">GitHub:</span>
              <div className="font-medium text-slate-800">{parsed.contact.github || 'N/A'}</div>
            </div>
          </div>

          {/* Professional Summary */}
          {parsed.summary && (
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Professional Summary
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed bg-slate-50/70 p-3 rounded-lg border border-slate-100">
                {parsed.summary}
              </p>
            </div>
          )}

          {/* Extracted Canonical Skills */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Extracted Canonical Skills ({parsed.skills.length})
              </h4>
              <span className="text-[11px] text-slate-400">Matched to ESCO / O*NET</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {parsed.skills.map((s, idx) => (
                <span
                  key={idx}
                  title={s.evidence.join(' | ')}
                  className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-800 border border-blue-200"
                >
                  {s.canonical_skill}
                  <span className="ml-1 text-[10px] text-blue-500 font-mono">
                    ({Math.round(s.confidence * 100)}%)
                  </span>
                </span>
              ))}
            </div>
          </div>

          {/* Experience Highlights */}
          {parsed.experience.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center">
                <Briefcase className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
                Work Experience ({parsed.experience.length})
              </h4>
              <div className="space-y-3 text-xs">
                {parsed.experience.map((exp, idx) => (
                  <div key={idx} className="border border-slate-100 rounded-lg p-3 bg-slate-50/40">
                    <div className="flex justify-between font-bold text-slate-900">
                      <span>{exp.job_title || 'Role'}</span>
                      <span className="text-slate-500 font-normal">
                        {exp.start_date} - {exp.end_date}
                      </span>
                    </div>
                    {exp.organization && (
                      <div className="text-slate-600 text-[11px] mb-1.5">{exp.organization}</div>
                    )}
                    <ul className="space-y-1 text-slate-600 mt-1">
                      {exp.bullets.map((b, bIdx) => (
                        <li key={bIdx} className="flex items-start">
                          <span className="mr-1.5 text-slate-400">•</span>
                          <span>{b}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects */}
          {parsed.projects.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                Key Projects ({parsed.projects.length})
              </h4>
              <div className="space-y-2 text-xs">
                {parsed.projects.map((proj, idx) => (
                  <div key={idx} className="border border-slate-100 rounded-lg p-3 bg-slate-50/40">
                    <div className="font-bold text-slate-900 mb-1">{proj.title}</div>
                    {proj.description && <p className="text-slate-600 mb-1.5">{proj.description}</p>}
                    {proj.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {proj.technologies.map((t, tIdx) => (
                          <span key={tIdx} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[10px]">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action to proceed to next step */}
          <div className="pt-4 border-t border-slate-200 flex justify-between items-center">
            <span className="text-xs text-slate-500 font-medium">
              ✓ Skills, experience, and projects extracted with sentence-level citations.
            </span>
            <button
              onClick={() => setStep('role')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-6 py-2.5 rounded-xl shadow-md transition-all flex items-center"
            >
              <span>Continue to Role Selection</span>
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
