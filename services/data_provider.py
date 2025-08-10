# services/data_provider.py
"""Stub interface — replace with your real data source.
Provide train & inference frames with required feature columns.
"""
from typing import Tuple, Dict
import numpy as np

REQUIRED_FEATURES = [
    "home_win_pct_10",
    "away_win_pct_10",
    "elo_diff",
    "rest_days_home",
    "rest_days_away",
    "injury_starters_diff",
    "odds_implied_edge",
]

class DataProvider:
    def get_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        # TODO: Replace with your dataset fetch/ETL
        # Synthetic placeholder: binary target with 1,000 rows
        rng = np.random.default_rng(42)
        X = rng.normal(size=(1000, len(REQUIRED_FEATURES)))
        y = (rng.random(1000) > 0.5).astype(int)
        return X, y

    def build_feature_row(self, payload: Dict) -> np.ndarray:
        # Map incoming payload to feature vector (in correct order)
        return np.array([[payload.get(k, 0.0) for k in REQUIRED_FEATURES]], dtype=float)

# Add to DataProvider class
    def get_upcoming_payloads(self):
        """Return a list of payload dicts (one per upcoming game) with required features.
        Include an optional unique `game_id` for caching. Replace with your real feed.
        """
        # DEMO: two synthetic games
        return [
            {
                "game_id": "DEMO-001",
                "home_win_pct_10": 0.62,
                "away_win_pct_10": 0.41,
                "elo_diff": 35,
                "rest_days_home": 2,
                "rest_days_away": 1,
                "injury_starters_diff": 0,
                "odds_implied_edge": 0.03,
            },
            {
                "game_id": "DEMO-002",
                "home_win_pct_10": 0.48,
                "away_win_pct_10": 0.55,
                "elo_diff": -18,
                "rest_days_home": 1,
                "rest_days_away": 3,
                "injury_starters_diff": -1,
                "odds_implied_edge": -0.01,
            },
        ]
