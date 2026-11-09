from datetime import datetime
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
      "live_line": [30.5, 12.5, 
