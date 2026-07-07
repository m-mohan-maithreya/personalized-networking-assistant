from app.services import event_analyzer


def test_event_analysis_returns_labels(monkeypatch):
    monkeypatch.setattr(event_analyzer, "_get_classifier", lambda: None)
    labels = ["AI", "healthcare", "blockchain"]
    result = event_analyzer.extract_event_themes("AI in healthcare and diagnostics", labels)
    assert isinstance(result, list)
    assert 0 < len(result) <= 3
    assert all(item in labels for item in result)


def test_event_analysis_empty_description_returns_empty():
    assert event_analyzer.extract_event_themes("") == []

