from typing import Dict, Any

# Claude extractor integration stub
# TODO: replace with real Claude/Sonnet client and secure credentials

SYSTEM_PROMPT = "You are an extractor that reads conversational text and returns structured state updates in JSON. Only return JSON object with fields: state_updates (dict), completion_map (dict), confidence_map (dict)."

CONFIDENCE_THRESHOLDS = {
    'auto': 0.85,
    'review': 0.65,
}


def extract_from_text(text: str) -> Dict[str, Any]:
    """Stub extractor: analyzes text and returns dummy structured extraction.
    Replace this with actual Claude/Sonnet call.
    """
    # Very naive placeholder: treat sentences as keys
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    state_updates = {f"s{i}": sentences[i] for i in range(len(sentences))}
    completion_map = {k: 0.0 for k in state_updates.keys()}
    confidence_map = {k: 0.7 for k in state_updates.keys()}
    overall_confidence = 0.7
    return {
        "state_updates": state_updates,
        "completion_map": completion_map,
        "confidence_map": confidence_map,
        "overall_confidence": overall_confidence,
    }
