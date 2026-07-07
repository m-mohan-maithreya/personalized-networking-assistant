from app.services import feedback_logger, history_logger, system_logger


def test_history_logger_round_trip(tmp_path, monkeypatch):
    history_file = tmp_path / "history.json"
    monkeypatch.setattr(history_logger, "HISTORY_FILE", history_file)

    entry = history_logger.log_conversation({"description": "AI event", "interests": ["AI"]})
    history = history_logger.load_history()

    assert entry["timestamp"]
    assert len(history) == 1
    assert history[0]["description"] == "AI event"


def test_feedback_logger_round_trip(tmp_path, monkeypatch):
    feedback_file = tmp_path / "feedback.json"
    monkeypatch.setattr(feedback_logger, "FEEDBACK_FILE", feedback_file)

    entry = feedback_logger.log_feedback("Try this starter", "like")
    feedback = feedback_logger.get_feedback()

    assert entry["feedback"] == "like"
    assert feedback[0]["suggestion"] == "Try this starter"


def test_system_logger_round_trip(tmp_path, monkeypatch):
    log_file = tmp_path / "logs.json"
    monkeypatch.setattr(system_logger, "LOG_FILE", log_file)

    entry = system_logger.log_entry("test_action", {"ok": True}, session_id="session-1")
    logs = system_logger.load_logs()

    assert entry["ActionType"] == "test_action"
    assert logs[0]["SessionID"] == "session-1"

