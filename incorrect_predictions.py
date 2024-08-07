import pandas as pd

def filter_incorrect_elo_predictions(csv_files, output_file):
    # Create an empty DataFrame for storing rows where ELO was not a good predictor
    incorrect_predictions = pd.DataFrame()
    
    for file in csv_files:
        # Load the CSV file
        df = pd.read_csv(file)
        
        # Filter rows where the higher initial ELO did not match the winner
        for index, row in df.iterrows():
            higher_elo_fighter = 'Red' if row['red fighter initial elo'] > row['blue fighter initial elo'] else 'Blue'
            if higher_elo_fighter != row['winner']:
                # Append the row to the incorrect_predictions DataFrame
                incorrect_predictions = incorrect_predictions._append(row)
    
    # Drop duplicate rows if processing multiple files with potential overlap
    incorrect_predictions.drop_duplicates(inplace=True)
    
    # Write the incorrect predictions to a new CSV file
    incorrect_predictions.to_csv(output_file, index=False)
    print(f"Filtered rows written to {output_file}")

# List of your CSV files
csv_files = [
    
    '/Users/richie/Documents/git_hub/elo_project/ufc/elo_scores_with_finish_multiplier_k.csv'
]

# Specify the path for the output CSV file
output_file = 'incorrect_elo_predictions.csv'

# Run the function
filter_incorrect_elo_predictions(csv_files, output_file)
