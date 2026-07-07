import pytest
from unittest.mock import patch, MagicMock
from app.services.fact_checker import fact_check

@patch("requests.get")
def test_fact_check_success(mock_get):
    """
    Test wikipedia fact check workflow under successful mock responses.
    """
    # Create two mocked GET responses:
    # 1. Search article list
    mock_search = MagicMock()
    mock_search.status_code = 200
    mock_search.json.return_value = {
        "query": {
            "search": [{"title": "Blockchain in healthcare"}]
        }
    }
    
    # 2. Page summary endpoint
    mock_summary = MagicMock()
    mock_summary.status_code = 200
    mock_summary.json.return_value = {
        "content_urls": {
            "desktop": {"page": "https://en.wikipedia.org/wiki/Blockchain_in_healthcare"}
        },
        "extract": "Blockchain technology is increasingly applied to healthcare data management."
    }
    
    mock_get.side_effect = [mock_search, mock_summary]
    
    res = fact_check("blockchain in healthcare")
    
    assert res["VerificationStatus"] == "verified"
    assert res["WikipediaSourceURL"] == "https://en.wikipedia.org/wiki/Blockchain_in_healthcare"
    assert "Blockchain technology" in res["Extract"]
    
@patch("requests.get")
def test_fact_check_no_results(mock_get):
    """
    Verify status when Wikipedia search yields no articles matching the query.
    """
    mock_search = MagicMock()
    mock_search.status_code = 200
    mock_search.json.return_value = {"query": {"search": []}}
    mock_get.return_value = mock_search
    
    res = fact_check("non_existent_topic_xyz_123")
    assert res["VerificationStatus"] == "unverified"
    assert "No Wikipedia articles matched" in res["Extract"]

@patch("requests.get")
def test_fact_check_network_failure(mock_get):
    """
    Verify network timeout exception handling.
    """
    mock_get.side_effect = Exception("Connection timed out")
    
    res = fact_check("blockchain")
    assert res["VerificationStatus"] == "unverified"
    assert "Error during factcheck processing" in res["Extract"]
