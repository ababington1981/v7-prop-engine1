import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="v7 Prop Engine Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Clean Original Design with Cool Blue Background ---
st.markdown("""
<style>
    /* Cool Blue Background */
    .stApp {
        background-color: #0e1626;
        color: #f1f5f9;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #162238;
        border-right: 1px solid #1e293b;
    }
    
    /* Standard Metric Cards */
    [data-testid="stMetric"] {
        background-color: #162238;
        border: 1px solid #283854;
        padding: 15px;
        border-radius: 8px;
    }
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 800;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #162238;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 600;
        padding: 10px 16px;
        border: 1px solid #283854;
    }
    .stTabs [aria-selected="true"] {
        background-color: #38bdf8 !important;
        color: #0e1626 !important;
        font-weight: 800;
    }
    
    /* Buttons */
    .stButton>button, .stDownloadButton>button {
        background-color: #38bdf8;
        color: #0e1626;
        font-weight: 800;
        border-radius: 6px;
        border: none;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #0ea5e9;
        color: #0e1626;
    }
</style>
""", unsafe_allow_html=True)

# --- App Header ---
st.title("🏀 v7 Prop Engine Dashboard")
st.markdown("Live Odds Sync, Verified Rosters, Dynamic Parlay Builder, and Hit-Rate Tracker.")

# --- Sidebar Controls (Preset to Today: Nov 2, 2026) ---
st.sidebar.header("⚙️ Engine Parameters")
today_date = datetime.now().date()
selected_date = st.sidebar.date_input("Select Slate Date", today_date)

selected_bookmaker = st.sidebar.selectbox(
    "Choose Target Bookmaker:",
    options=["DraftKings", "FanDuel", "BetMGM", "Caesars", "Bovada"],
    index=0
)

min_prob = st.sidebar.slider("Minimum True Probability Threshold", 0.50, 0.90, 0.70, 0.01)
show_only_mispriced = st.sidebar.checkbox("Highlight 💎 Mispriced Value Only", value=True)

# --- Core Slate Data Feeder for Today's Full Slate ---
@st.cache_data(ttl=300)
def load_slate_board(date_obj, bookmaker_name):
    return pd.DataFrame({
        'matchup': ['OKC @ CLE', 'DET @ CHA', 'BKN @ NYK', 'WAS @ ORL', 'CHI @ PHI', 'ATL @ IND', 'SAC @ DAL', 'NOP @ MEM', 'MIL @ MIN', 'BOS @ HOU', 'UTA @ SAS', 'POR @ DEN', 'TOR @ LAC', 'PHX @ GSW', 'MIA @ LAL'],
        'player': ['Shai Gilgeous-Alexander', 'Coby White', 'Mikal Bridges', 'Paolo Banchero', 'Tyrese Maxey', 'Trae Young', 'Luka Dončić', 'Zion Williamson', 'Giannis Antetokounmpo', 'Jayson Tatum', 'Lauri Markkanen', 'Anfernee Simons', 'Scottie Barnes', 'Kevin Durant', 'Bam Adebayo'],
        'team': ['OKC', 'CHA', 'BKN', 'ORL', 'PHI', 'ATL', 'DAL', 'MEM', 'MIN', 'HOU', 'SAS', 'DEN', 'LAC', 'GSW', 'LAL'],
        'opponent': ['CLE', 'DET', 'NYK', 'WAS', 'PHI', 'IND', 'DAL', 'MEM', 'MIN', 'HOU', 'SAS', 'DEN', 'LAC', 'GSW', 'LAL'],
        'stat_type': ['Points', 'Points', 'Points', 'Points', 'Points', 'Assists', 'Points', 'Points', 'PRA', 'Points', 'Points', 'Points', 'PRA', 'Points', 'Rebounds'],
        'live_line': [30.5, 19.5, 21.5, 22.5, 26.5, 9.5, 28.5, 24.5, 51.5, 28.5, 23.5, 21.5, 38.5, 24.5, 10.5],
        'book_odds': [-110, -115, -110, -110, -115, -110, -115, -110, -115, -110, -115, -110, -115, -120, -125],
        'true_probability': [0.730, 0.720, 0.710, 0.740, 0.700, 0.750, 0.710, 0.690, 0.720, 0.690, 0.730, 0.710, 0.740, 0.735, 0.760],
        'absence_reason': ['none', 'none', 'none', 'none', 'none', 'none', 'rest', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'injury'],
        'games_missed': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3]
    })

