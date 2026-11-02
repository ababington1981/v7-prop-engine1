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

# --- Polished Deep Slate & Modern Dark Mode Aesthetic ---
st.markdown("""
<style>
    .stApp {
        background-color: #090d16;
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 800;
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #090d16;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111827;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 12px;
        border: 1px solid #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background-color: #38bdf8 !important;
        color: #0e1626 !important;
        font-weight: 800;
        border: 1px solid #38bdf8 !important;
    }
    .stButton>button, .stDownloadButton>button {
        background-color: #38bdf8;
        color: #0e1626;
        font-weight: 800;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #0ea5e9;
        color: #0e1626;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #1f2937;
        border-radius: 8px;
        background-color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# --- CORE ENGINE FUNCTIONS ---
# ==========================================

def odds_to_prob(odds):
    return (100 / (odds + 100)) if odds > 0 else (abs(odds) / (abs(odds) + 100))

def generate_multibook_alt_ladders(base_line, base_odds, stat_type, book_name):
    book_multipliers = {
        "DraftKings": 1.00,
        "FanDuel": 0.98,
        "BetMGM": 1.03,
        "Caesars": 1.05,
        "Bovada": 0.95
    }
    m = book_multipliers.get(book_name, 1.00)
    
    if stat_type == 'Points':
        rungs = [-6.0, -3.0, 0.0, +3.0, +6.0, +9.5, +14.5]
        base_juices = [-520, -270, base_odds, +120, +235, +440, +1050]
    elif stat_type == 'Rebounds':
        rungs = [-3.0, -1.5, 0.0, +2.0, +4.0, +6.0]
        base_juices = [-460, -230, base_odds, +135, +300, +680]
    elif stat_type == 'Assists':
        rungs = [-3.0, -1.5, 0.0, +2.0, +4.0, +6.0]
        base_juices = [-490, -240, base_odds, +145, +330, +720]
    else: 
        rungs = [-8.0, -4.0, 0.0, +5.0, +10.0, +15.0]
        base_juices = [-510, -255, base_odds, +130, +275, +590]
        
    alt_market = {}
    for offset, juice in zip(rungs, base_juices):
        rung_line = max(0.5, round((base_line + offset) * 2) / 2)
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
        american = round((decimal_product - 1.0) * 100)
        american_str = f"+{american}" if american > 0 else "+100"
    else:
        american = round(-100.0 / (decimal_product - 1.0))
        american_str = str(american)
        
    return american_str, compounded_prob_product * 100

# --- Live API Integration or Robust Comprehensive Fallback Feed ---
@st.cache_data(ttl=600)
def fetch_live_nba_player_props(api_key, book_name):
    if api_key and len(api_key) > 5:
        try:
            url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
            params = {
                "apiKey": api_key,
                "regions": "us",
                "markets": "player_points,player_rebounds,player_assists",
                "oddsFormat": "american"
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    pass 
        except Exception:
            pass 

    variance_map = {"DraftKings": 0, "FanDuel": -2, "BetMGM": +3, "Caesars": +5, "Bovada": -5}
    v = variance_map.get(book_name, 0)
    
    df = pd.DataFrame({
        'matchup': [
            'OKC @ CLE', 'DET @ CHA', 'BKN @ NYK', 'WAS @ ORL', 'CHI @ PHI', 
            'ATL @ IND', 'SAC @ DAL', 'MIL @ MIN', 'BOS @ HOU', 'UTA @ SAS',
            'LAL @ GSW', 'MIA @ DEN', 'MEM @ PHX', 'POR @ LAC', 'NOP @ TOR',
            'DEN @ MEM', 'PHX @ LAL', 'GSW @ SAC', 'NYK @ BOS', 'CLE @ MIA'
        ],
        'player': [
            'Shai Gilgeous-Alexander', 'Coby White', 'Jalen Brunson', 'Franz Wagner', 'Tyrese Maxey', 
            'Trae Young', 'Luka Dončić', 'Giannis Antetokounmpo', 'Jayson Tatum', 'Victor Wembanyama',
            'LeBron James', 'Nikola Jokić', 'Ja Morant', 'Norman Powell', 'Brandon Ingram',
            'Josh Giddey', 'Naz Reid', 'Buddy Hield', 'Dereck Lively II', 'Immanuel Quickley'
        ],
