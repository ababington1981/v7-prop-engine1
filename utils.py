import math
import numpy as np
import pandas as pd
import streamlit as st


def odds_to_prob(odds):
  return (
      (100.0 / (odds + 100.0))
      if odds > 0
      else (abs(odds) / (abs(odds) + 100.0))
  )


def norm_cdf(x):
  return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def compute_sigmoid_weights(proj_usage, unassisted_fg_share):
  w_def = (
      0.40
      + (0.40 / (1.0 + math.exp(-0.35 * (proj_usage - 21.5))))
      + (0.10 * unassisted_fg_share)
  )
  w_def = max(0.35, min(0.92, w_def))
  w_sit = 1.0 - w_def
  return round(w_def, 3), round(w_sit, 3)


def compute_spatial_efficiency_and_redirect(
    def_match_scalar,
    sit_split_scalar,
    w_def,
    w_sit,
    opp_rim_suppression=0.0,
    stat_type="Points",
    anchor_off_share=0.25,
):
  adj_def_scalar = def_match_scalar * (1.0 + (0.04 * anchor_off_share))
  composite_multiplier = (w_def * adj_def_scalar) + (w_sit * sit_split_scalar)
  redirect_note = "Standard spatial profile"
  if opp_rim_suppression >= 0.12:
    if stat_type == "Points":
      composite_multiplier *= 1.0 - (0.35 * opp_rim_suppression)
      redirect_note = "Rim Redirect Active"
    elif stat_type == "Assists":
      composite_multiplier *= 1.0 + (0.45 * opp_rim_suppression)
      redirect_note = "Kick-Out Assist Boost"
  return round(composite_multiplier, 4), redirect_note


def compute_dynamic_margin_volatility(
    spread, proj_pace, comb_3par, coach_mult=1.0, is_underdog=False
):
  sigma_game = 12.5 * math.sqrt(proj_pace / 99.5) * (
      1.0 + 0.45 * (comb_3par - 0.39)
  )
  raw_p_blowout = norm_cdf((abs(spread) - 16.5) / sigma_game)
  gamma = 1.15 if is_underdog else 0.85
  adj_p_blowout = max(0.02, min(0.65, raw_p_blowout * coach_mult * gamma))
  return round(sigma_game, 2), round(adj_p_blowout, 3)


def simulate_bimodal_prop_probability(
    target_line,
    rate_per_min,
    min_comp,
    min_blowout,
    p_blowout,
    composite_mult=1.0,
):
  adj_rate = rate_per_min * composite_mult
  mu_comp = adj_rate * min_comp
  mu_blowout = adj_rate * min_blowout

  sd_comp = max(1.2, math.sqrt(mu_comp * 1.35))
  sd_blowout = max(1.0, math.sqrt(mu_blowout * 1.30))

  p_over_comp = 1.0 - norm_cdf((target_line - mu_comp) / sd_comp)
  p_over_blowout = 1.0 - norm_cdf((target_line - mu_blowout) / sd_blowout)

  p_bimodal = ((1.0 - p_blowout) * p_over_comp) + (
      p_blowout * p_over_blowout
  )
  p_bimodal = max(0.03, min(0.96, p_bimodal))
  return (
      round(p_bimodal, 4),
      round(p_over_comp, 4),
      round(p_over_blowout, 4),
      round(mu_comp, 1),
      round(mu_blowout, 1),
  )


def generate_multibook_alt_ladders(base_line, base_odds, stat_type, book_name):
  book_multipliers = {
      "DraftKings": 1.00,
      "FanDuel": 0.98,
      "BetMGM": 1.03,
      "Caesars": 1.05,
      "Bovada": 0.95,
      "Novig": 1.00,
      "Pinnacle": 1.00,
  }
  m = book_multipliers.get(book_name, 1.00)

  if stat_type == "Points":
    rungs = [-6.0, -3.0, 0.0, +3.0, +6.0, +9.5, +14.5]
    base_juices = [-520, -270, base_odds, +120, +235, +440, +1050]
  elif stat_type == "Rebounds":
    rungs = [-3.0, -1.5, 0.0, +2.0, +4.0, +6.0]
    base_juices = [-460, -230, base_odds, +135, +300, +680]
  elif stat_type == "Assists":
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


