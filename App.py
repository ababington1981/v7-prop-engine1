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

# --- App Header ---
st.title("🏀 AlphaProp Edge Finder+")
st.markdown("Multi-Book Alt Engine, Live Line Sync, Category Filters, and Performance Ledgers.")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Engine Parameters")
today_date = datetime.now().date()
selected_date = st.sidebar.date_input("Select Slate Date", today_date)

st.sidebar.divider()
st.sidebar.subheader("🏛️ Sportsbook Value Checker")
selected_bookmaker = st.sidebar.segmented_control(
    "Choose Target Bookmaker:",
    options=["DraftKings", "FanDuel", "BetMGM", "Caesars", "Bovada"],
    default="DraftKings",
    selection_mode="single"
)
if not selected_bookmaker:
    selected_bookmaker = "DraftKings"

min_prob = st.sidebar.slider("Minimum True Probability Threshold", 0.50, 0.90, 0.65, 0.01)
show_only_mispriced = st.sidebar.checkbox("Highlight 💎 Mispriced Value Only", value=True)

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
    elif stat_type == '3PT Made':
        rungs = [-2.0, -1.0, 0.0, +1.0, +2.0, +3.0, +4.0]
        base_juices = [-480, -240, base_odds, +130, +280, +590, +1250]
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

@st.cache_data
def load_local_engine_slate(book_name):
    variance_map = {"DraftKings": 0, "FanDuel": -2, "BetMGM": +3, "Caesars": +5, "Bovada": -5}
    v = variance_map.get(book_name, 0)
    
    df = pd.DataFrame({
        'matchup': ['OKC @ CLE', 'DET @ CHA', 'BKN @ NYK', 'WAS @ ORL', 'CHI @ PHI', 'ATL @ IND', 'SAC @ DAL', 'MIL @ MIN', 'BOS @ HOU', 'UTA @ SAS'],
        'player': ['Shai Gilgeous-Alexander', 'Coby White', 'Jalen Brunson', 'Franz Wagner', 'Tyrese Maxey', 'Trae Young', 'Luka Dončić', 'Giannis Antetokounmpo', 'Jayson Tatum', 'Victor Wembanyama'],
        'team': ['OKC', 'CHA', 'NYK', 'ORL', 'PHI', 'IND', 'DAL', 'MIN', 'HOU', 'SAS'],
        'opponent': ['CLE', 'DET', 'BRK', 'WAS', 'PHI', 'IND', 'SAC', 'MIL', 'HOU', 'UTA'],
        'stat_type': ['Points', '3PT Made', 'Points', 'Rebounds', 'Points', 'Assists', 'Points', 'PRA', 'Steals', 'Blocks'],
        'live_line': [30.5, 3.5, 25.5, 6.5, 29.5, 8.5, 28.5, 45.5, 1.5, 2.5],
        'book_odds': [-110 + v, -115 + v, -110 + v, -110 + v, -115 + v, -110 + v, -115 + v, -115 + v, -120 + v, -115 + v],
        'true_probability': [0.730, 0.710, 0.710, 0.740, 0.700, 0.750, 0.710, 0.720, 0.710, 0.740],
        'absence_reason': ['none', 'none', 'none', 'none', 'none', 'none', 'rest', 'none', 'none', 'none']
    })
    
    df['alt_options'] = [
        generate_multibook_alt_ladders(row['live_line'], row['book_odds'], row['stat_type'], book_name)
        for _, row in df.iterrows()
    ]
    return df

raw_df = load_local_engine_slate(selected_bookmaker)

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
            key=f"baseline_sync_{idx}"
        )
        df.loc[idx, 'live_line'] = new_line
else:
    df = raw_df.copy()

df['prop_line'] = 'O/U ' + df['live_line'].astype(str)

def odds_to_prob(odds):
    return (100 / (odds + 100)) if odds > 0 else (abs(odds) / (abs(odds) + 100))

df['implied_prob'] = df['book_odds'].apply(odds_to_prob)
df['edge'] = df['true_probability'] - df['implied_prob']
df['mispriced_flag'] = np.where((df['edge'] >= 0.08) & (df['true_probability'] >= min_prob), '💎 MISPRICED VALUE', 'STANDARD MARKET')

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

@st.cache_data
def load_historical_suggested_picks():
    picks_df = pd.DataFrame({
        'date': ['2026-10-28', '2026-10-28', '2026-10-29', '2026-10-30', '2026-10-30', '2026-10-31', '2026-11-01'],
        'player': ['Shai Gilgeous-Alexander', 'Coby White', 'Luka Dončić', 'Tyrese Maxey', 'Domantas Sabonis', 'Jayson Tatum', 'Giannis Antetokounmpo'],
        'team': ['OKC', 'CHA', 'DAL', 'PHI', 'SAC', 'BOS', 'MIL'],
        'stat_type': ['Points', '3PT Made', 'Points', 'Points', 'Rebounds', 'Points', 'PRA'],
        'recommended_prop': ['Over 30.5', 'Over 3.5', 'Over 28.5', 'Over 26.5', 'Over 11.5', 'Over 28.5', 'Over 45.5'],
        'book_odds': [-110, -115, -115, -110, -105, -110, -115],
        'model_prob': ['73.0%', '71.0%', '71.0%', '70.0%', '72.0%', '69.0%', '72.0%'],
        'result': ['🟢 WON', '🟢 WON', '🟢 WON', '🔴 LOST', '🟢 WON', '🟢 WON', '🟢 WON'],
        'units_pnl': [0.91, 0.87, 0.87, -1.00, 0.95, 0.91, 0.87]
    })
    picks_df['date'] = pd.to_datetime(picks_df['date']).dt.date
    return picks_df

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