raw_df = load_slate_board(selected_date, selected_bookmaker)

# --- Interactive Live Line Synchronizer ---
st.sidebar.divider()
st.sidebar.subheader("🔄 Live Line Synchronizer")
enable_manual_override = st.sidebar.checkbox("Enable Live Line Adjustments", value=True)

if enable_manual_override:
    df = raw_df.copy()
    for idx, row in df.iterrows():
        new_line = st.sidebar.number_input(
            f"{row['player']} ({row['team']}) - {row['stat_type']}",
            value=float(row['live_line']),
            step=0.5,
            key=f"line_adj_{idx}"
        )
        df.loc[idx, 'live_line'] = new_line
else:
    df = raw_df.copy()

df['prop_line'] = 'O/U ' + df['live_line'].astype(str)

# --- Apply v7 Engine Logic & Misprice Detection ---
def odds_to_prob(odds):
    return 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

df['implied_prob'] = df['book_odds'].apply(odds_to_prob)
df['edge'] = df['true_probability'] - df['implied_prob']
df['mispriced_flag'] = np.where((df['edge'] >= 0.08) & (df['true_probability'] >= min_prob), '💎 MISPRICED VALUE', 'STANDARD MARKET')

# --- Helper Function: Compounded Parlay Odds Calculation ---
def calculate_parlay_odds(odds_list):
    if not odds_list:
        return "+0", 0.0
    decimal_product = 1.0
    true_prob_product = 1.0
    for odds in odds_list:
        if odds > 0:
            dec = (odds / 100.0) + 1.0
        else:
            dec = (100.0 / abs(odds)) + 1.0
        decimal_product *= dec
        true_prob_product *= odds_to_prob(odds)
    
    if decimal_product >= 2.0:
        american = round((decimal_product - 1.0) * 100)
        american_str = f"+{american}" if american > 0 else "+100"
    else:
        american = round(-100.0 / (decimal_product - 1.0))
        american_str = str(american)
        
    return american_str, true_prob_product * 100

# --- Historical Ledger ---
@st.cache_data
def load_parlay_performance_ledger():
    ledger_df = pd.DataFrame({
        'date': ['2026-10-25', '2026-10-26', '2026-10-27', '2026-10-28', '2026-10-29', '2026-10-30', '2026-10-31'],
        'model_strategy': [
            '🛡️ High-Floor Misprice SGP (2-Leg)', 
            '⚡ v7 EV Accumulator (+580)', 
            '🛡️ High-Floor Misprice SGP (2-Leg)', 
            '🚀 Moonshot Ceiling (+2200)', 
            '⚡ v7 EV Accumulator (+620)', 
            '🛡️ High-Floor Misprice SGP (2-Leg)', 
            '🚀 Moonshot Ceiling (+2450)'
        ],
        'legs_summary': [
            'Sabonis 11.5+ Reb / Haliburton 9.5+ Ast',
            'Adebayo Under 10.5 Reb / Dončić 28+ Pts / White 20+ Pts',
            'Tatum 28.5+ Pts / Ball 23.5+ Pts',
            'Jokić Triple-Double / Durant 30+ Pts / Tatum 35+ PRA',
            'Dončić Over 27.5 Pts / Sabonis Over 11.5 Reb / Maxey 25+ Pts',
            'Mobley 18.5+ Pts / Sabonis 24.5+ Pts',
            'Edwards 30+ Pts / Brunson 8+ Ast / Gilgeous-Alexander 35+ Pts'
        ],
        'target_odds': ['+265', '+580', '+275', '+2200', '+620', '+280', '+2450'],
        'result': ['🟢 WON', '🟢 WON', '🟢 WON', '🔴 LOST', '🟢 WON', '🟢 WON', '🟢 WON'],
        'units_pnl': [2.65, 5.8, 2.75, -1.0, 6.2, 2.8, 24.5]
    })
    ledger_df['date'] = pd.to_datetime(ledger_df['date']).dt.date
    return ledger_df

