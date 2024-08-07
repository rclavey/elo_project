import pandas as pd
from datetime import datetime
from sklearn.metrics import accuracy_score, roc_curve, auc
import numpy as np
from tqdm import tqdm


'''
The best accuracy is: 67.5857843137255, with parameters: {'best decay rate': 0.9000000000000001, 
'best decay cap': -101, 'best sub': 1.7999999999999998, 'best ko': 1.7999999999999998, 
'best sdec': 1, 'best udec': 1.4, 'best dq': 1.0, 'best other': 1.0, 'best unknown': 1.0, 
'best k1': 301, 'best k2': 201, 'best k3': 1}

'''


def parse_date(date_str):
    if not isinstance(date_str, str):
        return date_str  # If it's already a datetime object, just return it as is
    
    for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError('No valid date format found for ' + str(date_str))


def dynamic_k_factor(total_fights, k1, k2, k3):
    if total_fights < 3:
        return k1
    elif total_fights < 5:
        return k2
    else:
        return k3

def update_elo(winner_elo, loser_elo, winner_fights, loser_fights, elo_decay_factor, win_type, sub, ko, sdec, udec, dq, other, unknown, k1, k2, k3):
    multiplier_dict = {
        'submission': sub,
        'knockout': ko,
        'decision': sdec,
        'unanimous decision': udec,
        'dq': dq,
        'other': other,
        'unknown': unknown
    }
    
    multiplier = multiplier_dict.get(win_type, 1.0)
    
    k_winner = dynamic_k_factor(winner_fights, k1, k2, k3) * multiplier
    k_loser = dynamic_k_factor(loser_fights, k1, k2, k3) * multiplier
    
    winner_elo -= elo_decay_factor
    loser_elo -= elo_decay_factor

    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))
    
    new_winner_elo = round(winner_elo + k_winner * (1 - expected_winner))
    new_loser_elo = round(loser_elo - k_loser * expected_loser)

    return new_winner_elo, new_loser_elo


def calculate_elo(df, decay_rate, decay_cap, sub, ko, sdec, udec, dq, other, unknown, k1, k2, k3):
    df['date'] = df['date'].apply(parse_date)
    df = df.sort_values(by='date')
    elo_scores = {}
    fight_counts = {}
    last_fight_dates = {}

    # Initialize ELO scores and fight counts for all fighters
    for fighter in pd.concat([df['R_fighter'], df['B_fighter']]).unique():
        elo_scores[fighter] = 1000  # Default ELO score
        fight_counts[fighter] = 0   # Default fight count

    for index, row in df.iterrows():
        r_fighter, b_fighter, date, winner, win_type = row['R_fighter'], row['B_fighter'], row['date'], row['Winner'], row['win_type']
        
        r_elo = elo_scores[r_fighter]
        b_elo = elo_scores[b_fighter]
        r_fights = fight_counts[r_fighter]
        b_fights = fight_counts[b_fighter]

        current_date = date
        r_inactive_days, b_inactive_days = 0, 0
        
        if r_fighter in last_fight_dates:
            r_inactive_days = (current_date - last_fight_dates[r_fighter]).days
        if b_fighter in last_fight_dates:
            b_inactive_days = (current_date - last_fight_dates[b_fighter]).days
        
        r_elo_decay = min(decay_rate * r_inactive_days, decay_cap)
        b_elo_decay = min(decay_rate * b_inactive_days, decay_cap)

        r_elo, b_elo = update_elo(r_elo, b_elo, r_fights, b_fights, r_elo_decay, win_type, k1, k2, k3, sub, ko, sdec, udec, dq, other, unknown)

        fight_counts[r_fighter] += 1
        fight_counts[b_fighter] += 1
        last_fight_dates[r_fighter] = current_date
        last_fight_dates[b_fighter] = current_date

        elo_scores[r_fighter] = r_elo
        elo_scores[b_fighter] = b_elo

    # Calculate 'elo_diff' and 'predicted_outcome' for each match
    df['elo_diff'] = df.apply(lambda row: elo_scores[row['R_fighter']] - elo_scores[row['B_fighter']], axis=1)
    df['predicted_outcome'] = df['elo_diff'].apply(lambda x: 'Red' if x > 0 else 'Blue')

    return df



def calculate_accuracy_by_elo_diff(df):
    if not df.empty:
        overall_accuracy = accuracy_score(df['Winner'], df['predicted_outcome']) * 100
    else:
        overall_accuracy = 0
    return overall_accuracy


input_file = '/Users/richie/Documents/git_hub/elo_project/ufc/cleaned_ufc_data_with_finish.csv'  
output_file = 'elo_scores_with_finish_multiplier_decay.csv'
best_accuracy = 0
best_parameters = {}
total_iterations = (
    len(np.arange(-0.2,1.0,0.1))* 
    len(np.arange(-101,301,50))*
    len(np.arange(1.0,2.0,0.2))* 
    len(np.arange(1.0,2.0,0.2))* 
    len(np.arange(1.0,2.0,0.5))*
    len(np.arange(301,601,50))* 
    len(np.arange(101,301,50))
)
# Load the DataFrame
df_initial = pd.read_csv(input_file)
df_initial['date'] = df_initial['date'].apply(parse_date)
df_initial = df_initial.sort_values(by='date')
print(total_iterations)
with tqdm(total=total_iterations) as pbar:
    for decay_rate in np.arange(-0.2,1.0,0.1):
        for decay_cap in np.arange(-101,301,50):
            for sub in np.arange(1.0,2.0,0.2):
                for udec in np.arange(1.0,2.0,0.2):
                        for other in np.arange(1.0,1.5,0.5):
                            for k1 in np.arange(301,601,50):
                                for k2 in np.arange(101,301,50):
                                    # Create a copy of the initial DataFrame for each iteration
                                    df_iter = df_initial.copy()
                                    updated_df = calculate_elo(df_iter, decay_rate, decay_cap, sub, sub, 1, udec, other, other, other, k1, k2, 1)
                                    # Calculate accuracy for the current parameter set
                                    accuracy = calculate_accuracy_by_elo_diff(updated_df)
                                    if accuracy >= best_accuracy:
                                        best_accuracy = accuracy
                                        best_parameters = {
                                            'best decay rate' : decay_rate,
                                            'best decay cap' : decay_cap,
                                            'best sub' : sub,
                                            'best ko' : sub,
                                            'best sdec' : 1,
                                            'best udec' : udec,
                                            'best dq' : other,
                                            'best other' : other,
                                            'best unknown' : other,
                                            'best k1' : k1,
                                            'best k2' : k2,
                                            'best k3' : 1 
                                        }
                                    pbar.update(1)
print(f'The best accuracy is: {best_accuracy}, with parameters: {best_parameters}.')
