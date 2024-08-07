import pandas as pd

def filter_predictions(csv_files, correct_elo_wrong_odds_file, correct_odds_wrong_elo_file):
    # DataFrames to store the specific instances
    correct_elo_wrong_odds = pd.DataFrame()
    correct_odds_wrong_elo = pd.DataFrame()
    
    for file in csv_files:
        # Load the CSV file
        df = pd.read_csv(file)
        
        # Iterate through each row to determine correctness of predictions
        for index, row in df.iterrows():
            if row['red fighter initial elo'] != 1000 and row['blue fighter initial elo'] != 1000:
                higher_elo_winner = 'Red' if row['red fighter initial elo'] > row['blue fighter initial elo'] else 'Blue'
                betting_favorite_winner = row['favorite']
                actual_winner = row['winner']
                
                # Check if ELO prediction was correct and betting odds were wrong
                if higher_elo_winner == actual_winner and betting_favorite_winner != actual_winner:
                    correct_elo_wrong_odds = correct_elo_wrong_odds._append(row)
                
                # Check if betting odds prediction was correct and ELO was wrong
                if betting_favorite_winner == actual_winner and higher_elo_winner != actual_winner:
                    correct_odds_wrong_elo = correct_odds_wrong_elo._append(row)
    
    # Write the instances to separate CSV files
    correct_elo_wrong_odds.drop_duplicates(inplace=True)
    correct_elo_wrong_odds.to_csv(correct_elo_wrong_odds_file, index=False)
    
    correct_odds_wrong_elo.drop_duplicates(inplace=True)
    correct_odds_wrong_elo.to_csv(correct_odds_wrong_elo_file, index=False)
    
    print(f"Instances where ELO was correct and betting odds were wrong written to {correct_elo_wrong_odds_file}")
    print(f"Instances where betting odds were correct and ELO was wrong written to {correct_odds_wrong_elo_file}")

# List of your CSV files
csv_files = [
    '/Users/richie/Documents/git_hub/elo_project/ufc/elo_scores_with_finish_multiplier_decay.csv',
    '/Users/richie/Documents/git_hub/elo_project/ufc/elo_scores_with_finish_multiplier_k.csv',
    '/Users/richie/Documents/git_hub/elo_project/ufc/elo_scores_with_finish_multiplier_simple.csv'
]

# Specify the paths for the output CSV files
correct_elo_wrong_odds_file = 'correct_elo_wrong_odds.csv'
correct_odds_wrong_elo_file = 'correct_odds_wrong_elo.csv'

# Execute the function
filter_predictions(csv_files, correct_elo_wrong_odds_file, correct_odds_wrong_elo_file)