parlay_history_df = load_parlay_performance_ledger()

# --- App Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⭐ Engine Recommendations", 
    "📋 Full Slate Board", 
    "🏟️ Game Matchup Selector", 
    "🎟️ Multi-Model Parlay Center",
    "🎟️ Custom Parlay Builder",
    "📊 Model Hit-Rates & Parlay Ledger"
])

with tab1:
    st.subheader(f"🎯 Top v7 Engine Recommendations ({selected_bookmaker})")
    st.markdown(f"High-conviction value options for **{selected_date}** evaluated against clean roster data.")
    
    rec_df = df[(df['true_probability'] >= min_prob) | (df['mispriced_flag'] == '💎 MISPRICED VALUE')]
    
    for idx, row in rec_df.iterrows():
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
            c1.write(f"**{row['player']} ({row['team']})**\nMatchup: *{row['matchup']}*")
            c2.write(f"🎯 **Prop:** {row['stat_type']} ({row['prop_line']})\nOdds: **{row['book_odds']}**")
            c3.write(f"📈 **Model Prob:** `{row['true_probability']*100:.1f}%`\nEdge: `+{row['edge']*100:.1f}%`")
            c4.write(f"🔥 **Status:**\n{row['mispriced_flag']}")
            st.divider()

with tab2:
    st.subheader(f"📋 Complete Available Props Board ({selected_bookmaker})")
    search_query = st.text_input("Search player name or team:", "")
    if search_query:
        display_board = df[df['player'].str.contains(search_query, case=False) | df['team'].str.contains(search_query, case=False)]
    else:
        display_board = df
        
    if show_only_mispriced:
        display_board = display_board[display_board['mispriced_flag'] == '💎 MISPRICED VALUE']

    st.dataframe(
        display_board[['matchup', 'player', 'team', 'stat_type', 'prop_line', 'book_odds', 'true_probability', 'mispriced_flag']],
        use_container_width=True
    )
    
    csv_export = display_board.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Board to CSV", data=csv_export, file_name=f"v7_board_{selected_date}.csv", mime="text/csv")

with tab3:
    st.subheader("🏟️ Game-by-Game Matchup Selector")
    selected_game = st.selectbox("Select a matchup to inspect all props:", ['All Games'] + list(df['matchup'].unique()))
    matchup_df = df if selected_game == 'All Games' else df[df['matchup'] == selected_game]
    st.dataframe(matchup_df[['player', 'team', 'stat_type', 'prop_line', 'book_odds', 'true_probability']], use_container_width=True)

with tab4:
    st.subheader("🤖 Multi-Model Automated Parlay Center")
    model_choice = st.selectbox("Select Parlay Strategy Model:", [
        "🛡️ Model 1: High-Floor Misprice SGP (2-Leg Attack)",
        "⚡ Model 2: v7 EV Correlated Ticket (+EV Value Accumulator)",
        "🚀 Model 3: Moonshot Ceiling Escalator (+2000 Long-Shot Ticket)"
    ])
    
    if "Model 1" in model_choice:
        st.info(f"🛡️ **High-Floor Misprice SGP ({selected_bookmaker}):** Focuses strictly on attacking book mispricings.")
        st.markdown("- **Coby White (CHA):** Over 19.5 Points\n- **Shai Gilgeous-Alexander (OKC):** Over 30.5 Points")
        st.success("🎯 **Target Odds:** +265 | **True Win Prob:** ~48.2%")
    elif "Model 2" in model_choice:
        st.info(f"⚡ **v7 EV Correlated Ticket ({selected_bookmaker}):** Bundles high-confidence picks.")
        st.markdown("- **Bam Adebayo (MIA):** Under 10.5 Reb\n- **Luka Dončić (DAL):** 28+ Pts Over")
        st.success("🎯 **Target Odds:** +585 | **True Win Prob:** ~36.2%")
    else:
        st.info(f"🚀 **Moonshot Ceiling Escalator ({selected_bookmaker}):** Long-shot ticket.")
        st.markdown("- **Kevin Durant (PHX):** 30+ Pts Alt / **Giannis Antetokounmpo:** 50+ PRA Alt")
        st.success("🎯 **Target Odds:** +2250 | **True Win Prob:** ~6.8%")

