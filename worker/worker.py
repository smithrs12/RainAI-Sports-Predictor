import os, time, signal, json, hashlib
from datetime import datetime, timezone
from common.logger import logger
from common.config import config
from common.redis_cache import get_redis
from services.training import train_and_save
from services.prediction import predict
from services.data_provider import DataProvider

STOP = False

def _handle_signal(sig, frame):
    global STOP
    logger.info(f"🛑 Received {sig}. Graceful shutdown after current cycle...")
    STOP = True

# Graceful shutdown
signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

# === Config ===
INTERVAL = int(os.getenv("WORKER_INTERVAL_SECONDS", "900"))  # seconds between cycles (default 15m)
MODEL_NAME = os.getenv("MODEL_NAME", "baseline_xgb_v1")
RETRAIN_HOUR_UTC = int(os.getenv("RETRAIN_HOUR_UTC", "6"))  # default 06:00 UTC daily

# === Globals ===
redis = get_redis()
provider = DataProvider()


def heartbeat():
    if redis:
        redis.set("worker:heartbeat", datetime.now(timezone.utc).isoformat(), ex=3600)


def maybe_retrain() -> bool:
    """Retrain once per UTC day after RETRAIN_HOUR_UTC; bump model version in Redis."""
    if not redis:
        return False
    key_last = f"model:{MODEL_NAME}:last_retrain_date"
    today = datetime.now(timezone.utc).date().isoformat()
    last = redis.get(key_last)
    if last == today:
        return False
    if datetime.now(timezone.utc).hour < RETRAIN_HOUR_UTC:
        return False

    logger.info("🧠 Starting model retraining ...")
    train_and_save()
    redis.set(key_last, today)
    # Signal API/web that a new model is available (API can watch this key to hot-reload)
    redis.set(f"model:{MODEL_NAME}:version", str(datetime.now(timezone.utc).timestamp()))
    logger.info("🎉 Retraining complete; model version bumped.")
    return True


def precompute_predictions() -> int:
    """Fetch upcoming games from DataProvider and cache predictions in Redis for fast UI loading."""
    upcoming = []
    if hasattr(provider, "get_upcoming_payloads"):
        try:
            upcoming = provider.get_upcoming_payloads()
        except Exception as e:
            logger.exception(f"Failed to fetch upcoming payloads: {e}")
            return 0
    else:
        logger.warning("DataProvider.get_upcoming_payloads() not implemented; skipping precompute.")
        return 0

    if not upcoming:
        logger.info("No upcoming payloads available to precompute.")
        return 0

    cached = 0
    for payload in upcoming:
        try:
            out = predict(payload)
            game_id = payload.get("game_id") or hashlib.md5(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()
            key = f"pred:{MODEL_NAME}:{game_id}"
            if redis:
                redis.set(
                    key,
                    json.dumps({
                        "payload": payload,
                        "prediction": out,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }),
                    ex=60 * 60 * 24,  # 24h
                )
            cached += 1
        except Exception as e:
            logger.exception(f"Precompute failed for payload={payload}: {e}")

    logger.info(f"✅ Precomputed {cached} predictions.")
    return cached


def main():
    logger.info("🚀 Worker started. Interval=%ss, RetrainHourUTC=%s", INTERVAL, RETRAIN_HOUR_UTC)
    while not STOP:
        try:
            heartbeat()
            maybe_retrain()
            precompute_predictions()
        except Exception as e:
            logger.exception(f"Worker cycle error: {e}")
        time.sleep(INTERVAL)
    logger.info("👋 Worker exiting.")


if __name__ == "__main__":
    main()