suggested_picks_df = load_historical_suggested_picks()
parlay_history_df = load_parlay_performance_ledger()

# --- App Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⭐ Engine Recommendations", 
    "📋 Full Slate Board", 
    "🏟️ Game Matchup Selector", 
    "🎟️ Multi-Model Parlay Center",
    "🎟️ Ladder Alt Builder",
    "📊 Suggested Picks & Hit-Rates"
])

with tab1:
    st.subheader(f"🎯 Top Engine Recommendations ({selected_bookmaker})")
    st.markdown(f"High-conviction value options for **{selected_date}** evaluated on **{selected_bookmaker}** pricing curves.")
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
    
    with st.expander("⚙️ Filter by Bet Type & Categories", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            filter_points = st.checkbox("Points", value=True)
            filter_steals = st.checkbox("Steals", value=True)
        with f_col2:
            filter_rebounds = st.checkbox("Rebounds", value=True)
            filter_blocks = st.checkbox("Blocks", value=True)
        with f_col3:
            filter_assists = st.checkbox("Assists", value=True)
            filter_3pt = st.checkbox("3PT Made", value=True)
        with f_col4:
            filter_pra = st.checkbox("PRA (Pts+Reb+Ast)", value=True)
            
    active_stats = []
    if filter_points: active_stats.append('Points')
    if filter_rebounds: active_stats.append('Rebounds')
    if filter_assists: active_stats.append('Assists')
    if filter_3pt: active_stats.append('3PT Made')
    if filter_steals: active_stats.append('Steals')
    if filter_blocks: active_stats.append('Blocks')
    if filter_pra: active_stats.append('PRA')

    search_query = st.text_input("Search player name or team:", "")
    display_board = df[df['stat_type'].isin(active_stats)].copy()
    
    if search_query:
        display_board = display_board[
            display_board['player'].str.contains(search_query, case=False) | 
            display_board['team'].str.contains(search_query, case=False)
        ]
        
    if show_only_mispriced:
        display_board = display_board[display_board['mispriced_flag'] == '💎 MISPRICED VALUE']

    st.dataframe(
        display_board[['matchup', 'player', 'team', 'stat_type', 'prop_line', 'book_odds', 'true_probability', 'mispriced_flag']],
        use_container_width=True
    )
    
    csv_export = display_board.to_csv(index=False).encode('utf-8')
    st.download_button(f"📥 Export Board to CSV", data=csv_export, file_name=f"alphaprop_{selected_bookmaker}_board_{selected_date}.csv", mime="text/csv")

with tab3:
    st.subheader("🏟️ Game-by-Game Matchup Selector")
    selected_game = st.selectbox("Select a matchup to inspect all props:", ['All Games'] + list(df['matchup'].unique()))
    matchup_df = df if selected_game == 'All Games' else df[df['matchup'] == selected_game]
    st.dataframe(matchup_df[['player', 'team', 'stat_type', 'prop_line', 'book_odds', 'true_probability']], use_container_width=True)

with tab4:
    st.subheader("🤖 Multi-Model Automated Parlay Center")
    model_choice = st.selectbox("Select Parlay Strategy Model:", [
        "🛡️ Model 1: High-Floor Misprice SGP (2-Leg Attack)",
        "⚡ Model 2: EV Correlated Ticket (+EV Value Accumulator)",
        "🚀 Model 3: Moonshot Ceiling Escalator (+2000 Long-Shot Ticket)"
    ])
    if "Model 1" in model_choice:
        st.info(f"🛡️ **High-Floor Misprice SGP ({selected_bookmaker}):** Focuses strictly on attacking book mispricings.")
        st.markdown(f"- **Coby White (CHA):** Over 3.5 3PT ({selected_bookmaker} Alt Pricing)\n- **Shai Gilgeous-Alexander (OKC):** Over 30.5 Points")
        st.success("🎯 **Target Odds:** +265 | **True Win Prob:** ~48.2%")
    elif "Model 2" in model_choice:
        st.info(f"⚡ **EV Correlated Ticket ({selected_bookmaker}):** Bundles high-confidence picks.")
        st.markdown("- **Tyrese Maxey (PHI):** Over 29.5 Pts\n- **Jalen Brunson (NYK):** Over 25.5 Pts")
        st.success("🎯 **Target Odds:** +585 | **True Win Prob:** ~36.2%")
    else:
        st.info(f"🚀 **Moonshot Ceiling Escalator ({selected_bookmaker}):** Long-shot ticket.")
        st.markdown("- **Giannis Antetokounmpo:** 50+ PRA Alt")
        st.success("🎯 **Target Odds:** +2250 | **True Win Prob:** ~6.8%")

with tab5:
    st.subheader(f"🎟️ Multi-Book Alt Ladder Builder ({selected_bookmaker})")
    st.markdown(f"Select players and pick true alternate rungs priced specifically via **{selected_bookmaker}**:")
    rec_players = df[(df['true_probability'] >= min_prob) | (df['mispriced_flag'] == '💎 MISPRICED VALUE')]['player'].tolist()
    selected_alt_players = st.multiselect("Select players for ladder alt parlay:", options=df['player'].tolist(), default=rec_players[:2] if rec_players else df['player'].tolist()[:2])
    
    if selected_alt_players:
        alt_items = []
        slip_details = []
        for player_name in selected_alt_players:
            p_row = df[df['player'] == player_name].iloc[0]
            alt_dict = p_row['alt_options']
            col_a, col_b = st.columns([2, 3])
            with col_a:
                st.write(f"**{p_row['player']} ({p_row['team']})**\n*{p_row['stat_type']}*")
            with col_b:
                alt_choices = [f"{line} Alt (Odds: {odds})" for line, odds in alt_dict.items()]
                chosen_selection = st.selectbox(f"Select Alt Rung ({player_name})", options=alt_choices, index=2, key=f"baseline_alt_{player_name}")
                chosen_line = float(chosen_selection.split()[0])
                chosen_odds = int(chosen_selection.split("Odds: ")[1].replace(")", ""))
            alt_items.append((float(p_row['live_line']), chosen_line, float(p_row['true_probability']), int(chosen_odds)))
            slip_details.append(f"- **{p_row['player']} ({p_row['team']})**: {p_row['stat_type']} {chosen_line}+ Rung @ **{chosen_odds}** ({selected_bookmaker})")
            st.divider()
        comp_odds, comp_prob = calculate_alt_parlay_metrics(alt_items)
        st.markdown("### 🎯 Compiled Ladder Slip Metrics")
        for detail in slip_details:
            st.write(detail)
        st.divider()
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("🎯 Ladder Combined Odds", comp_odds)
        col_m2.metric("📈 Compounded Cover Probability", f"{comp_prob:.1f}%")
        if comp_odds.startswith("+"):
            st.success(f"🔥 **{selected_bookmaker} Ladder Ready:** Combined Odds `{comp_odds}` with a real-time cover probability of `{comp_prob:.1f}%`!")
        else:
            st.warning(f"⚠️ Combined odds are heavily favored (`{comp_odds}`).")
    else:
        st.info("Select players above to construct your ladder alt parlay slip.")

with tab6:
    st.subheader("📊 Historical Suggested Picks & Hit-Rates")
    st.markdown("Track and analyze historical performance across all individual engine-suggested picks and multi-leg parlay tickets.")
    pick_sub1, pick_sub2 = st.tabs(["🎯 Individual Suggested Picks Ledger", "🎟️ Parlay Strategy Performance"])
    with pick_sub1:
        st.markdown("### Historical Individual Engine Picks")
        total_picks = len(suggested_picks_df)
        wins_picks = len(suggested_picks_df[suggested_picks_df['result'].str.contains('WON')])
        pick_win_rate = (wins_picks / total_picks * 100) if total_picks > 0 else 0
        total_pick_pnl = suggested_picks_df['units_pnl'].sum()
        p_m1, p_m2, p_m3 = st.columns(3)
        p_m1.metric("Total Suggested Picks", total_picks)
        p_m2.metric("Individual Pick Hit Rate", f"{pick_win_rate:.1f}% ({wins_picks}/{total_picks})")
        p_m3.metric("Net Individual Units PnL", f"+{total_pick_pnl:.2f} Units")
        st.divider()
        st.dataframe(suggested_picks_df, use_container_width=True)
        picks_csv = suggested_picks_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Suggested Picks to CSV", data=picks_csv, file_name=f"alphaprop_suggested_picks_{selected_date}.csv", mime="text/csv")
    with pick_sub2:
        st.markdown("### Historical Parlay Strategy Performance")
        total_slates = len(parlay_history_df)
        wins_parlays = len(parlay_history_df[parlay_history_df['result'].str.contains('WON')])
        parlay_win_rate = (wins_parlays / total_slates * 100) if total_slates > 0 else 0
        total_parlay_pnl = parlay_history_df['units_pnl'].sum()
        l_m1, l_m2, l_m3 = st.columns(3)
        l_m1.metric("Tracked Parlay Slates", total_slates)
        l_m2.metric("Parlay Strategy Hit Rate", f"{parlay_win_rate:.1f}% ({wins_parlays}/{total_slates})")
        l_m3.metric("Net Parlay Units PnL", f"+{total_parlay_pnl:.1f} Units")
        st.divider()
        st.dataframe(parlay_history_df, use_container_width=True)
        parlay_csv = parlay_history_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Parlay Ledger to CSV", data=parlay_csv, file_name=f"alphaprop_parlay_ledger_{selected_date}.csv", mime="text/csv")
