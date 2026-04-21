"""Basic smoke tests for SAFE-INTERN core flows."""

from __future__ import annotations

from agents.ml_agent import run_ml_analysis
from utils.file_parser import parse_uploaded_file
from utils.pattern_detector import detect_scam_patterns


def _test_ml_training() -> None:
    result = run_ml_analysis({"clean_text": "Pay registration fee now using upi and confirm today."})
    assert isinstance(result, dict), "ML result should be a dict"
    assert "ml_used" in result, "ML result must include ml_used flag"


def _test_pattern_detection() -> None:
    result = detect_scam_patterns(
        "Immediate joining. Pay now security deposit. Contact @hr_offerfast and scan qr to continue."
    )
    assert result.get("rule_score", 0) >= 1, "Rule score should be positive for scam text"
    assert isinstance(result.get("found_patterns"), dict), "Found patterns should be dict"


def _test_pdf_fallback() -> None:
    _, meta = parse_uploaded_file("broken.pdf", b"not-a-real-pdf")
    assert meta.get("status") == "error", "Broken PDF should fail gracefully"


def _test_unsupported_file() -> None:
    _, meta = parse_uploaded_file("archive.zip", b"123")
    assert meta.get("type") == "unsupported", "Unsupported file type must be reported"


def main() -> None:
    """Run all smoke checks and print success message."""
    _test_ml_training()
    _test_pattern_detection()
    _test_pdf_fallback()
    _test_unsupported_file()
    print("SAFE-INTERN system check passed")


if __name__ == "__main__":
    main()
