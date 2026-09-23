import os
import io
import re
import yaml
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF
import docx  # python-docx
import pdfplumber

from app.core.config import settings
from app.core.exceptions import FileValidationError, ParsingException
from app.utils.text_cleaner import clean_resume_text
from app.utils.logger import logger


class ResumeParserService:
    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        rules_path = os.path.join(settings.CONFIG_DIR, "extraction_rules.yaml")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {"sections": {}, "degrees": {}, "seniority_indicators": {}, "common_aliases": {}}

    def validate_file(self, filename: str, file_bytes: bytes) -> str:
        """Validates file extension, size, and non-empty content."""
        if not file_bytes or len(file_bytes) == 0:
            raise FileValidationError("Uploaded file is empty.")

        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_size_bytes:
            raise FileValidationError(f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.")

        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise FileValidationError(f"Unsupported file type '.{ext}'. Allowed types: {settings.ALLOWED_EXTENSIONS}")

        return ext

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using PyMuPDF, with fallback to pdfplumber."""
        text = ""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()
        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}. Falling back to pdfplumber.")

        # Fallback to pdfplumber if text is empty or sparse
        if not text.strip():
            try:
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            except Exception as e:
                logger.error(f"pdfplumber also failed: {e}")

        if not text.strip():
            raise ParsingException("Unable to extract text from PDF. The document may be scanned or empty.")

        return text

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text_chunks = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_chunks.append(para.text)
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        text_chunks.append(" | ".join(row_text))
            text = "\n".join(text_chunks)
        except Exception as e:
            raise ParsingException(f"Failed to read DOCX file: {str(e)}")

        if not text.strip():
            raise ParsingException("DOCX file contains no readable text.")

        return text

    def extract_raw_text(self, filename: str, file_bytes: bytes) -> tuple[str, str]:
        """Validates and extracts cleaned text from resume file."""
        ext = self.validate_file(filename, file_bytes)
        if ext == "pdf":
            raw_text = self.extract_text_from_pdf(file_bytes)
        elif ext == "docx":
            raw_text = self.extract_text_from_docx(file_bytes)
        else:
            raise FileValidationError(f"Unsupported format {ext}")

        cleaned = clean_resume_text(raw_text)
        return cleaned, ext

    def segment_sections(self, text: str) -> Dict[str, str]:
        """Segments resume text into standard sections based on regex/rules."""
        sections_config = self.rules.get("sections", {})
        
        # Build mapping of canonical section -> regex pattern
        patterns: Dict[str, re.Pattern] = {}
        for canonical, aliases in sections_config.items():
            pattern_str = r"^(?:[0-9\.\-\*\s]*)(?:" + "|".join(re.escape(a) for a in aliases) + r")(?:\s*[:\-])?\s*$"
            patterns[canonical] = re.compile(pattern_str, re.IGNORECASE)

        lines = text.split("\n")
        section_boundaries: List[tuple[int, str]] = []

        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or len(stripped) > 50:
                continue

            for section_name, pattern in patterns.items():
                if pattern.match(stripped):
                    section_boundaries.append((idx, section_name))
                    break

        segmented: Dict[str, str] = {}
        if not section_boundaries:
            # If no explicit headings detected, treat the beginning as contact/summary and remainder as body
            segmented["body"] = text
            return segmented

        # Capture header before first explicit section as contact/header
        first_idx, first_section = section_boundaries[0]
        if first_idx > 0:
            segmented["contact"] = "\n".join(lines[:first_idx]).strip()

        for i in range(len(section_boundaries)):
            start_idx, sec_name = section_boundaries[i]
            end_idx = section_boundaries[i + 1][0] if i + 1 < len(section_boundaries) else len(lines)
            content = "\n".join(lines[start_idx + 1:end_idx]).strip()
            
            if sec_name in segmented:
                segmented[sec_name] += "\n" + content
            else:
                segmented[sec_name] = content

        return segmented