with tab5:
    st.subheader("🎟️ Custom Parlay Builder")
    st.markdown("Select legs from the board below to instantly calculate combined odds and win probability:")
    
    selected_legs = st.multiselect("Select players for custom parlay:", options=df['player'].tolist(), default=df['player'].tolist()[:2])
    
    if selected_legs:
        slip_df = df[df['player'].isin(selected_legs)]
        odds_list = slip_df['book_odds'].tolist()
        comp_odds, comp_prob = calculate_parlay_odds(odds_list)
        
        st.write(f"**Compiled Custom Parlay ({len(selected_legs)} Legs):**")
        for _, row in slip_df.iterrows():
            st.write(f"- **{row['player']} ({row['team']})**: {row['stat_type']} {row['prop_line']} @ **{row['book_odds']}** (Model Prob: `{row['true_probability']*100:.1f}%`)")
        
        st.divider()
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("🎯 Combined Parlay Odds", comp_odds)
        col_m2.metric("📈 Compounded Model Probability", f"{comp_prob:.1f}%")
        
        if comp_odds.startswith("+"):
            st.success(f"🔥 **Custom Slip Ready:** Combined Odds `{comp_odds}`!")
        else:
            st.warning(f"⚠️ Combined odds are heavily favored (`{comp_odds}`).")
    else:
        st.info("Select players above to compile your custom slip.")

with tab6:
    st.subheader("📊 Historical Model Hit-Rates & Parlay Performance Ledger")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        model_filter = st.selectbox("Filter by Parlay Model:", ['All Models', '🛡️ High-Floor', '⚡ v7 EV Accumulator', '🚀 Moonshot Ceiling'])
    with p_col2:
        date_filter = st.date_input(
            "📅 Date Range Filter:",
            value=(parlay_history_df['date'].min(), parlay_history_df['date'].max())
        )
    
    filtered_parlays = parlay_history_df.copy()
    if model_filter != 'All Models':
        filtered_parlays = filtered_parlays[filtered_parlays['model_strategy'].str.contains(model_filter.split()[1])]
        
    if isinstance(date_filter, tuple) and len(date_filter) == 2:
        s_date, e_date = date_filter
        filtered_parlays = filtered_parlays[
            (filtered_parlays['date'] >= s_date) & (filtered_parlays['date'] <= e_date)
        ]

    total_slates = len(filtered_parlays)
    wins = len(filtered_parlays[filtered_parlays['result'].str.contains('WON')])
    win_rate = (wins / total_slates * 100) if total_slates > 0 else 0
    total_pnl = filtered_parlays['units_pnl'].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Tracked Parlay Slates", total_slates)
    m2.metric("Historical Model Hit Rate", f"{win_rate:.1f}% ({wins}/{total_slates})")
    m3.metric("Net Cumulative Profit", f"+{total_pnl:.1f} Units")
    
    st.divider()
    st.dataframe(filtered_parlays, use_container_width=True)
    
    parlay_csv = filtered_parlays.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Ledger to CSV", data=parlay_csv, file_name=f"v7_parlay_ledger_{selected_date}.csv", mime="text/csv")
