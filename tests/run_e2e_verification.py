import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_verification():
    print("=== STARTING PROGRAMMATIC E2E VERIFICATION ===")
    
    # 1. Test conversation generation
    gen_payload = {
        "BioText": "Professional urban designer and sustainability analyst.",
        "EventDescription": "Sustainable Smart Cities expo on renewable grids.",
        "Interests": ["smart grids", "climate change"]
    }
    
    print("\n1. Testing POST /api/v1/generate...")
    gen_res = requests.post(f"{BASE_URL}/generate", json=gen_payload, timeout=20)
    print(f"Status Code: {gen_res.status_code}")
    assert gen_res.status_code == 200, "Generation failed"
    gen_data = gen_res.json()
    print("Themes Extracted:", gen_data["Themes"])
    print("Starters Generated:")
    for idx, starter in enumerate(gen_data["Starters"]):
        print(f"  {idx+1}. {starter['StarterText']} (ID: {starter['StarterID']})")
        
    session_id = gen_data["SessionID"]
    starter_id = gen_data["Starters"][0]["StarterID"]
    starter_text = gen_data["Starters"][0]["StarterText"]
    
    # 2. Test feedback submission
    feed_payload = {
        "suggestion_text": starter_text,
        "action": "like",
        "session_id": session_id,
        "starter_id": starter_id
    }
    print("\n2. Testing POST /api/v1/feedback...")
    feed_res = requests.post(f"{BASE_URL}/feedback", json=feed_payload, timeout=10)
    print(f"Status Code: {feed_res.status_code}")
    assert feed_res.status_code == 200, "Feedback log failed"
    print("Feedback Response:", feed_res.json())
    
    # 3. Test verification check
    print("\n3. Testing GET /api/v1/verify...")
    verify_res = requests.get(
        f"{BASE_URL}/verify", 
        params={"query": "blockchain in healthcare", "session_id": session_id}, 
        timeout=15
    )
    print(f"Status Code: {verify_res.status_code}")
    assert verify_res.status_code == 200, "Fact check failed"
    verify_data = verify_res.json()
    print("Verification Status:", verify_data["VerificationStatus"])
    print("Wikipedia Link:", verify_data["WikipediaSourceURL"])
    print("Extract Header:", verify_data["Extract"][:100] + "...")
    
    # 4. Check conversation history
    print("\n4. Verification checking /history...")
    hist_res = requests.get(f"{BASE_URL}/history", timeout=10)
    print(f"Status: {hist_res.status_code}")
    assert hist_res.status_code == 200, "History load failed"
    history = hist_res.json()["history"]
    print(f"Total sessions logged: {len(history)}")
    print(f"Latest logged Session ID: {history[0]['SessionID']}")
    
    # 5. Check feedback history
    print("\n5. Verification checking /feedback/history...")
    feed_history_res = requests.get(f"{BASE_URL}/feedback/history", timeout=10)
    print(f"Status: {feed_history_res.status_code}")
    assert feed_history_res.status_code == 200, "Feedback history load failed"
    fb_hist = feed_history_res.json()["feedback"]
    print(f"Total feedback logs: {len(fb_hist)}")
    print(f"Latest Feedback item: Action='{fb_hist[0]['action']}', Text='{fb_hist[0]['suggestion_text'][:80]}'")
    
    print("\n=== PROGRAMMATIC E2E VERIFICATION SUCCESSFUL ===")

if __name__ == "__main__":
    run_verification()
