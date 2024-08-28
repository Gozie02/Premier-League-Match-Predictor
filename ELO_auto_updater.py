from ELO_system_runner import run_elo_system
from Performance_Tracker import show_recent_performance
import pandas as pd
import logging
import os
import schedule
combined_df = pd.read_csv('ELO_df.csv')
final_elos, elo_trends = run_elo_system(combined_df)
performance_df = show_recent_performance(combined_df)
performance_columns_to_drop = ['Home_Team_Avg_Date_home_Last_7', 'Home_Team_Avg_Time_home_Last_7', 'Home_Team_Avg_Round_home_Last_7', 'Home_Team_Avg_Day_home_Last_7',
                           'Home_Team_Avg_Home_Team_home_Last_7', 'Home_Team_Avg_Away_Team_home_Last_7', 'Home_Team_Avg_Referee_home_Last_7', 'Away_Team_Avg_Date_away_Last_7',
                           'Away_Team_Avg_Time_away_Last_7', 'Away_Team_Avg_Day_away_Last_7', 'Away_Team_Avg_Home_Team_away_Last_7','Away_Team_Avg_Away_Team_away_Last_7']

performance_df.drop(columns=performance_columns_to_drop, inplace=True)
combined_with_performance = pd.merge(combined_df, performance_df, on='Match_ID', how='left')
combined_with_performance_renamed = combined_with_performance.rename(columns={'Date_home': 'Date', 'Round_home': 'Round','Season_home': 'Season'})
combined_with_performance_unique = combined_with_performance_renamed.drop_duplicates(subset=['Match_ID'])
final_elos_unique = final_elos.drop_duplicates(subset=['Match_ID'])
final_df = pd.merge(combined_with_performance_unique, final_elos_unique, on='Match_ID', how='left')
final_df = final_df.drop(columns=['Match_ID'])
final_columns_to_drop = ['Unnamed: 0', 'Home_Team_x', 'Away_Team_x', 'Home_Team_y', 'Away_Team_y', 'Date_away', 'Time_away', 'Day_away', 'Referee_away', 'Round_y', 'Season_y', 'Date_y',
                     'Referee_home']
final_df.drop(columns=final_columns_to_drop, inplace=True)
final_df = final_df.loc[:,~final_df.columns.duplicated()]
final_df = final_df.astype({'Home_Team_Elo_Before': 'float', 'Away_Team_Elo_Before': 'float'})
csv_file = 'final_df_organized.csv'
print(f"Saving data to {csv_file}...")
logging.info(f"Saving data to {csv_file}")
final_df.to_csv(csv_file, index=False)
print(f"Data saved to {csv_file}")
logging.info(f"Data saved to {csv_file}")

all_teams = pd.concat([final_df['Home_Team_home'], final_df['Away_Team_home']]).unique()
home_dummies = pd.get_dummies(final_df['Home_Team_home'], prefix='home', dtype='int')
away_dummies = pd.get_dummies(final_df['Away_Team_home'], prefix='away', dtype='int')
final_df1 = pd.concat([final_df, home_dummies, away_dummies], axis=1)

# Drop the original team columns
final_df1 = final_df1.drop(['Home_Team_home', 'Away_Team_home'], axis=1)
final_df_test = final_df1._get_numeric_data()
final_df_test = final_df_test.loc[:,~final_df_test.columns.duplicated()]
final_df_modeling = final_df_test.drop(['Outcome_encoded_away', 'GF_Home_away', 'GF_Away_away'], axis = 1)
final_df_features = final_df_test.drop(['Outcome_encoded_home', 'Outcome_encoded_away', 'GF_Home_away', 'GF_Away_away'], axis = 1)
print("Data preprocessing completed")
logging.info("Data preprocessing completed")


print(final_df_features.head())
    
# Save the preprocessed data with Outcome_encoded to a CSV file
csv_file_with_outcome = 'model_training.csv'
print(f"Saving data to {csv_file_with_outcome}...")
logging.info(f"Saving data to {csv_file_with_outcome}")
final_df_modeling.to_csv(csv_file_with_outcome, index=False)

print(f"Data saved to {csv_file_with_outcome}")
logging.info(f"Data saved to {csv_file_with_outcome}")
    
csv_file_without_outcome = 'final_df_features.csv'
print(f"Saving data to {csv_file_without_outcome}...")
logging.info(f"Saving data to {csv_file_without_outcome}")
final_df_features.to_csv(csv_file_without_outcome, index=False)
print(f"Data saved to {csv_file_without_outcome}")
logging.info(f"Data saved to {csv_file_without_outcome}")

def run_script():
    exec(open("ELO_auto_updater.py").read())

schedule.every().thursday.at("20:00").do(run_script)
