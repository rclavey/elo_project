import pandas as pd

def process_ufc_data(input_file, output_file):
    try:
        # Load the data
        df = pd.read_csv(input_file)

        # Select the desired columns and add a column for the betting favorite, and make a copy to avoid SettingWithCopyWarning
        selected_columns = df[['R_fighter', 'B_fighter', 'date', 'Winner', 'R_odds', 'B_odds', 'finish', 'finish_details']].copy()

        # Function to determine the win type based on the 'finish' column
        def determine_win_type(row):
            if row['finish'] == 'SUB':
                return 'submission'
            elif row['finish'] == 'KO/TKO':
                return 'knockout'
            elif row['finish'] in ['S-DEC', 'M-DEC']:  
                return 'split'
            elif row['finish'] == 'U-DEC':
                return 'unanimous'
            elif row['finish'] == 'DQ':
                return 'dq'
            elif pd.isna(row['finish']):
                return 'unknown'  # For NaN values
            else:
                return 'other'  # Covers 'Overturned' and any other cases not explicitly handled

        # Apply the function to each row to determine win type
        selected_columns['win_type'] = selected_columns.apply(determine_win_type, axis=1)

        # Determine the betting favorite
        def determine_favorite(row):
            if row['R_odds'] < row['B_odds']:
                return 'Red'
            elif row['R_odds'] > row['B_odds']:
                return 'Blue'
            else:  # Handle potential edge case where odds are equal or not available
                return 'Even'

        # Apply the function to each row to determine the favorite
        selected_columns['Favorite'] = selected_columns.apply(determine_favorite, axis=1)

        # Drop the odds and finish columns as they are no longer needed
        final_df = selected_columns.drop(columns=['R_odds', 'B_odds', 'finish', 'finish_details'])

        # Reorder columns to place 'win_type' before 'Favorite'
        final_df = final_df[['R_fighter', 'B_fighter', 'date', 'Winner', 'win_type', 'Favorite']]

        # Reverse the DataFrame
        reversed_df = final_df.iloc[::-1]

        # Save the new DataFrame to a new CSV file
        reversed_df.to_csv(output_file, index=False)
        print(f"File saved successfully as {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Set the path to your input file
    input_file_path = '/Users/richie/Documents/git_hub/elo_project/ufc/ufc-master.csv'  # Update this path to your actual file location

    # Set the path to your output file
    output_file_path = 'cleaned_ufc_data_with_finish.csv'  # Update this path to your desired output location

    # Call the function with the file paths
    process_ufc_data(input_file_path, output_file_path)