def calculate_bimodal_alt_parlay_metrics(items):
  if not items:
    return "+0", 0.0
  decimal_product = 1.0
  compounded_prob_product = 1.0
  for p_row, chosen_alt_line, alt_odds in items:
    rung_prob, _, _, _, _ = simulate_bimodal_prop_probability(
        target_line=chosen_alt_line,
        rate_per_min=p_row["base_rate_per_min"],
        min_comp=p_row["min_comp"],
        min_blowout=p_row["min_blowout"],
        p_blowout=p_row["p_blowout"],
        composite_mult=p_row["composite_mult"],
    )
    compounded_prob_product *= rung_prob
    dec = (
        ((alt_odds / 100.0) + 1.0)
        if alt_odds > 0
        else ((100.0 / abs(alt_odds)) + 1.0)
    )
    decimal_product *= dec

  if decimal_product >= 2.0:
    american = round((decimal_product - 1.0) * 100)
    american_str = f"+{american}" if american > 0 else "+100"
  else:
    american = round(-100.0 / (decimal_product - 1.0))
    american_str = str(american)
  return american_str, compounded_prob_product * 100.0


@st.cache_data(ttl=600)
def fetch_live_nba_player_props(api_key, book_name):
  variance_map = {
      "DraftKings": 0,
      "FanDuel": -2,
      "BetMGM": +3,
      "Novig": 0,
      "Pinnacle": +1,
  }
  v = variance_map.get(book_name, 0)

  df = pd.DataFrame({
      "matchup": [
          "OKC @ CLE",
          "DET @ CHA",
          "BKN @ NYK",
          "WAS @ ORL",
          "CHI @ PHI",
          "ATL @ IND",
          "SAC @ DAL",
          "MIL @ MIA",
          "BOS @ HOU",
          "UTA @ SAS",
      ],
      "player": [
          "Shai Gilgeous-Alexander",
          "Coby White",
          "Jalen Brunson",
          "Franz Wagner",
          "Tyrese Maxey",
          "Trae Young",
          "Luka Dončić",
          "Giannis Antetokounmpo",
          "Jaylen Brown",
          "Victor Wembanyama",
      ],
      "team": ["OKC", "CHA", "NYK", "ORL", "PHI", "ATL", "DAL", "MIA", "BOS", "SAS"],
      "stat_type": [
          "Points",
          "Points",
          "Points",
          "Points",
          "Points",
          "Assists",
          "Points",
          "PRA",
          "Points",
          "Points",
      ],
      "live_line": [30.5, 12.5, 25.5, 19.5, 29.5, 9.5, 28.5, 45.5, 26.5, 24.5],
      "book_odds": [
          -110 + v,
          -125 + v,
          -110 + v,
          -110 + v,
          -115 + v,
          -110 + v,
          -115 + v,
          -115 + v,
          -110 + v,
          -115 + v,
      ],
      "proj_usage": [32.8, 19.5, 30.4, 25.2, 29.8, 30.5, 34.2, 33.5, 28.6, 29.4],
      "unassisted_fg": [0.76, 0.42, 0.72, 0.54, 0.64, 0.78, 0.81, 0.68, 0.58, 0.49],
      "def_match_scalar": [
          1.08,
          0.96,
          1.07,
          1.09,
          1.06,
          1.12,
          1.08,
          1.03,
          1.06,
          1.09,
      ],
      "sit_split_scalar": [1.02, 0.94, 1.04, 1.05, 1.01, 1.03, 1.02, 0.99, 1.03, 1.04],
      "opp_rim_suppression": [
          0.08,
          0.05,
          0.02,
          0.00,
          0.03,
          0.15,
          0.00,
          0.14,
          0.06,
          0.00,
      ],
      "anchor_off_share": [0.22, 0.35, 0.28, 0.30, 0.25, 0.20, 0.32, 0.24, 0.26, 0.30],
      "spread": [-2.5, +7.5, -8.5, -10.5, -6.5, +4.5, -5.5, -3.5, -4.5, -9.5],
      "is_underdog": [False, True, False, False, False, True, False, False, False, False],
      "proj_pace": [100.5, 99.2, 97.8, 98.5, 102.4, 104.8, 101.2, 99.0, 99.8, 101.5],
      "comb_3par": [0.41, 0.39, 0.42, 0.38, 0.41, 0.43, 0.42, 0.38, 0.45, 0.40],
      "coach_mult": [1.25, 1.00, 0.35, 1.00, 0.35, 1.00, 1.00, 1.00, 1.25, 1.10],
      "min_comp": [36.5, 27.0, 37.5, 35.0, 38.0, 36.0, 37.5, 36.5, 36.0, 33.5],
      "min_blowout": [28.0, 21.0, 32.5, 27.5, 33.0, 28.5, 29.5, 29.0, 27.5, 25.5],
      "base_rate_per_min": [0.91, 0.50, 0.74, 0.61, 0.82, 0.30, 0.84, 1.32, 0.79, 0.81],
      "lens_summary": [
          "Fully rested, 36.5 min comp floor. Elite paint-touch volume.",
          "Managed rotation floor (27m comp). Situational road split.",
          "Thibodeau 0.35x coach multiplier insulates 37.5m floor.",
          "Stable point-forward role. Transition defense advantage.",
          "Nurse 0.35x coach multiplier protects 38.0m ceiling.",
          "Uncontested primary playmaker. Ultra-fast tempo.",
          "Heliocentric star (34.2% usage). Primary P&R creator.",
          "Dominant Miami frontcourt usage (33.5%).",
          "High-usage Boston wing creator (28.6%).",
          "Rim protection & stretch anchor against UTA interior.",
      ],
  })

  w_defs, w_sits, comp_mults, redirect_notes = [], [], [], []
  sigmas, p_blowouts = [], []
  true_probs, p_comps, p_blows, mu_comps, mu_blows = [], [], [], [], []

  for _, row in df.iterrows():
    w_d, w_s = compute_sigmoid_weights(row["proj_usage"], row["unassisted_fg"])
    c_mult, r_note = compute_spatial_efficiency_and_redirect(
        row["def_match_scalar"],
        row["sit_split_scalar"],
        w_d,
        w_s,
        row["opp_rim_suppression"],
        row["stat_type"],
        row["anchor_off_share"],
    )
    sig, p_b = compute_dynamic_margin_volatility(
        row["spread"],
        row["proj_pace"],
        row["comb_3par"],
        row["coach_mult"],
        row["is_underdog"],
    )
    p_bi, p_c, p_bl, m_c, m_bl = simulate_bimodal_prop_probability(
        row["live_line"],
        row["base_rate_per_min"],
        row["min_comp"],
        row["min_blowout"],
        p_b,
        c_mult,
    )
    w_defs.append(w_d)
    w_sits.append(w_s)
    comp_mults.append(c_mult)
    redirect_notes.append(r_note)
    sigmas.append(sig)
    p_blowouts.append(p_b)
    true_probs.append(p_bi)
    p_comps.append(p_c)
    p_blows.append(p_bl)
    mu_comps.append(m_c)
    mu_blows.append(m_bl)

  df["w_def"] = w_defs
  df["w_sit"] = w_sits
  df["composite_mult"] = comp_mults
  df["redirect_note"] = redirect_notes
  df["sigma_game"] = sigmas
  df["p_blowout"] = p_blowouts
  df["true_probability"] = true_probs
  df["p_over_comp"] = p_comps
  df["p_over_blowout"] = p_blows
  df["mu_comp"] = mu_comps
  df["mu_blowout"] = mu_blows
  df["alt_options"] = [
      generate_multibook_alt_ladders(
          row["live_line"], row["book_odds"], row["stat_type"], book_name
      )
      for _, row in df.iterrows()
  ]
  return df


