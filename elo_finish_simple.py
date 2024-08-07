import pandas as pd
from datetime import datetime

def parse_date(date_str):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError('no valid date format found for', date_str)

def update_elo(winner_elo, loser_elo, win_type, k=32):
    # Define multipliers for different win types
    multiplier_dict = {
        'submission': 1.8,
        'knockout': 1.8,
        'decision': 1.0,  
        'unanimous decision': 1.4,
        'dq': 0.95,
        'other': 1.0,
        'unknown': 1.0
    }
    
    # Get the multiplier based on the win type
    multiplier = multiplier_dict.get(win_type, 1.0)
    
    # Adjust the K factor based on the win type
    win_type_multiplier = k * multiplier

    # Calculate the expected score for each player
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))
    
    # Update the Elo ratings with adjusted K factor
    new_winner_elo = round(winner_elo + win_type_multiplier * (1 - expected_winner))
    new_loser_elo = round(loser_elo - win_type_multiplier * expected_loser)
    
    return new_winner_elo, new_loser_elo

def calculate_elo(input_file, output_file):
    df = pd.read_csv(input_file)
    # Sort DataFrame by date after parsing dates
    df['date'] = df['date'].apply(parse_date)
    df = df.sort_values(by='date')
    
    elo_scores = {}
    rows_list = []  # Use a list to collect rows for efficiency

    for index, row in df.iterrows():
        r_fighter = row['R_fighter']
        b_fighter = row['B_fighter']
        date = row['date']
        winner = row['Winner']
        win_type = row['win_type']  # Assume 'win_type' column exists and contains the finish type
        favorite = row['Favorite']

        # Fetch the current Elo scores or initialize them
        r_elo = elo_scores.get(r_fighter, 1000)
        b_elo = elo_scores.get(b_fighter, 1000)

        # Correctly capture the initial Elo scores
        initial_r_elo = r_elo
        initial_b_elo = b_elo

        if winner == 'Red':
            updated_r_elo, updated_b_elo = update_elo(r_elo, b_elo, win_type)
        elif winner == 'Blue':
            updated_b_elo, updated_r_elo = update_elo(b_elo, r_elo, win_type)

        rows_list.append({
            'red fighter': r_fighter,
            'red fighter initial elo': initial_r_elo,
            'blue fighter': b_fighter,
            'blue fighter initial elo': initial_b_elo,
            'date': date,
            'winner': winner,
            'win_type': win_type,
            'red fighter new elo': updated_r_elo,
            'blue fighter new elo': updated_b_elo,
            'favorite': favorite
        })

        # Update the Elo scores in the dictionary with the new values
        elo_scores[r_fighter] = updated_r_elo
        elo_scores[b_fighter] = updated_b_elo

    # Create the DataFrame from the list of rows and reverse it to display the latest matches last
    new_df = pd.DataFrame(rows_list)
    new_df = new_df.iloc[::-1]
    new_df.to_csv(output_file, index=False)
    print(f'Elo scores calculated and saved to {output_file}')

input_file_path = '/Users/richie/Documents/git_hub/elo_project/ufc/cleaned_ufc_data_with_finish.csv' 
output_file_path = 'elo_scores_with_finish_multiplier_simple.csv'  

calculate_elo(input_file_path, output_file_path)
