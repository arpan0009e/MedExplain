from io import BytesIO

import pymupdf
import pytesseract
from PIL import Image
from pypdf import PdfReader


# If the normal PDF extraction produces less than this amount of
# meaningful text, we treat the PDF as potentially scanned/image-based.
MIN_EXTRACTED_TEXT_LENGTH = 50


def extract_text_from_pdf(file_content: bytes) -> tuple[str, int]:
    """
    Extract text from a PDF document.

    Normal text-based PDFs are processed with pypdf.
    If the extracted text is insufficient and the PDF contains
    image content, the PDF pages are rendered and processed using OCR.

    Args:
        file_content: PDF file content as bytes.

    Returns:
        A tuple containing:
        - extracted text
        - number of pages

    Raises:
        ValueError: If the PDF cannot be read or processed.
    """
    try:
        reader = PdfReader(BytesIO(file_content))

        pages_text = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        extracted_text = "\n\n".join(pages_text).strip()
        page_count = len(reader.pages)

        # Normal text extraction succeeded.
        if _has_usable_text(extracted_text):
            return extracted_text, page_count

        # There is no useful text. Only attempt OCR when the PDF
        # actually contains image content.
        if not _pdf_contains_images(file_content):
            return extracted_text, page_count

        # The PDF probably contains scanned/image-based pages.
        ocr_text = _extract_text_with_ocr(file_content)

        return ocr_text, page_count

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError("Unable to read the PDF file.") from exc


def _has_usable_text(text: str) -> bool:
    """
    Determine whether normal PDF extraction produced enough text
    to avoid the more expensive OCR fallback.
    """
    meaningful_text = " ".join(text.split())
    return len(meaningful_text) >= MIN_EXTRACTED_TEXT_LENGTH


def _pdf_contains_images(file_content: bytes) -> bool:
    """
    Check whether the PDF contains image objects.

    Scanned PDFs normally contain their page content as images,
    while a genuinely blank PDF does not.
    """
    try:
        with pymupdf.open(stream=file_content, filetype="pdf") as pdf_document:
            return any(
                page.get_images(full=True)
                for page in pdf_document
            )

    except Exception as exc:
        raise ValueError("Unable to inspect the PDF for image content.") from exc


def _extract_text_with_ocr(file_content: bytes) -> str:
    """
    Render PDF pages as images and extract text using Tesseract OCR.
    """
    try:
        pages_text = []

        with pymupdf.open(
            stream=file_content,
            filetype="pdf",
        ) as pdf_document:

            for page in pdf_document:
                # Render the page at a higher resolution to improve OCR accuracy.
                matrix = pymupdf.Matrix(2, 2)
                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                image_bytes = pixmap.tobytes("png")
                image = Image.open(BytesIO(image_bytes))

                text = pytesseract.image_to_string(
                    image,
                    lang="eng",
                )

                if text.strip():
                    pages_text.append(text.strip())

        return "\n\n".join(pages_text).strip()

    except Exception as exc:
        raise ValueError(
            "Unable to extract text from the PDF using OCR."
        ) from exc