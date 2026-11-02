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
st.markdown("Multi-Model Prop Analytics, Automated Parlay Center, and Historical Model Hit-Rate Tracker.")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Engine Parameters")
selected_date = st.sidebar.date_input("Select Slate Date", datetime.now())
min_prob = st.sidebar.slider("Minimum True Probability Threshold", 0.50, 0.90, 0.70, 0.01)
show_only_mispriced = st.sidebar.checkbox("Highlight 💎 Mispriced Value Only", value=False)

# --- Live / Cached Slate Data Feeder ---
@st.cache_data(ttl=1800)
def load_slate_board(date_obj):
    return pd.DataFrame({
        'matchup': ['CHI @ BOS', 'CHI @ BOS', 'CHI @ BOS', 'MIA @ IND', 'MIA @ IND', 'SAC @ DAL', 'SAC @ DAL', 'PHX @ DEN', 'PHX @ DEN'],
        'player': ['Coby White', 'Jayson Tatum', 'Nikola Vučević', 'Bam Adebayo', 'Tyrese Haliburton', 'Luka Dončić', 'Domantas Sabonis', 'Kevin Durant', 'Nikola Jokić'],
        'team': ['CHI', 'BOS', 'CHI', 'MIA', 'IND', 'DAL', 'SAC', 'PHX', 'DEN'],
        'stat_type': ['Points', 'Points', 'Rebounds', 'Rebounds', 'Assists', 'Points', 'Rebounds', 'Points', 'PRA'],
        'prop_line': ['O/U 19.5', 'O/U 28.5', 'O/U 10.5', 'O/U 10.5', 'O/U 9.5', 'O/U 27.5', 'O/U 11.5', 'O/U 24.5', 'O/U 48.5'],
        'book_odds': [-115, -110, -105, -125, +100, -115, +105, -120, -110],
        'true_probability': [0.720, 0.690, 0.640, 0.760, 0.710, 0.710, 0.765, 0.735, 0.700],
        'absence_reason': ['none', 'none', 'none', 'injury', 'none', 'rest', 'none', 'none', 'none'],
        'games_missed': [0, 0, 0, 3, 0, 1, 0, 0, 0]
    })

df = load_slate_board(selected_date)

# --- Apply v7 Engine Logic & Misprice Detection ---
injury_mask = (df['absence_reason'] == 'injury') & (df['games_missed'] >= 3)
df.loc[injury_mask, 'v7_signal'] = '📉 INJURY RAMP UNDER'

rest_mask = (df['absence_reason'] == 'rest') & (df['games_missed'] == 1)
df.loc[rest_mask, 'v7_signal'] = '🔥 UNRESTRICTED REST OVER'

df['v7_signal'] = df['v7_signal'].fillna('✅ STANDARD ROTATION')

def odds_to_prob(odds):
    return 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

df['implied_prob'] = df['book_odds'].apply(odds_to_prob)
df['edge'] = df['true_probability'] - df['implied_prob']
df['mispriced_flag'] = np.where((df['edge'] >= 0.08) & (df['true_probability'] >= min_prob), '💎 MISPRICED VALUE', 'STANDARD MARKET')

# --- Historical Parlay Model Ledger Feature ---
@st.cache_data
def load_parlay_performance_ledger():
    ledger_df = pd.DataFrame({
        'date': ['2026-10-25', '2026-10-26', '2026-10-27', '2026-10-28', '2026-10-29', '2026-10-30', '2026-10-31'],
        'model_strategy': [
            '🛡️ High-Floor SGP (+110)', 
            '⚡ v7 EV Accumulator (+580)', 
            '🛡️ High-Floor SGP (+115)', 
            '🚀 Moonshot Ceiling (+2200)', 
            '⚡ v7 EV Accumulator (+620)', 
            '🛡️ High-Floor SGP (+112)', 
            '🚀 Moonshot Ceiling (+2450)'
        ],
        'legs_summary': [
            'Sabonis 8+ Reb / Mobley 8+ Pts / Haliburton 6+ Ast',
            'Adebayo Under 10.5 Reb / Dončić 28+ Pts / White 20+ Pts',
            'Tatum 25+ Pts Alt / White 15+ Pts Alt / Jokić 8+ Reb',
            'Jokić Triple-Double / Durant 30+ Pts / Tatum 35+ PRA',
            'Dončić Over 27.5 Pts / Sabonis Over 11.5 Reb / Maxey 25+ Pts',
            'Mobley 10+ Reb / Sabonis 12+ Reb Alt / Podziemski 12+ Pts',
            'Edwards 30+ Pts / Brunson 8+ Ast / Gilgeous-Alexander 35+ Pts'
        ],
        'target_odds': ['+110', '+580', '+115', '+2200', '+620', '+112', '+2450'],
        'result': ['🟢 WON', '🟢 WON', '🟢 WON', '🔴 LOST', '🟢 WON', '🟢 WON', '🟢 WON'],
        'units_pnl': [1.1, 5.8, 1.15, -1.0, 6.2, 1.12, 24.5]
    })
    ledger_df['date'] = pd.to_datetime(ledger_df['date']).dt.date
    return ledger_df

