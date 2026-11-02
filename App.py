@st.cache_data(ttl=300)
def load_slate_board(date_obj):
    return pd.DataFrame({
        'matchup': ['CHA @ BOS', 'CHA @ BOS', 'CHI @ BOS', 'MIA @ IND', 'MIA @ IND', 'SAC @ DAL', 'SAC @ DAL', 'PHX @ DEN', 'PHX @ DEN'],
        'player': ['Coby White', 'LaMelo Ball', 'Jayson Tatum', 'Bam Adebayo', 'Tyrese Haliburton', 'Luka Dončić', 'Domantas Sabonis', 'Kevin Durant', 'Nikola Jokić'],
        'team': ['CHA', 'CHA', 'BOS', 'MIA', 'IND', 'DAL', 'SAC', 'PHX', 'DEN'],
        'opponent': ['BOS', 'BOS', 'CHA', 'IND', 'MIA', 'DAL', 'SAC', 'DEN', 'PHX'],
        'stat_type': ['Points', 'Points', 'Points', 'Rebounds', 'Assists', 'Points', 'Rebounds', 'Points', 'PRA'],
        'live_line': [19.5, 23.5, 28.5, 10.5, 9.5, 27.5, 11.5, 24.5, 48.5],
        'book_odds': [-115, -110, -110, -125, +100, -115, +105, -120, -110],
        'true_probability': [0.720, 0.750, 0.690, 0.760, 0.710, 0.710, 0.765, 0.735, 0.700],
        'absence_reason': ['none', 'none', 'none', 'injury', 'none', 'rest', 'none', 'none', 'none'],
        'games_missed': [0, 0, 0, 3, 0, 1, 0, 0, 0]
    })
