import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.models.schemas import (
    UserProfile, EventContext, NetworkingSession, GeneratedStarter, LogEntry
)
from app.services import data_store

def log_conversation(
    bio_text: str, 
    event_desc: str, 
    themes: List[str], 
    starters: List[str],
    prompt_used: str = ""
) -> Dict[str, Any]:
    """
    Creates and records all entities for a conversation generation session.
    Fulfills 1-to-many relationships in the ER model:
    - UserProfile -> Session (1:m)
    - EventContext -> Session (1:m)
    - Session -> GeneratedStarters (1:m)
    - Session -> LogEntry (1:m)
    """
    session_timestamp = datetime.utcnow().isoformat()
    
    # 1. Create IDs
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, bio_text[:50].replace(" ", "_")))
    event_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, event_desc[:50].replace(" ", "_")))
    session_id = str(uuid.uuid4())
    
    # 2. Save User Profile
    user_profile = UserProfile(
        UserID=user_id,
        BioText=bio_text,
        currentEventCache=event_desc
    )
    data_store.save_user_profile(user_profile)
    
    # 3. Save Event Context
    event_context = EventContext(
        EventID=event_id,
        EventDescription=event_desc,
        AnalyzedThemes=themes
    )
    data_store.save_event_context(event_context)
    
    # 4. Save Networking Session
    session = NetworkingSession(
        SessionID=session_id,
        UserID=user_id,
        EventID=event_id,
        SessionTimestamp=session_timestamp
    )
    data_store.save_networking_session(session)
    
    # 5. Save Generated Starters
    starters_saved = []
    for starter_text in starters:
        starter_id = str(uuid.uuid4())
        starter = GeneratedStarter(
            StarterID=starter_id,
            SessionID=session_id,
            StarterText=starter_text,
            ContextPromptUsed=prompt_used
        )
        data_store.save_generated_starter(starter)
        starters_saved.append(starter)
        
    # 6. Save audit Log Entry
    log_id = str(uuid.uuid4())
    log_entry = LogEntry(
        LogID=log_id,
        SessionID=session_id,
        ActionType="generate_starter",
        PayloadJSON={
            "user_id": user_id,
            "event_id": event_id,
            "themes": themes,
            "starters": starters
        },
        Timestamp=session_timestamp
    )
    data_store.save_log_entry(log_entry)
    
    return {
        "SessionID": session_id,
        "UserID": user_id,
        "EventID": event_id,
        "Themes": themes,
        "Starters": starters_saved
    }

def load_history() -> List[Dict[str, Any]]:
    """
    Loads historical sessions including parent user profile, event description, themes,
    and actual AI starters, sorted newest-first.
    """
    sessions = data_store.get_all_sessions()
    
    history_list = []
    
    for s in sessions:
        user = data_store.get_user_profile(s.UserID)
        event = data_store.get_event_context(s.EventID)
        starters = data_store.get_starters_by_session(s.SessionID)
        
        history_list.append({
            "SessionID": s.SessionID,
            "UserID": s.UserID,
            "BioText": user.BioText if user else "",
            "EventDescription": event.EventDescription if event else "",
            "Themes": event.AnalyzedThemes if event else [],
            "Starters": [{"StarterID": st.StarterID, "StarterText": st.StarterText} for st in starters],
            "Timestamp": s.SessionTimestamp
        })
        
    # Sort history descending by timestamp
    history_list.sort(key=lambda x: x["Timestamp"], reverse=True)
    return history_list