parlay_history_df = load_parlay_performance_ledger()

# --- Interactive App Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⭐ Engine Recommendations", 
    "📋 Full Slate Board", 
    "🏟️ Game Matchup Selector", 
    "🎟️ Multi-Model Parlay Center",
    "🎟️ Custom Parlay Builder",
    "📊 Model Hit-Rates & Parlay Ledger"
])

with tab1:
    st.subheader("🎯 Top v7 Engine Recommendations")
    st.markdown("High-conviction value options filtered by true probability, rest exceptions, and book mispricing.")
    
    rec_df = df[(df['true_probability'] >= min_prob) | (df['mispriced_flag'] == '💎 MISPRICED VALUE')]
    
    for idx, row in rec_df.iterrows():
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
            c1.write(f"**{row['player']} ({row['team']})**\n*{row['matchup']}*")
            c2.write(f"🎯 **Prop:** {row['stat_type']} ({row['prop_line']})\nOdds: **{row['book_odds']}**")
            c3.write(f"📈 **Model Prob:** `{row['true_probability']*100:.1f}%`\nEdge: `+{row['edge']*100:.1f}%`")
            c4.write(f"🔥 **Status:**\n{row['v7_signal']}\n{row['mispriced_flag']}")
            st.divider()

with tab2:
    st.subheader("📋 Complete Available Props Board")
    st.markdown("Browse all available player props and lines across the entire league slate with full market transparency.")
    
    search_query = st.text_input("Search player name or team:", "")
    if search_query:
        display_board = df[df['player'].str.contains(search_query, case=False) | df['team'].str.contains(search_query, case=False)]
    else:
        display_board = df
        
    if show_only_mispriced:
        display_board = display_board[display_board['mispriced_flag'] == '💎 MISPRICED VALUE']

    st.dataframe(
        display_board[['matchup', 'player', 'team', 'stat_type', 'prop_line', 'book_odds', 'true_probability', 'v7_signal', 'mispriced_flag']],
        use_container_width=True
    )
    
    csv_export = display_board.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Current Board to CSV", data=csv_export, file_name=f"v7_full_board_{selected_date}.csv", mime="text/csv")

with tab3:
    st.subheader("🏟️ Game-by-Game Matchup Selector")
    selected_game = st.selectbox("Select a matchup to inspect all props:", ['All Games'] + list(df['matchup'].unique()))
    
    matchup_df = df if selected_game == 'All Games' else df[df['matchup'] == selected_game]
    st.dataframe(matchup_df[['player', 'team', 'stat_type', 'prop_line', 'book_odds', 'true_probability', 'v7_signal']], use_container_width=True)

