from pathlib import Path

import pytest

from app.ingestion.pdf_extractor import extract_text_from_pdf
from app.ingestion.text_cleaner import clean_text


def test_clean_text():
    raw_text = "Hemoglobin:     13.5 g/dL\n\n\n\nWBC:    7200 /uL"

    result = clean_text(raw_text)

    assert result == "Hemoglobin: 13.5 g/dL\n\nWBC: 7200 /uL"


@pytest.mark.integration
def test_extract_text_from_scanned_pdf_uses_ocr():
    pdf_path = Path(__file__).parent / "synthetic_scanned_medical_report.pdf"

    file_content = pdf_path.read_bytes()

    extracted_text, page_count = extract_text_from_pdf(file_content)

    assert page_count == 1

    assert "SYNTHETIC MEDICAL LABORATORY REPORT" in extracted_text
    assert "Sample Patient" in extracted_text
    assert "Hemoglobin" in extracted_text
    assert "13.8 g/dL" in extracted_text
    assert "LDL Cholesterol" in extracted_text
    assert "118 mg/dL" in extracted_text
    assert "5.6%" in extracted_text