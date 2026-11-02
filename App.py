import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AlphaProp Edge Finder+",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 AlphaProp Edge Finder+")
st.markdown("### Stable Baseline Engine (Recovery Mode)")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Engine Parameters")
selected_date = st.sidebar.date_input("Select Slate Date", datetime.now().date())
selected_bookmaker = st.sidebar.selectbox("Choose Target Bookmaker:", ["DraftKings", "FanDuel", "BetMGM", "Caesars", "Bovada"])
min_prob = st.sidebar.slider("Minimum True Probability Threshold", 0.50, 0.90, 0.65, 0.01)

# --- Core Data Feed ---
@st.cache_data
def load_slate():
    return pd.DataFrame({
        'matchup': ['OKC @ CLE', 'DET @ CHA', 'BKN @ NYK', 'WAS @ ORL', 'CHI @ PHI', 'ATL @ IND', 'SAC @ DAL', 'MIL @ MIN'],
        'player': ['Shai Gilgeous-Alexander', 'Coby White', 'Jalen Brunson', 'Franz Wagner', 'Tyrese Maxey', 'Trae Young', 'Luka Dončić', 'Giannis Antetokounmpo'],
        'team': ['OKC', 'CHA', 'NYK', 'ORL', 'PHI', 'IND', 'DAL', 'MIN'],
        'stat_type': ['Points', 'Points', 'Points', 'Points', 'Points', 'Assists', 'Points', 'PRA'],
        'live_line': [30.5, 12.5, 25.5, 19.5, 29.5, 9.5, 28.5, 45.5],
        'book_odds': [-110, -125, -110, -110, -115, -110, -115, -115],
        'true_probability': [0.730, 0.680, 0.710, 0.740, 0.700, 0.750, 0.710, 0.720],
        'mispriced_flag': ['💎 MISPRICED VALUE', 'STANDARD MARKET', '💎 MISPRICED VALUE', '💎 MISPRICED VALUE', 'STANDARD MARKET', '💎 MISPRICED VALUE', 'STANDARD MARKET', '💎 MISPRICED VALUE']
    })

df = load_slate()

# --- Main App Tabs ---
tab1, tab2 = st.tabs(["⭐ Recommendations", "📋 Props Board"])

with tab1:
    st.subheader(f"Top Engine Recommendations ({selected_bookmaker})")
    rec_df = df[df['true_probability'] >= min_prob]
    for _, row in rec_df.iterrows():
        st.write(f"**{row['player']} ({row['team']})** | {row['stat_type']} O/U {row['live_line']} | Odds: {row['book_odds']} | Model Prob: `{row['true_probability']*100:.1f}%`")

with tab2:
    st.subheader(f"Complete Props Board ({selected_bookmaker})")
    st.dataframe(df, use_container_width=True)
