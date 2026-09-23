import re
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher
from sqlalchemy.orm import Session

from app.models.taxonomy import TaxonomySkill, CustomSkill, TaxonomyOccupation
from app.repositories.taxonomy_repo import TaxonomyRepository
from app.core.config import settings
from app.utils.logger import logger


class TaxonomyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaxonomyRepository(db)
        self._load_memory_cache()

    def _load_memory_cache(self):
        """Pre-loads skills and aliases into fast in-memory lookup dicts."""
        self.exact_map: Dict[str, TaxonomySkill] = {}
        self.alias_map: Dict[str, TaxonomySkill] = {}
        self.related_clusters: Dict[str, List[str]] = {
            "fastapi": ["flask", "django", "tornado", "rest api", "aiohttp"],
            "flask": ["fastapi", "django", "rest api"],
            "django": ["fastapi", "flask", "drf", "rest api"],
            "postgresql": ["mysql", "sqlite", "sql", "mariadb", "oracle", "sql server"],
            "mysql": ["postgresql", "sqlite", "sql", "mariadb"],
            "react": ["vue.js", "angular", "svelte", "next.js", "front-end", "react native"],
            "react native": ["react", "mobile development", "swift", "kotlin"],
            "vue.js": ["react", "angular", "nuxt.js"],
            "aws": ["google cloud platform", "azure", "cloud computing", "amazon web services"],
            "amazon web services": ["aws", "google cloud platform", "azure", "cloud computing"],
            "azure": ["aws", "google cloud platform", "cloud computing", "microsoft azure"],
            "microsoft azure": ["aws", "azure", "cloud computing"],
            "google cloud platform": ["aws", "azure", "cloud computing", "gcp"],
            "docker": ["kubernetes", "podman", "containerization"],
            "kubernetes": ["docker", "openshift", "helm"],
            "graphql": ["rest api", "grpc", "api design"],
            "rest api": ["graphql", "grpc", "fastapi"],
            "mongodb": ["dynamodb", "couchdb", "cassandra", "nosql"],
            "pytorch": ["tensorflow", "keras", "machine learning", "deep learning"],
            "tensorflow": ["pytorch", "keras", "machine learning", "deep learning"],
            "selenium": ["cypress", "playwright", "testing", "pytest"],
            "cypress": ["selenium", "playwright", "testing"],
            "tableau": ["power bi", "data visualization", "looker"],
            "power bi": ["tableau", "data visualization", "looker"],
            "pandas": ["numpy", "data analysis", "sql"],
        }

        # Built-in canonical baseline skills
        builtin_skills = [
            ("Python", "esco", ["python3", "python programming", "py", "cpython"], "technical"),
            ("FastAPI", "esco", ["fast-api", "fastapi framework"], "framework"),
            ("Flask", "esco", ["flask framework", "python-flask"], "framework"),
            ("PostgreSQL", "esco", ["postgres", "pgsql", "postgresql database"], "database"),
            ("MySQL", "esco", ["mysql server", "mariadb"], "database"),
            ("Docker", "esco", ["docker engine", "docker container", "dockerization"], "tool"),
            ("Kubernetes", "esco", ["k8s", "k8s cluster", "kube"], "tool"),
            ("React", "esco", ["reactjs", "react.js", "react framework"], "framework"),
            ("TypeScript", "esco", ["ts", "typescript lang"], "technical"),
            ("JavaScript", "esco", ["js", "javascript lang"], "technical"),
            ("REST API", "esco", ["restful api", "rest", "restful web services"], "architecture"),
            ("System Design", "esco", ["software architecture", "high level design"], "architecture"),
            ("Git", "esco", ["github", "gitlab", "version control"], "tool"),
            ("Amazon Web Services", "onet", ["aws", "amazon cloud", "aws cloud"], "cloud"),
            ("Microsoft Azure", "onet", ["azure", "ms azure"], "cloud"),
            ("Google Cloud Platform", "onet", ["gcp", "google cloud"], "cloud"),
            ("SQL", "onet", ["structured query language", "sql queries"], "database"),
            ("Redis", "onet", ["redis cache", "in-memory store"], "database"),
            ("CI/CD", "onet", ["continuous integration", "continuous deployment", "cicd"], "devops"),
            ("Linux", "onet", ["unix", "ubuntu", "debian", "linux os"], "system"),
            ("HTML", "esco", ["html5"], "technical"),
            ("CSS", "esco", ["css3", "stylesheets"], "technical"),
            ("Tailwind CSS", "custom", ["tailwindcss", "tailwind"], "framework"),
            ("Next.js", "custom", ["nextjs", "next js"], "framework"),
            ("GraphQL", "onet", ["graphql api", "gql"], "architecture"),
            ("Terraform", "onet", ["terraform iac", "hashicorp terraform"], "tool"),
            ("Bash", "onet", ["shell script", "shell scripting", "bash script"], "technical"),
            ("Monitoring", "onet", ["observability", "metrics monitoring"], "devops"),
            ("Data Analysis", "esco", ["data analytics", "analyzing data"], "analytical"),
            ("Tableau", "onet", ["tableau software", "tableau desktop"], "tool"),
            ("Power BI", "onet", ["powerbi", "microsoft power bi"], "tool"),
            ("Excel", "onet", ["ms excel", "spreadsheets"], "tool"),
            ("Pandas", "custom", ["python pandas", "pandas dataframe"], "framework"),
            ("Statistics", "esco", ["statistical analysis", "applied statistics"], "analytical"),
            ("Data Visualization", "esco", ["data viz", "visual analytics"], "analytical"),
            ("Apache Spark", "onet", ["spark", "pyspark"], "framework"),
            ("Apache Airflow", "onet", ["airflow", "workflow orchestration"], "tool"),
            ("Kafka", "onet", ["apache kafka", "event streaming"], "tool"),
            ("Snowflake", "onet", ["snowflake data warehouse", "snowflake dw"], "database"),
            ("Machine Learning", "esco", ["ml", "machine learning algorithms"], "ai_ml"),
            ("PyTorch", "custom", ["torch", "pytorch framework"], "framework"),
            ("TensorFlow", "custom", ["tf", "tensorflow framework"], "framework"),
            ("MLOps", "custom", ["machine learning operations", "ml pipelines"], "ai_ml"),
            ("Scikit-Learn", "custom", ["sklearn", "scikit learn"], "framework"),
            ("Testing", "esco", ["software testing", "qa testing"], "quality"),
            ("Selenium", "onet", ["selenium webdriver"], "tool"),
            ("Pytest", "custom", ["pytest framework", "python testing"], "tool"),
            ("Cypress", "custom", ["cypress.io", "cypress testing"], "tool"),
            ("Postman", "onet", ["postman api", "api testing"], "tool"),
            ("Performance Testing", "esco", ["load testing", "stress testing"], "quality"),
            ("Cybersecurity", "esco", ["information security", "infosec", "cyber security"], "security"),
            ("Networking", "onet", ["computer networks", "tcp/ip", "network protocols"], "system"),
            ("Vulnerability Assessment", "onet", ["vulnerability scanning", "security audit"], "security"),
            ("SIEM", "onet", ["security information and event management", "splunk"], "security"),
            ("Incident Response", "onet", ["security incident handling"], "security"),
            ("Penetration Testing", "onet", ["pen testing", "ethical hacking"], "security"),
            ("Cloud Security", "onet", ["cloud security posture"], "security"),
            ("React Native", "custom", ["react-native", "rn"], "framework"),
            ("Swift", "esco", ["swift programming", "ios swift"], "technical"),
            ("Kotlin", "esco", ["kotlin lang", "android kotlin"], "technical"),
            ("Mobile UI/UX", "esco", ["mobile design", "responsive mobile"], "design"),
            ("Prometheus", "onet", ["prometheus monitoring"], "tool"),
            ("Incident Management", "onet", ["production incident management"], "devops"),
        ]

        for canon_name, source, aliases, stype in builtin_skills:
            pseudo_skill = TaxonomySkill(
                id=f"builtin-{canon_name.lower()}",
                source=source,
                source_id=f"builtin-{canon_name.lower()}",
                canonical_name=canon_name,
                aliases=aliases,
                skill_type=stype
            )
            self.exact_map[canon_name.strip().lower()] = pseudo_skill
            for a in aliases:
                self.alias_map[a.strip().lower()] = pseudo_skill

        try:
            skills = self.repo.find_all_skills()
            for s in skills:
                canon_key = s.canonical_name.strip().lower()
                self.exact_map[canon_key] = s
                if s.aliases and isinstance(s.aliases, list):
                    for alias in s.aliases:
                        self.alias_map[alias.strip().lower()] = s
                if s.related_skills and isinstance(s.related_skills, list):
                    existing = self.related_clusters.get(canon_key, [])
                    self.related_clusters[canon_key] = list(set(existing + [r.lower() for r in s.related_skills]))
        except Exception as e:
            logger.warning(f"Failed to load taxonomy from database (table may be empty or unmigrated): {e}")

        # Also load custom skills
        try:
            custom_skills = self.repo.get_custom_skills()
            for cs in custom_skills:
                canon_key = cs.canonical_name.strip().lower()
                # Create a pseudo TaxonomySkill object representation
                mock_s = TaxonomySkill(
                    id=cs.id,
                    source="custom",
                    source_id=f"custom-{canon_key}",
                    canonical_name=cs.canonical_name,
                    aliases=cs.aliases or [],
                    skill_type=cs.skill_type or "technical"
                )
                self.exact_map[canon_key] = mock_s
                if cs.aliases and isinstance(cs.aliases, list):
                    for alias in cs.aliases:
                        self.alias_map[alias.strip().lower()] = mock_s
        except Exception as e:
            logger.warning(f"Failed to load custom skills: {e}")

    def normalize_skill_name(self, raw_name: str) -> str:
        """Normalizes skill text by stripping punctuation, extra spaces, and casing."""
        name = raw_name.strip()
        name = re.sub(r"[^\w\s\.\+\#\-]", "", name)
        return name

    def resolve_skill(self, raw_name: str) -> Dict[str, Any]:
        """Resolves a skill string into a canonical skill with confidence and source."""
        normalized = self.normalize_skill_name(raw_name).lower()
        if not normalized:
            return {
                "raw_text": raw_name,
                "canonical_skill": raw_name.strip(),
                "taxonomy_source": "unmapped",
                "taxonomy_id": None,
                "confidence": 0.0,
            }

        # 1. Exact Match
        if normalized in self.exact_map:
            s = self.exact_map[normalized]
            return {
                "raw_text": raw_name,
                "canonical_skill": s.canonical_name,
                "taxonomy_source": s.source,
                "taxonomy_id": s.source_id or str(s.id),
                "confidence": 1.0,
            }

        # 2. Alias Match
        if normalized in self.alias_map:
            s = self.alias_map[normalized]
            return {
                "raw_text": raw_name,
                "canonical_skill": s.canonical_name,
                "taxonomy_source": s.source,
                "taxonomy_id": s.source_id or str(s.id),
                "confidence": 0.96,
            }

        # 3. Fuzzy Match
        best_match: Optional[TaxonomySkill] = None
        best_ratio = 0.0

        for canon_key, skill_obj in self.exact_map.items():
            ratio = SequenceMatcher(None, normalized, canon_key).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = skill_obj

        for alias_key, skill_obj in self.alias_map.items():
            ratio = SequenceMatcher(None, normalized, alias_key).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = skill_obj

        if best_match and best_ratio >= settings.FUZZY_MATCH_THRESHOLD:
            return {
                "raw_text": raw_name,
                "canonical_skill": best_match.canonical_name,
                "taxonomy_source": best_match.source,
                "taxonomy_id": best_match.source_id or str(best_match.id),
                "confidence": round(best_ratio, 2),
            }

        # Unmapped fallback
        return {
            "raw_text": raw_name,
            "canonical_skill": raw_name.strip().title(),
            "taxonomy_source": "custom",
            "taxonomy_id": f"unmapped-{normalized[:20]}",
            "confidence": 0.50,
        }

    def are_skills_related(self, skill_a: str, skill_b: str) -> Tuple[bool, Optional[str]]:
        """Checks if two skills are closely related/transferable in the taxonomy."""
        a = skill_a.strip().lower()
        b = skill_b.strip().lower()

        if a == b:
            return True, "identical"

        related_to_a = self.related_clusters.get(a, [])
        if b in related_to_a:
            return True, f"{skill_a} is transferable to {skill_b}"

        related_to_b = self.related_clusters.get(b, [])
        if a in related_to_b:
            return True, f"{skill_b} is transferable to {skill_a}"

        return False, None
