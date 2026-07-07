import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

def fact_check(query: str) -> Dict[str, Any]:
    """
    Queries the Wikipedia API to retrieve a summary and sources URL for the given query.
    1. Triggers a Wikipedia web search payload to find the most relevant article title.
    2. Calls the Wikipedia REST REST API for summary extract.
    """
    res = {
        "VerifiedQueryText": query,
        "VerificationStatus": "unverified",
        "WikipediaSourceURL": "",
        "Extract": "No verification source found."
    }
    
    clean_query = query.strip()
    if not clean_query:
        return res
        
    headers = {
        "User-Agent": "PersonalizedNetworkingAssistant/1.0 (srini@example.com) Python-requests"
    }
    
    try:
        # Step 1: Search Wikipedia for the best matching page title
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": clean_query,
            "format": "json"
        }
        
        response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
        if response.status_code != 200:
            res["Extract"] = f"Wikipedia API returned code {response.status_code}."
            return res
            
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        
        if not search_results:
            res["Extract"] = f"No Wikipedia articles matched query: '{clean_query}'"
            return res
            
        # Select key title from best search result
        best_title = search_results[0]["title"]
        
        # Step 2: Fetch the page summary from Wikipedia Page Summary REST API
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(best_title)}"
        summary_response = requests.get(summary_url, headers=headers, timeout=5)
        
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            res["VerificationStatus"] = "verified"
            res["WikipediaSourceURL"] = summary_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{best_title.replace(' ', '_')}")
            res["Extract"] = summary_data.get("extract", "No extract detail available.")
        elif summary_response.status_code == 404:
            res["Extract"] = f"Summary not found for topic: '{best_title}'."
        else:
            res["Extract"] = f"Could not retrieve summary details (status code: {summary_response.status_code})."
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error verification call: {e}")
        res["Extract"] = "Network validation source offline. Please check internet connection."
    except Exception as e:
        logger.error(f"Error during verification calculation: {e}")
        res["Extract"] = f"Error during factcheck processing: {str(e)}"
        
    return res
