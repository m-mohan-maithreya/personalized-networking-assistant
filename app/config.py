"""Application configuration."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MODEL_NAMES = {
    "event_analysis": "facebook/bart-large-mnli",
    "text_generator": "gpt2",
}

FACT_CHECK_API = "https://en.wikipedia.org/api/rest_v1/page/summary"
HISTORY_FILE = DATA_DIR / "history.json"
FEEDBACK_FILE = DATA_DIR / "feedback.json"
LOG_FILE = DATA_DIR / "logs.json"

DEFAULT_CANDIDATE_LABELS = [
    "AI",
    "healthcare",
    "blockchain",
    "education",
    "sustainability",
    "climate change",
    "urban planning",
    "finance",
    "technology",
    "leadership",
]

