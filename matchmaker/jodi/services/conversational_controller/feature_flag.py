import hashlib
from .config import settings

def in_rollout(user_id: str) -> bool:
    """Deterministically decide whether a user is in the feature rollout based on FEATURE_ROLLOUT_PCT"""
    pct = settings.FEATURE_ROLLOUT_PCT
    if pct <= 0:
        return False
    if pct >= 100:
        return True
    h = hashlib.sha256(user_id.encode()).hexdigest()
    val = int(h[:8], 16) % 100
    return val < pct
