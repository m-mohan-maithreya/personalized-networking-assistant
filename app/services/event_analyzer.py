import logging
from typing import List

logger = logging.getLogger(__name__)

# Try to initialize the zero-shot classifier, fallback to heuristic keyword analysis on failure
CLASSIFIER = None
DEFAULT_CANDIDATE_LABELS = [
    "AI", "blockchain", "healthcare", "sustainability", 
    "education", "business", "climate change", "urban planning",
    "technology", "finance", "networking"
]

try:
    from transformers import pipeline
    # Loading typeform/distilbert-base-uncased-mnli for zero-shot classification
    logger.info("Initializing DistilBERT zero-shot classifier...")
    CLASSIFIER = pipeline(
        "zero-shot-classification", 
        model="typeform/distilbert-base-uncased-mnli",
        device=-1 # Deploy to CPU by default
    )
    logger.info("DistilBERT zero-shot classifier loaded successfully.")
except Exception as e:
    logger.warning(
        f"Failed to load transformers pipeline: {e}. "
        "Falling back to rule-based keyword theme extraction."
    )
    CLASSIFIER = None


def extract_event_themes(event_description: str, candidate_labels: List[str] = None) -> List[str]:
    """
    Extracts the top 3 themes from an event description.
    Uses DistilBERT zero-shot classification if available, otherwise runs a heuristic fallback.
    """
    if not candidate_labels:
        candidate_labels = DEFAULT_CANDIDATE_LABELS

    # Guard mapping: clean inputs
    desc_clean = event_description.strip()
    if not desc_clean:
        return []

    # 1. Pipeline path
    if CLASSIFIER is not None:
        try:
            result = CLASSIFIER(desc_clean, candidate_labels, multi_label=False)
            # Scores are in descending order, extract top 3 labels
            labels = result.get("labels", [])
            return labels[:3]
        except Exception as e:
            logger.error(f"Error during transformer inference: {e}. Falling back to keywords...")
            # Proceed to fallback below

    # 2. Rule-based Fallback path
    scores = {}
    desc_lower = desc_clean.lower()
    for label in candidate_labels:
        # Check frequency of occurrences of the label in the text
        count = desc_lower.count(label.lower())
        if count > 0:
            scores[label] = count
        else:
            # Check partial match for multi-word labels like "climate change" or "urban planning"
            parts = label.lower().split()
            part_matches = sum(1 for part in parts if part in desc_lower)
            if len(parts) > 1 and part_matches > 0:
                scores[label] = part_matches / len(parts)

    sorted_labels = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    results = [label for label, score in sorted_labels]
    
    # If no labels found via keyword matching, return default labels
    if not results:
        # Return first 3 candidate labels as default
        return candidate_labels[:3]
        
    return results[:3]
