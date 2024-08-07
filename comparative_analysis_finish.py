import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, roc_curve, auc
import numpy as np

def calculate_accuracy_by_elo_diff(df):
    elo_diff_categories = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 250), (250, 300), (300, 350), (350, 400), (400, 450), (450, 500)]
    accuracies = []

    for lower_bound, upper_bound in elo_diff_categories:
        filtered_df = df[abs(df['elo_diff']).between(lower_bound, upper_bound)]
        if not filtered_df.empty:
            accuracy = accuracy_score(filtered_df['winner'], filtered_df['predicted_outcome']) * 100
        else:
            accuracy = 0  # Changed from None to 0 for plotting
        accuracies.append(accuracy)

    return accuracies

def prepare_data_for_plots(csv_file):
    df = pd.read_csv(csv_file)
    if 'elo_diff' not in df.columns:
        df['elo_diff'] = df['red fighter initial elo'] - df['blue fighter initial elo']
    df['predicted_outcome'] = df['elo_diff'].apply(lambda diff: 'Red' if diff >= 0 else 'Blue')
    df['winner_numeric'] = df['winner'].apply(lambda x: 1 if x == 'Red' else 0)
    df['pred_prob_red'] = df['elo_diff'].apply(lambda x: 1 if x >= 0 else 0)
    
    return df

def plot_combined_roc(csv_files):
    plt.figure(figsize=(8, 6))
    for csv_file in csv_files:
        df = prepare_data_for_plots(csv_file)
        model_name = csv_file.split('/')[-1].replace('.csv', '')
        true_values = df['winner_numeric'].values
        predicted_probs = df['pred_prob_red'].values
        fpr, tpr, _ = roc_curve(true_values, predicted_probs)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.2f})')

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Combined ROC Curves')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig('combined_roc_curves.png')
    plt.close()

def plot_combined_accuracy(csv_files):
    category_labels = ['0-50', '50-100', '100-150', '150-200', '200-250', '250-300', '300-350', '350-400', '400-450', '450-500']
    x = np.arange(len(category_labels))  # the label locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots(figsize=(14, 8))
    for i, csv_file in enumerate(csv_files):
        df = prepare_data_for_plots(csv_file)
        accuracies = calculate_accuracy_by_elo_diff(df)
        model_name = csv_file.split('/')[-1].replace('.csv', '')
        rects = ax.bar(x + width*i, accuracies, width, label=model_name)

    ax.set_xlabel('Elo Difference Categories')
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('Accuracy by Elo Difference Across Models')
    ax.set_xticks(x + width / len(csv_files))
    ax.set_xticklabels(category_labels)
    ax.legend()
    ax.axhline(50, color='gray', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('combined_accuracy_bars.png')
    plt.close()

csv_files = [
    '/Users/richie/Documents/git_hub/elo_project/ufc/elo_scores_with_finish_multiplier_decay.csv',
    '/Users/richie/Documents/git_hub/elo_project/ufc/elo_scores_with_finish_multiplier_k.csv',
    '/Users/richie/Documents/git_hub/elo_project/ufc/elo_scores_with_finish_multiplier_simple.csv'
]

plot_combined_roc(csv_files)
plot_combined_accuracy(csv_files)
