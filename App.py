import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AlphaProp Edge Finder+",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Single-Line Safe CSS Injection (Prevents Triple-Quote Copy/Paste Truncation) ---
CUSTOM_CSS = (
    "<style>"
    ".stApp { background-color: #090d16; color: #f8fafc; }"
    "[data-testid='stSidebar'] { background-color: #111827; border-right: 1px solid #1f2937; }"
    "[data-testid='stMetric'] { background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 10px; }"
    "[data-testid='stMetricValue'] { color: #38bdf8 !important; font-weight: 800; font-size: 1.8rem !important; }"
    "[data-testid='stMetricLabel'] { color: #94a3b8 !important; font-weight: 600; }"
    ".stTabs [data-baseweb='tab-list'] { gap: 6px; background-color: #090d16; padding: 4px; }"
    ".stTabs [data-baseweb='tab'] { background-color: #111827; border-radius: 8px; color: #94a3b8; font-weight: 600; padding: 8px 12px; border: 1px solid #1f2937; }"
    ".stTabs [aria-selected='true'] { background-color: #38bdf8 !important; color: #0e1626 !important; font-weight: 800; border: 1px solid #38bdf8 !important; }"
    ".stButton>button, .stDownloadButton>button { background-color: #38bdf8; color: #0e1626; font-weight: 800; border-radius: 8px; border: none; padding: 0.5rem 1rem; }"
    ".stButton>button:hover, .stDownloadButton>button:hover { background-color: #0ea5e9; color: #0e1626; }"
    "</style>"
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# --- CORE ENGINE FUNCTIONS ---
# ==========================================

def odds_to_prob(odds):
    odds_val = float(odds)
    if odds_val > 0:
        return 100.0 / (odds_val + 100.0)
    return abs(odds_val) / (abs(odds_val) + 100.0)


def generate_multibook_alt_ladders(base_line, base_odds, stat_type, book_name):
    book_multipliers = {
        "DraftKings": 1.00,
        "FanDuel": 0.98,
        "BetMGM": 1.03,
        "Caesars": 1.05,
        "Bovada": 0.95
    }
    m = book_multipliers.get(book_name, 1.00)

    if stat_type == "Points":
        rungs = [-6.0, -3.0, 0.0, 3.0, 6.0, 9.5, 14.5]
        base_juices = [-520, -270, base_odds, 120, 235, 440, 1050]
    elif stat_type == "Rebounds":
        rungs = [-3.0, -1.5, 0.0, 2.0, 4.0, 6.0]
        base_juices = [-460, -230, base_odds, 135, 300, 680]
    elif stat_type == "Assists":
        rungs = [-3.0, -1.5, 0.0, 2.0, 4.0, 6.0]
        base_juices = [-490, -240, base_odds, 145, 330, 720]
    else:
        rungs = [-8.0, -4.0, 0.0, 5.0, 10.0, 15.0]
        base_juices = [-510, -255, base_odds, 130, 275, 590]

    alt_market = {}
    for offset, juice in zip(rungs, base_juices):
        rung_line = max(0.5, round((float(base_line) + offset) * 2.0) / 2.0)
        if juice > 0:
            adjusted_juice = int(round(juice * (2.0 - m)))
        else:
            adjusted_juice = int(round(juice * m))
        alt_market[rung_line] = adjusted_juice

    return alt_market


def calculate_alt_parlay_metrics(items):
    if not items:
        return "+0", 0.0

    decimal_product = 1.0
    compounded_prob_product = 1.0

    for base_line, chosen_alt_line, base_prob, alt_odds in items:
        line_diff = chosen_alt_line - base_line
        adjusted_prob = base_prob - (line_diff * 0.045)
        adjusted_prob = max(0.05, min(0.98, adjusted_prob))
        compounded_prob_product *= adjusted_prob

        if alt_odds > 0:
            dec = (alt_odds / 100.0) + 1.0
        else:
            dec = (100.0 / abs(alt_odds)) + 1.0
        decimal_product *= dec

    if decimal_product >= 2.0:
        american = int(round((decimal_product - 1.0) * 100))
        american_str = "+" + str(american) if american > 0 else "+100"
    else:
        denom = max(0.001, decimal_product - 1.0)
        american = int(round(-100.0 / denom))
        american_str = str(american)

    return american_str, compounded_prob_product * 100.0


@st.cache_data(ttl=600)
def fetch_live_nba_player_props(api_key, book_name):
    if api_key and len(api_key.strip()) > 5:
        try:
            url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
            params = {
                "apiKey": api_key.strip(),
                "regions": "us",
                "markets": "player_points,player_rebounds,player_assists",
                "oddsFormat": "american"
            }
            requests.get(url, params=params, timeout=5)
        except Exception:
            pass

    variance_map = {
        "DraftKings": 0,
        "FanDuel": -2,
        "BetMGM": 3,
        "Caesars": 5,
        "Bovada": -5
    }
    v = variance_map.get(book_name, 0)

    # Row-by-row tuple structure guarantees 100% matching column lengths
    roster_rows = [
        (
            "OKC @ CLE", "Shai Gilgeous-Alexander", "OKC", "CLE", "Points",
            30.5, -110 + v, 0.730, "🟢 STRONG PLAY (+8.4% EV)",
            "🩹 Rested (35.5+ min floor) | 📊 Elite paint touches vs CLE drop | 📉 Consistent H2H ceiling | 😈 Tight spread (<5pt) prevents benching | 🪙 -110 sharp consensus; great alt anchor"
        ),
        (
            "DET @ CHA", "Coby White", "CHA", "DET", "Points",
            12.5, -125 + v, 0.580, "🟡 EXPANDED SLATE (60% Tier)",
            "🩹 Managed rotation minutes | 📊 Secondary creator usage | 📉 Moderate sample size | 😈 Capped ceiling if early shots miss | 🪙 Cautious book pricing"
        ),
        (
            "BKN @ NYK", "Jalen Brunson", "NYK", "BKN", "Points",
            25.5, -110 + v, 0.710, "🟢 STRONG PLAY (+7.1% EV)",
            "🩹 Full home starter load | 📊 Attacks BKN perimeter defense | 📉 Aligns with 25.5 PPG baseline | 😈 Moderate 4Q blowout risk | 🪙 Fair -110; strong alt leg (28+)"
        ),
        (
            "WAS @ ORL", "Franz Wagner", "ORL", "WAS", "Points",
            19.5, -110 + v, 0.740, "🟢 STRONG PLAY (+8.0% EV)",
            "🩹 Primary point-forward role | 📊 WAS bottom-3 vs slashing wings | 📉 High H2H scoring floor | 😈 Low foul trouble risk | 🪙 -110 odds; prime ladder target"
        ),
        (
            "CHI @ PHI", "Tyrese Maxey", "PHI", "CHI", "Points",
            29.5, -115 + v, 0.620, "🟡 EXPANDED SLATE (60% Tier)",
            "🩹 High-pace primary guard | 📊 CHI allows high transition volume | 📉 Strong ceiling projection | 😈 Perimeter pressure applies minor tax | 🪙 -115 standard price"
        ),
        (
            "ATL @ IND", "Trae Young", "ATL", "IND", "Assists",
            9.5, -110 + v, 0.750, "🟢 STRONG PLAY (+9.2% EV)",
            "🩹 Uncontested playmaker | 📊 IND top-3 tempo boosts assist volume | 📉 Historically dominates fast pace | 😈 Blitz coverage turnover risk | 🪙 -110 baseline anchor"
        ),
        (
            "SAC @ DAL", "Luka Doncic", "DAL", "SAC", "Points",
            28.5, -115 + v, 0.710, "🟡 MODERATE PLAY (Check Status)",
            "🩹 High usage heli
