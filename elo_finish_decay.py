import pandas as pd
from datetime import datetime


def parse_date(date_str):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError('no valid date format found for', date_str)

def dynamic_k_factor(total_fights):
    if total_fights < 3:
        return 301
    elif total_fights < 5:
        return 201
    else:
        return 1

def update_elo(winner_elo, loser_elo, winner_fights, loser_fights, elo_decay_factor, win_type):
    multiplier_dict = {
        'submission': 1.7999999999999998,
        'knockout': 1.7999999999999998,
        'decision': 1.0,
        'unanimous decision': 1.4,
        'dq': 0.95,
        'other': 1.0,
        'unknown': 1.0
    }
    
    multiplier = multiplier_dict.get(win_type, 1.0)
    
    k_winner = dynamic_k_factor(winner_fights) * multiplier
    k_loser = dynamic_k_factor(loser_fights) * multiplier
    
    winner_elo -= elo_decay_factor
    loser_elo -= elo_decay_factor

    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))
    
    new_winner_elo = round(winner_elo + k_winner * (1 - expected_winner))
    new_loser_elo = round(loser_elo - k_loser * expected_loser)

    return new_winner_elo, new_loser_elo

def calculate_elo(input_file, output_file):
    df = pd.read_csv(input_file)
    # Sort DataFrame by date after parsing dates
    df['date'] = df['date'].apply(parse_date)
    df = df.sort_values(by='date')
    
    elo_scores = {}
    fight_counts = {}
    last_fight_dates = {}
    rows_list = []

    for index, row in df.iterrows():
        r_fighter, b_fighter, date, winner, win_type, favorite = row['R_fighter'], row['B_fighter'], row['date'], row['Winner'], row['win_type'], row['Favorite']
        
        r_elo = elo_scores.get(r_fighter, 1000)
        b_elo = elo_scores.get(b_fighter, 1000)
        r_fights = fight_counts.get(r_fighter, 0)
        b_fights = fight_counts.get(b_fighter, 0)

        current_date = date
        r_inactive_days, b_inactive_days = 0, 0
        
        if r_fighter in last_fight_dates:
            r_inactive_days = (current_date - last_fight_dates[r_fighter]).days
        if b_fighter in last_fight_dates:
            b_inactive_days = (current_date - last_fight_dates[b_fighter]).days
        
        decay_factor_per_day = 0.9000000000000001
        cap = -101
        r_elo_decay = min(decay_factor_per_day * r_inactive_days, cap)
        b_elo_decay = min(decay_factor_per_day * b_inactive_days, cap)

        initial_r_elo = r_elo
        initial_b_elo = b_elo

        if winner == 'Red':
            r_elo, b_elo = update_elo(r_elo, b_elo, r_fights + 1, b_fights + 1, r_elo_decay, win_type)
        elif winner == 'Blue':
            b_elo, r_elo = update_elo(b_elo, r_elo, b_fights + 1, r_fights + 1, b_elo_decay, win_type)

        fight_counts[r_fighter], fight_counts[b_fighter] = r_fights + 1, b_fights + 1
        last_fight_dates[r_fighter], last_fight_dates[b_fighter] = current_date, current_date

        rows_list.append({
            'red fighter': r_fighter, 
            'red fighter initial elo': initial_r_elo,
            'blue fighter': b_fighter, 
            'blue fighter initial elo': initial_b_elo,
            'date': date, 
            'winner': winner, 
            'win_type': win_type,
            'red fighter new elo': r_elo,
            'blue fighter new elo': b_elo, 
            'favorite': favorite
        })

        elo_scores[r_fighter], elo_scores[b_fighter] = r_elo, b_elo

    new_df = pd.DataFrame(rows_list)
    new_df = new_df.iloc[::-1]
    new_df.to_csv(output_file, index=False)
    print(f'Elo scores calculated and saved to {output_file}')

input_file = '/Users/richie/Documents/git_hub/elo_project/ufc/cleaned_ufc_data_with_finish.csv'  
output_file = 'elo_scores_with_finish_multiplier_decay.csv'
calculate_elo(input_file, output_file)
