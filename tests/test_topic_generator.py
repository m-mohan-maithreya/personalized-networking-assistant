from app.services import topic_generator


def test_topic_generation_returns_suggestions(monkeypatch):
    monkeypatch.setattr(topic_generator, "_get_generator", lambda: None)
    suggestions = topic_generator.generate_topics(["AI", "healthcare"], ["ethics", "automation"])
    assert isinstance(suggestions, list)
    assert len(suggestions) == 3
    assert all(isinstance(item, str) for item in suggestions)
    assert all(item.strip() for item in suggestions)


def test_build_prompt_includes_context():
    prompt = topic_generator.build_prompt(["AI"], ["climate"], "Engineer")
    assert "AI" in prompt
    assert "climate" in prompt
    assert "Engineer" in prompt

