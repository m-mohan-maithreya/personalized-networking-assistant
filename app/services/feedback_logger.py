import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from app.models.schemas import LogEntry
from app.services import data_store

logger = logging.getLogger(__name__)

FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.json"

def init_feedback_file():
    """Ensures files and directories are initialized."""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

# Initialize on import
init_feedback_file()

def log_feedback(
    suggestion_text: str, 
    action: str, 
    session_id: str = "", 
    starter_id: str = ""
) -> Dict[str, Any]:
    """
    Saves feedback ('like' or 'dislike') on a starter suggestion.
    Also creates an audit log entry in the system logs.
    """
    timestamp = datetime.utcnow().isoformat()
    feedback_entry = {
         "feedback_id": str(uuid.uuid4()),
         "session_id": session_id,
         "starter_id": starter_id,
         "suggestion_text": suggestion_text,
         "action": action,
         "timestamp": timestamp
    }
    
    # 1. Save to feedback.json (history array for Streamlit UI)
    try:
        if not FEEDBACK_FILE.exists():
             init_feedback_file()
             
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
             contents = json.load(f)
             
        contents.append(feedback_entry)
        
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
             json.dump(contents, f, indent=4)
             
    except Exception as e:
        logger.error(f"Error persisting feedback to JSON file: {e}")
        
    # 2. Also log inside ER LogEntry database table for auditing
    log_id = str(uuid.uuid4())
    log_entry = LogEntry(
        LogID=log_id,
        SessionID=session_id if session_id else None,
        ActionType=f"feedback_{action}",
        PayloadJSON={
            "starter_id": starter_id,
            "suggestion_text": suggestion_text,
            "action": action
        },
        Timestamp=timestamp
    )
    # Save log to logs.json via data_store
    data_store.save_log_entry(log_entry)
    
    return feedback_entry

def load_feedback_history() -> List[Dict[str, Any]]:
    """Loads all saved feedback values (newest first)."""
    try:
        if not FEEDBACK_FILE.exists():
             return []
             
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
             contents = json.load(f)
             
        # Sort by timestamp descending
        contents.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return contents
    except Exception:
        return []
