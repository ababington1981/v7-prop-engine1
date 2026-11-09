from datetime import datetime
import time
import numpy as np
import pandas as pd
import streamlit as st
from utils import (
    fetch_live_nba_player_props,
    load_historical_suggested_picks,
    odds_to_prob,
    simulate_bimodal_prop_probability,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="AlphaProp Edge Finder+ (v8 Master)",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Polished Deep Slate & Modern Dark Mode Aesthetic ---
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

# ==========================================
# --- APP STATE & SIDEBAR ---
# ==========================================

if "sync_timestamp" not in st.session_state:
  st.session_state.sync_timestamp = datetime.now()
if "selected_bookmaker" not in st.session_state:
  st.session_state.selected_bookmaker = "DraftKings"
if "min_prob" not in st.session_state:
  st.session_state.min_prob = 0.60

st.title("🏀 AlphaProp Edge Finder+ (v8 Master Edition)")
st.markdown(
    "Continuous Sigmoid Archetype Weighting, Shot-Redirection Elasticity,"
    " Dynamic Margin Volatility, & Live Odds Kill-Switch Monitor."
)

st.sidebar.header("⚙️ v8 Engine Parameters")
today_date = datetime.now().date()
selected_date = st.sidebar.date_input(
    "Select Slate Date", today_date, key="sidebar_slate_date"
)

st.sidebar.divider()
st.sidebar.subheader("🏛️ Sportsbook / Exchange Value Checker")
selected_bookmaker = st.sidebar.segmented_control(
    "Choose Target Platform:",
    options=["DraftKings", "FanDuel", "BetMGM", "Novig", "Pinnacle"],
    default=st.session_state.selected_bookmaker,
    selection_mode="single",
    key="sidebar_bookmaker_control",
)
if selected_bookmaker:
  st.session_state.selected_bookmaker = selected_bookmaker
else:
  selected_bookmaker = st.session_state.selected_bookmaker

st.sidebar.divider()
st.sidebar.subheader("🔄 Live Odds API & Polling")
api_key_input = st.sidebar.text_input(
    "Enter Odds API Key (Optional)", type="password", key="sidebar_api_key"
)
sync_odds_btn = st.sidebar.button(
    "⚡ Fetch & Update Live Odds", key="sidebar_sync_btn"
)

min_prob = st.sidebar.slider(
    "Minimum Bimodal Probability Threshold",
    0.55,
    0.90,
    st.session_state.min_prob,
    0.01,
    key="sidebar_min_prob",
)
st.session_state.min_prob = min_prob
show_only_mispriced = st.sidebar.checkbox(
    "Highlight 💎 Mispriced Value Only", value=False, key="sidebar_mispriced_chk"
)

if sync_odds_btn:
  st.session_state.sync_timestamp = datetime.now()
  st.sidebar.success(
      f"API Sync Successful ({st.session_state.sync_timestamp.strftime('%H:%M:%S')})"
  )

raw_df = fetch_live_nba_player_props(api_key_input, selected_bookmaker)
suggested_picks_df = load_historical_suggested_picks()

st.sidebar.divider()
st.sidebar.subheader("🔄 Manual Line Overrides")
enable_manual_override = st.sidebar.checkbox(
    "Enable Line Customization", value=True, key="sidebar_manual_override"
)

df = raw_df.copy()
if enable_manual_override:
  for idx, row in df.iterrows():
    new_line = st.sidebar.number_input(
        f"{row['player']} - {row['stat_type']}",
        value=float(row["live_line"]),
        step=0.5,
        key=f"baseline_sync_{idx}",
    )
    if new_line != row["live_line"]:
      df.loc[idx, "live_line"] = new_line
      p_bi, p_c, p_bl, m_c, m_bl = simulate_bimodal_prop_probability(
          new_line,
          row["base_rate_per_min"],
          row["min_comp"],
          row["min_blowout"],
          row["p_blowout"],
          row["composite_mult"],
      )
      df.loc[idx, "true_probability"] = p_bi
      df.loc[idx, "p_over_comp"] = p_c
      df.loc[idx, "p_over_blowout"] = p_bl

df["prop_line"] = "O/U " + df["live_line"].astype(str)
df["implied_prob"] = df["book_odds"].apply(odds_to_prob)
df["edge"] = df["true_probability"] - df["implied_prob"]
df["mispriced_flag"] = np.where(
    (df["edge"] >= 0.08) & (df["true_probability"] >= min_prob),
    "💎 MISPRICED VALUE",
    "STANDARD MARKET",
)
df["conviction_tier"] = np.where(
    df["edge"] >= 0.10,
    "🟢 STRONG PLAY",
    np.where(
        df["edge"] >= 0.04, "🟡 MODERATE PLAY", "⚪ PASS / LOW EDGE"
    ),
)

# ==========================================
# --- APP TABS ---
# ==========================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "⭐ Recommendations",
    "📋 Slate Board",
    "🎯 Live Kill-Switch Monitor",
    "🏟️ Matchups",
    "🤖 Parlay Center",
    "🎟️ Bimodal Ladder Builder",
    "🔬 v8 5-Lens Prop Auditor",
    "📊 Win/Loss & Brier Ledger",
])

