import os, requests, streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

st.set_page_config(page_title="Sports AI", layout="centered")

st.title("🏈 Sports Betting AI — Demo")

with st.expander("1) Login (demo)"):
    email = st.text_input("Email", value="demo@example.com")
    if st.button("Get Token"):
        r = requests.post(f"{API_BASE}/login", json={"email": email})
        if r.ok:
            st.session_state["token"] = r.json()["token"]
            st.success("Token acquired")
        else:
            st.error(r.text)

auth = st.session_state.get("token")

st.markdown("---")
st.subheader("2) Make a Prediction")

cols = st.columns(2)
with cols[0]:
    home_win_pct_10 = st.number_input("home_win_pct_10", 0.0, 1.0, 0.55)
    away_win_pct_10 = st.number_input("away_win_pct_10", 0.0, 1.0, 0.45)
    elo_diff = st.number_input("elo_diff", -500.0, 500.0, 25.0)
with cols[1]:
    rest_days_home = st.number_input("rest_days_home", 0.0, 10.0, 2.0)
    rest_days_away = st.number_input("rest_days_away", 0.0, 10.0, 2.0)
    injury_starters_diff = st.number_input("injury_starters_diff", -5.0, 5.0, 0.0)

odds_implied_edge = st.number_input("odds_implied_edge", -0.5, 0.5, 0.02, step=0.01)

if st.button("Predict"):
    if not auth:
        st.error("Login first to get a token")
    else:
        headers = {"Authorization": f"Bearer {auth}"}
        payload = {
            "home_win_pct_10": home_win_pct_10,
            "away_win_pct_10": away_win_pct_10,
            "elo_diff": elo_diff,
            "rest_days_home": rest_days_home,
            "rest_days_away": rest_days_away,
            "injury_starters_diff": injury_starters_diff,
            "odds_implied_edge": odds_implied_edge,
        }
        r = requests.post(f"{API_BASE}/predict", json=payload, headers=headers)
        if r.ok:
            out = r.json()
            st.json(out)
        else:
            st.error(r.text)

st.markdown("---")
st.subheader("3) (Optional) Train Model")
if st.button("Start Training"):
    if not auth:
        st.error("Login first to get a token")
    else:
        headers = {"Authorization": f"Bearer {auth}"}
        r = requests.post(f"{API_BASE}/train", headers=headers)
        if r.ok:
            st.success("Training kicked off (check API logs)")
        else:
            st.error(r.text)

st.markdown("---")
st.caption("This demo is for educational purposes. No guarantees of performance. Gamble responsibly.")
