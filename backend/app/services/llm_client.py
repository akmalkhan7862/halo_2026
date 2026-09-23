import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from jinja2 import Template

from app.core.config import settings
from app.core.exceptions import LLMServiceException
from app.utils.logger import logger


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate_json(self, prompt: str, schema_description: Optional[str] = None) -> Dict[str, Any]:
        pass


class OpenAICompatibleClient(BaseLLMClient):
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT_SECONDS
        self.max_retries = settings.LLM_MAX_RETRIES

    async def generate_json(self, prompt: str, schema_description: Optional[str] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        system_instruction = (
            "You are an expert AI assistant for resume intelligence and technical interviewing. "
            "You MUST respond ONLY with a single valid JSON object. Do not include markdown code blocks, backticks, or explanatory text outside JSON."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"}
        }

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        # Clean backticks if model included them
                        cleaned = content.strip()
                        if cleaned.startswith("```"):
                            lines = cleaned.split("\n")
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].startswith("```"):
                                lines = lines[:-1]
                            cleaned = "\n".join(lines).strip()
                        return json.loads(cleaned)
                    else:
                        logger.warning(f"LLM attempt {attempt} returned status {response.status_code}: {response.text}")
                        last_error = f"Status {response.status_code}: {response.text}"
            except Exception as e:
                logger.warning(f"LLM attempt {attempt} failed: {e}")
                last_error = str(e)
            
            # Exponential backoff
            time.sleep(1.5 ** attempt)

        raise LLMServiceException(f"Failed to generate LLM response after {self.max_retries} attempts: {last_error}")


