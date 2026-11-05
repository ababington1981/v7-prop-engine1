import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, date

# --- Page Configuration ---
st.set_page_config(
    page_title="AlphaProp Edge Finder+",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Polished Deep Slate & Modern Dark Mode Aesthetic ---
st.markdown(
    """
    <style>
        .stApp { background-color: #090d16; color: #f8fafc; }
        [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
        [data-testid="stMetric"] { background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 10px; }
        [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 800; font-size: 1.8rem !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: #090d16; padding: 4px; }
        .stTabs [data-baseweb="tab"] { background-color: #111827; border-radius: 8px; color: #94a3b8; font-weight: 600; padding: 8px 12px; border: 1px solid #1f2937; }
        .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: #0e1626 !important; font-weight: 800; border: 1px solid #38bdf8 !important; }
        .stButton>button { background-color: #38bdf8; color: #0e1626; font-weight: 800; border-radius: 8px; border: none; padding: 0.5rem 1rem; }
        [data-testid="stDataFrame"] { border: 1px solid #1f2937; border-radius: 8px; background-color: #111827; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# --- DEFAULT TEAM EPM JSON CONFIGURATION ---
# ==========================================
DEFAULT_TEAM_EPM_JSON = {
    "metadata": {
        "season": "2025-26",
        "last_updated": "2026-11-04",
        "description": "Team-level EPM ratings, offensive/defensive multipliers, and rolling location-based Net Rating splits."
    },
    "teams": {
        "OKC": {"team_name": "Oklahoma City Thunder", "off_epm": 6.8, "def_epm": -4.3, "net_epm": 11.1, "home_net_l10": 11.5, "road_net_l10": 9.8},
        "SAS": {"team_name": "San Antonio Spurs", "off_epm": 5.2, "def_epm": -3.1, "net_epm": 8.3, "home_net_l10": 9.2, "road_net_l10": 7.1},
        "DET": {"team_name": "Detroit Pistons", "off_epm": 4.5, "def_epm": -3.7, "net_epm": 8.2, "home_net_l10": 8.9, "road_net_l10": 7.4},
        "BOS": {"team_name": "Boston Celtics", "off_epm": 5.9, "def_epm": -2.2, "net_epm": 8.1, "home_net_l10": 9.4, "road_net_l10": 6.8},
        "NYK": {"team_name": "New York Knicks", "off_epm": 4.1, "def_epm": -2.4, "net_epm": 6.5, "home_net_l10": 7.2, "road_net_l10": 5.8},
        "HOU": {"team_name": "Houston Rockets", "off_epm": 3.2, "def_epm": -2.2, "net_epm": 5.4, "home_net_l10": 6.1, "road_net_l10": 4.7},
        "DEN": {"team_name": "Denver Nuggets", "off_epm": 7.1, "def_epm": -1.9, "net_epm": 5.2, "home_net_l10": 7.8, "road_net_l10": 3.2},
        "CHA": {"team_name": "Charlotte Hornets", "off_epm": 3.8, "def_epm": 1.2, "net_epm": 5.0, "home_net_l10": 5.5, "road_net_l10": 4.2},
        "CLE": {"team_name": "Cleveland Cavaliers", "off_epm": 3.5, "def_epm": 0.6, "net_epm": 4.1, "home_net_l10": 4.8, "road_net_l10": 3.4},
        "MIN": {"team_name": "Minnesota Timberwolves", "off_epm": 1.9, "def_epm": -1.4, "net_epm": 3.3, "home_net_l10": 4.1, "road_net_l10": 2.5},
        "TOR": {"team_name": "Toronto Raptors", "off_epm": 1.2, "def_epm": -1.7, "net_epm": 2.9, "home_net_l10": 3.5, "road_net_l10": 2.1},
        "ATL": {"team_name": "Atlanta Hawks", "off_epm": 2.5, "def_epm": -0.1, "net_epm": 2.4, "home_net_l10": 3.0, "road_net_l10": 1.8},
        "MIA": {"team_name": "Miami Heat", "off_epm": 2.1, "def_epm": -0.1, "net_epm": 2.2, "home_net_l10": 2.8, "road_net_l10": 1.6},
        "LAL": {"team_name": "Los Angeles Lakers", "off_epm": 3.1, "def_epm": -1.3, "net_epm": 1.8, "home_net_l10": 2.4, "road_net_l10": 1.2},
        "ORL": {"team_name": "Orlando Magic", "off_epm": -0.4, "def_epm": -1.0, "net_epm": 0.6, "home_net_l10": 1.2, "road_net_l10": 0.1},
        "PHI": {"team_name": "Philadelphia 76ers", "off_epm": -0.2, "def_epm": 0.0, "net_epm": -0.2, "home_net_l10": 0.5, "road_net_l10": -0.9},
        "CHI": {"team_name": "Chicago Bulls", "off_epm": -2.1, "def_epm": 3.0, "net_epm": -5.1, "home_net_l10": -4.2, "road_net_l10": -6.0},
        "WAS": {"team_name": "Washington Wizards", "off_epm": -3.5, "def_epm": 8.3, "net_epm": -11.8, "home_net_l10": -10.5, "road_net_l10": -13.1},
        "GSW": {"team_name": "Golden State Warriors", "off_epm": 4.2, "def_epm": -1.8, "net_epm": 6.0, "home_net_l10": 6.8, "road_net_l10": 5.2},
        "PHX": {"team_name": "Phoenix Suns", "off_epm": 4.8, "def_epm": -0.5, "net_epm": 4.3, "home_net_l10": 5.1, "road_net_l10": 3.9},
        "IND": {"team_name": "Indiana Pacers", "off_epm": 5.0, "def_epm": -0.8, "net_epm": 4.2, "home_net_l10": 5.8, "road_net_l10": 3.5},
        "MEM": {"team_name": "Memphis Grizzlies", "off_epm": 3.6, "def_epm": -2.0, "net_epm": 5.6, "home_net_l10": 6.2, "road_net_l10": 4.5},
        "NOP": {"team_name": "New Orleans Pelicans", "off_epm": 2.2, "def_epm": -0.4, "net_epm": 1.8, "home_net_l10": 2.5, "road_net_l10": 1.1},
        "POR": {"team_name": "Portland Trail Blazers", "off_epm": -1.5, "def_epm": 2.1, "net_epm": -3.6, "home_net_l10": -2.8, "road_net_l10": -4.5},
        "SAC": {"team_name": "Sacramento Kings", "off_epm": 3.4, "def_epm": 0.2, "net_epm": 3.2, "home_net_l10": 4.0, "road_net_l10": 2.4},
        "UTA": {"team_name": "Utah Jazz", "off_epm": -1.8, "def_epm": 3.5, "net_epm": -5.3, "home_net_l10": -4.1, "road_net_l10": -6.8},
        "BRK": {"team_name": "Brooklyn Nets", "off_epm": -0.8, "def_epm": 1.5, "net_epm": -2.3, "home_net_l10": -1.5, "road_net_l10": -3.2},
        "LAC": {"team_name": "Los Angeles Clippers", "off_epm": 3.0, "def_epm": -1.5, "net_epm": 4.5, "home_net_l10": 5.2, "road_net_l10": 3.8}
    }
}

# ==========================================
# --- INJURY EXCLUSION DATABASE (Lens 1) ---
# ==========================================
ACTIVE_INJURIES = {
    "Chet Holmgren": {"team": "OKC", "status": "OUT", "reason": "Patellar Tendinitis"},
    "Jalen Williams": {"team": "OKC", "status": "OUT", "reason": "Ankle Sprain"},
    "Paolo Banchero": {"team": "ORL", "status": "OUT", "reason": "Oblique Strain"},
    "Jalen Suggs": {"team": "ORL", "status": "OUT", "reason": "Knee Soreness"},
    "Joel Embiid": {"team": "PHI", "status": "GTD", "reason": "Rest / Knee Management"},
    "Devin Vassell": {"team": "SAS", "status": "OUT", "reason": "Foot Recovery"}
}

# ==========================================
# --- STRICTLY VERIFIED 2026-27 ROSTERS ---
# ==========================================
VERIFIED_ROSTERS = {
    "ATL": ["Trae Young", "Jalen Johnson", "Dyson Daniels", "Onyeka Okongwu", "Zaccharie Risacher", "C.J. McCollum"],
    "BOS": ["Jayson Tatum", "Paul George", "Derrick White", "Kristaps Porzingis", "Jrue Holiday", "Payton Pritchard"],
    "BKN": ["Julius Randle", "Michael Porter Jr.", "Day'Ron Sharpe", "Cam Thomas", "Nic Claxton"],
    "CHA": ["Brandon Miller", "Dennis Schroder", "Naz Reid", "Moussa Diabate", "Grayson Allen", "LaMelo Ball"],
    "CHI": ["Josh Giddey", "Norman Powell", "Matas Buzelis", "Caleb Wilson", "Jalen Smith", "Coby White"],
    "CLE": ["James Harden", "Donovan Mitchell", "Evan Mobley", "Jarrett Allen", "Sam Merrill"],
    "DAL": ["Luka Doncic", "Kyrie Irving", "P.J. Washington", "Daniel Gafford", "Dereck Lively II"],
    "DEN": ["Nikola Jokic", "Jamal Murray", "Michael Porter Jr.", "Aaron Gordon", "Russell Westbrook"],
    "DET": ["Cade Cunningham", "Duncan Robinson", "Jalen Duren", "Ausar Thompson", "Tobias Harris"],
    "GSW": ["Stephen Curry", "Draymond Green", "Jonathan Kuminga", "Brandin Podziemski", "Buddy Hield"],
    "HOU": ["Kevin Durant", "Alperen Sengun", "Amen Thompson", "Fred VanVleet", "Tari Eason", "Jalen Green"],
    "IND": ["Tyrese Haliburton", "Pascal Siakam", "Myles Turner", "Bennedict Mathurin", "Andrew Nembhard"],
    "LAC": ["Kawhi Leonard", "James Harden", "Norman Powell", "Ivica Zubac", "Darius Garland"],
    "LAL": ["LeBron James", "Anthony Davis", "Austin Reaves", "D'Angelo Russell", "Rui Hachimura"],
    "MEM": ["Ja Morant", "Desmond Bane", "Jaren Jackson Jr.", "Zach Edey", "Marcus Smart"],
    "MIA": ["Giannis Antetokounmpo", "Bam Adebayo", "Jimmy Butler", "Terry Rozier", "Jaime Jaquez Jr."],
    "MIL": ["Damian Lillard", "Khris Middleton", "Brook Lopez", "Bobby Portis", "Tyler Herro"],
    "MIN": ["Anthony Edwards", "Julius Randle", "Rudy Gobert", "Jaden McDaniels", "Mike Conley"],
    "NOP": ["Zion Williamson", "CJ McCollum", "Brandon Ingram", "Herb Jones", "Trey Murphy III"],
    "NYK": ["Jalen Brunson", "Karl-Anthony Towns", "Mikal Bridges", "OG Anunoby", "Josh Hart"],
    "OKC": ["Shai Gilgeous-Alexander", "Isaiah Hartenstein", "Alex Caruso", "Cason Wallace", "Luguentz Dort"],
    "ORL": ["Franz Wagner", "Wendell Carter Jr.", "Cole Anthony", "Jett Howard", "Jonathan Isaac"],
    "PHI": ["Tyrese Maxey", "Joel Embiid", "Paul George", "Kelly Oubre Jr.", "Caleb Martin"],
    "PHX": ["Devin Booker", "Kevin Durant", "Bradley Beal", "Grayson Allen", "Jusuf Nurkic"],
    "POR": ["Anfernee Simons", "Scoot Henderson", "Shaedon Sharpe", "Deni Avdija", "Deandre Ayton"],
    "SAC": ["De'Aaron Fox", "Domantas Sabonis", "DeMar DeRozan", "Keegan Murray", "Kevin Huerter"],
    "SAS": ["Victor Wembanyama", "Devin Vassell", "Chris Paul", "Jeremy Sochan", "Harrison Barnes"],
    "TOR": ["Scottie Barnes", "Immanuel Quickley", "RJ Barrett", "Jakob Poeltl", "Gradey Dick"],
    "UTA": ["Lauri Markkanen", "Keyonte George", "Collin Sexton", "Walker Kessler", "John Collins"],
    "WAS": ["Jordan Poole", "Kyle Kuzma", "Malcolm Brogdon", "Bilal Coulibaly", "Alex Sarr"]
}

# ==========================================
# --- OFFICIAL DYNAMIC GAME SCHEDULES ---
# ==========================================
OFFICIAL_SCHEDULES = {
    date(2026, 11, 2): [("OKC", "CLE"), ("DET", "CHA"), ("BOS", "HOU"), ("UTA", "SAS"), ("MIA", "LAL"), ("CHI", "PHI")],
    date(2026, 11, 3): [], 
    date(2026, 11, 4): [("PHI", "DET"), ("ATL", "WAS"), ("MIL", "BOS"), ("CHA", "BKN"), ("CHI", "NYK"), ("CLE", "OKC"), ("IND", "MEM"), ("UTA", "NOP"), ("MIN", "HOU"), ("TOR", "DEN"), ("POR", "PHX"), ("DAL", "SAS"), ("LAL", "SAC"), ("MIA", "LAC")],
    date(2026, 11, 5): [("OKC", "GSW"), ("BOS", "DEN"), ("LAL", "NYK"), ("MIA", "DAL")]
}

def odds_to_prob(odds):
    return (100.0 / (odds + 100.0)) if odds > 0 else (abs(odds) / (abs(odds) + 100.0))

def prob_to_stars(prob):
    if prob >= 0.75:
        return "⭐⭐⭐⭐⭐ (75%+ Elite Lock)"
    elif prob >= 0.70:
        return "⭐⭐⭐⭐ (70%+ Strong Play)"
    elif prob >= 0.65:
        return "⭐⭐⭐ (65%+ Solid Value)"
    elif prob >= 0.60:
        return "⭐⭐ (60%+ Lean Edge)"
    else:
        return "⭐ (<60% Marginal)"

def generate_multibook_alt_ladders(base_line, base_odds, stat_type, book_name):
    book_multipliers = {"DraftKings": 1.00, "FanDuel": 0.98, "BetMGM": 1.03, "Caesars": 1.05, "Bovada": 0.95}
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
        adjusted_juice = int(round(juice * (2.0 - m))) if juice > 0 else int(round(juice * m))
        alt_market[rung_line] = adjusted_juice
    return alt_market

def calculate_alt_parlay_metrics(items):
    if not items:
        return "+0", 0.0
    decimal_product = 1.0
    compounded_prob = 1.0
    for base_line, chosen_alt_line, base_prob, alt_odds in items:
        line_diff = chosen_alt_line - base_line
        adjusted_prob = max(0.05, min(0.98, base_prob - (line_diff * 0.045)))
        compounded_prob *= adjusted_prob
        dec = ((alt_odds / 100.0) + 1.0) if alt_odds > 0 else ((100.0 / abs(alt_odds)) + 1.0)
        decimal_product *= dec
    if decimal_product >= 
