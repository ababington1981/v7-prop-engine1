from datetime import datetime
import math
import time
import numpy as np
import pandas as pd
import streamlit as st

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
# --- CORE v8 QUANTITATIVE ENGINE FUNCTIONS ---
# ==========================================


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
