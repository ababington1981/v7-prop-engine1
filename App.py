import streamlit as st
import pandas as pd
import numpy as np
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
    /* Main App Background - Deep Slate Midnight */
    .stApp {
        background-color: #090d16;
        color: #f8fafc;
    }
    
    /* Sidebar Styling - Distinct Slate Container */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    
    /* Metric Cards - Elevated Slate Surface with Cyan Glow Border */
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
    
    /* Tabs Styling - Crisp Contrast */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #090d16;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111827;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 10px 14px;
        border: 1px solid #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background-color: #38bdf8 !important;
        color: #0e1626 !important;
        font-weight: 800;
        border: 1px solid #38bdf8 !important;
    }
    
    /* Buttons - Vibrant Action Cyan */
    .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
        background-color: #38bdf8 !important;
        color: #0e1626 !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
        background-color: #0ea5e9 !important;
        color: #0e1626 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
    
    /* Dataframes & Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #1f2937;
        border-radius: 8px;
        background-color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# --- App Header ---
st.title("🏀 AlphaProp Edge Finder+")
st.markdown("Multi-Book Alt Engine, Live Line Sync, Multi-Stat Scouring (Pts, Reb, Ast, Stl, Blk, 3PT, PRA), and Suggested Picks Ledger.")

# --- Sidebar Controls Form & Submit Button ---
st.sidebar.header("⚙️ Engine Parameters")

with st.sidebar.form(key="engine_params_form"):
    today_date = datetime.now().date()
    selected_date = st.date_input("Select Slate Date", today_date)

    st.divider()
    st.subheader("🏛️ Sportsbook Value Checker")
    selected_bookmaker = st.segmented_control(
        "Choose Target Bookmaker:",
        options=["DraftKings", "FanDuel", "BetMGM", "Caesars", "Bovada"],
        default="DraftKings",
        selection_mode="single"
    )
    
    min_prob = st.slider("Minimum True Probability Threshold", 0.50, 0.90, 0.65, 0.01)
    
    st.divider()
    st.subheader("🔍 Stat Category Scourer")
    selected_stats_filter = st.multiselect(
        "Scour Stat Categories:",
        options=['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', '3PT Made', 'PRA (Pts+Reb+Ast)'],
        default=['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', '3PT Made', 'PRA (Pts+Reb+Ast)']
    )
    
    show_only_mispriced = st.checkbox("Highlight 💎 Mispriced Value Only", value=True)

    st.divider()
    submit_button = st.form_submit_button(label="🔄 Refresh & Apply Engine")

if not selected_bookmaker:
    selected_bookmaker = "DraftKings"
if not selected_stats_filter:
    selected_stats_filter = ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', '3PT Made', 'PRA (Pts+Reb+Ast)']

# --- Universal Multi-Book Alt-Line Pricing Engine ---
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
    elif stat_type == 'Steals':
        rungs = [-1.0, -0.5, 0.0, +1.0, +2.0, +3.0]
        base_juices = [-380, -190, base_odds, +155, +340, +780]
    elif stat_type == 'Blocks':
        rungs = [-1.0, -0.5, 0.0, +1.0, +2.0, +3.0]
        base_juices = [-410, -210, base_odds, +165, +360, +820]
    elif stat_type == '3PT Made':
        rungs = [-2.0, -1.0, 0.0, +1.0, +2.0, +3.0, +4.0]
        base_juices = [-480, -240, base_odds, +130, +280, +590, +1250]
    elif stat_type == 'PRA (Pts+Reb+Ast)':
        rungs = [-8.0, -4.0, 0.0, +5.0, +10.0, +15.0]
        base_juices = [-510, -255, base_odds, +130, +275, +590]
    else: 
        rungs = [-6.0, -3.0, 0.0, +3.0, +6.0, +9.5]
        base_juices = [-500, -250, base_odds, +130, +270, +600]
        
    alt_market = {}
    for offset, juice in zip(rungs, base_juices):
        rung_line = max(0.5, round((base_line + offset) * 2) / 2)
        if juice > 0:
            adjusted_juice = int(round(juice * (2.0 - m)))
        else:
            adjusted_juice = int(round(juice * m))
        alt_market[rung_line] = adjusted_juice
        
    return alt_market

# --- Slate Feed ---
@st.cache_data
def load_local_engine_slate(book_name):
    variance_map = {"DraftKings": 0, "FanDuel": -2, "BetMGM": +3, "Caesars": +5, "Bovada": -5}
    v = variance_map.get(book_name, 0)
    
    df = pd.DataFrame({
        'matchup': ['OKC @ CLE', 'DET @ CHA', 'BKN @ NYK', 'WAS @ ORL', 'CHI @ PHI', 'ATL @ IND', 'SAC @ DAL', 'MIL @ MIN', 'BOS @ HOU', 'UTA @ SAS', 'LAL @ GSW', 'PHX @ DEN'],
        'player': ['Shai Gilgeous-Alexander', 'Coby White', 'Jalen Brunson', 'Franz Wagner', 'Tyrese Maxey', 'Trae Young', 'Luka Dončić', 'Giannis Antetokounmpo', 'Jayson Tatum', 'Victor Wembanyama', 'Anthony Davis', 'Kevin Durant'],
        'team': ['OKC', 'CHA', 'NYK', 'ORL', 'PHI', 'IND', 'DAL', 'MIN', 'HOU', 'SAS', 'LAL', 'PHX'],
        'opponent': ['CLE', 'DET', 'BRK', 'WAS', 'PHI', 'IND', 'SAC', 'MIL', 'HOU', 'UTA', 'GSW', 'DEN'],
        'stat_type': ['Points', 'Points', 'Assists', 'Rebounds', 'Points', 'Assists', 'PRA (Pts+Reb+Ast)', 'Rebounds', 'Steals', 'Blocks', 'Steals', '3PT Made'],
        'live_line': [30.5, 12.5, 8.5, 6.5, 29.5, 9.5, 45.5, 11.5, 1.5, 2.5, 1.5, 2.5],
        'book_odds': [-110 + v, -132 + v, -110 + v, -110 + v, -115 + v, -110 + v, -115 + v, -115 + v, -110 + v, -115 + v, -120 + v, -110 + v],
        'true_probability': [0.730, 0.680, 0.740, 0.710, 0.700, 0.750, 0.720, 0.720, 0.690, 0.740, 0.710, 0.730],
        'absence_reason': ['none', 'season_debut_mins_limit', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none']
    })
    
    df['alt_options'] = [
        generate_multibook_alt_ladders(row['live_line'], row['book_odds'], row['stat_type'], book_name)
        for _, row in df.iterrows()
    ]
    return df

raw_df = load_local_engine_slate(selected_bookmaker)
df = raw_df[raw_df['stat_type'].isin(selected_stats_filter)].reset_index(drop=True)

# --- Interactive Live Line Synchronizer ---
st.sidebar.divider()
st.sidebar.subheader("🔄 Live Line Synchronizer")
enable_manual_override = st.sidebar.checkbox("Enable Live Line Adjustments", value=True)

if enable_manual_override and len(df) > 0:
    synced_rows = []
    for idx, row in df.iterrows():
        new_line = st.sidebar.number_input(
            f"{row['player']} ({row['team']}) - {row['stat_type']}",
            value=float(row['live_line']),
            step=0.5,
            key=f"syntaxfix_sync_{idx}_{row['player']}"
        )
        row_copy = row.copy()
        row_copy['live_line'] = new_line
        synced_rows.append(row_copy)
    df = pd.DataFrame(synced_rows)

df['prop_line'] = 'O/U ' + df['live_line'].astype(str)

def odds_to_prob(odds):
    return 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

df['implied_prob'] = df['book_odds'].apply(odds_to_prob)
df['edge'] = df['true_probability'] - df['implied_prob']
df['mispriced_flag'] = np.where((df['edge'] >= 0.08) & (df['true_probability'] >= min_prob), '💎 MISPRICED VALUE', 'STANDARD MARKET')

def calculate_alt_parlay_metrics(items):
    if not items:
        return "+0", 0.0
    
