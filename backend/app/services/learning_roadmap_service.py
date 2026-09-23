from typing import Dict, Any, List, Optional


class LearningRoadmapService:
    """
    Generates a personalized, prioritized, resume-grounded learning roadmap
    focused on candidate's missing and weak skills for the target role.
    """

    # Curated knowledge base of canonical resources and best practices
    SKILL_RESOURCE_CATALOG: Dict[str, Dict[str, Any]] = {
        "docker": {
            "why_it_matters": "Containerization is standard for modern deployments. Backend interviewers expect you to know how to containerize applications, manage multi-stage builds, and configure environments reproducibly.",
            "resources": [
                {"type": "course", "title": "Docker for Developers – freeCodeCamp Course", "url": "https://www.freecodecamp.org/news/docker-for-developers-free-course/"},
                {"type": "docs", "title": "Official Docker Documentation & Getting Started", "url": "https://docs.docker.com/get-started/"},
                {"type": "book", "title": "Docker in Action (Manning)", "url": "https://www.manning.com/books/docker-in-action-second-edition"}
            ],
            "task_template": "Containerize your '{project_title}' service using a multi-stage Dockerfile that minimizes image size, and write a docker-compose.yml file to orchestrate the app and its database with health checks.",
            "effort": "1–2 weeks, 5–7 hours/week",
            "success_criteria": [
                "Your application and database start cleanly with a single 'docker compose up' command.",
                "Multi-stage Dockerfile produces an image under 150MB with non-root security execution.",
                "You can sketch the container networking and volume persistence model on an interview whiteboard."
            ]
        },
        "ci/cd": {
            "why_it_matters": "Production engineering teams require automated testing and deployment. Interviewers probe how you prevent regressions and ensure zero-downtime releases.",
            "resources": [
                {"type": "course", "title": "Automate with GitHub Actions – GitHub Skills Lab", "url": "https://skills.github.com/"},
                {"type": "docs", "title": "GitHub Actions Official Workflow Documentation", "url": "https://docs.github.com/en/actions"},
                {"type": "tutorial", "title": "Continuous Integration with pytest and GitHub Actions", "url": "https://realpython.com/github-actions-python/"}
            ],
            "task_template": "Create a GitHub Actions CI workflow for your '{project_title}' project that automatically executes linters (ruff/flake8) and test suites on every pull request, gating merges on 100% test pass.",
            "effort": "2 weeks, 4–6 hours/week",
            "success_criteria": [
                "Pull requests automatically run automated tests in under 3 minutes.",
                "Failing tests cleanly block merging, with notifications posted in GitHub checks.",
                "You can walk an interviewer through your release pipeline stages and rollback strategy."
            ]
        },
        "kubernetes": {
            "why_it_matters": "Kubernetes is the industry standard container orchestrator. Understanding pods, services, ingress, and rolling updates is vital for scalable backend operations.",
            "resources": [
                {"type": "course", "title": "Kubernetes for Beginners – edX / Linux Foundation", "url": "https://www.edx.org/learn/kubernetes/the-linux-foundation-introduction-to-kubernetes"},
                {"type": "docs", "title": "Kubernetes Concepts & Architecture Official Guide", "url": "https://kubernetes.io/docs/concepts/"},
                {"type": "book", "title": "Kubernetes: Up and Running (O'Reilly)", "url": "https://www.oreilly.com/library/view/kubernetes-up-and/9781098132965/"}
            ],
            "task_template": "Deploy your containerized '{project_title}' application onto a local Minikube or kind cluster with Deployment and Service manifests, configuring readiness and liveness probes.",
            "effort": "3 weeks, 6–8 hours/week",
            "success_criteria": [
                "Your application runs with 2 replicas and survives pod termination automatically.",
                "Traffic is routed through a Kubernetes Service with zero dropped requests during rolling updates.",
                "You can articulate the difference between ClusterIP, NodePort, and LoadBalancer in an interview."
            ]
        },
        "aws": {
            "why_it_matters": "Cloud infrastructure knowledge (ECS, S3, RDS, IAM) demonstrates that you can take code from local development to production-scale cloud deployments.",
            "resources": [
                {"type": "course", "title": "AWS Cloud Practitioner Essentials (Free Digital Training)", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"},
                {"type": "docs", "title": "AWS Architecture Center & Developer Guides", "url": "https://aws.amazon.com/architecture/"},
                {"type": "tutorial", "title": "Deploying Python Web Apps to AWS ECS with Fargate", "url": "https://aws.amazon.com/getting-started/hands-on/deploy-docker-containers/"}
            ],
            "task_template": "Deploy a containerized microservice from your '{project_title}' to AWS ECS Fargate or AWS App Runner, connecting to an RDS PostgreSQL instance with least-privilege IAM roles.",
            "effort": "3–4 weeks, 6–8 hours/week",
            "success_criteria": [
                "Application is accessible via an HTTPS domain backed by an Application Load Balancer.",
                "Database credentials are securely loaded from AWS Secrets Manager rather than hardcoded.",
                "You can explain AWS VPC architecture (subnets, route tables, security groups) in a system design interview."
            ]
        },
        "redis": {
            "why_it_matters": "Caching and in-memory key-value stores are ubiquitous for low-latency backend systems. Interviewers regularly ask about cache-aside patterns, TTL, and cache stampede prevention.",
            "resources": [
                {"type": "course", "title": "Redis for Python Developers – Redis University", "url": "https://university.redis.io/courses/ru102py/"},
                {"type": "docs", "title": "Redis Official Data Types and Commands Documentation", "url": "https://redis.io/docs/latest/develop/data-types/"},
                {"type": "book", "title": "Redis in Action (Manning)", "url": "https://www.manning.com/books/redis-in-action"}
            ],
            "task_template": "Add a Redis caching layer to your '{project_title}' API implementing the Cache-Aside pattern for expensive database queries, with automatic TTL expiration and cache invalidation on write operations.",
            "effort": "1–2 weeks, 4–6 hours/week",
            "success_criteria": [
                "Endpoint p95 response time drops by at least 40% when serving cached responses.",
                "Cache is cleanly invalidated whenever target records are updated or deleted.",
                "You can explain Cache Stampede, Cache Penetration, and Cache Avalanche defense strategies."
            ]
        },
        "postgresql": {
            "why_it_matters": "Relational data modeling, indexing, transaction isolation, and query optimization are mandatory core competencies for backend developers.",
            "resources": [
                {"type": "course", "title": "PostgreSQL Tutorial for Beginners – freeCodeCamp", "url": "https://www.freecodecamp.org/news/postgresql-course-for-beginners/"},
                {"type": "docs", "title": "PostgreSQL Official Documentation – Indexes & Concurrency", "url": "https://www.postgresql.org/docs/current/"},
                {"type": "book", "title": "Designing Data-Intensive Applications (O'Reilly)", "url": "https://dataintensive.net/"}
            ],
            "task_template": "Audit database queries in '{project_title}' using EXPLAIN ANALYZE, create B-tree and partial indexes to eliminate sequential scans on high-traffic tables, and enforce foreign key cascading constraints.",
            "effort": "2 weeks, 5–7 hours/week",
            "success_criteria": [
                "Identified and optimized at least 2 slow queries using EXPLAIN ANALYZE.",
                "All transactional database writes operate under appropriate ACID transaction blocks.",
                "You can explain index data structures and index selectivity in technical rounds."
            ]
        },
        "system design": {
            "why_it_matters": "System design rounds evaluate your ability to architect scalable, available, and fault-tolerant architectures under real-world constraints.",
            "resources": [
                {"type": "course", "title": "System Design Primer – Donne Martin (GitHub)", "url": "https://github.com/donnemartin/system-design-primer"},
                {"type": "docs", "title": "High Scalability Real Architecture Case Studies", "url": "http://highscalability.com/"},
                {"type": "book", "title": "System Design Interview – An Insider's Guide by Alex Xu", "url": "https://bytebytego.com/"}
            ],
            "task_template": "Draw and document an end-to-end architecture diagram for '{project_title}' detailing client traffic routing, load balancers, application server clusters, read replicas, and asynchronous worker queues.",
            "effort": "3–4 weeks, 5–7 hours/week",
            "success_criteria": [
                "Complete architecture diagram with clearly identified single-points-of-failure and mitigations.",
                "Quantified back-of-the-envelope capacity estimations for storage, throughput (QPS), and bandwidth.",
                "Can confidently articulate trade-offs between consistency and availability (CAP theorem) during mock rounds."
            ]
        },
        "unit testing": {
            "why_it_matters": "Testing discipline differentiates junior engineers from reliable production contributors. Technical interviews often evaluate unit, integration, and mocking patterns.",
            "resources": [
                {"type": "course", "title": "Python Testing with pytest – TestDriven.io", "url": "https://testdriven.io/courses/python-testing/"},
                {"type": "docs", "title": "pytest Official Documentation & Fixture Guide", "url": "https://docs.pytest.org/en/latest/"},
                {"type": "tutorial", "title": "Effective Mocking and Dependency Injection in Python", "url": "https://realpython.com/python-mock-library/"}
            ],
            "task_template": "Write a comprehensive test suite for '{project_title}' using pytest and HTTP test clients, using fixtures for database setup and mocking external API network dependencies to achieve 80%+ branch coverage.",
            "effort": "1–2 weeks, 4–6 hours/week",
            "success_criteria": [
                "Test suite executes in under 15 seconds with isolated mock database fixtures.",
                "Code coverage report verifies at least 80% branch coverage across critical business logic.",
                "You can explain mocking vs stubbing and unit vs integration test trade-offs."
            ]
        }
    }

    def generate_roadmap(
        self,
        role_key: str,
        display_name: str,
        seniority: str,
        domain: str,
        gap_analysis: Dict[str, Any],
        resume_data: Dict[str, Any],
        interview_session: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Builds a customized learning roadmap with priority skills, why it matters,
        clickable resources, resume-grounded project tasks, timelines, and advice.
        """
        resume_projects = resume_data.get("projects", [])
        primary_project = resume_projects[0].get("title", "Portfolio Backend Service") if resume_projects else "Main Web Service"

        critical_missing = gap_analysis.get("critical_missing_skills", [])
        skill_gap_details = gap_analysis.get("skill_gap_details", [])

        # 1. Select 3-6 priority skills to focus on
        priority_skill_names = self._select_priority_skills(
            critical_missing=critical_missing,
            skill_gap_details=skill_gap_details
        )

        # 2. Build detail for each priority skill
        priority_skills: List[Dict[str, Any]] = []
        for skill_name in priority_skill_names:
            detail = self._build_priority_skill_detail(
                skill=skill_name,
                role_display_name=display_name,
                seniority=seniority,
                project_title=primary_project
            )
            priority_skills.append(detail)

        # 3. Suggested sequence timeline
        suggested_sequence = self._build_suggested_sequence(priority_skills, primary_project)

        # 4. General actionable advice
        general_advice = [
            f"Focus on one skill at a time and directly apply each concept to your '{primary_project}' project rather than building disconnected toy tutorials.",
            "Commit code frequently and write clear, professional git commit messages following the Conventional Commits specification.",
            "Document your architectural decisions, data models, and trade-offs in a detailed README with visual architecture diagrams.",
            "Practice articulating your implementation challenges and solutions out loud to prepare for behavioral and technical interview questions.",
            "Measure and highlight concrete results (e.g. latency reduced by X%, test coverage at Y%, automated pipeline execution time) on your resume."
        ]

        learning_roadmap_content = {
            "priority_skills": priority_skills,
            "suggested_sequence": suggested_sequence,
            "general_advice": general_advice
        }

        return {
            "role_key": role_key,
            "display_name": display_name,
            "learning_roadmap": learning_roadmap_content
        }

    def _select_priority_skills(
        self,
        critical_missing: List[str],
        skill_gap_details: List[Dict[str, Any]]
    ) -> List[str]:
        """Picks 3-6 priority skills prioritizing required missing and weak competencies."""
        selected: List[str] = []

        # 1. Critical missing (required)
        for s in critical_missing:
            if s not in selected:
                selected.append(s)
            if len(selected) >= 4:
                break

        # 2. Weak skills (listed without deep evidence)
        for d in skill_gap_details:
            if d.get("status") == "weak":
                w_skill = d["skill"]
                if w_skill not in selected:
                    selected.append(w_skill)
            if len(selected) >= 5:
                break

        # 3. Related partial skills needing bridge
        for d in skill_gap_details:
            if d.get("status") == "related_partial":
                r_skill = d["skill"]
                if r_skill not in selected:
                    selected.append(r_skill)
            if len(selected) >= 5:
                break

        # Fallback if list is too small
        if len(selected) < 3:
            for d in skill_gap_details:
                if d.get("status") == "missing" and d["skill"] not in selected:
                    selected.append(d["skill"])
                if len(selected) >= 3:
                    break

        return selected[:5]

    def _build_priority_skill_detail(
        self,
        skill: str,
        role_display_name: str,
        seniority: str,
        project_title: str
    ) -> Dict[str, Any]:
        """Constructs rich roadmap entry for a priority skill."""
        skill_key = skill.lower().strip()

        # Check catalog
        matching_key = None
        for k in self.SKILL_RESOURCE_CATALOG.keys():
            if k in skill_key or skill_key in k:
                matching_key = k
                break

        if matching_key:
            data = self.SKILL_RESOURCE_CATALOG[matching_key]
            why_it_matters = data["why_it_matters"]
            resources = data["resources"]
            project_task = data["task_template"].format(project_title=project_title)
            effort = data["effort"]
            success_criteria = data["success_criteria"]
        else:
            # Intelligent fallback for arbitrary skills
            why_it_matters = (
                f"{skill} is a core competency for {seniority} {role_display_name} roles. "
                f"Engineering teams look for hands-on experience and solid understanding of {skill} principles during technical evaluations."
            )
            resources = [
                {
                    "type": "course",
                    "title": f"{skill} Fundamentals & Practical Mastery",
                    "url": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}"
                },
                {
                    "type": "docs",
                    "title": f"Official {skill} Documentation & Reference",
                    "url": f"https://en.wikipedia.org/wiki/{skill.replace(' ', '_')}"
                },
                {
                    "type": "tutorial",
                    "title": f"Practical Hands-On Guide to {skill}",
                    "url": f"https://dev.to/search?q={skill.replace(' ', '+')}"
                }
            ]
            project_task = (
                f"Implement a dedicated module in your '{project_title}' utilizing {skill} to solve a concrete engineering problem, "
                f"incorporating error handling, configuration management, and unit tests."
            )
            effort = "2–3 weeks, 5–7 hours/week"
            success_criteria = [
                f"Successfully integrated {skill} into your project repository with passing automated tests.",
                f"Created an architecture diagram and documented configuration in your project README.",
                f"Prepared to explain core {skill} architecture decisions, trade-offs, and failure modes in interviews."
            ]

        return {
            "skill": skill,
            "why_it_matters": why_it_matters,
            "resources": resources,
            "project_task": project_task,
            "estimated_effort": effort,
            "success_criteria": success_criteria
        }

    def _build_suggested_sequence(
        self,
        priority_skills: List[Dict[str, Any]],
        project_title: str
    ) -> List[str]:
        """Creates a coherent weekly timeline progression."""
        timeline: List[str] = []
        if not priority_skills:
            return ["Weeks 1–4: Core backend engineering fundamentals and project enhancement."]

        # Segment into 2-3 week chunks
        current_week = 1
        for i, item in enumerate(priority_skills):
            skill_name = item["skill"]
            duration = 2
            if i >= 2:
                duration = 3
            end_week = current_week + duration - 1
            if current_week == end_week:
                week_str = f"Week {current_week}"
            else:
                week_str = f"Weeks {current_week}–{end_week}"

            timeline.append(
                f"{week_str}: Focus on {skill_name} – Complete foundational tutorials and implement integration into '{project_title}'."
            )
            current_week = end_week + 1

        timeline.append(
            f"Weeks {current_week}–{current_week + 1}: Final Polish & Interview Prep – Document architecture, benchmark performance metrics, and rehearse technical talking points."
        )

        return timeline
