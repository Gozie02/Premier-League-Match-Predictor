import pandas as pd
def calculate_recent_performance(team_stats, team, metrics, n=7):
    """
    Calculate the average performance of a given team over the last `n` games for specified metrics.

    Parameters:
    - team_stats: DataFrame containing match data.
    - team: The team for which to calculate performance.
    - metrics: List of columns to average (metrics to consider).
    - n: Number of recent games to consider.

    Returns:
    - Dictionary with average performance for each metric.
    """
    # Filter matches for the given team
    matches = team_stats[(team_stats['Home_Team_home'] == team) | (team_stats['Away_Team_home'] == team)]

    # Sort matches by date
    matches = matches.sort_values(by='Date_home', ascending=False)

    # Prepare dictionary to store average performance for each metric
    performance = {}

    for metric in metrics:
        # Check if the team is playing at home or away
        if team in matches['Home_Team_home'].values:
            recent_games = matches[matches['Home_Team_home'] == team].head(n)
            metric_values = recent_games[metric] if metric in recent_games.columns else pd.Series()
        else:
            recent_games = matches[matches['Away_Team_home'] == team].head(n)
            metric_values = recent_games[metric] if metric in recent_games.columns else pd.Series()

        # Calculate the average performance for the metric, excluding date, time and string columns
        if metric_values.dtype in [int, float]: # Check if the metric values are numeric
            performance[metric] = metric_values.mean() if not metric_values.empty else None

    return performance

# ... rest of the code remains the same ...

def show_recent_performance(team_stats):
    """
    Show the average performance of the last seven games for both teams in each match for multiple metrics.

    Parameters:
    - team_stats: DataFrame containing match data.

    Returns:
    - DataFrame with average performance of both teams in each match.
    """
    # Identify columns for home and away metrics
    home_metrics = [col for col in team_stats.columns if col.endswith('_home')]
    away_metrics = [col for col in team_stats.columns if col.endswith('_away')]

    # List to store results
    results = []

    # Loop through each match
    for _, match in team_stats.iterrows():
        home_team = match['Home_Team_home']
        away_team = match['Away_Team_home']

        # Calculate average performance for home team
        home_performance = calculate_recent_performance(team_stats, home_team, home_metrics)

        # Calculate average performance for away team
        away_performance = calculate_recent_performance(team_stats, away_team, away_metrics)

        # Append the results
        result = {
            'Date': match['Date_home'],
            'Round': match['Round_home'],
            'Home_Team': home_team,
            'Away_Team': away_team,
            'Match_ID': match['Match_ID']
        }

        # Add home team metrics to result
        result.update({f'Home_Team_Avg_{metric}_Last_7': home_performance.get(metric, None) for metric in home_metrics})

        # Add away team metrics to result
        result.update({f'Away_Team_Avg_{metric}_Last_7': away_performance.get(metric, None) for metric in away_metrics})

        results.append(result)

    # Convert results to DataFrame
    performance_df = pd.DataFrame(results)

    return performance_df
