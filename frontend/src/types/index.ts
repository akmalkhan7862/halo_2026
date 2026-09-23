export interface ContactInfo {
  name?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  location?: string;
}

export interface ExtractedSkill {
  raw_text: string;
  canonical_skill: string;
  taxonomy_source: string;
  taxonomy_id?: string;
  confidence: number;
  evidence: string[];
}

export interface ExtractedExperience {
  job_title?: string;
  organization?: string;
  start_date?: string;
  end_date?: string;
  duration_months?: number;
  bullets: string[];
  skills: string[];
}

export interface ExtractedProject {
  title: string;
  description?: string;
  technologies: string[];
  outcomes: string[];
  skills: string[];
}

export interface ParsedResume {
  contact: ContactInfo;
  summary?: string;
  skills: ExtractedSkill[];
  unmapped_skills: string[];
  experience: ExtractedExperience[];
  projects: ExtractedProject[];
  extracted_keywords: string[];
  raw_text_length: number;
}

export interface ResumeRecord {
  id: string;
  original_filename: string;
  file_type: string;
  status: string;
  parsed_json?: ParsedResume;
  created_at: string;
}

export interface JDSkillRequirement {
  raw_text: string;
  canonical_skill: string;
  importance: 'required' | 'preferred';
  confidence: number;
}

export interface ParsedJD {
  job_title: string;
  company?: string;
  seniority: string;
  required_skills: JDSkillRequirement[];
  preferred_skills: JDSkillRequirement[];
  responsibilities: string[];
  qualifications: string[];
  keywords: string[];
  experience_requirements: {
    minimum_years: number;
    maximum_years?: number;
    detected_from_text: boolean;
  };
  domain: string;
}

export interface JDRecord {
  id: string;
  title: string;
  company?: string;
  parsed_json?: ParsedJD;
  created_at: string;
}

export interface SkillClassificationItem {
  canonical_skill: string;
  raw_text?: string;
  status: 'MATCHED' | 'WEAK' | 'MISSING' | 'RELATED_PARTIAL' | 'EXTRA';
  importance?: 'required' | 'preferred' | 'extra';
  confidence: number;
  evidence_citation?: string;
  related_to?: string;
  reason: string;
}

export interface GapSummary {
  overall_readiness: 'high' | 'moderate' | 'low' | string;
  overall_fit?: 'high' | 'moderate' | 'low' | string;
  critical_missing_skills: string[];
  top_missing_skills?: string[];
  quick_wins: string[];
  recommended_focus_areas?: string[];
  narrative_summary: string;
  coverage_ratio?: number;
}

export interface ScoreBreakdownItem {
  reason: string;
  impact: string;
}

export interface ComponentScore {
  score: number;
  max_score: number;
  weight: number;
  breakdown: ScoreBreakdownItem[];
  recommendations: string[];
}

export interface OverallScores {
  overall_score: number;
  overall_breakdown?: ScoreBreakdownItem[];
  skill_match_score: ComponentScore;
  experience_score: ComponentScore;
  project_score: ComponentScore;
  keyword_score: ComponentScore;
  seniority_score: ComponentScore;
}

export interface AnalysisRecord {
  id: string;
  resume_id: string;
  job_description_id?: string;
  role_key?: string | null;
  mode?: 'taxonomy_role' | 'manual_jd';
  role_display_name?: string;
  target_role: string;
  matched_skills: SkillClassificationItem[];
  weak_skills: SkillClassificationItem[];
  missing_skills: SkillClassificationItem[];
  related_partial_skills: SkillClassificationItem[];
  extra_skills: string[];
  gap_summary: GapSummary;
  gap_analysis?: SkillGapAnalysis;
  learning_roadmap?: PersonalizedRoadmap;
  scores: OverallScores;
  explanations: Record<string, any>;
  provenance: Record<string, any>;
  created_at: string;
}

export interface InterviewQuestion {
  question_id: string;
  type: 'technical' | 'project_based' | 'behavioral' | 'gap_probing' | 'scenario';
  difficulty: string;
  skill_focus: string[];
  resume_evidence?: string;
  question_text: string;
  expected_answer_points: string[];
  follow_up_possible: boolean;
  follow_up_hint?: string;
}

export interface AnswerEvaluation {
  question_id: string;
  score: number;
  verdict: 'exceptional' | 'good' | 'adequate' | 'weak' | 'unsatisfactory';
  strengths: string[];
  weaknesses: string[];
  missing_points: string[];
  suggested_improvement: string;
  follow_up_question?: string;
}

export interface AnswerRecord {
  id: string;
  question_id: string;
  question_text: string;
  answer_text: string;
  score?: number;
  evaluation_json?: AnswerEvaluation;
  created_at: string;
}

