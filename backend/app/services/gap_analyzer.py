from typing import Dict, Any, List


class GapAnalyzerService:
    def generate_gap_summary(
        self,
        target_role: str,
        seniority: str,
        matched_skills: List[Dict[str, Any]],
        weak_skills: List[Dict[str, Any]],
        missing_skills: List[Dict[str, Any]],
        related_partial_skills: List[Dict[str, Any]],
        extra_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Synthesizes skill gap classifications into an explainable summary with
        overall readiness assessment, critical blockers, quick wins, and narrative.
        """
        critical_missing = [
            m["canonical_skill"] for m in missing_skills if m.get("importance") == "required"
        ]

        total_reqs = len(matched_skills) + len(weak_skills) + len(missing_skills) + len(related_partial_skills)
        matched_count = len(matched_skills)
        partial_count = len(related_partial_skills)

        # Readiness determination
        coverage_ratio = (matched_count + 0.5 * partial_count) / max(total_reqs, 1)
        if coverage_ratio >= 0.75 and len(critical_missing) <= 1:
            readiness = "high"
        elif coverage_ratio >= 0.45:
            readiness = "moderate"
        else:
            readiness = "low"

        # Actionable quick wins
        quick_wins = []
        if weak_skills:
            first_weak = weak_skills[0]["canonical_skill"]
            quick_wins.append(
                f"Add quantified project bullet points demonstrating hands-on usage of '{first_weak}'."
            )
        if related_partial_skills:
            rel = related_partial_skills[0]
            quick_wins.append(
                f"Explicitly mention how your expertise in '{rel.get('related_to')}' enables you to rapidly adapt to '{rel.get('canonical_skill')}'."
            )
        if critical_missing:
            quick_wins.append(
                f"Complete a focused starter implementation incorporating '{critical_missing[0]}' and link the GitHub repository in your resume."
            )
        quick_wins.append("Ensure every project bullet point includes measurable engineering impact metrics (e.g. latency, throughput, cost).")

        # Explainable narrative summary
        narrative_parts = []
        if matched_skills:
            top_matched = ", ".join([m["canonical_skill"] for m in matched_skills[:4]])
            narrative_parts.append(
                f"The candidate exhibits solid alignment with core {target_role} requirements, showing verified hands-on evidence in {top_matched}."
            )
        else:
            narrative_parts.append(
                f"The candidate currently demonstrates limited direct overlap with the required stack for {target_role}."
            )

        if related_partial_skills:
            rel_details = "; ".join([f"{r.get('related_to')} -> {r.get('canonical_skill')}" for r in related_partial_skills[:3]])
            narrative_parts.append(
                f"Transferable competencies provide strong bridging opportunities ({rel_details}), indicating high adaptability."
            )

        if critical_missing:
            narrative_parts.append(
                f"The primary areas requiring immediate focus prior to technical rounds are missing mandatory requirements: {', '.join(critical_missing[:4])}."
            )

        if weak_skills:
            weak_names = ", ".join([w["canonical_skill"] for w in weak_skills[:3]])
            narrative_parts.append(
                f"Skills such as {weak_names} are currently listed without sufficient project or operational evidence and should be bolstered with concrete metrics."
            )

        narrative_summary = " ".join(narrative_parts)

        return {
            "overall_readiness": readiness,
            "critical_missing_skills": critical_missing[:6],
            "quick_wins": quick_wins[:4],
            "narrative_summary": narrative_summary
        }
