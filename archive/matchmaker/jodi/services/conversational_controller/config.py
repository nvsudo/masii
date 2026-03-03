from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/jodi")
    FEATURE_ROLLOUT_PCT: int = int(os.getenv("FEATURE_ROLLOUT_PCT", "0"))

settings = Settings()

# Confidence thresholds
AUTO_CONFIDENCE = 0.85
REVIEW_CONFIDENCE = 0.65
