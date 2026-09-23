from typing import List, Dict, Any, Tuple
from app.services.taxonomy_service import TaxonomyService


class SkillMatcherService:
    def __init__(self, taxonomy_service: TaxonomyService):
        self.taxonomy_service = taxonomy_service

    def match_skills(
        self,
        resume_skills: List[Dict[str, Any]],
        jd_required_skills: List[Dict[str, Any]],
        jd_preferred_skills: List[Dict[str, Any]],
        resume_experience: List[Dict[str, Any]],
        resume_projects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compares resume skills with JD requirements and classifies each into:
        - MATCHED: Direct evidence in project/experience
        - WEAK: Listed only without project/experience proof, or confidence is marginal
        - RELATED_PARTIAL: Transferable cluster match (e.g. Flask -> FastAPI, MySQL -> PostgreSQL)
        - MISSING: No direct or related evidence
        - EXTRA_RESUME_SKILLS: Candidate strengths not required by the JD
        """
        # Build map of candidate skills
        candidate_skills_map: Dict[str, Dict[str, Any]] = {}
        for s in resume_skills:
            canon = s.get("canonical_skill", "").strip().lower()
            if canon:
                candidate_skills_map[canon] = s

        # Identify skills that have experiential proof (in experience or projects)
        experiential_skills = set()
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

        all_jd_requirements = []
        for req in jd_required_skills:
            all_jd_requirements.append({**req, "importance": "required"})
        for pref in jd_preferred_skills:
            all_jd_requirements.append({**pref, "importance": "preferred"})

        matched_skills = []
        weak_skills = []
        missing_skills = []
        related_partial_skills = []
        covered_candidate_skills = set()

        for jd_item in all_jd_requirements:
            canon_jd = jd_item.get("canonical_skill", "").strip()
            canon_jd_lower = canon_jd.lower()
            importance = jd_item.get("importance", "required")

            # 1. Direct candidate match check
            if canon_jd_lower in candidate_skills_map:
                cand_info = candidate_skills_map[canon_jd_lower]
                covered_candidate_skills.add(canon_jd_lower)
                evidence = cand_info.get("evidence", [])
                
                # Check whether there is experiential proof
                has_experience_proof = (
                    canon_jd_lower in experiential_skills or
                    any("experience" in ev.lower() or "project" in ev.lower() for ev in evidence)
                )

                if has_experience_proof:
                    citation = evidence[0] if evidence else f"Demonstrated in work experience or projects."
                    matched_skills.append({
                        "canonical_skill": canon_jd,
                        "raw_text": jd_item.get("raw_text", canon_jd),
                        "status": "MATCHED",
                        "importance": importance,
                        "confidence": cand_info.get("confidence", 1.0),
                        "evidence_citation": citation,
                        "related_to": None,
                        "reason": f"Directly demonstrated with project or work experience evidence: {citation}"
                    })
                else:
                    citation = evidence[0] if evidence else f"Listed in skills section only."
                    weak_skills.append({
                        "canonical_skill": canon_jd,
                        "raw_text": jd_item.get("raw_text", canon_jd),
                        "status": "WEAK",
                        "importance": importance,
                        "confidence": 0.65,
                        "evidence_citation": citation,
                        "related_to": None,
                        "reason": f"Mentioned in skills list but lacks deep project or experiential corroboration: {citation}"
                    })
                continue

            # 2. Related Transferable Skill Check
            found_related = False
            for cand_canon_lower, cand_info in candidate_skills_map.items():
                is_rel, rel_desc = self.taxonomy_service.are_skills_related(canon_jd, cand_info.get("canonical_skill", ""))
                if is_rel and cand_canon_lower not in covered_candidate_skills:
                    covered_candidate_skills.add(cand_canon_lower)
                    found_related = True
                    citation = cand_info.get("evidence", ["Found in profile"])[0]
                    related_partial_skills.append({
                        "canonical_skill": canon_jd,
                        "raw_text": jd_item.get("raw_text", canon_jd),
                        "status": "RELATED_PARTIAL",
                        "importance": importance,
                        "confidence": 0.75,
                        "evidence_citation": citation,
                        "related_to": cand_info.get("canonical_skill"),
                        "reason": f"Candidate has transferable skill '{cand_info.get('canonical_skill')}' ({rel_desc})"
                    })
                    break

            if found_related:
                continue

            # 3. Missing Requirement
            missing_skills.append({
                "canonical_skill": canon_jd,
                "raw_text": jd_item.get("raw_text", canon_jd),
                "status": "MISSING",
                "importance": importance,
                "confidence": 1.0,
                "evidence_citation": None,
                "related_to": None,
                "reason": f"JD specifies '{canon_jd}' as {importance}, but no direct or transferable evidence was identified in the resume."
            })

        # 4. Extra Candidate Skills
        extra_skills = []
        for cand_canon_lower, cand_info in candidate_skills_map.items():
            if cand_canon_lower not in covered_candidate_skills:
                extra_skills.append(cand_info.get("canonical_skill"))

        return {
            "matched_skills": matched_skills,
            "weak_skills": weak_skills,
            "missing_skills": missing_skills,
            "related_partial_skills": related_partial_skills,
            "extra_skills": extra_skills
        }
