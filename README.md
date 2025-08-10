# Sports Betting AI SaaS — Starter

## 1) Clone & Configure
- Copy `.env.example` to `.env` locally (or create Render env vars)
- Create two Render services from this repo:
  - **sports-ai-api** (rootDir: `api`)
  - **sports-ai-web** (rootDir: `web`)
- Add env vars:
  - Shared: `REDIS_URL`, `JWT_SECRET`
  - Web: `STRIPE_PUBLISHABLE_KEY`, `API_BASE_URL`
  - API: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `MODEL_STORAGE_PATH`

## 2) First Deploy
- Deploy **API** first; note its public URL (e.g., `https://sports-ai-api.onrender.com`)
- Set that as `API_BASE_URL` on the **Web** service and redeploy

## 3) Test Locally (optional)
```bash
# API
cd api && pip install -r requirements.txt && uvicorn api.main:app --reload
# Web
cd web && pip install -r requirements.txt && streamlit run web/app.py
