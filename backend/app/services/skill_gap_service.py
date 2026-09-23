from typing import Dict, Any, List, Optional, Set


class SkillGapService:
    """
    Role-aware, resume-grounded, explainable skill gap analysis service.
    Examines candidate's resume evidence against target ESCO / O*NET canonical requirements.
    """

    def analyze_skill_gaps(
        self,
        role_key: str,
        display_name: str,
        seniority: str,
        domain: str,
        required_skills: List[str],
        preferred_skills: List[str],
        resume_data: Dict[str, Any],
        matched_skills: List[Dict[str, Any]],
        weak_skills: List[Dict[str, Any]],
        missing_skills: List[Dict[str, Any]],
        related_partial_skills: List[Dict[str, Any]],
        extra_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Produces an explainable, role-specific skill gap summary with evidence citations,
        granular status explanations, coverage ratios, critical gaps, quick wins, and narrative.
        """
        extra_skills = extra_skills or []
        resume_skills = resume_data.get("skills", [])
        resume_projects = resume_data.get("projects", [])
        resume_experience = resume_data.get("experience", [])
        certifications = resume_data.get("certifications", [])
        summary_text = resume_data.get("summary", "")

        # Quick lookup for match results
        matched_map = {m["canonical_skill"].lower(): m for m in matched_skills}
        weak_map = {w["canonical_skill"].lower(): w for w in weak_skills}
        missing_map = {m["canonical_skill"].lower(): m for m in missing_skills}
        related_map = {r["canonical_skill"].lower(): r for r in related_partial_skills}

        # Build list of all requirements with importance
        requirements: List[Dict[str, str]] = []
        for req in required_skills:
            requirements.append({"skill": req, "importance": "required"})
        for pref in preferred_skills:
            requirements.append({"skill": pref, "importance": "preferred"})

        skill_gap_details: List[Dict[str, Any]] = []
        matched_count = 0
        matched_required = 0
        matched_preferred = 0
        required_count = len(required_skills)
        preferred_count = len(preferred_skills)

        for item in requirements:
            skill_name = item["skill"]
            importance = item["importance"]
            skill_lower = skill_name.lower().strip()

            # Determine classification status
            status = "missing"
            related_to = None

            if skill_lower in matched_map:
                status = "matched"
                matched_count += 1
                if importance == "required":
                    matched_required += 1
                else:
                    matched_preferred += 1
            elif skill_lower in weak_map:
                status = "weak"
            elif skill_lower in related_map:
                status = "related_partial"
                related_to = related_map[skill_lower].get("related_to")
            elif skill_lower in missing_map:
                status = "missing"
            else:
                # Default fallback status check
                status = "missing"

            # Gather concrete evidence citations from candidate resume
            evidence = self._extract_evidence_citations(
                skill_name=skill_name,
                resume_skills=resume_skills,
                resume_projects=resume_projects,
                resume_experience=resume_experience,
                certifications=certifications,
                summary_text=summary_text,
                status=status,
                related_to=related_to
            )

            # Generate explainable narrative reason
            explanation = self._build_explanation(
                skill=skill_name,
                importance=importance,
                status=status,
                role_display_name=display_name,
                seniority=seniority,
                evidence=evidence,
                related_to=related_to
            )

            detail_entry: Dict[str, Any] = {
                "skill": skill_name,
                "importance": importance,
                "status": status,
                "evidence": evidence,
                "explanation": explanation
            }
            if related_to:
                detail_entry["related_to"] = related_to

            skill_gap_details.append(detail_entry)

        # 3. Compute coverage metrics
        total_skills_count = required_count + preferred_count
        coverage_ratio = round(matched_count / max(total_skills_count, 1), 2)
        required_cov = round(matched_required / max(required_count, 1), 2)
        preferred_cov = round(matched_preferred / max(preferred_count, 1), 2)

        # 4. Critical Missing Skills (required skills that are missing or weak)
        critical_missing_skills: List[str] = []
        for d in skill_gap_details:
            if d["importance"] == "required" and d["status"] in ["missing", "weak"]:
                critical_missing_skills.append(d["skill"])

        # Also add weak preferred if critical list is small
        if len(critical_missing_skills) < 3:
            for d in skill_gap_details:
                if d["importance"] == "preferred" and d["status"] == "missing":
                    if d["skill"] not in critical_missing_skills:
                        critical_missing_skills.append(d["skill"])
                if len(critical_missing_skills) >= 4:
                    break

        # 5. Quick Wins (actionable steps tied to projects or weak/related skills)
        quick_wins = self._generate_quick_wins(
            skill_gap_details=skill_gap_details,
            resume_projects=resume_projects,
            display_name=display_name
        )

        # 6. Narrative Gap Summary (3-6 sentences)
        gap_narrative = self._generate_gap_narrative(
            display_name=display_name,
            seniority=seniority,
            skill_gap_details=skill_gap_details,
            critical_missing_skills=critical_missing_skills,
            quick_wins=quick_wins,
            coverage_ratio=coverage_ratio
        )

        return {
            "role_key": role_key,
            "display_name": display_name,
            "coverage_ratio": coverage_ratio,
            "required_coverage": required_cov,
            "preferred_coverage": preferred_cov,
            "skill_gap_details": skill_gap_details,
            "critical_missing_skills": critical_missing_skills,
            "quick_wins": quick_wins,
            "gap_narrative": gap_narrative
        }

    def _extract_evidence_citations(
        self,
        skill_name: str,
        resume_skills: List[Dict[str, Any]],
        resume_projects: List[Dict[str, Any]],
        resume_experience: List[Dict[str, Any]],
        certifications: List[Any],
        summary_text: str,
        status: str,
        related_to: Optional[str] = None
    ) -> List[str]:
        """Extracts concrete evidence strings from candidate's resume entries."""
        if status == "missing":
            return []

        search_term = (related_to or skill_name).lower().strip()
        evidence_list: List[str] = []

        # 1. Projects evidence
        for proj in resume_projects:
            title = proj.get("title", "Project")
            techs = [t.lower() for t in proj.get("technologies", [])]
            outcomes = proj.get("outcomes", [])
            desc = proj.get("description", "")

            matched_bullet = None
            if search_term in techs:
                matched_bullet = f"Utilized {skill_name} in {title}"
            for out in outcomes:
                if search_term in out.lower():
                    matched_bullet = out
                    break
            if not matched_bullet and search_term in desc.lower():
                matched_bullet = desc

            if matched_bullet:
                citation = f"Project: {title} – '{matched_bullet.strip()}'"
                if citation not in evidence_list:
                    evidence_list.append(citation)

        # 2. Experience evidence
        for exp in resume_experience:
            role_title = exp.get("job_title", "Software Engineer")
            company = exp.get("organization") or exp.get("company", "Company")
            bullets = exp.get("bullets", [])
            exp_skills = [s.lower() for s in exp.get("skills", [])]

            matched_bullet = None
            if search_term in exp_skills:
                matched_bullet = f"Leveraged {skill_name} as part of core responsibilities"
            for b in bullets:
                if search_term in b.lower():
                    matched_bullet = b
                    break

            if matched_bullet:
                citation = f"Experience: {role_title} at {company} – '{matched_bullet.strip()}'"
                if citation not in evidence_list:
                    evidence_list.append(citation)

        # 3. Certifications
        for cert in certifications:
            cert_name = cert if isinstance(cert, str) else cert.get("name", "")
            if search_term in cert_name.lower():
                evidence_list.append(f"Certification: '{cert_name}'")

        # 4. If status is WEAK and no project/exp bullets were found, extract from summary or skills list
        if status == "weak" and not evidence_list:
            if summary_text and search_term in summary_text.lower():
                evidence_list.append(f"Summary: '{summary_text.strip()}'")
            else:
                for s in resume_skills:
                    if s.get("canonical_skill", "").lower() == search_term:
                        raw_ev = s.get("evidence", [])
                        if raw_ev:
                            evidence_list.append(f"Skills Section: '{raw_ev[0]}'")
                        else:
                            evidence_list.append(f"Skills Section: Listed under technical proficiencies")
                        break

        # 5. If matched or related and no direct quote was matched, pull from skill evidence
        if not evidence_list and status in ["matched", "related_partial"]:
            for s in resume_skills:
                if s.get("canonical_skill", "").lower() == search_term:
                    for ev in s.get("evidence", []):
                        evidence_list.append(ev)
                    break

        if not evidence_list and status == "weak":
            evidence_list.append(f"Skills Section: Listed under technical skills without project metrics")

        return evidence_list[:3]

    def _build_explanation(
        self,
        skill: str,
        importance: str,
        status: str,
        role_display_name: str,
        seniority: str,
        evidence: List[str],
        related_to: Optional[str] = None
    ) -> str:
        """Constructs human-readable explainable justification for the classification."""
        if status == "matched":
            if len(evidence) >= 2:
                return (
                    f"{skill} is well demonstrated through both project and employment experience "
                    f"with concrete engineering deliverables."
                )
            elif evidence and "Project:" in evidence[0]:
                return (
                    f"{skill} is verified with hands-on project implementation evidence, "
                    f"satisfying {importance} expectations for {role_display_name}."
                )
            elif evidence and "Experience:" in evidence[0]:
                return (
                    f"{skill} is substantiated through professional workplace experience, "
                    f"directly meeting {importance} role requirements."
                )
            return f"{skill} is directly supported by candidate profile evidence."

        elif status == "weak":
            if evidence and "Summary:" in evidence[0]:
                return (
                    f"{skill} is only mentioned in the summary with no project or experience "
                    f"evidence of building, testing, or deploying systems with it."
                )
            return (
                f"{skill} is listed in skills inventory without concrete project metrics or "
                f"workplace responsibility bullets to verify practical proficiency."
            )

        elif status == "related_partial":
            rel_name = related_to or "a related technology"
            return (
                f"While {skill} is not directly cited, the candidate demonstrates hands-on proficiency "
                f"in related technology '{rel_name}', providing strong transferable architecture concepts."
            )

        else:  # missing
            if importance == "required":
                return (
                    f"No {skill} tools, frameworks, or implementations are mentioned in projects or experience, "
                    f"despite being a core mandatory expectation for {seniority} {role_display_name} roles."
                )
            else:
                return (
                    f"No evidence for preferred competency {skill} was found in the resume, "
                    f"which represents an opportunity to differentiate against competitor candidates."
                )

    def _generate_quick_wins(
        self,
        skill_gap_details: List[Dict[str, Any]],
        resume_projects: List[Dict[str, Any]],
        display_name: str
    ) -> List[str]:
        """Generates 1-3 actionable, high-leverage quick wins."""
        quick_wins: List[str] = []
        primary_project = resume_projects[0].get("title", "main project") if resume_projects else "core project"

        # Check weak skills first
        weak_items = [d for d in skill_gap_details if d["status"] == "weak"]
        if weak_items:
            w_skill = weak_items[0]["skill"]
            quick_wins.append(
                f"Add 1–2 quantified bullet points to your '{primary_project}' detailing how you configured and used {w_skill}."
            )

        # Check missing infrastructure/tooling skills
        missing_infra = [
            d["skill"] for d in skill_gap_details
            if d["status"] == "missing" and d["skill"].lower() in ["docker", "ci/cd", "kubernetes", "aws", "git", "linux", "testing"]
        ]
        if missing_infra:
            infra_skill = missing_infra[0]
            if infra_skill.lower() == "docker":
                quick_wins.append(
                    f"Add a multi-stage Dockerfile and docker-compose setup to your '{primary_project}' repository."
                )
            elif infra_skill.lower() in ["ci/cd", "git"]:
                quick_wins.append(
                    f"Set up a GitHub Actions CI pipeline on your '{primary_project}' repo that runs linting and unit tests on push."
                )
            else:
                quick_wins.append(
                    f"Build a focused starter module showcasing {infra_skill} integration with your '{primary_project}'."
                )

        # Check related partial skills
        related_items = [d for d in skill_gap_details if d["status"] == "related_partial"]
        if related_items and len(quick_wins) < 3:
            rel = related_items[0]
            quick_wins.append(
                f"Explicitly document how your hands-on background in '{rel.get('related_to')}' enables rapid ramp-up for '{rel['skill']}'."
            )

        if not quick_wins:
            quick_wins.append(
                f"Document architecture diagrams and benchmark latency/throughput metrics for your '{primary_project}'."
            )

        return quick_wins[:3]

    def _generate_gap_narrative(
        self,
        display_name: str,
        seniority: str,
        skill_gap_details: List[Dict[str, Any]],
        critical_missing_skills: List[str],
        quick_wins: List[str],
        coverage_ratio: float
    ) -> str:
        """Synthesizes a 3-6 sentence explainable gap narrative specific to candidate and role."""
        matched_names = [d["skill"] for d in skill_gap_details if d["status"] == "matched"]
        weak_names = [d["skill"] for d in skill_gap_details if d["status"] == "weak"]
        related_names = [f"{d.get('related_to')} for {d['skill']}" for d in skill_gap_details if d["status"] == "related_partial"]

        sentences: List[str] = []

        # 1. Strengths
        if matched_names:
            top_matched = ", ".join(matched_names[:4])
            sentences.append(
                f"The candidate demonstrates strong alignment with official {display_name} taxonomy standards, "
                f"with solid evidence for {top_matched} through verified employment and project work."
            )
        else:
            sentences.append(
                f"The candidate demonstrates foundational software engineering capabilities, but currently shows "
                f"limited direct verified overlap with core {display_name} requirements."
            )

        # 2. Critical gaps
        if critical_missing_skills:
            top_crit = ", ".join(critical_missing_skills[:3])
            sentences.append(
                f"However, key competencies including {top_crit} are currently unverified or absent from the resume, "
                f"which impacts competitive readiness for production {seniority} {display_name} positions."
            )

        # 3. Transferable or weak nuances
        if related_names:
            sentences.append(
                f"Transferable competencies ({', '.join(related_names[:2])}) offer natural transition paths, "
                f"indicating the candidate can quickly bridge conceptual gaps."
            )
        elif weak_names:
            sentences.append(
                f"Skills such as {', '.join(weak_names[:2])} are mentioned in passing but need concrete operational evidence to confirm depth."
            )

        # 4. Quick wins & conclusion
        if quick_wins:
            sentences.append(
                f"Quick wins include: {quick_wins[0]}"
            )
        sentences.append(
            f"Targeted preparation focused on these priority gaps will significantly strengthen technical interview performance."
        )

        return " ".join(sentences)
