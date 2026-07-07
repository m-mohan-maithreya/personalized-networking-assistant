import pytest
from app.services.topic_generator import generate_topics, generate_template_starters

def test_generate_topics_structure():
    """
    Verify structure of generated topics list: type, counts, and string properties.
    """
    themes = ["AI", "sustainability", "urban planning"]
    interests = ["climate change", "smart grids"]
    
    starters = generate_topics(themes, interests)
    
    assert isinstance(starters, list)
    assert len(starters) > 0
    assert len(starters) <= 3
    for s in starters:
        assert isinstance(s, str)
        assert len(s.strip()) > 5

def test_generate_template_starters():
    """
    Verify fallback template-based generation logic.
    """
    themes = ["blockchain"]
    interests = ["healthcare"]
    
    templates = generate_template_starters(themes, interests)
    assert isinstance(templates, list)
    assert len(templates) >= 2
    for s in templates:
        assert "blockchain" in s.lower() or "healthcare" in s.lower()
