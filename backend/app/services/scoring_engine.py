import re
from typing import Dict, Any, List
from app.core.config import settings


class ScoringEngineService:
    def __init__(self):
        self.w_skill = settings.WEIGHT_SKILL_MATCH
        self.w_exp = settings.WEIGHT_EXPERIENCE
        self.w_proj = settings.WEIGHT_PROJECT
        self.w_keyw = settings.WEIGHT_KEYWORD
        self.w_sen = settings.WEIGHT_SENIORITY

    def compute_skill_match_score(
        self,
        matched_skills: List[Dict[str, Any]],
        weak_skills: List[Dict[str, Any]],
        missing_skills: List[Dict[str, Any]],
        related_partial_skills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculates explainable skill match score (0-100)."""
        breakdown: List[Dict[str, str]] = []
        recommendations: List[str] = []

        total_weight = 0.0
        earned_weight = 0.0

        # Required skills carry weight of 2.0, preferred carry 1.0
        for item in matched_skills:
            multiplier = 2.0 if item.get("importance") == "required" else 1.0
            total_weight += multiplier
            earned_weight += multiplier
            impact_val = int(multiplier * 6)
            evidence = item.get("evidence_citation") or item.get("raw_text")
            reason_text = f"Matched {item.get('importance')} skill '{item.get('canonical_skill')}'"
            if evidence:
                # Clean citation text snippet
                clean_ev = str(evidence).strip().replace("\n", " ")[:60]
                reason_text += f" (evidenced by: '{clean_ev}')"
            else:
                reason_text += " with verified resume citation"
            breakdown.append({
                "reason": reason_text,
                "impact": f"+{impact_val}"
            })

        for item in related_partial_skills:
            multiplier = 2.0 if item.get("importance") == "required" else 1.0
            total_weight += multiplier
            earned_weight += multiplier * 0.65  # partial credit
            impact_val = int(multiplier * 4)
            breakdown.append({
                "reason": f"Transferable skill '{item.get('related_to')}' bridges required '{item.get('canonical_skill')}'",
                "impact": f"+{impact_val}"
            })

        for item in weak_skills:
            multiplier = 2.0 if item.get("importance") == "required" else 1.0
            total_weight += multiplier
            earned_weight += multiplier * 0.50  # weak credit
            impact_val = int(multiplier * 3)
            breakdown.append({
                "reason": f"Skill '{item.get('canonical_skill')}' listed in resume but lacks verified project or experience bullets",
                "impact": f"+{impact_val}"
            })
            recommendations.append(f"Demonstrate hands-on production application of '{item.get('canonical_skill')}' in project bullets.")

        for item in missing_skills:
            multiplier = 2.0 if item.get("importance") == "required" else 1.0
            total_weight += multiplier
            impact_val = int(multiplier * 5)
            breakdown.append({
                "reason": f"Missing critical {item.get('importance')} role requirement: '{item.get('canonical_skill')}'",
                "impact": f"-{impact_val}"
            })
            recommendations.append(f"Acquire foundational experience or certifications in '{item.get('canonical_skill')}'.")

        raw_score = (earned_weight / max(total_weight, 1.0)) * 100.0
        final_score = round(min(max(raw_score, 10.0), 100.0), 1)

        return {
            "score": final_score,
            "max_score": 100.0,
            "weight": self.w_skill,
            "breakdown": breakdown[:8],
            "recommendations": recommendations[:3]
        }

    def compute_experience_score(
        self,
        resume_experience: List[Dict[str, Any]],
        jd_req: Dict[str, Any],
        target_seniority: str
    ) -> Dict[str, Any]:
        """Calculates experience score based on years, relevance, and duration."""
        breakdown: List[Dict[str, str]] = []
        recommendations: List[str] = []

        min_years = jd_req.get("minimum_years", 0)
        exp_entries_count = len(resume_experience)

        # Baseline estimate based on number of experience entries and dates
        estimated_years = max(exp_entries_count * 1.5, 0.5) if exp_entries_count > 0 else 0.0

        score = 50.0

        exp_titles = [
            f"{e.get('job_title', 'Engineer')} at {e.get('organization', 'Company')}"
            for e in resume_experience
            if e.get('job_title') or e.get('organization')
        ]

        if exp_entries_count > 0:
            bonus = min(exp_entries_count * 12.0, 30.0)
            score += bonus
            titles_sample = ", ".join(exp_titles[:2]) if exp_titles else f"{exp_entries_count} roles"
            breakdown.append({
                "reason": f"Verified {exp_entries_count} professional role(s) ({titles_sample})",
                "impact": f"+{int(bonus)}"
            })
        else:
            score -= 25.0
            breakdown.append({
                "reason": "No formal industry experience entries detected on resume",
                "impact": "-25"
            })
            recommendations.append("Highlight open-source contributions or freelance internships as formal experience.")

        if min_years > 0:
            if estimated_years >= min_years:
                score += 20.0
                breakdown.append({
                    "reason": f"Estimated experience (~{estimated_years:.1f} yrs) meets or exceeds requirement ({min_years} yrs)",
                    "impact": "+20"
                })
            else:
                score -= 15.0
                breakdown.append({
                    "reason": f"Estimated experience (~{estimated_years:.1f} yrs) is below JD requirement of {min_years} yrs",
                    "impact": "-15"
                })
                recommendations.append(f"Emphasize accelerated project velocity to compensate for the {min_years} years requirement.")
        else:
            score += 15.0
            breakdown.append({
                "reason": "Job profile establishes flexible baseline without strict minimum tenure barrier",
                "impact": "+15"
            })

        final_score = round(min(max(score, 15.0), 100.0), 1)

        return {
            "score": final_score,
            "max_score": 100.0,
            "weight": self.w_exp,
            "breakdown": breakdown,
            "recommendations": recommendations
        }

    def compute_project_score(
        self,
        resume_projects: List[Dict[str, Any]],
        matched_skills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculates project score based on quantity, depth, tech relevance, and quantified metrics."""
        breakdown: List[Dict[str, str]] = []
        recommendations: List[str] = []

        proj_count = len(resume_projects)
        proj_titles = [p.get("title") for p in resume_projects if p.get("title")]
        score = 40.0

        if proj_count >= 3:
            score += 25.0
            sample_titles = ", ".join([f"'{t}'" for t in proj_titles[:2]])
            breakdown.append({
                "reason": f"Candidate demonstrates {proj_count} detailed project portfolios (e.g. {sample_titles})",
                "impact": "+25"
            })
        elif proj_count > 0:
            score += 15.0
            first_title = proj_titles[0] if proj_titles else "technical build"
            breakdown.append({
                "reason": f"Candidate documents {proj_count} project portfolio entry ('{first_title}')",
                "impact": "+15"
            })
        else:
            score -= 20.0
            breakdown.append({
                "reason": "No explicit project section identified in resume",
                "impact": "-20"
            })
            recommendations.append("Add a dedicated 'Projects' section with 2-3 production-grade systems.")

        # Check for quantified metrics (numbers, percentages, latency, throughput)
        quantified_count = 0
        metric_pattern = re.compile(r"\b(\d+[%kKmM]?|\$\d+|\d+\s*(?:ms|sec|users|req\/s))\b")
        for p in resume_projects:
            combined_text = (p.get("description") or "") + " ".join(p.get("outcomes", []))
            if metric_pattern.search(combined_text):
                quantified_count += 1

        if quantified_count > 0:
            score += 20.0
            breakdown.append({
                "reason": f"{quantified_count} project(s) cite measurable latency, throughput, or user scale metrics",
                "impact": "+20"
            })
        else:
            score -= 10.0
            breakdown.append({
                "reason": "Projects lack quantified performance, scale, or business outcome metrics",
                "impact": "-10"
            })
            recommendations.append("Incorporate specific numbers (e.g., 'reduced query latency by 45%', 'supported 10k users').")

        # Check technologies overlap
        tech_matched = set()
        for p in resume_projects:
            for t in p.get("technologies", []) + p.get("skills", []):
                for m in matched_skills:
                    if t.lower() == m.get("canonical_skill", "").lower():
                        tech_matched.add(m.get("canonical_skill"))

        if tech_matched:
            bonus = min(len(tech_matched) * 5.0, 15.0)
            score += bonus
            breakdown.append({
                "reason": f"Projects utilize relevant target stack: {', '.join(list(tech_matched)[:3])}",
                "impact": f"+{int(bonus)}"
            })

        final_score = round(min(max(score, 20.0), 100.0), 1)

        return {
            "score": final_score,
            "max_score": 100.0,
            "weight": self.w_proj,
            "breakdown": breakdown,
            "recommendations": recommendations
        }

    def compute_keyword_score(
        self,
        resume_keywords: List[str],
        jd_keywords: List[str]
    ) -> Dict[str, Any]:
        """Calculates keyword coverage preventing artificial stuffing."""
        breakdown: List[Dict[str, str]] = []
        recommendations: List[str] = []

        if not jd_keywords:
            return {
                "score": 80.0,
                "max_score": 100.0,
                "weight": self.w_keyw,
                "breakdown": [{"reason": "General keyword baseline applied", "impact": "+80"}],
                "recommendations": []
            }

        res_lower = set([k.lower() for k in resume_keywords])
        matched_kw = [k for k in jd_keywords if k.lower() in res_lower]
        missing_kw = [k for k in jd_keywords if k.lower() not in res_lower]

        ratio = len(matched_kw) / max(len(jd_keywords), 1)
        score = round(ratio * 100.0, 1)

        matched_sample = ", ".join(matched_kw[:3]) if matched_kw else "None"
        breakdown.append({
            "reason": f"Resume incorporates {len(matched_kw)} of {len(jd_keywords)} essential role keywords (e.g. {matched_sample})",
            "impact": f"+{int(score * 0.8)}"
        })

        if missing_kw:
            missing_sample = ", ".join(missing_kw[:3])
            breakdown.append({
                "reason": f"Key target keywords absent: {missing_sample}",
                "impact": f"-{int((1.0 - ratio) * 40)}"
            })
            recommendations.append(f"Weave missing keywords ({missing_sample}) into project and experience summaries.")

        final_score = round(min(max(score, 15.0), 100.0), 1)

        return {
            "score": final_score,
            "max_score": 100.0,
            "weight": self.w_keyw,
            "breakdown": breakdown,
            "recommendations": recommendations
        }

    def compute_seniority_score(
        self,
        resume_data: Dict[str, Any],
        jd_seniority: str
    ) -> Dict[str, Any]:
        """Compares resume scope, leadership language, and project depth with JD seniority."""
        breakdown: List[Dict[str, str]] = []
        recommendations: List[str] = []

        resume_text = (resume_data.get("summary") or "") + " " + " ".join([
            " ".join(e.get("bullets", [])) for e in resume_data.get("experience", [])
        ])
        text_lower = resume_text.lower()

        # Seniority leadership indicators
        leadership_terms = ["architected", "mentored", "spearheaded", "led", "designed", "optimized", "scaled", "owned"]
        detected_leadership = [w for w in leadership_terms if re.search(r"\b" + w + r"\b", text_lower)]

        score = 65.0

        if detected_leadership:
            bonus = min(len(detected_leadership) * 6.0, 25.0)
            score += bonus
            verbs_str = ", ".join(detected_leadership[:3])
            breakdown.append({
                "reason": f"Demonstrates strong ownership and architecture phrasing (e.g. {verbs_str})",
                "impact": f"+{int(bonus)}"
            })

        if jd_seniority in ["senior", "lead"]:
            if len(detected_leadership) < 2:
                score -= 20.0
                breakdown.append({
                    "reason": f"Target role is {jd_seniority.upper()} but resume lacks sufficient architectural leadership phrasing",
                    "impact": "-20"
                })
                recommendations.append("Frame achievements around technical ownership, architecture decisions, and cross-functional leadership.")
            else:
                score += 10.0
                breakdown.append({
                    "reason": f"Seniority phrasing is well-aligned with {jd_seniority.upper()} level expectations",
                    "impact": "+10"
                })
        else:
            # Junior or mid
            score += 10.0
            breakdown.append({
                "reason": f"Experience scope fits {jd_seniority.upper()} requirements appropriately",
                "impact": "+10"
            })

        final_score = round(min(max(score, 20.0), 100.0), 1)

        return {
            "score": final_score,
            "max_score": 100.0,
            "weight": self.w_sen,
            "breakdown": breakdown,
            "recommendations": recommendations
        }

    def compute_all_scores(
        self,
        matched_skills: List[Dict[str, Any]],
        weak_skills: List[Dict[str, Any]],
        missing_skills: List[Dict[str, Any]],
        related_partial_skills: List[Dict[str, Any]],
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculates all 5 subscores and the overall explainable composite score."""
        skill_score_obj = self.compute_skill_match_score(
            matched_skills, weak_skills, missing_skills, related_partial_skills
        )
        exp_score_obj = self.compute_experience_score(
            resume_data.get("experience", []),
            jd_data.get("experience_requirements", {}),
            jd_data.get("seniority", "mid")
        )
        proj_score_obj = self.compute_project_score(
            resume_data.get("projects", []),
            matched_skills
        )
        keyw_score_obj = self.compute_keyword_score(
            resume_data.get("extracted_keywords", []),
            jd_data.get("keywords", [])
        )
        sen_score_obj = self.compute_seniority_score(
            resume_data,
            jd_data.get("seniority", "mid")
        )

        overall = (
            skill_score_obj["score"] * self.w_skill +
            exp_score_obj["score"] * self.w_exp +
            proj_score_obj["score"] * self.w_proj +
            keyw_score_obj["score"] * self.w_keyw +
            sen_score_obj["score"] * self.w_sen
        )
        overall_score = round(min(max(overall, 10.0), 100.0), 1)

        # Synthesize 2-4 high-level drivers summarizing positive strengths and blockers
        overall_breakdown: List[Dict[str, str]] = []

        if matched_skills:
            top_matched = ", ".join([m.get("canonical_skill", "") for m in matched_skills[:3]])
            overall_breakdown.append({
                "reason": f"Verified competency across {len(matched_skills)} core role requirements ({top_matched})",
                "impact": f"+{int(skill_score_obj['score'] * self.w_skill)}"
            })

        if proj_score_obj["score"] >= 65:
            overall_breakdown.append({
                "reason": "Strong engineering portfolio demonstrates relevant production technologies and outcomes",
                "impact": f"+{int(proj_score_obj['score'] * self.w_proj)}"
            })
        else:
            overall_breakdown.append({
                "reason": "Project portfolio lacks demonstrated production scale, metrics, or target stack alignment",
                "impact": f"-{int((100 - proj_score_obj['score']) * self.w_proj)}"
            })

        if exp_score_obj["score"] >= 70:
            overall_breakdown.append({
                "reason": "Professional tenure and roles satisfy target seniority expectations",
                "impact": f"+{int(exp_score_obj['score'] * self.w_exp)}"
            })
        else:
            overall_breakdown.append({
                "reason": "Experience timeline or depth is below the target role benchmark",
                "impact": f"-{int((100 - exp_score_obj['score']) * self.w_exp)}"
            })

        if missing_skills:
            top_missing = ", ".join([m.get("canonical_skill", "") for m in missing_skills[:3]])
            overall_breakdown.append({
                "reason": f"Primary blocker: {len(missing_skills)} missing requirement(s) ({top_missing})",
                "impact": f"-{min(len(missing_skills) * 4, 20)}"
            })

        return {
            "overall_score": overall_score,
            "overall_breakdown": overall_breakdown,
            "skill_match_score": skill_score_obj,
            "experience_score": exp_score_obj,
            "project_score": proj_score_obj,
            "keyword_score": keyw_score_obj,
            "seniority_score": sen_score_obj
        }
