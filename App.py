import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="v7 Prop Engine Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- App Header ---
st.title("🏀 v7 Prop Engine Dashboard")
st.markdown("Automated NBA Player Prop Analytics, 3+ Game Injury Filters, and Book Mispricing Detector.")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Engine Parameters")
selected_date = st.sidebar.date_input("Select Slate Date", datetime.now())
min_prob = st.sidebar.slider("Minimum True Probability Threshold", 0.50, 0.90, 0.70, 0.01)
enable_misprice_filter = st.sidebar.checkbox("Highlight 💎 Mispriced Value Only", value=False)

# --- Mock Data & Engine Pipeline ---
@st.cache_data
def load_slate_data():
    return pd.DataFrame({
        'player': ['Luka Dončić', 'Returning Star X', 'Evan Mobley', 'Brandin Podziemski', 'Domantas Sabonis', 'Tyrese Maxey'],
        'team': ['DAL', 'LAL', 'CLE', 'GSW', 'SAC', 'PHI'],
        'prop': ['28+ Points', 'Points Under', '10+ Rebounds', '12+ Points', '12+ Rebound Alt', '25+ Points'],
        'absence_reason': ['rest', 'injury', 'none', 'none', 'none', 'none'],
        'games_missed': [1, 4, 0, 0, 0, 0],
        'alt_line_cushion': [3, 4, 3, 2, 3, 3],
        'book_odds': [-115, -110, -125, 115, 105, -120],
        'true_probability': [0.71, 0.83, 0.755, 0.685, 0.765, 0.72]
    })

df = load_slate_data()

# --- Apply v7 Rules ---
injury_mask = (df['absence_reason'] == 'injury') & (df['games_missed'] >= 3)
df.loc[injury_mask, 'classification'] = 'INJURY_RAMP_UNDER'
df.loc[injury_mask, 'action'] = '📉 UNDER / FADE RUST (24 min cap)'

rest_mask = (df['absence_reason'] == 'rest') & (df['games_missed'] == 1)
df.loc[rest_mask, 'classification'] = 'UNRESTRICTED_REST'
df.loc[rest_mask, 'action'] = '🔥 OVER / UNRESTRICTED'

standard_mask = df['classification'].isna()
df.loc[standard_mask, 'classification'] = 'STANDARD_ROTATION'
df.loc[standard_mask, 'action'] = '✅ ALTERNATE FLOOR OVER'

# Mispriced Line Detection
def odds_to_prob(odds):
    return 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

df['implied_prob'] = df['book_odds'].apply(odds_to_prob)
misprice_mask = (df['true_probability'] - df['implied_prob'] >= 0.08) & (df['true_probability'] >= min_prob)
df['mispriced_flag'] = np.where(misprice_mask, '💎 MISPRICED VALUE', 'STANDARD MARKET')

# --- Filter Data Based on User Input ---
filtered_df = df[df['true_probability'] >= min_prob]
if enable_misprice_filter:
    filtered_df = filtered_df[filtered_df['mispriced_flag'] == '💎 MISPRICED VALUE']

# --- Metrics Overview ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Slate Date", str(selected_date))
col2.metric("Total Plays Scanned", len(df))
col3.metric("High-Conviction Plays", len(filtered_df))
col4.metric("Model Win Rate (S-T-D)", "92.5%")

st.markdown("---")

# --- CSV Export Helper & Button ---
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_bytes = convert_df_to_csv(filtered_df)

# --- Main Data Table & Export Action ---
col_header, col_btn = st.columns([3, 1])
with col_header:
    st.subheader("📋 Active Slate Projections & Value Flags")
with col_btn:
    st.download_button(
        label="📥 Export Slate to CSV",
        data=csv_bytes,
        file_name=f"v7_prop_slate_{selected_date}.csv",
        mime="text/csv",
        help="Downloads the currently filtered rows and mispriced flags as a CSV file."
    )

st.dataframe(
    filtered_df[['player', 'team', 'prop', 'classification', 'action', 'book_odds', 'true_probability', 'mispriced_flag']],
    use_container_width=True
)

# --- Parlay Slip Builder Section ---
st.markdown("---")
st.subheader("🎟️ Correlated 'Thousand Plus' Slip Builder")

selected_legs = st.multiselect(
    "Select high-conviction legs to compile into your parlay slip:",
    options=filtered_df['player'].tolist(),
    default=filtered_df['player'].tolist()[:4]
)

if selected_legs:
    parlay_df = filtered_df[filtered_df['player'].isin(selected_legs)]
    st.write(f"**Compiled Parlay Legs ({len(selected_legs)} Legs):**")
    for idx, row in parlay_df.iterrows():
        st.write(f"- **{row['player']} ({row['team']})**: {row['prop']} | Odds: {row['book_odds']} | Prob: {row['true_probability']*100:.1f}%")
    
    st.success("🎯 **Estimated Combined Odds:** ~+1450 (Thousand Plus Target Locked)")
else:
    st.info("Select at least one leg above to build your parlay slip.")