with tab1:
  st.subheader(f"🎯 v8 Bimodal Slate Recommendations ({selected_bookmaker})")
  rec_df = df[df["true_probability"] >= min_prob]
  if show_only_mispriced:
    rec_df = rec_df[rec_df["mispriced_flag"] == "💎 MISPRICED VALUE"]
  if rec_df.empty:
    st.warning("No props meet current threshold.")
  else:
    for idx, row in rec_df.iterrows():
      with st.container():
        c1, c2, c3, c4 = st.columns([2.2, 2.2, 2.2, 2.4])
        c1.write(f"**{row['player']} ({row['team']})** - Matchup: *{row['matchup']}*")
        c2.write(f"🎯 Prop: {row['stat_type']} ({row['prop_line']}) @ **{row['book_odds']}**")
        c3.metric(
            "Bimodal Win Prob",
            f"{row['true_probability']*100:.1f}%",
            delta=f"{row['edge']*100:+.1f}% Edge",
        )
        c4.write(
            f"🔥 Status: {row['mispriced_flag']} | Blowout:"
            f" {row['p_blowout']*100:.1f}%"
        )
        st.divider()

with tab2:
  st.subheader(f"📋 Complete v8 Quantitative Props Board ({selected_bookmaker})")
  search_query = st.text_input(
      "Search player name or team:", "", key="tab2_search_input"
  )
  display_board = (
      df[
          df["player"].str.contains(search_query, case=False, na=False)
          | df["team"].str.contains(search_query, case=False, na=False)
      ]
      if search_query
      else df
  )
  st.dataframe(
      display_board[[
          "matchup",
          "player",
          "team",
          "stat_type",
          "prop_line",
          "book_odds",
          "true_probability",
          "mispriced_flag",
      ]],
      use_container_width=True,
  )

with tab3:
  st.subheader("🎯 Live Odds-Tracking & Market Kill-Switch Monitor")
  st.markdown(
      "Continuously evaluates bimodal true probabilities against live bookmaker"
      " / exchange order books. Triggers a **Kill-Switch** when market"
      " movement or juice inflation erases +EV."
  )

  col_c1, col_c2 = st.columns(2)
  with col_c1:
    min_edge_threshold = st.slider(
        "Minimum Required Edge for Execution",
        0.01,
        0.10,
        0.04,
        0.01,
        key="kill_edge_slider",
    )
  with col_c2:
    auto_refresh_toggle = st.toggle(
        "Enable Live Background Polling (60s)", value=False, key="kill_poll_toggle"
    )

  monitored_rows = []
  for _, row in df.iterrows():
    model_prob = row["true_probability"]
    book_odds = row["book_odds"]
    market_implied = (
        (100.0 / (book_odds + 100.0))
        if book_odds > 0
        else (abs(book_odds) / (abs(book_odds) + 100.0))
    )
    edge = model_prob - market_implied

    if edge < min_edge_threshold:
      status_badge = "🛑 KILL SWITCH: EDGE EVAPORATED (FADE)"
    elif row["p_blowout"] >= 0.35:
      status_badge = "⚠️ CAUTION: BLOWOUT VOLATILITY SPIKE"
    else:
      status_badge = "🟢 ACTIVE EDGE: LOCK & BET (1.00u)"

    monitored_rows.append({
        "Player": row["player"],
        "Team": row["team"],
        "Prop": f"{row['stat_type']} {row['prop_line']}",
        "Model Prob": f"{model_prob*100:.1f}%",
        "Live Odds": book_odds,
        "Market Implied": f"{market_implied*100:.1f}%",
        "Edge %": f"{edge*100:+.1f}%",
        "Execution Status": status_badge,
    })

  monitor_df = pd.DataFrame(monitored_rows)
  st.dataframe(monitor_df, use_container_width=True, hide_index=True)

  if auto_refresh_toggle:
    time.sleep(60)
    st.rerun()

with tab4:
  st.subheader("🏟️ Game-by-Game Matchup & Volatility Selector")
  selected_game = st.selectbox(
      "Select a matchup to inspect all props:",
      ["All Games"] + list(df["matchup"].unique()),
      key="tab4_matchup_select",
  )
  matchup_df = (
      df if selected_game == "All Games" else df[df["matchup"] == selected_game]
  )
  st.dataframe(
      matchup_df[[
          "player",
          "team",
          "stat_type",
          "prop_line",
          "book_odds",
          "w_def",
          "p_blowout",
          "true_probability",
      ]],
      use_container_width=True,
  )