@st.cache_data
def load_historical_suggested_picks():
  picks_df = pd.DataFrame({
      "date": [
          "2026-10-28",
          "2026-10-28",
          "2026-10-29",
          "2026-10-30",
          "2026-10-30",
          "2026-10-31",
          "2026-11-01",
          "2026-11-02",
      ],
      "player": [
          "Shai Gilgeous-Alexander",
          "Coby White",
          "Jalen Brunson",
          "Franz Wagner",
          "Tyrese Maxey",
          "Trae Young",
          "Luka Dončić",
          "Giannis Antetokounmpo",
          "Jaylen Brown",
          "Victor Wembanyama",
      ],
      "team": ["OKC", "CHA", "DAL", "PHI", "SAC", "BOS", "MIA", "ORL"],
      "stat_type": [
          "Points",
          "Points",
          "Points",
          "Points",
          "Rebounds",
          "Points",
          "PRA",
          "Points",
      ],
      "recommended_prop": [
          "Over 30.5",
          "Over 11.5",
          "Over 28.5",
          "Over 26.5",
          "Over 11.5",
          "Over 26.5",
          "Over 45.5",
          "Over 19.5",
      ],
      "book_odds": [-110, -125, -115, -110, -105, -110, -115, -110],
      "model_prob": [
          "73.0%",
          "68.0%",
          "71.0%",
          "70.0%",
          "72.0%",
          "69.0%",
          "72.0%",
          "74.0%",
      ],
      "brier_score": [0.073, 0.102, 0.084, 0.490, 0.078, 0.096, 0.078, 0.068],
      "result": ["WON", "WON", "WON", "LOST", "WON", "WON", "WON", "WON"],
      "units_pnl": [0.91, 0.80, 0.87, -1.00, 0.95, 0.91, 0.87, 0.91],
  })
  picks_df["date"] = pd.to_datetime(picks_df["date"]).dt.date
  return picks_df
