"""Text cleaning and normalization utilities for extracted document content."""

import re


def clean_text(raw_text: str) -> str:
    """Normalizes extracted document text without altering meaning.

    - Removes null bytes and unprintable control characters.
    - Joins words split across line breaks by hyphens (e.g. 'auto-\nmation' -> 'automation').
    - Normalizes horizontal spacing (multiple spaces/tabs to a single space).
    - Preserves meaningful paragraph breaks while collapsing 3+ newlines into 2.
    - Trims leading and trailing whitespace.
    """
    if not raw_text:
        return ""

    # 1. Replace null bytes and unprintable control characters with space (preserving standard newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", raw_text)

    # 2. Normalize Windows/Mac line endings to standard \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Replace non-breaking spaces with standard spaces
    text = text.replace("\u00a0", " ")

    # 4. Join hyphenated words split across line breaks
    text = re.sub(r"([A-Za-z]+)-\n([A-Za-z]+)", r"\1\2", text)

    # 5. Clean each line: collapse excessive horizontal spaces, trim line edges
    cleaned_lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(cleaned_line)

    text = "\n".join(cleaned_lines)

    # 6. Normalize paragraph breaks: collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
