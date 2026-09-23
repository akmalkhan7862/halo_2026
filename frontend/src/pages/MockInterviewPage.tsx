import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { submitAnswer, completeInterview, getFinalReport } from '../api/client';
import { QuestionCard } from '../components/QuestionCard';
import { AnswerFeedback } from '../components/AnswerFeedback';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { AnswerEvaluation } from '../types';
import {
  Send,
  ArrowRight,
  CheckCircle,
  HelpCircle,
  Award,
  Sparkles,
  AlertCircle
} from 'lucide-react';

export const MockInterviewPage: React.FC = () => {
  const { interview, setInterview, analysis, setReport, setStep } = useApp();
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answerText, setAnswerText] = useState('');
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [evaluations, setEvaluations] = useState<Record<string, AnswerEvaluation>>({});
  const [error, setError] = useState<string | null>(null);

  if (!interview || !interview.generated_questions || interview.generated_questions.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center text-slate-500">
        No active interview session. Please run gap analysis and start an interview first.
      </div>
    );
  }

  const questions = interview.generated_questions;
  const currentQ = questions[currentIdx];
  const currentEval = evaluations[currentQ.question_id];

  const handleAnswerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answerText.trim() || answerText.trim().length < 5) return;
    setEvaluating(true);
    setError(null);

    try {
      const evaluation = await submitAnswer(
        interview.id,
        currentQ.question_id,
        answerText.trim()
      );
      setEvaluations((prev) => ({
        ...prev,
        [currentQ.question_id]: evaluation,
      }));
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate answer.');
    } finally {
      setEvaluating(false);
    }
  };

  const handleNext = () => {
    setAnswerText('');
    setError(null);
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    }
  };

  const handleCompleteInterview = async () => {
    setCompleting(true);
    setError(null);
    try {
      await completeInterview(interview.id);
      if (analysis) {
        const finalReport = await getFinalReport(analysis.id);
        setReport(finalReport);
        setStep('report');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to complete interview session.');
    } finally {
      setCompleting(false);
    }
  };

  const totalAnswered = Object.keys(evaluations).length;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      {/* Session Progress Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 mb-6">
        <div>
          <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">
            Step 4 of 5 • Dynamic Simulation
          </span>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
            Target Role: {interview.target_role}
          </h2>
          <p className="text-xs text-slate-500">
            Difficulty: <span className="capitalize font-semibold">{interview.difficulty}</span> •
            Progress: {totalAnswered} of {questions.length} answered
          </p>
        </div>

        <button
          onClick={handleCompleteInterview}
          disabled={completing}
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-sm transition-all flex items-center"
        >
          {completing ? (
            <span>Generating Report...</span>
          ) : (
            <>
              <Award className="w-4 h-4 mr-1.5" />
              <span>Finish & View Report</span>
            </>
          )}
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

      {/* Question Selector Tabs */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-3 mb-4">
        {questions.map((q, idx) => {
          const isAnswered = !!evaluations[q.question_id];
          const isCurrent = idx === currentIdx;

          return (
            <button
              key={q.question_id}
              onClick={() => {
                setCurrentIdx(idx);
                setAnswerText('');
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold shrink-0 transition-all flex items-center ${
                isCurrent
                  ? 'bg-blue-600 text-white shadow-xs'
                  : isAnswered
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <span>Q{idx + 1}</span>
              {isAnswered && <CheckCircle className="w-3 h-3 ml-1 text-emerald-600" />}
            </button>
          );
        })}
      </div>

      {/* Current Question Card */}
      <QuestionCard question={currentQ} index={currentIdx} total={questions.length} />

      {/* Answer Form (if not yet answered) */}
      {!currentEval && (
        <form onSubmit={handleAnswerSubmit} className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Your Answer / Explanation:
            </label>
            <textarea
              required
              rows={6}
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              placeholder="Type your response thoroughly. Reference concrete project metrics, trade-offs, and technical rationale..."
              className="w-full p-3 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-sans leading-relaxed"
            />
            <div className="flex items-center justify-between pt-3 text-xs text-slate-500 border-t border-slate-100 mt-2">
              <span>Aim for clarity, system design reasoning, and quantifiable outcomes.</span>
              <button
                type="submit"
                disabled={evaluating || answerText.trim().length < 5}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-5 py-2 rounded-lg shadow-sm transition-all flex items-center disabled:opacity-50"
              >
                {evaluating ? (
                  <span>Evaluating Answer...</span>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5 mr-1.5" />
                    <span>Submit Answer</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Real-time Evaluation Card */}
      {currentEval && (
        <div className="space-y-4">
          <AnswerFeedback evaluation={currentEval} />

          <div className="flex justify-between items-center">
            <button
              onClick={() => {
                const nextEvals = { ...evaluations };
                delete nextEvals[currentQ.question_id];
                setEvaluations(nextEvals);
              }}
              className="text-xs text-slate-500 hover:text-slate-800"
            >
              Retry Answer
            </button>

            {currentIdx < questions.length - 1 ? (
              <button
                onClick={handleNext}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-md transition-all flex items-center"
              >
                <span>Next Question (Q{currentIdx + 2})</span>
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </button>
            ) : (
              <button
                onClick={handleCompleteInterview}
                disabled={completing}
                className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-6 py-2.5 rounded-lg shadow-md transition-all flex items-center"
              >
                <Award className="w-4 h-4 mr-1.5" />
                <span>Complete Interview & Generate Final Report</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
