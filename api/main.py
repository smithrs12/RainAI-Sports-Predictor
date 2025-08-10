# api/main.py
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict
import stripe
from common.config import config
from common.redis_cache import get_redis
from common.auth import create_jwt, verify_jwt
from services.prediction import predict
from services.training import train_and_save
from api.stripe_handlers import router as stripe_router

stripe.api_key = None  # set only in stripe_handlers for security

app = FastAPI(title="Sports AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str

class PredictRequest(BaseModel):
    home_win_pct_10: float = 0
    away_win_pct_10: float = 0
    elo_diff: float = 0
    rest_days_home: float = 0
    rest_days_away: float = 0
    injury_starters_diff: float = 0
    odds_implied_edge: float = 0

class PredictResponse(BaseModel):
    pick: str
    confidence: float
    proba: Dict[str, float]
    threshold_pass: bool


def require_auth(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split()[1]
    try:
        return verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid/expired token")

@app.get("/health")
def health():
    r = get_redis()
    ok = False
    try:
        if r: r.ping(); ok = True
    except Exception:
        ok = False
    return {"status": "ok", "redis": ok}

@app.post("/login")
def login(req: LoginRequest):
    # In production, verify email ownership and subscription (DB/Stripe)
    token = create_jwt({"sub": req.email})
    return {"token": token}

@app.post("/predict", response_model=PredictResponse)
def predict_route(req: PredictRequest, user=Depends(require_auth)):
    return predict(req.model_dump())

@app.post("/train")
def train_route(user=Depends(require_auth)):
    train_and_save()
    return {"status": "training_started"}

# Stripe webhooks & helper routes
app.include_router(stripe_router)
