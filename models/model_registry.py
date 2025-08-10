# models/model_registry.py
import os
from typing import Optional
from models.baseline_xgb import BaselineXGB, MODEL_NAME as BASE_NAME
from common.config import config

REGISTRY = {
    BASE_NAME: BaselineXGB,
}

DEFAULT_MODEL = BASE_NAME

def load_model(name: Optional[str] = None):
    name = name or DEFAULT_MODEL
    cls = REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Unknown model: {name}")
    # attempt to load saved weights if present
    path = os.path.join(config.MODEL_STORAGE_PATH, f"{name}.joblib")
    if os.path.exists(path):
        return cls.load(path)
    return cls()
