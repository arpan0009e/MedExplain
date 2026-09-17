from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(file_content: bytes) -> tuple[str, int]:
    """
    Extract text from a PDF document.

    Args:
        file_content: PDF file content as bytes.

    Returns:
        A tuple containing:
        - extracted text
        - number of pages

    Raises:
        ValueError: If the PDF cannot be read.
    """
    try:
        reader = PdfReader(BytesIO(file_content))

        pages_text = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        extracted_text = "\n\n".join(pages_text)

        return extracted_text, len(reader.pages)

    except Exception as exc:
        raise ValueError("Unable to read the PDF file.") from exc