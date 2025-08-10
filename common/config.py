import os

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "")
    JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
    MODEL_STORAGE_PATH = os.getenv("MODEL_STORAGE_PATH", "/opt/models")

    # Prediction thresholds (baseline defaults — tune these)
    MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", 0.55))

config = Config()
