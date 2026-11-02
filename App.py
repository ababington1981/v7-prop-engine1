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
        font
