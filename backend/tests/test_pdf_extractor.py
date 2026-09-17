from app.ingestion.text_cleaner import clean_text


def test_clean_text():
    raw_text = "Hemoglobin:     13.5 g/dL\n\n\n\nWBC:    7200 /uL"

    result = clean_text(raw_text)

    assert result == "Hemoglobin: 13.5 g/dL\n\nWBC: 7200 /uL"