export interface InterviewSessionRecord {
  id: string;
  analysis_result_id: string;
  target_role: string;
  difficulty: string;
  question_count: number;
  status: string;
  interview_plan?: Record<string, any>;
  generated_questions: InterviewQuestion[];
  answers: AnswerRecord[];
  overall_score?: number;
  summary_feedback?: Record<string, any>;
  created_at: string;
}

export interface ShortTermAction {
  topic: string;
  timeframe: string;
  recommended_resources: string[];
  learning_objective: string;
}

export interface ProjectSuggestion {
  project_title: string;
  technologies: string[];
  problem_statement: string;
  demonstrated_outcomes: string[];
}

export interface CertificationSuggestion {
  certification_name: string;
  issuer: string;
  relevance: string;
}

export interface CareerRoadmap {
  immediate_resume_improvements: string[];
  short_term_learning_actions: ShortTermAction[];
  project_suggestions: ProjectSuggestion[];
  certification_suggestions: CertificationSuggestion[];
  interview_preparation_focus_areas: string[];
}

export interface ResumeFitScores {
  skill_match_score: number;
  experience_score: number;
  project_score: number;
  keyword_score: number;
  seniority_score: number;
  overall_resume_score: number;
}

export interface ResumeFitReport {
  role_key?: string;
  display_name: string;
  scores: ResumeFitScores;
  gap_summary: {
    overall_fit: string;
    narrative_summary: string;
    top_missing_skills: string[];
    quick_wins: string[];
    recommended_focus_areas: string[];
  };
}

export interface CommunicationFeedback {
  strengths: string[];
  improvements: string[];
}

export interface InterviewPerformanceReport {
  overall_interview_score: number;
  dimension_scores: {
    technical_accuracy: number;
    relevance: number;
    completeness: number;
    structure_and_clarity: number;
    communication: number;
  };
  question_count: number;
  answered_count: number;
  score_distribution: {
    strong: number;
    good: number;
    moderate: number;
    weak: number;
  };
  key_strengths: string[];
  key_weaknesses: string[];
  recommendations: string[];
  communication_feedback: CommunicationFeedback;
}

export interface FinalReportRecord {
  analysis_id: string;
  generated_at: string;
  candidate_profile: {
    contact?: ContactInfo;
    summary?: string;
    skills_count: number;
    projects_count: number;
    experience_count: number;
  };
  target_job: {
    title: string;
    company?: string;
    seniority: string;
    domain: string;
  };
  resume_fit?: ResumeFitReport;
  interview_performance?: InterviewPerformanceReport;
  analysis: AnalysisRecord;
  interview_session?: InterviewSessionRecord;
  roadmap: CareerRoadmap;
  gap_analysis?: SkillGapAnalysis;
  learning_roadmap?: PersonalizedRoadmap;
}

export interface SkillGapDetail {
  skill: string;
  importance: 'required' | 'preferred';
  status: 'matched' | 'weak' | 'missing' | 'related_partial';
  evidence: string[];
  explanation: string;
  related_to?: string;
}

export interface SkillGapAnalysis {
  role_key: string;
  display_name: string;
  coverage_ratio: number;
  required_coverage: number;
  preferred_coverage: number;
  skill_gap_details: SkillGapDetail[];
  critical_missing_skills: string[];
  quick_wins: string[];
  gap_narrative: string;
}

export interface RoadmapResource {
  type: 'course' | 'docs' | 'book' | 'tutorial' | string;
  title: string;
  url: string;
}

export interface PrioritySkillRoadmap {
  skill: string;
  why_it_matters: string;
  resources: RoadmapResource[];
  project_task: string;
  estimated_effort: string;
  success_criteria: string[];
}

export interface LearningRoadmapContent {
  priority_skills: PrioritySkillRoadmap[];
  suggested_sequence: string[];
  general_advice: string[];
}

export interface PersonalizedRoadmap {
  role_key: string;
  display_name: string;
  learning_roadmap: LearningRoadmapContent;
}

export interface TargetRoleSummary {
  id: string;
  role_key: string;
  display_name: string;
  seniority: string;
  domain: string;
  description: string;
  required_skills_count: number;
  preferred_skills_count: number;
}

export interface TargetRoleDetail extends TargetRoleSummary {
  required_skills: string[];
  preferred_skills: string[];
  sources: string[];
}

export interface RoleFitInterviewResponse {
  analysis_id: string;
  mode?: 'taxonomy_role' | 'manual_jd';
  role_key?: string | null;
  display_name: string;
  role_display_name?: string;
  target_role?: string;
  matched_skills: SkillClassificationItem[];
  missing_skills: SkillClassificationItem[];
  weak_skills: SkillClassificationItem[];
  extra_skills: string[];
  coverage_ratio: number;
  gap_summary: GapSummary;
  gap_analysis?: SkillGapAnalysis;
  learning_roadmap?: PersonalizedRoadmap;
  scores?: OverallScores;
  interview: {
    session_id: string;
    questions: InterviewQuestion[];
  };
}
