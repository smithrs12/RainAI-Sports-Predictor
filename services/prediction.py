# services/prediction.py
from typing import Dict
from models.model_registry import load_model, DEFAULT_MODEL
from services.data_provider import DataProvider
from common.config import config

provider = DataProvider()
_model_cache = None

def _get_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = load_model(DEFAULT_MODEL)
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
