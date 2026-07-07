import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.models.schemas import (
    UserProfile, EventContext, NetworkingSession, 
    GeneratedStarter, WikipediaFactCheck, LogEntry
)

# Base directory for data files
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# File paths matching ER tables
FILES = {
    "users": DATA_DIR / "users.json",
    "events": DATA_DIR / "events.json",
    "sessions": DATA_DIR / "sessions.json",
    "starters": DATA_DIR / "starters.json",
    "fact_checks": DATA_DIR / "fact_checks.json",
    "logs": DATA_DIR / "logs.json",
}

def init_db():
    """Initializes the database folders and files if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for model_key, file_path in FILES.items():
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

# Initialize immediately on import
init_db()

def _load_data(model_key: str) -> List[Dict[str, Any]]:
    """Loads text from JSON file."""
    file_path = FILES.get(model_key)
    if not file_path or not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_data(model_key: str, data: List[Dict[str, Any]]):
    """Writes list database to file."""
    file_path = FILES.get(model_key)
    if not file_path:
        return
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# operations for USER_PROFILE
def save_user_profile(user: UserProfile):
    profiles = _load_data("users")
    # Update if exists, else append
    profiles = [p for p in profiles if p.get("UserID") != user.UserID]
    profiles.append(user.model_dump())
    _save_data("users", profiles)

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    profiles = _load_data("users")
    for p in profiles:
        if p.get("UserID") == user_id:
            return UserProfile(**p)
    return None

def get_all_user_profiles() -> List[UserProfile]:
    return [UserProfile(**p) for p in _load_data("users")]

# operations for EVENT_CONTEXT
def save_event_context(event: EventContext):
    events = _load_data("events")
    events = [e for e in events if e.get("EventID") != event.EventID]
    events.append(event.model_dump())
    _save_data("events", events)

def get_event_context(event_id: str) -> Optional[EventContext]:
    events = _load_data("events")
    for e in events:
        if e.get("EventID") == event_id:
            return EventContext(**e)
    return None

# operations for NETWORKING_SESSION
def save_networking_session(session: NetworkingSession):
    sessions = _load_data("sessions")
    sessions.append(session.model_dump())
    _save_data("sessions", sessions)

def get_all_sessions() -> List[NetworkingSession]:
    return [NetworkingSession(**s) for s in _load_data("sessions")]

# operations for GENERATED_STARTER
def save_generated_starter(starter: GeneratedStarter):
    starters = _load_data("starters")
    starters.append(starter.model_dump())
    _save_data("starters", starters)

def get_starters_by_session(session_id: str) -> List[GeneratedStarter]:
    starters = _load_data("starters")
    return [GeneratedStarter(**s) for s in starters if s.get("SessionID") == session_id]

# operations for WIKIPEDIA_FACT_CHECK
def save_wikipedia_fact_check(fc: WikipediaFactCheck):
    checks = _load_data("fact_checks")
    checks.append(fc.model_dump())
    _save_data("fact_checks", checks)

def get_fact_checks_by_session(session_id: str) -> List[WikipediaFactCheck]:
    checks = _load_data("fact_checks")
    return [WikipediaFactCheck(**c) for c in checks if c.get("SessionID") == session_id]

def get_all_fact_checks() -> List[WikipediaFactCheck]:
    return [WikipediaFactCheck(**c) for c in _load_data("fact_checks")]

# operations for LOG_ENTRY (Interaction/Audit logs)
def save_log_entry(log: LogEntry):
    logs = _load_data("logs")
    logs.append(log.model_dump())
    _save_data("logs", logs)

def get_all_logs() -> List[LogEntry]:
    return [LogEntry(**l) for l in _load_data("logs")]
