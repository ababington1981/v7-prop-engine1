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
st.markdown("Multi-Book Alt Engine, Live Line Sync, 3-Pointer Value Scourer, and Performance Ledgers.")

# --- Sidebar Controls & Book Selector Button Group ---
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
    st.subheader("🎯 Market Focus")
    market_focus = st.selectbox(
        "Select Stat Track:",
        options=["🔥 3-Pointers Made (3PT) Focus", "📋 Full Board (All Stats)"],
        index=0,
        key="sidebar_market_focus"
    )
    
    show_only_mispriced = st.checkbox("Highlight 💎 Mispriced Value Only", value=True)

    st.divider()
    submit_button = st.form_submit_button(label="🔄 Refresh & Apply Engine")

if not selected_bookmaker:
    selected_bookmaker = "DraftKings"

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
    
    if stat_type == '3PT Made':
        rungs = [-2.0, -1.0, 0.0, +1.0, +2.0, +3.0, +4.0]
        base_juices = [-480, -240, base_odds, +130, +280, +590, +1250]
    elif stat_type == 'Points':
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
        'stat_type': ['3PT Made', '3PT Made', 'Assists', 'Rebounds', 'Points', '3PT Made', 'Points', 'PRA', '3PT Made', 'Blocks', 'Steals', '3PT Made'],
        'live_line': [2.5, 3.5, 8.5, 6.5, 29.5, 3.5, 28.5, 45.5, 3.5, 2.5, 1.5, 4.5],
        'book_odds': [-115 + v, -110 + v, -110 + v, -110 + v, -115 + v, -120 + v, -115 + v, -115 + v, -110 + v, -115 + v, -120 + v, -110 + v],
        'true_probability': [0.730, 0.710, 0.740, 0.710, 0.700, 0.720, 0.710, 0.720, 0.750, 0.740, 0.710, 0.730],
        'absence_reason': ['none', 'none', 'none', 'none', 'none', 'none', 'rest', 'none', 'none', 'none', 'none', 'none']
    })
    
    df['alt_options'] = [
        generate_multibook_alt_ladders(row['live_line'], row['book_odds'], row['stat_type'], book_name)
        for _, row in df.iterrows()
    ]
    return df

raw_df = load_local_engine_slate(selected_bookmaker)

if "3-Pointers" in market_focus:
    df = raw_df[raw_df['stat_type'] == '3PT Made'].reset_index(drop=True)
else:
    df = raw_df.copy()

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
            key=f"syntaxfix_css_sync_{idx}_{row['player']}"
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
        'stat_type': ['3PT Made', '3PT Made', 'Points', 'Points', 'Rebounds', '3PT Made', 'PRA'],
        'recommended_prop': ['Over 2.5', 'Over 3.5', 'Over 28.5', 'Over 26.5', 'Over 11.5', 'Over 3.5', 'Over 45.5'],
        'book_odds': [-110, -115, -115, -110, -105, -110, -115],
        'model_prob': ['73.0%', '71.0%', '71.0%', '70.0%', '72.0%', '75.0%', '72.0%'],
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

# --- App Tabs (6 Clean Tabs) ---
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
    
    if len(rec_df) == 0:
        st.info(f"No recommendations meet your criteria. Try adjusting your probability threshold or switching market focus in the sidebar.")
    else:
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
    search_query = st.text_input("Search player name or team:", "", key="board_search_input")
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
    st.download_button(f"📥 Export {selected_bookmaker} Board to CSV", data=csv_export, file_name=f"alphaprop_{selected_bookmaker}_board_{selected_date}.csv", mime="text/csv")

with tab3:
    st.subheader("🏟️ Game-by-Game Matchup Selector")
    selected_game = st.selectbox("Select a matchup to inspect all props:", ['All Games'] + list(df['matchup'].unique()) if len(df) > 0 else ['All Games'])
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
        st.markdown(f"- **Coby White (CHA):** Over 3.5 3PT ({selected_bookmaker} Alt Pricing)\n- **Shai Gilgeous-Alexander (OKC):** Over 2.5 3PT")
        st.success("🎯 **Target Odds:** +265 | **True Win Prob:** ~48.2%")
    elif "Model 2" in model_choice:
        st.info(f"⚡ **EV Correlated Ticket ({selected_bookmaker}):** Bundles high-confidence perimeter scoring options.")
        st.markdown("- **Tyrese Maxey (PHI):** Over 29.5 Pts\n- **Kevin Durant (PHX):** Over 4.5 3PT Alt")
        st.success("🎯 **Target Odds:** +585 | **True Win Prob:** ~36.2%")
    else:
        st.info(f"🚀 **Moonshot Ceiling Escalator ({selected_bookmaker}):** Long-shot perimeter ticket.")
        st.markdown("- **Coby White / Kevin Durant / Shai Gilgeous-Alexander:** Multi-Leg 3PT Escalator")
        st.success("🎯 **Target Odds:** +2250 | **True Win Prob:** ~6.8%")

with tab5:
    st.subheader(f"🎟️ Multi-Book Alt Ladder Builder ({selected_bookmaker})")
    st.markdown(f"Select players and pick true alternate rungs priced specifically via **{selected_bookmaker}**:")
    
    rec_players = df['player'].tolist() if len(df) > 0 else []
    selected_alt_players = st.multiselect(
        "Select players for ladder alt parlay:", 
        options=df['player'].tolist() if len(df) > 0 else [], 
        default=rec_players[:2] if len(rec_players) >= 2 else rec_players
    )
    
    if selected_alt_players and len(df) > 0:
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
                chosen_selection = st.selectbox(
                    f"Select Alt Rung ({player_name})", 
                    options=alt_choices, 
                    index=2, 
                    key=f"final_app_alt_{player_name}"
                )
                
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
        
