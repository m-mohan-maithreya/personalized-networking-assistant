from unittest.mock import MagicMock

from app.services import fact_checker


def test_fact_checker_returns_summary(monkeypatch):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "extract": "Artificial intelligence is intelligence demonstrated by machines.",
        "content_urls": {"desktop": {"page": "https://example.com/ai"}},
    }
    mock_response.raise_for_status.return_value = None
    monkeypatch.setattr(fact_checker.requests, "get", lambda *args, **kwargs: mock_response)

    result = fact_checker.fact_check("Artificial Intelligence")
    assert result["status"] == "verified"
    assert "machines" in result["summary"]
    assert result["source_url"] == "https://example.com/ai"


def test_fact_checker_handles_missing_summary(monkeypatch):
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None
    monkeypatch.setattr(fact_checker.requests, "get", lambda *args, **kwargs: mock_response)

    result = fact_checker.fact_check("Unknown topic")
    assert result["status"] == "not_found"
    assert result["summary"] == "No summary found."


def test_fact_checker_handles_errors(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("network error")

    monkeypatch.setattr(fact_checker.requests, "get", raise_error)
    result = fact_checker.fact_check("Artificial Intelligence")
    assert result["status"] == "error"

