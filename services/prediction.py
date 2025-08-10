# services/prediction.py
from typing import Dict
import os
from models.model_registry import load_model, DEFAULT_MODEL
from services.data_provider import DataProvider
from common.config import config
from common.redis_cache import get_redis
from common.logger import logger

provider = DataProvider()

# Allow overriding via environment so API & Worker stay in sync
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)

# Caches
_model_cache = None
_model_version_cache = None
_redis = get_redis()


def _load_fresh_model():
    global _model_cache
    logger.info(f"🔁 Loading model '{MODEL_NAME}' from storage path {config.MODEL_STORAGE_PATH}")
    _model_cache = load_model(MODEL_NAME)
    return _model_cache


def _get_model():
    """Return cached model, but hot‑reload if Redis version changed."""
    global _model_cache, _model_version_cache

    # First boot
    if _model_cache is None:
        _load_fresh_model()
        if _redis:
            _model_version_cache = _redis.get(f"model:{MODEL_NAME}:version") or "boot"
        return _model_cache

    # Hot‑reload if a new version is announced
    if _redis:
        current_ver = _redis.get(f"model:{MODEL_NAME}:version")
        if current_ver and current_ver != _model_version_cache:
            logger.info(
                f"⚡ Detected new model version for {MODEL_NAME}: {current_ver} (was {_model_version_cache}). Reloading..."
            )
            _load_fresh_model()
            _model_version_cache = current_ver

    return _model_cache


def predict(payload: Dict):
    model = _get_model()
    X = provider.build_feature_row(payload)
    proba = model.predict_proba(X)[0]
    # Assume proba[1] = probability of home team win
    home_win_prob = float(proba[1])
    away_win_prob = float(proba[0])
    pick = "HOME" if home_win_prob >= away_win_prob else "AWAY"
    confidence = max(home_win_prob, away_win_prob)
    return {
        "pick": pick,
        "confidence": confidence,
        "proba": {"home": home_win_prob, "away": away_win_prob},
        "threshold_pass": confidence >= config.MIN_CONFIDENCE,
    }
