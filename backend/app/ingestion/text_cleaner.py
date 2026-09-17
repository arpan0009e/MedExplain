import re


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving meaningful structure.
    """

    # Normalize Windows and old-style line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing whitespace from each line
    text = "\n".join(line.strip() for line in text.splitlines())

    # Collapse 3+ consecutive blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse repeated spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()