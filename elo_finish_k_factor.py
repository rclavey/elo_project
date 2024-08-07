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
    # Adjusts K-factor based on the number of fights
    if total_fights < 3:
        return 401  # Drastic change for new fighters with less than 3 fights
    elif total_fights < 5:
        return 331  # More change for fighters with less than 5 fights
    else:
        return 200  # Standard Elo k-factor for fighters with 5 or more fights

def update_elo(winner_elo, loser_elo, winner_fights, loser_fights, win_type):
    # Multipliers for different win types
    multiplier_dict = {
        'submission': 1.2,
        'knockout': 1.2,
        'decision': 1.0,  
        'unanimous decision': 1.05,
        'dq': 0.95,
        'other': 1.0,
        'unknown': 1.0
    }
    
    # Get the dynamic K-factor based on the number of fights
    k_winner = dynamic_k_factor(winner_fights)
    k_loser = dynamic_k_factor(loser_fights)
    
    # Apply the multiplier based on the win type
    multiplier = multiplier_dict.get(win_type, 1.0)

    # Calculate the expected scores
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))
    
    # Update the Elo ratings
    new_winner_elo = round(winner_elo + k_winner * multiplier * (1 - expected_winner))
    new_loser_elo = round(loser_elo - k_loser * multiplier * (expected_loser))
    
    return new_winner_elo, new_loser_elo

def calculate_elo(input_file, output_file):
    df = pd.read_csv(input_file)
    # Sort DataFrame by date after parsing dates
    df['date'] = df['date'].apply(parse_date)
    df = df.sort_values(by='date')

    elo_scores = {}
    fight_counts = {}  # Track the number of fights for each fighter

    rows_list = []  # List to hold rows for the new DataFrame

    for index, row in df.iterrows():
        r_fighter, b_fighter, date, winner, win_type, favorite = row['R_fighter'], row['B_fighter'], row['date'], row['Winner'], row['win_type'], row['Favorite']

        # Initialize ELO scores and fight counts if not already present
        r_elo = elo_scores.get(r_fighter, 1000)
        b_elo = elo_scores.get(b_fighter, 1000)
        r_fights = fight_counts.get(r_fighter, 0)
        b_fights = fight_counts.get(b_fighter, 0)

        # Capture initial Elo scores
        initial_r_elo = r_elo
        initial_b_elo = b_elo

        if winner == 'Red':
            r_elo, b_elo = update_elo(r_elo, b_elo, r_fights, b_fights, win_type)
        elif winner == 'Blue':
            b_elo, r_elo = update_elo(b_elo, r_elo, b_fights, r_fights, win_type)

        # Update the fight counts
        fight_counts[r_fighter] = r_fights + 1
        fight_counts[b_fighter] = b_fights + 1

        # Append new row with updated information
        rows_list.append({
            'red fighter': r_fighter, 'red fighter initial elo': initial_r_elo,
            'blue fighter': b_fighter, 'blue fighter initial elo': initial_b_elo,
            'date': date, 'winner': winner, 'win_type': win_type,
            'red fighter new elo': r_elo, 'blue fighter new elo': b_elo,
            'favorite': favorite
        })

        # Update ELO scores in the dictionary
        elo_scores[r_fighter] = r_elo
        elo_scores[b_fighter] = b_elo

    # Create the DataFrame from the list of rows
    new_df = pd.DataFrame(rows_list)

    # Reverse the DataFrame to display the latest matches last
    new_df = new_df.iloc[::-1]

    # Save the DataFrame to a CSV file
    new_df.to_csv(output_file, index=False)
    print(f"Elo scores calculated and saved to {output_file}")

# Update these paths to match your file locations
input_file_path = '/Users/richie/Documents/git_hub/elo_project/ufc/cleaned_ufc_data_with_finish.csv'
output_file_path = 'elo_scores_with_finish_multiplier_k.csv'

calculate_elo(input_file_path, output_file_path)
