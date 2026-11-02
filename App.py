# --- Authoritative Roster & Matchup Master Dictionary ---
AUTHORITATIVE_ROSTERS = {
    "Coby White": {"team": "CHA", "opponent": "BOS", "matchup": "CHA @ BOS"},
    "LaMelo Ball": {"team": "CHA", "opponent": "BOS", "matchup": "CHA @ BOS"},
    "Jayson Tatum": {"team": "BOS", "opponent": "CHA", "matchup": "CHA @ BOS"},
    "Nikola Vučević": {"team": "CHI", "opponent": "BOS", "matchup": "CHI @ BOS"},
    "Bam Adebayo": {"team": "MIA", "opponent": "IND", "matchup": "MIA @ IND"},
    "Tyrese Haliburton": {"team": "IND", "opponent": "MIA", "matchup": "MIA @ IND"},
    "Luka Dončić": {"team": "DAL", "opponent": "SAC", "matchup": "SAC @ DAL"},
    "Domantas Sabonis": {"team": "SAC", "opponent": "DAL", "matchup": "SAC @ DAL"},
    "Kevin Durant": {"team": "PHX", "opponent": "DEN", "matchup": "PHX @ DEN"},
    "Nikola Jokić": {"team": "DEN", "opponent": "PHX", "matchup": "PHX @ DEN"}
}

def sanitize_and_map_rosters(df):
    """
    Intercepts any raw dataframe, standardizes player names, 
    and enforces correct verified team affiliations and matchups.
    """
    for idx, row in df.iterrows():
        player_name = row['player']
        if player_name in AUTHORITATIVE_ROSTERS:
            # Enforce strict authoritative team and matchup mapping
            df.loc[idx, 'team'] = AUTHORITATIVE_ROSTERS[player_name]['team']
            df.loc[idx, 'opponent'] = AUTHORITATIVE_ROSTERS[player_name]['opponent']
            df.loc[idx, 'matchup'] = AUTHORITATIVE_ROSTERS[player_name]['matchup']
            
    return df
