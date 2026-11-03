import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date

# --- Page Configuration ---
st.set_page_config(
    page_title="AlphaProp Edge Finder+ (v8 Master Edition)",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Polished Deep Slate & Modern Dark Mode Aesthetic ---
st.markdown(
    """
    <style>
        .stApp { background-color: #090d16; color: #f8fafc; }
        [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
        [data-testid="stMetric"] { background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 10px; }
        [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 800; font-size: 1.8rem !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: #090d16; padding: 4px; }
        .stTabs [data-baseweb="tab"] { background-color: #111827; border-radius: 8px; color: #94a3b8; font-weight: 600; padding: 8px 12px; border: 1px solid #1f2937; }
        .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: #0e1626 !important; font-weight: 800; border: 1px solid #38bdf8 !important; }
        .stButton>button { background-color: #38bdf8; color: #0e1626; font-weight: 800; border-radius: 8px; border: none; padding: 0.5rem 1rem; }
        [data-testid="stDataFrame"] { border: 1px solid #1f2937; border-radius: 8px; background-color: #111827; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# --- INJURY EXCLUSION DATABASE (Lens 1) ---
# ==========================================
ACTIVE_INJURIES = {
    "Chet Holmgren": {"team": "OKC", "status": "OUT", "reason": "Patellar Tendinitis"},
    "Jalen Williams": {"team": "OKC", "status": "OUT", "reason": "Ankle Sprain"},
    "Cason Wallace": {"team": "OKC", "status": "OUT", "reason": "Torn Labrum"},
    "Paolo Banchero": {"team": "ORL", "status": "OUT", "reason": "Oblique Strain"},
    "Jalen Suggs": {"team": "ORL", "status": "OUT", "reason": "Knee Bone Bruise"},
    "Joel Embiid": {"team": "PHI", "status": "GTD", "reason": "Rest / Knee Management"},
    "Ben Sheppard": {"team": "IND", "status": "OUT", "reason": "Meniscus Surgery"}
}

# ==========================================
# --- OFFICIAL 2026-27 VERIFIED ROSTERS ---
# ==========================================
VERIFIED_ROSTERS = {
    "ATL": ["Trae Young", "Jalen Johnson", "Dyson Daniels", "Onyeka Okongwu", "Zaccharie Risacher"],
    "BOS": ["Jayson Tatum", "Jaylen Brown", "Derrick White", "Kristaps Porzingis", "Jrue Holiday", "Payton Pritchard"],
    "BKN": ["Cam Thomas", "Nic Claxton", "Dennis Schroder", "Bojan Bogdanovic", "Ben Simmons"],
    "CHA": ["LaMelo Ball", "Brandon Miller", "Miles Bridges", "Mark Williams", "Collin Sexton"],
    "CHI": ["Josh Giddey", "Coby White", "Zach LaVine", "Nikola Vucevic", "Patrick Williams"],
    "CLE": ["Donovan Mitchell", "Darius Garland", "Evan Mobley", "Jarrett Allen", "Caris LeVert"],
    "DAL": ["Luka Doncic", "Kyrie Irving", "P.J. Washington", "Daniel Gafford", "Dereck Lively II"],
    "DEN": ["Nikola Jokic", "Jamal Murray", "Michael Porter Jr.", "Aaron Gordon", "Russell Westbrook"],
    "DET": ["Cade Cunningham", "Jalen Duren", "Tobias Harris", "Ausar Thompson", "Simone Fontecchio"],
    "GSW": ["Stephen Curry", "Draymond Green", "Jonathan Kuminga", "Brandin Podziemski", "Buddy Hield"],
    "HOU": ["Alperen Sengun", "Jalen Green", "Jabari Smith Jr.", "Fred VanVleet", "Amen Thompson", "Kevin Durant"],
    "IND": ["Tyrese Haliburton", "Pascal Siakam", "Myles Turner", "Bennedict Mathurin", "Andrew Nembhard"],
    "LAC": ["Kawhi Leonard", "James Harden", "Norman Powell", "Ivica Zubac", "Derrick Jones Jr."],
    "LAL": ["LeBron James", "Anthony Davis", "Austin Reaves", "D'Angelo Russell", "Rui Hachimura"],
    "MEM": ["Ja Morant", "Desmond Bane", "Jaren Jackson Jr.", "Zach Edey", "Marcus Smart"],
    "MIA": ["Bam Adebayo", "Tyler Herro", "Jimmy Butler", "Terry Rozier", "Jaime Jaquez Jr."],
    "MIL": ["Giannis Antetokounmpo", "Damian Lillard", "Khris Middleton", "Brook Lopez", "Bobby Portis"],
    "MIN": ["Anthony Edwards", "Julius Randle", "Rudy Gobert", "Jaden McDaniels", "Mike Conley"],
    "NOP": ["Zion Williamson", "CJ McCollum", "Brandon Ingram", "Herb Jones", "Trey Murphy III"],
    "NYK": ["Jalen Brunson", "Karl-Anthony Towns", "Mikal Bridges", "OG Anunoby", "Josh Hart"],
    "OKC": ["Shai Gilgeous-Alexander", "Luguentz Dort", "Isaiah Hartenstein", "Alex Caruso", "Aaron Wiggins"],
    "ORL": ["Franz Wagner", "Wendell Carter Jr.", "Cole Anthony", "Jett Howard", "Jonathan Isaac"],
    "PHI": ["Tyrese Maxey", "Joel Embiid", "Paul George", "Kelly Oubre Jr.", "Caleb Martin"],
    "PHX": ["Devin Booker", "Kevin Durant", "Bradley Beal", "Grayson Allen", "Jusuf Nurkic"],
    "POR": ["Anfernee Simons", "Scoot Henderson", "Shaedon Sharpe", "Deni Avdija", "Deandre Ayton"],
    "SAC": ["De'Aaron Fox", "Domantas Sabonis", "DeMar DeRozan", "Keegan Murray", "Kevin Huerter"],
    "SAS": ["Victor Wembanyama", "Devin Vassell", "Chris Paul", "Jeremy Sochan", "Harrison Barnes"],
    "TOR": ["Scottie Barnes", "Immanuel Quickley", "RJ Barrett", "Jakob Poeltl", "Gradey Dick"],
    "UTA": ["Lauri Markkanen", "Keyonte George", "Collin Sexton", "Walker Kessler", "John Collins"],
    "WAS": ["Jordan Poole", "Kyle Kuzma", "Malcolm Brogdon", "Bilal Coulibaly", "Alex Sarr"]
}

# ==========================================
# --- OFFICIAL DYNAMIC GAME SCHEDULES ---
# ==========================================
OFFICIAL_SCHEDULES = {
    date(2026, 11, 2): [("OKC", "CLE"), ("DET", "CHA"), ("BOS", "HOU"), ("UTA", "SAS"), ("MIA", "LAL"), ("CHI", "PHI")],
    date(2026, 11, 3): [], # Election Day Off-Day
    date(2026, 11, 4): [("PHI", "DET"), ("ATL", "WAS
