import re
from typing import Dict, Any, List, Set, Optional, Tuple
import spacy
from spacy.matcher import Matcher, PhraseMatcher

from app.services.taxonomy_service import TaxonomyService
from app.utils.logger import logger


class EntityExtractorService:
    def __init__(self, taxonomy_service: TaxonomyService):
        self.taxonomy_service = taxonomy_service
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            logger.warning("en_core_web_sm not found, initializing spacy.blank('en')")
            self.nlp = spacy.blank("en")

        self.matcher = Matcher(self.nlp.vocab)
        self._init_matchers()

    def _init_matchers(self):
        # Email & Phone regex
        self.email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        self.phone_regex = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
        self.linkedin_regex = re.compile(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+", re.IGNORECASE)
        self.github_regex = re.compile(r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+", re.IGNORECASE)
        self.date_range_regex = re.compile(
            r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{4})\s*(?:-|–|to)\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{4}|present|current)",
            re.IGNORECASE
        )

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extracts contact details from header/contact section or full text."""
        contact = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "location": None
        }

        # Email
        email_match = self.email_regex.search(text)
        if email_match:
            contact["email"] = email_match.group(0).strip()

        # Phone
        phone_match = self.phone_regex.search(text)
        if phone_match:
            contact["phone"] = phone_match.group(0).strip()

        # LinkedIn & GitHub
        li_match = self.linkedin_regex.search(text)
        if li_match:
            contact["linkedin"] = li_match.group(0).strip()

        gh_match = self.github_regex.search(text)
        if gh_match:
            contact["github"] = gh_match.group(0).strip()

        # Name extraction heuristic: First non-empty line of contact section or document
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Skip if it's an email, phone, or URL
            if "@" in line or "http" in line or "www." in line or re.search(r"\d{3}", line):
                continue
            # Words in name should typically be letters
            words = line.split()
            if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
                contact["name"] = line
                break

        return contact

    def extract_skills_with_evidence(self, sections: Dict[str, str], raw_text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Extracts skills across all resume sections while preserving evidence (bullet/line and section).
        Resolves to canonical taxonomy.
        """
        raw_candidates: Set[str] = set()
        evidence_map: Dict[str, List[str]] = {}

        # 1. Look specifically in "skills" section
        skills_text = sections.get("skills", "")
        if skills_text:
            # Common delimiters: commas, bullets, pipes, slashes, newlines
            tokens = re.split(r"[,|\n\•\*\/\;\t]", skills_text)
            for t in tokens:
                token = t.strip()
                # Clean prefix/suffix punctuation
                token = re.sub(r"^[\-\:\s]+|[\-\:\s]+$", "", token)
                if 2 <= len(token) <= 40:
                    raw_candidates.add(token)
                    evidence_map.setdefault(token, []).append(f"Listed under Skills: '{token}'")

        # 2. Extract from Experience and Projects sections
        for sec_name in ["experience", "projects", "summary", "body"]:
            sec_content = sections.get(sec_name, "")
            if not sec_content:
                continue

            lines = sec_content.split("\n")
            for line in lines:
                clean_line = line.strip()
                if not clean_line or len(clean_line) < 5:
                    continue

                # Scan known taxonomy skills in line
                for canon_key, skill_obj in self.taxonomy_service.exact_map.items():
                    # Word boundary search
                    pattern = r"\b" + re.escape(canon_key) + r"\b"
                    if re.search(pattern, clean_line, re.IGNORECASE):
                        matched_term = skill_obj.canonical_name
                        raw_candidates.add(matched_term)
                        evidence_map.setdefault(matched_term, []).append(
                            f"[{sec_name.capitalize()}] {clean_line[:120]}"
                        )

                # Also check aliases
                for alias_key, skill_obj in self.taxonomy_service.alias_map.items():
                    pattern = r"\b" + re.escape(alias_key) + r"\b"
                    if re.search(pattern, clean_line, re.IGNORECASE):
                        matched_term = skill_obj.canonical_name
                        raw_candidates.add(matched_term)
                        evidence_map.setdefault(matched_term, []).append(
                            f"[{sec_name.capitalize()}] {clean_line[:120]}"
                        )

        # 3. Canonicalize each extracted candidate
        mapped_skills: List[Dict[str, Any]] = []
        unmapped_skills: List[str] = []
        seen_canonical: Set[str] = set()

        for cand in raw_candidates:
            res = self.taxonomy_service.resolve_skill(cand)
            canon = res["canonical_skill"]

            if canon in seen_canonical:
                continue
            seen_canonical.add(canon)

            # Deduplicate evidence
            raw_ev = evidence_map.get(cand, []) + evidence_map.get(canon, [])
            dedup_ev = list(dict.fromkeys(raw_ev))[:4]  # top 4 citations

            if res["taxonomy_source"] != "unmapped" and res["confidence"] >= 0.70:
                mapped_skills.append({
                    "raw_text": cand,
                    "canonical_skill": canon,
                    "taxonomy_source": res["taxonomy_source"],
                    "taxonomy_id": res["taxonomy_id"],
                    "confidence": res["confidence"],
                    "evidence": dedup_ev if dedup_ev else [f"Found in resume text: '{cand}'"]
                })
            else:
                unmapped_skills.append(cand)

        return mapped_skills, unmapped_skills

    def extract_experience(self, exp_text: str) -> List[Dict[str, Any]]:
        """Extracts structured job entries from experience section."""
        if not exp_text:
            return []

        entries = []
        lines = [l.strip() for l in exp_text.split("\n") if l.strip()]
        current_entry: Optional[Dict[str, Any]] = None

        for line in lines:
            # Check if this line looks like a title or company with date range
            date_match = self.date_range_regex.search(line)
            is_bullet = line.startswith("*") or line.startswith("-") or line.startswith("•")

            if date_match and not is_bullet:
                if current_entry:
                    entries.append(current_entry)

                # Parse company and title from line excluding the date
                date_str = date_match.group(0)
                remaining = line.replace(date_str, "").strip(" -|,")
                parts = [p.strip() for p in re.split(r"\||–|-| at ", remaining) if p.strip()]

                title = parts[0] if parts else "Role / Position"
                org = parts[1] if len(parts) > 1 else ""

                current_entry = {
                    "job_title": title,
                    "organization": org,
                    "start_date": date_match.group(1),
                    "end_date": date_match.group(2),
                    "duration_months": None,
                    "bullets": [],
                    "skills": []
                }
            elif current_entry:
                clean_bullet = re.sub(r"^[\*\-\•]\s*", "", line)
                current_entry["bullets"].append(clean_bullet)

                # Extract skills mentioned in this bullet
                for canon_key, skill_obj in self.taxonomy_service.exact_map.items():
                    if re.search(r"\b" + re.escape(canon_key) + r"\b", line, re.IGNORECASE):
                        if skill_obj.canonical_name not in current_entry["skills"]:
                            current_entry["skills"].append(skill_obj.canonical_name)
            else:
                # First line before date header
                current_entry = {
                    "job_title": line,
                    "organization": "",
                    "start_date": "",
                    "end_date": "",
                    "duration_months": None,
                    "bullets": [],
                    "skills": []
                }

        if current_entry:
            entries.append(current_entry)

        return entries

    def extract_projects(self, proj_text: str) -> List[Dict[str, Any]]:
        """Extracts structured projects from projects section."""
        if not proj_text:
            return []

        projects = []
        lines = [l.strip() for l in proj_text.split("\n") if l.strip()]
        current_project: Optional[Dict[str, Any]] = None

        for line in lines:
            is_bullet = line.startswith("*") or line.startswith("-") or line.startswith("•")
            # If line is short and not a bullet, treat as title
            if not is_bullet and len(line) < 70 and not line.endswith("."):
                if current_project:
                    projects.append(current_project)

                current_project = {
                    "title": line,
                    "description": "",
                    "technologies": [],
                    "outcomes": [],
                    "skills": []
                }
            elif current_project:
                bullet = re.sub(r"^[\*\-\•]\s*", "", line)
                if not current_project["description"]:
                    current_project["description"] = bullet
                else:
                    current_project["outcomes"].append(bullet)

                # Detect technologies
                for canon_key, skill_obj in self.taxonomy_service.exact_map.items():
                    if re.search(r"\b" + re.escape(canon_key) + r"\b", line, re.IGNORECASE):
                        if skill_obj.canonical_name not in current_project["technologies"]:
                            current_project["technologies"].append(skill_obj.canonical_name)
                            current_project["skills"].append(skill_obj.canonical_name)

        if current_project:
            projects.append(current_project)

        return projects

    def extract_education(self, edu_text: str) -> List[Dict[str, Any]]:
        if not edu_text:
            return []

        education_list = []
        lines = [l.strip() for l in edu_text.split("\n") if l.strip()]
        for line in lines:
            degree = None
            for deg_type in ["bachelor", "master", "phd", "b.s.", "m.s.", "b.tech", "m.tech", "degree", "diploma"]:
                if deg_type in line.lower():
                    degree = line
                    break
            if degree or len(education_list) == 0:
                education_list.append({
                    "degree": degree or line,
                    "institution": line if not degree else None,
                    "graduation_year": next(iter(re.findall(r"\b(19\d\d|20\d\d)\b", line)), None),
                    "gpa": next(iter(re.findall(r"\b(?:gpa|cgpa)[:\s]*([0-9\.]+)", line, re.IGNORECASE)), None)
                })
        return education_list

    def extract_certifications(self, cert_text: str) -> List[Dict[str, Any]]:
        if not cert_text:
            return []

        certs = []
        lines = [re.sub(r"^[\*\-\•]\s*", "", l.strip()) for l in cert_text.split("\n") if l.strip()]
        for line in lines:
            certs.append({
                "name": line,
                "issuer": None,
                "year": next(iter(re.findall(r"\b(19\d\d|20\d\d)\b", line)), None)
            })
        return certs

    def extract_all(self, sections: Dict[str, str], raw_text: str) -> Dict[str, Any]:
        """Full hybrid extraction execution."""
        # 1. Contact info
        contact_seed = sections.get("contact", "") or raw_text[:500]
        contact = self.extract_contact_info(contact_seed)

        # 2. Skills with evidence
        skills, unmapped_skills = self.extract_skills_with_evidence(sections, raw_text)

        # 3. Experience
        experience = self.extract_experience(sections.get("experience", ""))

        # 4. Projects
        projects = self.extract_projects(sections.get("projects", ""))

        # 5. Education & Certifications
        education = self.extract_education(sections.get("education", ""))
        certifications = self.extract_certifications(sections.get("certifications", ""))

        # 6. Keywords
        extracted_keywords = list(set(
            [s["canonical_skill"] for s in skills] +
            [w.lower() for w in re.findall(r"\b[A-Za-z]{3,}\b", raw_text) if len(w) > 3][:50]
        ))

        return {
            "contact": contact,
            "summary": sections.get("summary", ""),
            "skills": skills,
            "unmapped_skills": unmapped_skills,
            "experience": experience,
            "projects": projects,
            "education": education,
            "certifications": certifications,
            "extracted_keywords": extracted_keywords[:35],
            "raw_text_length": len(raw_text)
        }
