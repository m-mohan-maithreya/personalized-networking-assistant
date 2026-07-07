import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Verify HTTP GET / returns API server health details."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch("app.routers.conversation.extract_event_themes")
@patch("app.routers.conversation.generate_topics")
def test_generate_endpoint_success(mock_generate, mock_extract):
    """Test generating starters endpoint using mocked engines."""
    mock_extract.return_value = ["AI", "sustainability"]
    mock_generate.return_value = ["How is AI helping carbon offsets?", "What urban systems use AI?"]
    
    payload = {
        "BioText": "I work in carbon tech and software optimization.",
        "EventDescription": "Conference on green AI systems and carbon reduction",
        "Interests": ["green AI", "carbon counting"]
    }
    
    response = client.post("/api/v1/generate", json=payload)
    
    assert response.status_code == 200
    resp_json = response.json()
    assert "SessionID" in resp_json
    assert "UserID" in resp_json
    assert "EventID" in resp_json
    assert resp_json["Themes"] == ["AI", "sustainability"]
    assert len(resp_json["Starters"]) == 2
    assert resp_json["Starters"][0]["StarterText"] == "How is AI helping carbon offsets?"

def test_generate_endpoint_invalid_payload():
    """Verify endpoint triggers 422 error on schema violations."""
    # Interests field missing or wrong type
    payload = {
        "BioText": "Junior Developer",
        "EventDescription": "Networking event"
    }
    response = client.post("/api/v1/generate", json=payload)
    assert response.status_code == 422

@patch("app.routers.conversation.fact_check")
def test_verify_endpoint_success(mock_check):
    """Test verification endpoint using mocked engine response."""
    mock_check.return_value = {
        "VerifiedQueryText": "blockchain",
        "VerificationStatus": "verified",
        "WikipediaSourceURL": "https://en.wikipedia.org/wiki/Blockchain",
        "Extract": "A blockchain is a distributed ledger."
    }
    
    response = client.get("/api/v1/verify?query=blockchain&session_id=test_session")
    
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["VerificationStatus"] == "verified"
    assert resp_json["WikipediaSourceURL"] == "https://en.wikipedia.org/wiki/Blockchain"
    assert resp_json["Extract"] == "A blockchain is a distributed ledger."

def test_feedback_endpoint_success():
    """Test submitting likes and dislikes logs to database files."""
    payload = {
        "suggestion_text": "How do you apply green architecture?",
        "action": "like",
        "session_id": "test_session_123",
        "starter_id": "starter_567"
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Test invalid action input
    invalid_payload = payload.copy()
    invalid_payload["action"] = "some_invalid_rating"
    response = client.post("/api/v1/feedback", json=invalid_payload)
    assert response.status_code == 400

def test_history_endpoints():
    """Test retrieving session lists and feedback audits directories."""
    # Ensure they return 200 list responses
    response_hist = client.get("/api/v1/history")
    assert response_hist.status_code == 200
    assert "history" in response_hist.json()
    
    response_feed = client.get("/api/v1/feedback/history")
    assert response_feed.status_code == 200
    assert "feedback" in response_feed.json()
