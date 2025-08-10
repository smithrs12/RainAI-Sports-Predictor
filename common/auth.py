# common/auth.py
import time, hmac, hashlib, base64, json
from typing import Dict
from common.config import config

HEADER = {"alg": "HS256", "typ": "JWT"}

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def create_jwt(payload: Dict, exp_seconds: int = 86400) -> str:
    body = payload.copy()
    body["exp"] = int(time.time()) + exp_seconds
    header_b64 = _b64url(json.dumps(HEADER).encode())
    payload_b64 = _b64url(json.dumps(body).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    sig = hmac.new(config.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url(sig)}"

def verify_jwt(token: str) -> Dict:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(config.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
        if _b64url(expected_sig) != sig_b64:
            raise ValueError("Invalid signature")
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "=="))
        if payload.get("exp", 0) < int(time.time()):
            raise ValueError("Token expired")
        return payload
    except Exception as e:
        raise ValueError("Invalid token") from e
