import re
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup

from app.services.taxonomy_service import TaxonomyService
from app.utils.text_cleaner import clean_resume_text
from app.utils.logger import logger


class JobDescriptionParserService:
    def __init__(self, taxonomy_service: TaxonomyService):
        self.taxonomy_service = taxonomy_service

    async def fetch_url_content(self, url: str) -> str:
        """Fetches and cleans text from a public job posting URL with timeouts and error handling."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Remove script, style, header, footer elements
                for elem in soup(["script", "style", "header", "footer", "nav", "noscript"]):
                    elem.extract()

                text = soup.get_text(separator="\n")
                return clean_resume_text(text)
        except Exception as e:
            logger.error(f"Failed to fetch JD from URL {url}: {e}")
            raise ValueError(f"Could not retrieve job description from the provided URL: {str(e)}")

    def detect_seniority(self, text: str) -> str:
        text_lower = text.lower()
        if any(term in text_lower for term in ["principal", "staff engineer", "tech lead", "lead engineer", "architect", "engineering manager"]):
            return "lead"
        if any(term in text_lower for term in ["senior", "sr.", "sr ", "advanced", "5+ years", "6+ years", "7+ years", "8+ years"]):
            return "senior"
        if any(term in text_lower for term in ["junior", "jr.", "entry level", "entry-level", "graduate", "associate"]):
            return "junior"
        if any(term in text_lower for term in ["intern", "internship", "co-op"]):
            return "intern"
        return "mid"

    def detect_experience_years(self, text: str) -> Dict[str, Any]:
        """Detects required years of experience from patterns like '3+ years', '3-5 years', etc."""
        pattern = re.compile(
            r"(\d{1,2})(?:\s*[\-\–\to]\s*(\d{1,2}))?\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?",
            re.IGNORECASE
        )
        matches = pattern.findall(text)
        if matches:
            first_match = matches[0]
            min_years = int(first_match[0])
            max_years = int(first_match[1]) if first_match[1] else None
            return {
                "minimum_years": min_years,
                "maximum_years": max_years,
                "detected_from_text": True
            }
        return {
            "minimum_years": 0,
            "maximum_years": None,
            "detected_from_text": False
        }

    def detect_job_title(self, text: str, default_title: Optional[str] = None) -> str:
        if default_title and default_title.strip():
            return default_title.strip()

        # Look for title-like phrases in first few lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:5]:
            if any(term in line.lower() for term in ["engineer", "developer", "architect", "manager", "designer", "analyst", "lead", "specialist"]):
                if len(line) < 80:
                    return line
        return "Software Engineer"

    def parse(self, raw_text: str, title: Optional[str] = None, company: Optional[str] = None) -> Dict[str, Any]:
        cleaned_text = clean_resume_text(raw_text)
        resolved_title = self.detect_job_title(cleaned_text, title)
        seniority = self.detect_seniority(cleaned_text)
        exp_req = self.detect_experience_years(cleaned_text)

        # Detect domain
        domain = "software_engineering"
        text_lower = cleaned_text.lower()
        if any(w in text_lower for w in ["machine learning", "data science", "pytorch", "tensorflow", "nlp"]):
            domain = "data_ai"
        elif any(w in text_lower for w in ["devops", "sre", "infrastructure", "kubernetes", "terraform"]):
            domain = "devops_cloud"
        elif any(w in text_lower for w in ["frontend", "front-end", "react", "css", "html", "vue"]):
            domain = "frontend"

        # Split into mandatory vs preferred sections
        required_skills: List[Dict[str, Any]] = []
        preferred_skills: List[Dict[str, Any]] = []
        responsibilities: List[str] = []
        qualifications: List[str] = []

        # Segment JD lines
        lines = [l.strip() for l in cleaned_text.split("\n") if l.strip()]
        current_section = "required"
        required_lines: List[str] = []
        preferred_lines: List[str] = []

        for line in lines:
            line_lower = line.lower()
            if any(h in line_lower for h in ["preferred", "nice to have", "bonus", "plus", "desired", "good to have", "optional"]):
                current_section = "preferred"
            elif any(h in line_lower for h in ["required", "requirements", "qualifications", "must have", "what you need", "core skills", "minimum requirements"]):
                current_section = "required"
            elif any(h in line_lower for h in ["responsibilities", "what you'll do", "what you will do", "duties", "the role"]):
                current_section = "responsibilities"

            if current_section == "responsibilities":
                responsibilities.append(re.sub(r"^[\*\-\•]\s*", "", line))
            elif current_section == "preferred":
                preferred_lines.append(line)
                qualifications.append(re.sub(r"^[\*\-\•]\s*", "", line))
            else:
                required_lines.append(line)
                qualifications.append(re.sub(r"^[\*\-\•]\s*", "", line))

        preferred_blob = " \n ".join(preferred_lines).lower()
        required_blob = " \n ".join(required_lines).lower()

        # Scan text for taxonomy skills
        seen_canonical = set()
        for canon_key, skill_obj in self.taxonomy_service.exact_map.items():
            pattern = r"\b" + re.escape(canon_key) + r"\b"
            if re.search(pattern, cleaned_text, re.IGNORECASE):
                canon = skill_obj.canonical_name
                if canon in seen_canonical:
                    continue
                seen_canonical.add(canon)

                in_preferred = bool(re.search(pattern, preferred_blob))
                in_required = bool(re.search(pattern, required_blob))

                # If in preferred and not in required, mark preferred; else required
                is_preferred = in_preferred and not in_required

                skill_dict = {
                    "raw_text": canon_key,
                    "canonical_skill": canon,
                    "importance": "preferred" if is_preferred else "required",
                    "confidence": 0.95
                }
                if is_preferred:
                    preferred_skills.append(skill_dict)
                else:
                    required_skills.append(skill_dict)

        # Fallback if no skills detected
        if not required_skills:
            for fallback_skill in ["Python", "REST API", "Git"]:
                required_skills.append({
                    "raw_text": fallback_skill,
                    "canonical_skill": fallback_skill,
                    "importance": "required",
                    "confidence": 0.70
                })

        keywords = list(set([s["canonical_skill"] for s in required_skills + preferred_skills]))

        return {
            "job_title": resolved_title,
            "company": company,
            "seniority": seniority,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "responsibilities": responsibilities[:10],
            "qualifications": qualifications[:10],
            "keywords": keywords,
            "experience_requirements": exp_req,
            "domain": domain
        }
