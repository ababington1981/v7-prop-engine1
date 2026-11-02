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
st.markdown("Multi-Book Alt Engine, Live Line Sync, Category Filters, Sorted Odds, and Performance Ledgers.")

# --- Sidebar Controls & Book Selector Button Group ---
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
    selected_bookmaker =
