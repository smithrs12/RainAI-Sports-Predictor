# models/baseline_xgb.py
import os, joblib
import numpy as np
from xgboost import XGBClassifier
from models.feature_defs import BASELINE_FEATURES
from common.config import config
from common.logger import logger

MODEL_NAME = "baseline_xgb_v1"

class BaselineXGB:
    def __init__(self):
        self.model = XGBClassifier(
            n_estimators=400,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            learning_rate=0.05,
            eval_metric="logloss",
            tree_method="hist",
        )
        self.features = BASELINE_FEATURES.features

    def train(self, X: np.ndarray, y: np.ndarray):
        logger.info(f"Training {MODEL_NAME} on shape={X.shape}")
        self.model.fit(X, y)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def save(self, path: str = None):
        path = path or os.path.join(config.MODEL_STORAGE_PATH, f"{MODEL_NAME}.joblib")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "features": self.features,
        }, path)
        logger.info(f"💾 Saved model to {path}")

    @staticmethod
    def load(path: str = None):
        path = path or os.path.join(config.MODEL_STORAGE_PATH, f"{MODEL_NAME}.joblib")
        data = joblib.load(path)
        obj = BaselineXGB()
        obj.model = data["model"]
        obj.features = data["features"]
        return obj
