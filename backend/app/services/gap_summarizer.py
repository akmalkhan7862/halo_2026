from typing import Dict, Any, List


class GapSummarizerService:
    def summarize_role_gap(
        self,
        role_display_name: str,
        seniority: str,
        matched_skills: List[Dict[str, Any]],
        weak_skills: List[Dict[str, Any]],
        missing_skills: List[Dict[str, Any]],
        related_partial_skills: List[Dict[str, Any]],
        extra_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Synthesizes an explainable, concise skill-gap summary for a target taxonomy role
        without needing any manual Job Description.
        """
        critical_missing = [
            m["canonical_skill"] for m in missing_skills if m.get("importance") == "required"
        ]

        total_reqs = len(matched_skills) + len(weak_skills) + len(missing_skills) + len(related_partial_skills)
        matched_count = len(matched_skills)
        partial_count = len(related_partial_skills)

        # Compute readiness level
        coverage_ratio = (matched_count + 0.6 * partial_count) / max(total_reqs, 1)
        if coverage_ratio >= 0.70 and len(critical_missing) <= 1:
            readiness = "high"
        elif coverage_ratio >= 0.40:
            readiness = "moderate"
        else:
            readiness = "low"

        # Actionable quick wins
        quick_wins = []
        if critical_missing:
            quick_wins.append(
                f"Prioritize building a practical project demonstrating '{critical_missing[0]}' to satisfy core {role_display_name} criteria."
            )
        if weak_skills:
            first_weak = weak_skills[0]["canonical_skill"]
            quick_wins.append(
                f"Add quantified metrics and project bullets for '{first_weak}' to turn listed familiarity into verified evidence."
            )
        if related_partial_skills:
            rel = related_partial_skills[0]
            quick_wins.append(
                f"Highlight how your expertise in '{rel.get('related_to')}' gives you rapid ramp-up for '{rel.get('canonical_skill')}'."
            )
        if extra_skills:
            quick_wins.append(
                f"Position your extra skills ({', '.join(extra_skills[:3])}) as unique cross-functional differentiators."
            )

        # Concise narrative summary
        narrative_parts = []
        if matched_skills:
            top_matched = ", ".join([m["canonical_skill"] for m in matched_skills[:4]])
            narrative_parts.append(
                f"The candidate demonstrates strong alignment with official {role_display_name} taxonomy standards, showing verified evidence in {top_matched}."
            )
        else:
            narrative_parts.append(
                f"The candidate has foundational software experience but limited direct overlap with the core {role_display_name} skill taxonomy."
            )

        if related_partial_skills:
            rel_details = "; ".join([f"{r.get('related_to')} -> {r.get('canonical_skill')}" for r in related_partial_skills[:3]])
            narrative_parts.append(
                f"Transferable skill clusters bridge key requirements: {rel_details}."
            )

        if critical_missing:
            narrative_parts.append(
                f"Key missing skills to address for full readiness: {', '.join(critical_missing[:4])}."
            )

        narrative_summary = " ".join(narrative_parts)

        # Focus areas recommendation
        focus_areas = []
        if critical_missing:
            focus_areas.extend(critical_missing[:3])
        if related_partial_skills:
            focus_areas.extend([r.get("canonical_skill") for r in related_partial_skills[:2]])
        if not focus_areas and weak_skills:
            focus_areas.extend([w.get("canonical_skill") for w in weak_skills[:3]])
        if not focus_areas:
            focus_areas = [f"{role_display_name} Advanced Patterns"]

        return {
            "overall_fit": readiness,
            "overall_readiness": readiness,
            "top_missing_skills": critical_missing[:6],
            "critical_missing_skills": critical_missing[:6],
            "quick_wins": quick_wins[:4],
            "recommended_focus_areas": focus_areas[:4],
            "narrative_summary": narrative_summary,
            "coverage_ratio": round(coverage_ratio, 2)
        }
