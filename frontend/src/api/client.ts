import {
  ResumeRecord,
  JDRecord,
  AnalysisRecord,
  InterviewSessionRecord,
  AnswerEvaluation,
  FinalReportRecord,
  RoleFitInterviewResponse
} from '../types';

const API_BASE = '/api/v1';

export async function uploadResume(file: File, asyncProcessing = false): Promise<{ resume_id: string; status: string; message: string }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('async_processing', String(asyncProcessing));

  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(errorData.detail || 'Resume upload failed');
  }
  return res.json();
}

export async function getResume(id: string): Promise<ResumeRecord> {
  const res = await fetch(`${API_BASE}/resumes/${id}`);
  if (!res.ok) throw new Error('Failed to retrieve resume details');
  return res.json();
}

export async function createJobDescription(data: {
  title?: string;
  company?: string;
  rawText?: string;
  url?: string;
  file?: File;
}): Promise<JDRecord> {
  const formData = new FormData();
  if (data.title) formData.append('title', data.title);
  if (data.company) formData.append('company', data.company);
  if (data.rawText) formData.append('raw_text', data.rawText);
  if (data.url) formData.append('url', data.url);
  if (data.file) formData.append('file', data.file);

  const res = await fetch(`${API_BASE}/job-descriptions`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to create Job Description' }));
    throw new Error(err.detail || 'Failed to create Job Description');
  }
  return res.json();
}

export async function runAnalysis(params: {
  resumeId: string;
  jobDescriptionId: string;
  targetRole?: string;
}): Promise<AnalysisRecord> {
  const res = await fetch(`${API_BASE}/analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_id: params.resumeId,
      job_description_id: params.jobDescriptionId,
      target_role: params.targetRole,
      taxonomy_sources: ['esco', 'onet', 'custom'],
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail || 'Analysis execution failed');
  }
  return res.json();
}

export async function getAnalysis(id: string): Promise<AnalysisRecord> {
  const res = await fetch(`${API_BASE}/analysis/${id}`);
  if (!res.ok) throw new Error('Failed to retrieve analysis');
  return res.json();
}

export async function createInterview(params: {
  analysisId: string;
  questionCount?: number;
  difficulty?: string;
}): Promise<InterviewSessionRecord> {
  const res = await fetch(`${API_BASE}/interviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      analysis_id: params.analysisId,
      question_count: params.questionCount || 8,
      difficulty: params.difficulty || 'medium',
      interview_type: 'technical_behavioral_mixed',
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Interview creation failed' }));
    throw new Error(err.detail || 'Interview creation failed');
  }
  return res.json();
}

export async function getInterview(id: string): Promise<InterviewSessionRecord> {
  const res = await fetch(`${API_BASE}/interviews/${id}`);
  if (!res.ok) throw new Error('Failed to fetch interview session');
  return res.json();
}

export async function submitAnswer(interviewId: string, questionId: string, answerText: string): Promise<AnswerEvaluation> {
  const res = await fetch(`${API_BASE}/interviews/${interviewId}/answers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question_id: questionId,
      answer_text: answerText,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Answer evaluation failed' }));
    throw new Error(err.detail || 'Answer submission failed');
  }
  return res.json();
}

export async function completeInterview(interviewId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/interviews/${interviewId}/complete`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to complete interview');
  return res.json();
}

export async function getFinalReport(analysisId: string): Promise<FinalReportRecord> {
  const res = await fetch(`${API_BASE}/reports/${analysisId}`);
  if (!res.ok) throw new Error('Failed to retrieve final report');
  return res.json();
}

export function getReportDownloadUrl(analysisId: string): string {
  return `${API_BASE}/reports/${analysisId}/download`;
}

export async function getTargetRoles(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/roles`);
  if (!res.ok) throw new Error('Failed to load target roles');
  return res.json();
}

export async function getTargetRoleDetail(roleKey: string): Promise<any> {
  const res = await fetch(`${API_BASE}/roles/${roleKey}`);
  if (!res.ok) throw new Error(`Failed to load role details for ${roleKey}`);
  return res.json();
}

export async function analyzeResumeAgainstRoles(resumeId: string, roleKey?: string): Promise<any> {
  const res = await fetch(`${API_BASE}/roles/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_id: resumeId,
      target_role_key: roleKey || 'all',
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Role analysis failed' }));
    throw new Error(err.detail || 'Role analysis failed');
  }
  return res.json();
}

export async function analyzeRoleFitWithInterview(
  resumeId: string,
  roleKey: string,
  difficulty: string = 'medium',
  questionCount: number = 8
): Promise<RoleFitInterviewResponse> {
  const res = await fetch(`${API_BASE}/analysis/role-fit-with-interview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_id: resumeId,
      role_key: roleKey,
      difficulty,
      question_count: questionCount,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Role analysis and interview generation failed' }));
    throw new Error(err.detail || 'Role analysis and interview generation failed');
  }
  return res.json();
}

export async function analyzeManualJD(
  resumeId: string,
  jdText: string,
  difficulty: string = 'medium',
  questionCount: number = 8
): Promise<RoleFitInterviewResponse> {
  const res = await fetch(`${API_BASE}/analysis/manual-jd`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_id: resumeId,
      jd_text: jdText,
      difficulty,
      question_count: questionCount,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Manual JD analysis and interview generation failed' }));
    throw new Error(err.detail || 'Manual JD analysis and interview generation failed');
  }
  return res.json();
}

export async function getSkillGapAnalysis(analysisId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/analysis/${analysisId}/gap`);
  if (!res.ok) throw new Error('Failed to retrieve skill gap analysis');
  return res.json();
}

export async function getLearningRoadmap(analysisId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/analysis/${analysisId}/roadmap`);
  if (!res.ok) throw new Error('Failed to retrieve learning roadmap');
  return res.json();
}