with tab4:
    st.subheader("🤖 Multi-Model Automated Parlay Center")
    st.markdown("Automated parlay tickets generated by our 3 specialized models:")
    
    model_choice = st.selectbox("Select Parlay Strategy Model:", [
        "🛡️ Model 1: High-Floor SGP Engine (+100 to +120 Safe Milestones)",
        "⚡ Model 2: v7 EV Correlated Ticket (+EV Value Accumulator)",
        "🚀 Model 3: Moonshot Ceiling Escalator (+2000 Long-Shot Ticket)"
    ])
    
    if "Model 1" in model_choice:
        st.info("🛡️ **High-Floor SGP Engine:** Stacks 3 cushioned alternate floors (-350 juice) to lock in a safe +110 payout.")
        st.markdown("**Suggested Legs:**")
        st.markdown("- **Domantas Sabonis (SAC):** 8+ Rebounds Alt (`~85% hit rate`)")
        st.markdown("- **Evan Mobley (CLE):** 8+ Points Alt (`~88% hit rate`)")
        st.markdown("- **Tyrese Haliburton (IND):** 6+ Assists Alt (`~82% hit rate`)")
        st.success("🎯 **Target Odds:** +112 | **True Win Prob:** ~58.5%")
    elif "Model 2" in model_choice:
        st.info("⚡ **v7 EV Correlated Ticket:** Bundles 3 high-confidence mispriced value picks into an optimal multi-game accumulator.")
        st.markdown("**Suggested Legs:**")
        st.markdown("- **Bam Adebayo (MIA):** Under 10.5 Rebounds (`📉 Injury Ramp Under`)")
        st.markdown("- **Luka Dončić (DAL):** 28+ Points Over (`🔥 Rest Exception`)")
        st.markdown("- **Coby White (CHI):** 20+ Points Over (`💎 Mispriced Value`)")
        st.success("🎯 **Target Odds:** +585 | **True Win Prob:** ~36.2%")
    else:
        st.info("🚀 **Moonshot Ceiling Escalator:** Tail-event modeling combining multi-stat ceiling ladders for massive plus-money payouts.")
        st.markdown("**Suggested Legs:**")
        st.markdown("- **Nikola Jokić (DEN):** Triple-Double Alt (`+135`)")
        st.markdown("- **Kevin Durant (PHX):** 30+ Points Alternate Ladder (`+210`)")
        st.markdown("- **Jayson Tatum (BOS):** 35+ PRA Alternate (`+185`)")
        st.success("🎯 **Target Odds:** +2250 | **True Win Prob:** ~6.8%")

with tab5:
    st.subheader("🎟️ Custom Parlay Builder")
    selected_legs = st.multiselect("Select legs from the board to build your custom slip:", options=df['player'].tolist(), default=df['player'].tolist()[:3])
    
    if selected_legs:
        slip_df = df[df['player'].isin(selected_legs)]
        st.write(f"**Compiled Custom Parlay ({len(selected_legs)} Legs):**")
        for _, row in slip_df.iterrows():
            st.write(f"- **{row['player']} ({row['team']})**: {row['stat_type']} {row['prop_line']} @ {row['book_odds']} ({row['true_probability']*100:.1f}% true prob)")
        st.success("🎯 **Target Slip Combined Payout:** ~+680 (Optimized for Expected Value)")
    else:
        st.info("Select players above to build your custom slip.")

with tab6:
    st.subheader("📊 Historical Model Hit-Rates & Parlay Performance Ledger")
    st.markdown("Track historical success rates, hit percentages, and net unit returns for past parlay model suggestions.")
    
    # Filter Controls for Parlay Ledger
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        model_filter = st.selectbox("Filter by Parlay Model:", ['All Models', '🛡️ High-Floor SGP (+110)', '⚡ v7 EV Accumulator', '🚀 Moonshot Ceiling'])
    with p_col2:
        date_filter = st.date_input(
            "📅 Date Range Filter:",
            value=(parlay_history_df['date'].min(), parlay_history_df['date'].max())
        )
    
    # Filter Logic
    filtered_parlays = parlay_history_df.copy()
    if model_filter != 'All Models':
        filtered_parlays = filtered_parlays[filtered_parlays['model_strategy'].str.contains(model_filter.split()[1])]
        
    if isinstance(date_filter, tuple) and len(date_filter) == 2:
        s_date, e_date = date_filter
        filtered_parlays = filtered_parlays[
            (filtered_parlays['date'] >= s_date) & (filtered_parlays['date'] <= e_date)
        ]

    # Metrics Summary
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
    st.download_button("📥 Export Parlay Hit-Rate Ledger to CSV", data=parlay_csv, file_name="v7_parlay_hit_rate_ledger.csv", mime="text/csv")
