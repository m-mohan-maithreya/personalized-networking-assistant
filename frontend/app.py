import streamlit as st
import requests
import sys
import os
from pathlib import Path

# Add project root to sys.path to allow services import if needed
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Backend configuration
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

# Clean, professional theme styling using Streamlit configurations
st.set_page_config(
    page_title="Personalized Networking Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design aesthetics (minimalist, clean grids, bold labels)
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }
    h1 {
        color: #1e293b;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }
    h2, h3 {
        color: #334155;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }
    .starter-card {
        background-color: #ffffff;
        color: #1e293b;
        padding: 18px;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .theme-badge {
        display: inline-block;
        background-color: #eff6ff;
        color: #1d4ed8;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 500;
        font-size: 0.85rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)


# --- STATE MANAGEMENT ---
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "session_id" not in st.session_state:
    st.session_state.session_id = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "current_themes" not in st.session_state:
    st.session_state.current_themes = []
if "fact_check_result" not in st.session_state:
    st.session_state.fact_check_result = None
if "feedback_logged" not in st.session_state:
    # Tracks which suggestions have logged feedback in current session
    st.session_state.feedback_logged = set()


# Header
st.title("🤝 Personalized Networking Assistant")
st.markdown("Generate smart, context-aware conversation starters and verify background knowledge in real time.")

# App Layout using grids
col_input, col_results = st.columns([1, 1], gap="medium")

with col_input:
    st.subheader("📋 Context Settings")
    st.caption("Provide your professional background and event details to compute custom prompts.")
    
    bio_input = st.text_area(
        "Your Background / Professional Biography",
        placeholder="e.g., Senior Software Developer with 5 years experience. Passionate about climate tech, carbon accounting and cloud architectures.",
        height=100
    )
    
    event_input = st.text_area(
        "Event Name / Description",
        placeholder="e.g., 'EcoTech Summit 2026: AI for Sustainable Cities' focusing on renewable energy grids, urban climate resilience, and eco-friendly infrastructures.",
        height=100
    )
    
    interests_input = st.text_input(
        "Your Specific Topics of Interest (comma-separated)",
        placeholder="e.g., climate change, clean energy, urban planning"
    )
    
    generate_btn = st.button("Generate Conversational Starters 🚀", use_container_width=True)
    
    if generate_btn:
        if not bio_input.strip() or not event_input.strip() or not interests_input.strip():
            st.error("Please fill in all biography, event description, and interest fields.")
        else:
            with st.spinner("Analyzing event themes and generating icebreakers (DistilBERT & GPT-2)..."):
                try:
                    interests_list = [i.strip() for i in interests_input.split(",") if i.strip()]
                    payload = {
                        "BioText": bio_input,
                        "EventDescription": event_input,
                        "Interests": interests_list
                    }
                    
                    response = requests.post(f"{BASE_URL}/generate", json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.suggestions = data.get("Starters", [])
                        st.session_state.session_id = data.get("SessionID", "")
                        st.session_state.user_id = data.get("UserID", "")
                        st.session_state.current_themes = data.get("Themes", [])
                        st.session_state.feedback_logged = set()  # Reset feedback status
                        st.success("Successfully generated starters!")
                    else:
                        st.error(f"Error ({response.status_code}): {response.json().get('detail', 'Unknown error occurred.')}")
                except Exception as e:
                    st.error(f"Failed to reach API server: {e}")

with col_results:
    st.subheader("💡 Tailored Starters")
    
    if st.session_state.suggestions:
        # Display Extracted Themes
        st.markdown("**Extracted Event Themes:**")
        theme_badges = ""
        for theme in st.session_state.current_themes:
             theme_badges += f'<span class="theme-badge">{theme}</span>'
        st.markdown(theme_badges, unsafe_allow_html=True)
        st.write("")
        
        # Display Suggestions cards
        for idx, starter in enumerate(st.session_state.suggestions):
            starter_id = starter.get("StarterID")
            text = starter.get("StarterText")
            
            # HTML Card design
            st.markdown(f'<div class="starter-card">{text}</div>', unsafe_allow_html=True)
            
            # Feedback interaction
            c_like, c_dislike, _ = st.columns([0.15, 0.15, 0.7])
            
            # Formulate unique keys to avoid state conflicts
            like_key = f"like_{starter_id}_{idx}"
            dislike_key = f"dislike_{starter_id}_{idx}"
            
            # Disable indicator if logged
            is_recorded = starter_id in st.session_state.feedback_logged
            
            with c_like:
                if st.button("👍", key=like_key, disabled=is_recorded):
                    # Submit feedback payload
                    try:
                        f_payload = {
                            "suggestion_text": text,
                            "action": "like",
                            "session_id": st.session_state.session_id,
                            "starter_id": starter_id
                        }
                        res = requests.post(f"{BASE_URL}/feedback", json=f_payload)
                        if res.status_code == 200:
                            st.session_state.feedback_logged.add(starter_id)
                            st.rerun()
                    except Exception as ex:
                        st.error(f"Feedback failure: {ex}")
                        
            with c_dislike:
                if st.button("👎", key=dislike_key, disabled=is_recorded):
                    try:
                        f_payload = {
                            "suggestion_text": text,
                            "action": "dislike",
                            "session_id": st.session_state.session_id,
                            "starter_id": starter_id
                        }
                        res = requests.post(f"{BASE_URL}/feedback", json=f_payload)
                        if res.status_code == 200:
                            st.session_state.feedback_logged.add(starter_id)
                            st.rerun()
                    except Exception as ex:
                        st.error(f"Feedback failure: {ex}")
                        
        if st.session_state.feedback_logged:
            st.info("Feedback saved! We will use this to improve prompt generation.")
    else:
        st.info("Fill out the context settings and click generate to view tailored conversation starters.")

st.markdown("---")

# --- KNOWLEDGE FACT VERIFICATION ---
st.subheader("🔍 Wikipedia Fact Verification")
col_fact_left, col_fact_right = st.columns([1, 1], gap="medium")

with col_fact_left:
    st.write("attending a conference or discussing obscure details? Quick check concepts below:")
    
    fact_query = st.text_input("Factcheck Query", placeholder="e.g. blockchain in healthcare, carbon accounting models")
    fact_btn = st.button("Verify Query 🔍", use_container_width=True)
    
    if fact_btn:
        if not fact_query.strip():
            st.error("Please enter a factcheck query first.")
        else:
            with st.spinner("Searching and validating via Wikipedia REST endpoint..."):
                try:
                    # Provide default session context if user hasn't generated one yet
                    s_id = st.session_state.session_id if st.session_state.session_id else "global_factcheck"
                    params = {"query": fact_query, "session_id": s_id}
                    
                    response = requests.get(f"{BASE_URL}/verify", params=params, timeout=12)
                    if response.status_code == 200:
                        st.session_state.fact_check_result = response.json()
                    else:
                        st.error(f"Wikipedia Check error ({response.status_code}): {response.text}")
                except Exception as e:
                    st.error(f"Could not reach server API: {e}")

with col_fact_right:
    if st.session_state.fact_check_result:
        res = st.session_state.fact_check_result
        status = res.get("VerificationStatus")
        url = res.get("WikipediaSourceURL")
        query_text = res.get("VerifiedQueryText")
        extract = res.get("Extract")
        
        # Display nicely in colors
        if status == "verified":
            st.success(f"**Verified Fact Context: '{query_text}'**")
            st.markdown(f"**Extract:** {extract}")
            if url:
                st.markdown(f"[Read Full Article on Wikipedia 🌐]({url})")
        else:
            st.warning(f"**Status: {status.upper()}**")
            st.markdown(f"**System report:** {extract}")
    else:
        st.info("Type a query and query search to test. Verification details will appear here.")

st.markdown("---")

# --- CONVERSATION AND FEEDBACK LOG HISTORY ---
st.subheader("⏱️ History & Analytics Audit")

tab_hist, tab_feed = st.tabs(["📜 Session History", "📊 Feedback Reports"])

with tab_hist:
    # Refresh button
    if st.button("Refresh History 🔄"):
        st.rerun()
         
    try:
        hist_response = requests.get(f"{BASE_URL}/history", timeout=5)
        if hist_response.status_code == 200:
            history = hist_response.json().get("history", [])
            if not history:
                 st.write("No session records logged yet.")
            else:
                 # Display last 5 sessions
                 for h in history[:5]:
                      st.markdown(f"### Session Context: `{h.get('SessionID')[:8]}...`")
                      st.write(f"**Timestamp:** {h.get('Timestamp')}")
                      st.write(f"**User Professional Bio:** {h.get('BioText')}")
                      st.write(f"**Event Description:** {h.get('EventDescription')}")
                      
                      # Themes
                      badge_str = ""
                      for t in h.get("Themes", []):
                           badge_str += f'<span class="theme-badge">{t}</span>'
                      st.markdown(f"**Extracted Themes:** {badge_str}", unsafe_allow_html=True)
                      
                      # Starters
                      st.write("**Generated Starters:**")
                      for st_item in h.get("Starters", []):
                           st.markdown(f"- {st_item.get('StarterText')}")
                      st.markdown("---")
        else:
             st.error("Error fetching historical logs.")
    except Exception as e:
         st.error(f"Cannot connect to database check: {e}")

with tab_feed:
    try:
        feed_response = requests.get(f"{BASE_URL}/feedback/history", timeout=5)
        if feed_response.status_code == 200:
            feed_data = feed_response.json().get("feedback", [])
            if not feed_data:
                st.write("No user feedback logged yet.")
            else:
                for f in feed_data[:10]:
                    emoji = "👍 Thumbs Up" if f.get("action") == "like" else "👎 Thumbs Down"
                    st.markdown(f"**Rating:** {emoji} | **Timestamp:** {f.get('timestamp')}")
                    st.markdown(f"> **Starter:** {f.get('suggestion_text')}")
                    st.write(f"*Linked Session ID:* `{f.get('session_id')[:8] if f.get('session_id') else 'N/A'}`")
                    st.markdown("---")
        else:
            st.error("Error fetching feedback report database.")
    except Exception as e:
        st.error(f"Cannot connect to feedback reports check: {e}")
