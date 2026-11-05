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
        "WAS": {"team_name": "Washington Wizards", "off_