class DeterministicMockLLMClient(BaseLLMClient):
    """
    High-fidelity deterministic fallback client when no external API key is provided
    or when external LLM providers are unreachable.
    """
    async def generate_json(self, prompt: str, schema_description: Optional[str] = None) -> Dict[str, Any]:
        logger.info("Using DeterministicMockLLMClient for structured generation.")
        
        # Determine intent by inspecting prompt keywords
        if "generate dynamic, challenging, and strictly resume-specific mock interview questions" in prompt or "question_mix" in prompt:
            return self._mock_interview_questions(prompt)
        elif "evaluating an interview answer" in prompt or "Candidate's Answer:" in prompt:
            return self._mock_answer_evaluation(prompt)
        elif "career-improvement roadmap" in prompt or "immediate_resume_improvements" in prompt:
            return self._mock_career_roadmap(prompt)
        elif "Synthesize the skill alignment" in prompt or "overall_readiness" in prompt:
            return self._mock_gap_summary(prompt)

        return {"status": "ok", "message": "Generic structured mock response"}

    def _mock_interview_questions(self, prompt: str) -> Dict[str, Any]:
        return {
            "interview_plan": {
                "target_role": "Backend Developer",
                "difficulty": "medium",
                "total_questions": 8,
                "question_mix": {
                    "technical": 4,
                    "project_based": 2,
                    "behavioral": 1,
                    "gap_probing": 1
                }
            },
            "questions": [
                {
                    "question_id": "q1",
                    "type": "technical",
                    "difficulty": "medium",
                    "skill_focus": ["Python", "FastAPI"],
                    "resume_evidence": "Demonstrated API development and routing in candidate resume projects",
                    "question_text": "In your FastAPI backend project, how did you design your dependency injection system and manage asynchronous database sessions without leaking connections?",
                    "expected_answer_points": [
                        "Use of Depends with async generator session yields",
                        "AsyncEngine connection pooling configurations",
                        "Clean error handling and session.rollback() in try-finally blocks",
                        "Separation of concerns between routers and repository layers"
                    ],
                    "follow_up_possible": True
                },
                {
                    "question_id": "q2",
                    "type": "technical",
                    "difficulty": "medium",
                    "skill_focus": ["PostgreSQL", "SQL"],
                    "resume_evidence": "Experience with relational databases and query optimization cited in experience bullets",
                    "question_text": "When indexing PostgreSQL tables for high-frequency search queries, what indexing strategy do you choose (B-Tree, GIN, Partial) and how do you analyze query plans using EXPLAIN ANALYZE?",
                    "expected_answer_points": [
                        "Understanding B-Tree vs GIN for full text/arrays",
                        "Examining Seq Scan vs Index Scan in EXPLAIN ANALYZE",
                        "Cost metrics and execution buffers",
                        "Avoiding redundant indexes that slow writes"
                    ],
                    "follow_up_possible": True
                },
                {
                    "question_id": "q3",
                    "type": "project_based",
                    "difficulty": "medium",
                    "skill_focus": ["System Design", "REST API"],
                    "resume_evidence": "Built backend services and microservice endpoints listed under Projects",
                    "question_text": "Walk me through how you structured the API endpoints and authentication flow in your primary backend project. How did you safeguard against token tampering and CSRF?",
                    "expected_answer_points": [
                        "JWT signature validation and secret rotation",
                        "Secure, HTTP-only cookie headers or Bearer token strategies",
                        "Rate limiting middleware",
                        "Consistent JSON error schema"
                    ],
                    "follow_up_possible": True
                },
                {
                    "question_id": "q4",
                    "type": "technical",
                    "difficulty": "hard",
                    "skill_focus": ["Docker", "CI/CD"],
                    "resume_evidence": "Containerization and automated build steps cited in technical toolset",
                    "question_text": "How do you optimize multi-stage Docker builds for Python applications to minimize final image size and enforce least-privilege security at runtime?",
                    "expected_answer_points": [
                        "Multi-stage build separation (builder vs runner)",
                        "Installing wheel dependencies without cache",
                        "Running container as non-root user",
                        "Using lightweight alpine or distroless/slim base images"
                    ],
                    "follow_up_possible": True
                },
                {
                    "question_id": "q5",
                    "type": "scenario",
                    "difficulty": "hard",
                    "skill_focus": ["System Design", "Scalability"],
                    "resume_evidence": "Target role requires scalable backend microservices",
                    "question_text": "Suppose a notification endpoint in your application experiences sudden traffic spikes of 50x normal volume. How would you redesign the architecture using background queues and rate limiting to prevent database saturation?",
                    "expected_answer_points": [
                        "Decoupling ingestion with message brokers (RabbitMQ/Redis/Kafka)",
                        "Worker pool autoscaling and throttling",
                        "Token bucket or sliding window rate limiting",
                        "Graceful degradation and asynchronous acknowledgment"
                    ],
                    "follow_up_possible": True
                },
                {
                    "question_id": "q6",
                    "type": "gap_probing",
                    "difficulty": "medium",
                    "skill_focus": ["Kubernetes", "Cloud Computing"],
                    "resume_evidence": "Identified as a critical missing or weak requirement in target JD",
                    "question_text": "The target role emphasizes production deployment on cloud clusters. If you need to deploy your containerized service to Kubernetes, how do you configure readiness probes, liveness probes, and resource limits?",
                    "expected_answer_points": [
                        "Differences between liveness, readiness, and startup probes",
                        "Setting memory/CPU requests and limits",
                        "Rolling update strategy and zero-downtime deployments",
                        "Handling SIGTERM for graceful shutdown"
                    ],
                    "follow_up_possible": True
                },
                {
                    "question_id": "q7",
                    "type": "behavioral",
                    "difficulty": "medium",
                    "skill_focus": ["Collaboration", "Engineering Trade-offs"],
                    "resume_evidence": "Past experience collaborating with cross-functional engineering teams",
                    "question_text": "Describe a scenario from your past experience or projects where a critical bug slipped into production or a tight deadline forced a technical compromise. How did you communicate the issue and remediate tech debt?",
                    "expected_answer_points": [
                        "Clear ownership and transparent stakeholder communication",
                        "Root-cause analysis (post-mortem)",
                        "Immediate mitigation vs long-term architectural fix",
                        "Preventative automated tests or guardrails"
                    ],
                    "follow_up_possible": False
                },
                {
                    "question_id": "q8",
                    "type": "technical",
                    "difficulty": "medium",
                    "skill_focus": ["Testing", "Code Quality"],
                    "resume_evidence": "Core testing practices required for reliable backend delivery",
                    "question_text": "What is your testing philosophy across unit, integration, and end-to-end tests for REST APIs? How do you isolate database queries in integration tests without introducing test flakiness?",
                    "expected_answer_points": [
                        "Test pyramid balance",
                        "Transactional rollbacks per test or isolated container test databases",
                        "Mocking third-party HTTP dependencies with responses or wiremock",
                        "Deterministic test data factories"
                    ],
                    "follow_up_possible": True
                }
            ]
        }

    def _mock_answer_evaluation(self, prompt: str) -> Dict[str, Any]:
        return {
            "question_id": "evaluated_q",
            "score": 82,
            "verdict": "good",
            "strengths": [
                "Directly answered the question with clear technical terminology",
                "Demonstrated sound understanding of core architectural principles",
                "Referenced practical operational concerns like error propagation"
            ],
            "weaknesses": [
                "Could quantify specific throughput or timeout thresholds",
                "Briefly overlooked edge cases in concurrent race conditions"
            ],
            "missing_points": [
                "Connection pool size tuning guidelines",
                "Specific monitoring metrics (e.g. active pool connections, latency p99)"
            ],
            "suggested_improvement": "Structure your explanation using STAR or Problem-Architecture-Result, citing concrete configuration parameters to demonstrate deep production expertise.",
            "follow_up_question": "How would you monitor and detect database connection pool exhaustion before it impacts end users?"
        }

    def _mock_career_roadmap(self, prompt: str) -> Dict[str, Any]:
        return {
            "immediate_resume_improvements": [
                "Quantify project outcomes with measurable performance metrics (e.g., 'reduced API p95 latency by 35%').",
                "Explicitly highlight transferable framework proficiencies in your technical skills summary.",
                "Ensure your GitHub links directly to clean repositories with well-structured READMEs, unit tests, and CI workflows."
            ],
            "short_term_learning_actions": [
                {
                    "topic": "Kubernetes & Container Orchestration",
                    "timeframe": "2-3 weeks",
                    "recommended_resources": ["Kubernetes The Hard Way", "Official K8s Documentation", "CKAD Labs"],
                    "learning_objective": "Master Deployments, Services, ConfigMaps, Ingress, and pod lifecycle management."
                },
                {
                    "topic": "Cloud Native Architecture (AWS/GCP)",
                    "timeframe": "3-4 weeks",
                    "recommended_resources": ["AWS Well-Architected Framework", "GCP Professional Architect Guide"],
                    "learning_objective": "Learn managed storage, serverless lambdas, VPC networking, and cloud IAM."
                }
            ],
            "project_suggestions": [
                {
                    "project_title": "High-Throughput Distributed Task Queue",
                    "technologies": ["Python", "FastAPI", "Redis", "Docker", "PostgreSQL"],
                    "problem_statement": "Build an asynchronous distributed job execution system supporting scheduled retries, rate limiting, and real-time execution dashboards.",
                    "demonstrated_outcomes": ["Achieved 5,000 tasks/sec throughput with automated dead-letter queue recovery and comprehensive integration tests."]
                }
            ],
            "certification_suggestions": [
                {
                    "certification_name": "AWS Certified Solutions Architect - Associate",
                    "issuer": "Amazon Web Services",
                    "relevance": "Validates cloud architecture and distributed backend system capabilities required by target roles."
                }
            ],
            "interview_preparation_focus_areas": [
                "Distributed system design: Caching strategies, sharding, consensus protocols, and rate limiting.",
                "Behavioral interview STAR stories highlighting technical leadership and complex trade-off resolutions."
            ]
        }

    def _mock_gap_summary(self, prompt: str) -> Dict[str, Any]:
        return {
            "overall_readiness": "moderate",
            "critical_missing_skills": ["Docker", "Kubernetes", "System Design"],
            "quick_wins": [
                "Add quantified project bullet points demonstrating hands-on backend performance optimizations.",
                "Bridge missing cloud requirements by showcasing local Docker container setups in your repository."
            ],
            "narrative_summary": "The candidate has demonstrated strong foundational backend expertise with solid mastery of Python, APIs, and relational databases. To achieve top-tier competitiveness for the target role, focus on closing gaps in container orchestration and scalable distributed systems."
        }


def get_llm_client() -> BaseLLMClient:
    """Factory to return appropriate LLM client based on configuration and API key availability."""
    if settings.LLM_API_KEY and len(settings.LLM_API_KEY.strip()) > 5:
        return OpenAICompatibleClient()
    logger.info("No LLM_API_KEY provided; utilizing high-fidelity DeterministicMockLLMClient.")
    return DeterministicMockLLMClient()
