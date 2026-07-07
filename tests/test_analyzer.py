import pytest
from app.services.event_analyzer import extract_event_themes

def test_extract_event_themes_structure():
    """
    Verify structure of the returned event themes list: type and size constraints.
    """
    desc = "National Summit on Artificial Intelligence and Sustainable Energy Systems for Urban Development"
    candidates = ["AI", "sustainability", "business", "education", "blockchain"]
    
    themes = extract_event_themes(desc, candidate_labels=candidates)
    
    assert isinstance(themes, list)
    assert len(themes) <= 3
    # Check that returned themes are in the candidate set
    for theme in themes:
        assert theme in candidates

def test_extract_event_themes_empty_guard():
    """
    Verify event analyzer safely handles empty inputs.
    """
    assert extract_event_themes("") == []
    assert extract_event_themes("   ") == []

def test_extract_event_themes_default_candidates():
    """
    Verify themes default extraction list structure when no explicit candidate labels are passed.
    """
    desc = "Blockchain finance conference on medical records data transparency"
    themes = extract_event_themes(desc)
    
    assert isinstance(themes, list)
    assert len(themes) > 0
    assert len(themes) <= 3
