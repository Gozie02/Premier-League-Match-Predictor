import pandas as pd
import numpy as np
import math

# Function to calculate win probabilities
def win_probs(home_elo, away_elo, home_court_advantage=50):
    home_elo_rating = math.pow(10, home_elo / 400)
    away_elo_rating = math.pow(10, away_elo / 400)
    home_advantage_factor = math.pow(10, home_court_advantage / 400)
    denom = away_elo_rating + home_advantage_factor * home_elo_rating
    home_prob = home_advantage_factor * home_elo_rating / denom
    away_prob = away_elo_rating / denom
    return home_prob, away_prob

# Function to calculate K-factor
def elo_k(MOV, elo_diff):
    k = 30
    if elo_diff == 0:
        multiplier = 1
    else:
        if MOV > 0:
            multiplier = (MOV + 3) ** 0.8 / (7.5 + 0.006 * abs(elo_diff))
        else:
            multiplier = (-MOV + 3) ** 0.8 / (7.5 + 0.006 * abs(elo_diff))
    return k * multiplier

# Function to update ELO ratings
def update_elo(home_score, away_score, home_elo, away_elo, home_court_advantage=50):
    home_prob, away_prob = win_probs(home_elo, away_elo, home_court_advantage)
    result = 1 if home_score > away_score else 0 if home_score < away_score else 0.5
    MOV = home_score - away_score
    k = elo_k(MOV, home_elo - away_elo)
    k = min(max(k, 10), 30)
    updated_home_elo = home_elo + k * (result - home_prob)
    updated_away_elo = away_elo + k * ((1 - result) - away_prob)

    return updated_home_elo, updated_away_elo


def initialize_season_elo(elo_df, teams, initial_elo, season):
    last_season = season - 1

    # Get the ELOs at the end of the last season
    last_season_elo = elo_df[elo_df['Season'] == last_season]
    last_season_final_round = last_season_elo['Round'].max()
    final_elo_last_season = last_season_elo[last_season_elo['Round'] == last_season_final_round]

    # Get final ELO values for both home and away teams
    home_team_final_elo = final_elo_last_season[['Home_Team', 'Home_Team_Elo_After']]
    away_team_final_elo = final_elo_last_season[['Away_Team', 'Away_Team_Elo_After']]

    # Combine home and away ELOs into one DataFrame
    combined_final_elo = pd.concat([home_team_final_elo.rename(columns={'Home_Team': 'Team', 'Home_Team_Elo_After': 'Elo'}),
                                    away_team_final_elo.rename(columns={'Away_Team': 'Team', 'Away_Team_Elo_After': 'Elo'})])

    # Calculate the 4th and 5th worst ELO values if there are at least 5 teams
    if len(combined_final_elo) >= 5:
        sorted_elos = combined_final_elo.sort_values(by='Elo')
        fourth_worst_elo = sorted_elos.iloc[3]['Elo']
        fifth_worst_elo = sorted_elos.iloc[4]['Elo']
        average_elo = (fourth_worst_elo + fifth_worst_elo) / 2
    else:
        average_elo = combined_final_elo['Elo'].mean()

    # Initialize new season ELOs
    new_season_elo = {}

    for team in teams:
        if team in combined_final_elo['Team'].values:
            # Carry over the last season's ELO
            team_elo = combined_final_elo[combined_final_elo['Team'] == team]['Elo'].values
            new_season_elo[team] = team_elo[0] if team_elo.size > 0 else average_elo
        else:
            # Assign average ELO based on 4th and 5th worst or default to initial ELO
            new_season_elo[team] = average_elo

    return new_season_elo

# Main function to run ELO system
def run_elo_system(team_stats):
    # Initialize ELO ratings
    team_stats = team_stats.sort_values(by=['Season_home', 'Round_home'])
    initial_elo = {team: 1500 for team in pd.unique(team_stats[['Home_Team_home', 'Away_Team_home']].values.ravel())}
    elo_df = pd.DataFrame(columns=['Round', 'Home_Team', 'Away_Team', 'Home_Team_Elo_Before',
                                   'Away_Team_Elo_Before', 'Home_Team_Elo_After', 'Away_Team_Elo_After',
                                   'Season'])
    trends_df = pd.DataFrame(columns=['Round', 'Team', 'Elo', 'Date', 'Where_Played', 'Season'])

    # Initialize ELO for each team
    current_elo = pd.Series(initial_elo)

    # Loop through each season and matchweek
    for season in sorted(team_stats['Season_home'].unique()):
        print(f"Processing Season: {season}")
        home_teams = team_stats['Home_Team_home'].unique()
        away_teams = team_stats['Away_Team_home'].unique()
        teams = pd.unique(np.concatenate((home_teams, away_teams)))

        # Initialize ELO for the new season
        new_season_elo = initialize_season_elo(elo_df, teams, initial_elo, season)
        current_elo.update(new_season_elo)

        for matchweek in sorted(team_stats[team_stats['Season_home'] == season]['Round_home'].unique()):
            print(f"  Processing Matchweek: {matchweek}")
            current_week_matches = team_stats[(team_stats['Season_home'] == season) & (team_stats['Round_home'] == matchweek)]

            for _, match in current_week_matches.iterrows():
                home_team = match['Home_Team_home']
                away_team = match['Away_Team_home']
                home_score = match['GF_Home_home']
                away_score = match['GF_Away_home']
                game_date = match['Date_home']

                home_elo_before = current_elo[home_team]
                away_elo_before = current_elo[away_team]

                home_elo_after, away_elo_after = update_elo(home_score, away_score, home_elo_before, away_elo_before)

                current_elo[home_team] = home_elo_after
                current_elo[away_team] = away_elo_after

                # Store results
                elo_df = pd.concat([elo_df, pd.DataFrame([{
                    'Date': game_date,
                    'Round': match['Round_home'],
                    'Home_Team': home_team,
                    'Away_Team': away_team,
                    'Home_Team_Elo_Before': home_elo_before,
                    'Away_Team_Elo_Before': away_elo_before,
                    'Home_Team_Elo_After': home_elo_after,
                    'Away_Team_Elo_After': away_elo_after,
                    'Season': season,
                    'Match_ID': match['Match_ID']
                }])], ignore_index=True)

                trends_df = pd.concat([trends_df, pd.DataFrame([{
                    'Round': match['Round_home'],
                    'Team': home_team,
                    'Elo': home_elo_before,
                    'Date': game_date,
                    'Where_Played': 'Home',
                    'Season': season,
                    'Match_ID': match['Match_ID']
                }, {
                    'Round': match['Round_home'],
                    'Team': away_team,
                    'Elo': away_elo_before,
                    'Date': game_date,
                    'Where_Played': 'Away',
                    'Season': season,
                    'Match_ID': match['Match_ID']
                }])], ignore_index=True)

    return elo_df, trends_df
