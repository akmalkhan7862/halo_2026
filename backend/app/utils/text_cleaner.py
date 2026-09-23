import re
import unicodedata
from typing import List


def normalize_unicode(text: str) -> str:
    """Normalize unicode and fix common ligatures (e.g. fi, fl)."""
    text = unicodedata.normalize("NFKC", text)
    ligature_map = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "–": "-",
        "—": "-",
        "’": "'",
        "“": '"',
        "”": '"',
        "•": "*",
        "◦": "*",
        "▪": "*",
        "▫": "*",
        "►": "*",
        "✔": "*",
    }
    for k, v in ligature_map.items():
        text = text.replace(k, v)
    return text


def remove_page_numbers_and_footers(lines: List[str]) -> List[str]:
    """Filter out lines that look like page numbers, headers, or footers."""
    page_patterns = [
        re.compile(r"^\s*page\s+\d+\s*(of\s+\d+)?\s*$", re.IGNORECASE),
        re.compile(r"^\s*-\s*\d+\s*-\s*$"),
        re.compile(r"^\s*\d+\s*/\s*\d+\s*$"),
        re.compile(r"^\s*\d+\s*$"),
        re.compile(r"^\s*curriculum\s+vitae\s*$", re.IGNORECASE),
        re.compile(r"^\s*resume\s*$", re.IGNORECASE),
    ]
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        if any(p.match(stripped) for p in page_patterns):
            continue
        cleaned.append(line)
    return cleaned


def clean_resume_text(text: str) -> str:
    """Full cleaning pipeline for raw extracted text."""
    if not text:
        return ""

    # Normalize unicode
    text = normalize_unicode(text)

    # Standardize newline characters
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Clean lines
    raw_lines = text.split("\n")
    filtered_lines = remove_page_numbers_and_footers(raw_lines)

    processed_lines = []
    for line in filtered_lines:
        # Normalize bullet indicators
        line = re.sub(r"^\s*[\*\-\•\◦\▪\▫\►\✔]\s*", "* ", line)
        # Collapse excessive inline spaces
        line = re.sub(r"[ \t]{2,}", " ", line)
        processed_lines.append(line.rstrip())

    cleaned_text = "\n".join(processed_lines)
    # Collapse more than 2 consecutive newlines
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text.strip()