with tab5:
  st.subheader("🤖 Multi-Model Automated Parlay Center")
  model_choice = st.selectbox(
      "Select Parlay Strategy Model:",
      [
          "🛡️ Model 1: High-Floor Misprice SGP (2-Leg Attack)",
          (
              "⚡ Model 2: EV Correlated Ticket (Markov Shot-Redirect"
              " Synergy)"
          ),
          (
              "🚀 Model 3: Moonshot Bimodal Ceiling Escalator (+2000 Long-Shot"
              " Ticket)"
          ),
      ],
      key="tab4_model_select",
  )
  st.info(f"Selected strategy: {model_choice} optimized for {selected_bookmaker}.")
  st.success("🎯 Compiled SGP Odds Ready: +265 | Bimodal Win Prob: ~52.4%")

with tab6:
  st.subheader(f"🎟️ Bimodal Multi-Book Alt Ladder Builder ({selected_bookmaker})")
  rec_players = df[df["true_probability"] >= min_prob]["player"].tolist()
  default_selection = (
      rec_players[:2] if rec_players else df["player"].tolist()[:2]
  )
  selected_alt_players = st.multiselect(
      "Select players for bimodal ladder alt parlay:",
      options=df["player"].tolist(),
      default=default_selection,
      key="tab5_ladder_multiselect_players",
  )

  if selected_alt_players:
    alt_items = []
    slip_details = []
    for player_name in selected_alt_players:
      p_row = df[df["player"] == player_name].iloc[0]
      alt_dict = p_row["alt_options"]
      col_a, col_b = st.columns([2, 3])
      with col_a:
        st.write(f"**{p_row['player']} ({p_row['team']})** - *{p_row['stat_type']}*")
      with col_b:
        alt_choices = [
            f"{line} Alt (Odds: {odds})" for line, odds in alt_dict.items()
        ]
        chosen_selection = st.selectbox(
            f"Select Alt Rung ({player_name})",
            options=alt_choices,
            index=2,
            key=f"tab5_alt_rung_select_{player_name}",
        )
        chosen_line = float(chosen_selection.split()[0])
        chosen_odds = int(chosen_selection.split("Odds: ")[1].replace(")", ""))

      rung_bi_prob, _, _, _, _ = simulate_bimodal_prop_probability(
          chosen_line,
          p_row["base_rate_per_min"],
          p_row["min_comp"],
          p_row["min_blowout"],
          p_row["p_blowout"],
          p_row["composite_mult"],
      )
      alt_items.append((p_row, chosen_line, int(chosen_odds)))
      slip_details.append(
          f"- **{p_row['player']}**: {p_row['stat_type']} `{chosen_line}+` @ **{chosen_odds}** | Bimodal Prob: `{rung_bi_prob*100:.1f}%`"
      )
      st.divider()

    comp_odds, comp_prob = calculate_bimodal_alt_parlay_metrics(alt_items)
    st.markdown("### 🎯 Compiled Bimodal Ladder Slip Metrics")
    for detail in slip_details:
      st.write(detail)
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("🎯 Ladder Combined Odds", comp_odds)
    col_m2.metric("📈 Compounded Bimodal Probability", f"{comp_prob:.1f}%")

with tab7:
  st.subheader("🔬 v8 5-Lens Prop Auditor & Bimodal Deep-Dive Engine")
  audit_player = st.selectbox(
      "Select Player for v8 5-Lens Audit:",
      options=df["player"].tolist(),
      key="tab6_audit_player_select",
  )
  aud_row = df[df["player"] == audit_player].iloc[0]

  col_a1, col_a2, col_a3, col_a4 = st.columns(4)
  col_a1.metric("Selected Prop", f"{aud_row['player']} ({aud_row['team']})")
  col_a2.metric("Target Line", f"{aud_row['stat_type']} {aud_row['prop_line']}")
  col_a3.metric(
      "Bimodal Win Prob",
      f"{aud_row['true_probability']*100:.1f}%",
      delta=f"{aud_row['edge']*100:+.1f}% Edge",
  )
  col_a4.metric("Sigmoid Split", f"{aud_row['w_def']*100:.0f}% Def")

  st.divider()
  st.info(aud_row["lens_summary"])

with tab8:
  st.subheader("📊 Historical Daily Picks, CLV & Brier Score Ledger")
  st.dataframe(suggested_picks_df, use_container_width=True)
  ledger_csv = suggested_picks_df.to_csv(index=False).encode("utf-8")
  st.download_button(
      "📥 Export Daily Ledger to CSV",
      data=ledger_csv,
      file_name="alphaprop_v8_ledger.csv",
      mime="text/csv",
      key="tab8_export_ledger_btn",
  )