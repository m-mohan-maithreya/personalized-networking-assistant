import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.config import LOG_FILE


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def log_entry(action_type: str, payload: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
    entry = {
        "LogID": str(uuid4()),
        "SessionID": session_id,
        "ActionType": action_type,
        "PayloadJSON": payload,
        "Timestamp": datetime.now().isoformat(),
    }
    logs = _read_json_list(LOG_FILE)
    logs.append(entry)
    with LOG_FILE.open("w", encoding="utf-8") as file:
        json.dump(logs, file, indent=2)
    return entry


def load_logs() -> List[Dict[str, Any]]:
    return _read_json_list(LOG_FILE)

