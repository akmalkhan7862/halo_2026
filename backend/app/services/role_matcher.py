from typing import List, Dict, Any, Set
from app.models.role_profile import RoleProfile
from app.services.taxonomy_service import TaxonomyService
from app.services.gap_summarizer import GapSummarizerService


class RoleMatcherService:
    def __init__(self, taxonomy_service: TaxonomyService):
        self.taxonomy_service = taxonomy_service
        self.gap_summarizer = GapSummarizerService()

    def match_resume_to_role(
        self,
        resume_data: Dict[str, Any],
        role: RoleProfile
    ) -> Dict[str, Any]:
        """
        Compares candidate extracted resume skills with a target role's canonical taxonomy requirements.
        Returns:
          - matched_skills: Direct evidence in project/experience
          - weak_skills: Listed only without project/experience proof
          - missing_skills: Role requires it, but no direct or related evidence found
          - related_partial_skills: Candidate possesses a transferable counterpart (e.g. Flask for FastAPI)
          - extra_skills: Skills in resume not required by this target role
          - gap_summary: Concise explainable narrative and quick wins
          - fit_score: 0 to 100 explainable score
        """
        resume_skills: List[Dict[str, Any]] = resume_data.get("skills", [])
        resume_experience: List[Dict[str, Any]] = resume_data.get("experience", [])
        resume_projects: List[Dict[str, Any]] = resume_data.get("projects", [])

        # Build map of candidate skills
        candidate_skills_map: Dict[str, Dict[str, Any]] = {}
        for s in resume_skills:
            canon = s.get("canonical_skill", "").strip().lower()
            if canon:
                candidate_skills_map[canon] = s

        # Identify experiential proof
        experiential_skills: Set[str] = set()
        for exp in resume_experience:
            for s in exp.get("skills", []):
                experiential_skills.add(s.strip().lower())
            for bullet in exp.get("bullets", []):
                for canon_key in self.taxonomy_service.exact_map.keys():
                    if canon_key in bullet.lower():
                        experiential_skills.add(canon_key)

        for proj in resume_projects:
            for s in proj.get("technologies", []) + proj.get("skills", []):
                experiential_skills.add(s.strip().lower())
            for outcome in proj.get("outcomes", []):
                for canon_key in self.taxonomy_service.exact_map.keys():
                    if canon_key in outcome.lower():
                        experiential_skills.add(canon_key)

        required_skills: List[str] = role.required_skills or []
        preferred_skills: List[str] = role.preferred_skills or []

        all_role_requirements = []
        for req in required_skills:
            all_role_requirements.append({"canonical_skill": req, "importance": "required"})
        for pref in preferred_skills:
            all_role_requirements.append({"canonical_skill": pref, "importance": "preferred"})

        matched_skills = []
        weak_skills = []
        missing_skills = []
        related_partial_skills = []
        covered_candidate_skills: Set[str] = set()

        total_weight = 0.0
        earned_weight = 0.0

        for item in all_role_requirements:
            canon = item["canonical_skill"]
            canon_lower = canon.strip().lower()
            importance = item["importance"]
            weight_multiplier = 2.0 if importance == "required" else 1.0
            total_weight += weight_multiplier

            # 1. Direct match check
            if canon_lower in candidate_skills_map:
                cand_info = candidate_skills_map[canon_lower]
                covered_candidate_skills.add(canon_lower)
                evidence = cand_info.get("evidence", [])

                has_experience_proof = (
                    canon_lower in experiential_skills or
                    any("experience" in ev.lower() or "project" in ev.lower() for ev in evidence)
                )

                if has_experience_proof:
                    earned_weight += weight_multiplier
                    citation = evidence[0] if evidence else f"Demonstrated in work experience or projects."
                    matched_skills.append({
                        "canonical_skill": canon,
                        "status": "MATCHED",
                        "importance": importance,
                        "confidence": cand_info.get("confidence", 1.0),
                        "evidence_citation": citation,
                        "related_to": None,
                        "reason": f"Directly demonstrated in candidate profile: {citation}"
                    })
                else:
                    earned_weight += weight_multiplier * 0.55  # weak partial credit
                    citation = evidence[0] if evidence else "Listed in skills section only."
                    weak_skills.append({
                        "canonical_skill": canon,
                        "status": "WEAK",
                        "importance": importance,
                        "confidence": 0.65,
                        "evidence_citation": citation,
                        "related_to": None,
                        "reason": f"Listed in skills section without explicit project or work experience metrics."
                    })
                continue

            # 2. Transferable cluster check
            found_related = False
            for cand_canon_lower, cand_info in candidate_skills_map.items():
                is_rel, rel_desc = self.taxonomy_service.are_skills_related(canon, cand_info.get("canonical_skill", ""))
                if is_rel and cand_canon_lower not in covered_candidate_skills:
                    covered_candidate_skills.add(cand_canon_lower)
                    found_related = True
                    earned_weight += weight_multiplier * 0.70  # transferable credit
                    citation = cand_info.get("evidence", ["Present in candidate background"])[0]
                    related_partial_skills.append({
                        "canonical_skill": canon,
                        "status": "RELATED_PARTIAL",
                        "importance": importance,
                        "confidence": 0.75,
                        "evidence_citation": citation,
                        "related_to": cand_info.get("canonical_skill"),
                        "reason": f"Candidate possesses transferable skill '{cand_info.get('canonical_skill')}' ({rel_desc})"
                    })
                    break

            if found_related:
                continue

            # 3. Missing skill
            missing_skills.append({
                "canonical_skill": canon,
                "status": "MISSING",
                "importance": importance,
                "confidence": 1.0,
                "evidence_citation": None,
                "related_to": None,
                "reason": f"Taxonomy specifies '{canon}' as {importance}, but no direct or transferable evidence was found."
            })

        # 4. Extra Skills (in candidate resume but not required by this role)
        extra_skills = []
        for cand_canon_lower, cand_info in candidate_skills_map.items():
            if cand_canon_lower not in covered_candidate_skills:
                extra_skills.append(cand_info.get("canonical_skill"))

        # Calculate fit score (0-100)
        raw_score = (earned_weight / max(total_weight, 1.0)) * 100.0
        fit_score = round(min(max(raw_score, 10.0), 100.0), 1)

        # Generate concise gap summary
        gap_summary = self.gap_summarizer.summarize_role_gap(
            role_display_name=role.display_name,
            seniority=role.seniority,
            matched_skills=matched_skills,
            weak_skills=weak_skills,
            missing_skills=missing_skills,
            related_partial_skills=related_partial_skills,
            extra_skills=extra_skills
        )

        return {
            "role_key": role.role_key,
            "display_name": role.display_name,
            "seniority": role.seniority,
            "domain": role.domain,
            "fit_score": fit_score,
            "matched_skills": matched_skills,
            "weak_skills": weak_skills,
            "missing_skills": missing_skills,
            "related_partial_skills": related_partial_skills,
            "extra_skills": extra_skills,
            "gap_summary": gap_summary
        }
