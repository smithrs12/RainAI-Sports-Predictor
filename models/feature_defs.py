# models/feature_defs.py
from dataclasses import dataclass
from typing import List

@dataclass
class FeatureSet:
    features: List[str]

# Example baseline features — replace with your engineered signals
BASELINE_FEATURES = FeatureSet(features=[
    "home_win_pct_10",
    "away_win_pct_10",
    "elo_diff",
    "rest_days_home",
    "rest_days_away",
    "injury_starters_diff",
    "odds_implied_edge",
])
