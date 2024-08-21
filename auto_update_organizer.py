import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import numpy as np
from ELO_system_runner import run_elo_system
from Performance_Tracker import show_recent_performance
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Starting update_premier_league_organizer_data.py script")
def fetch_organized_premier_league_data():
    logging.info("Starting Premier League data fetch")
    current_year = 2024  # Update this to the current Premier League season
    PL_History = "https://fbref.com/en/comps/9/Premier-League-Stats"
    matches = []

    seasons = requests.get(PL_History)
    soup = BeautifulSoup(seasons.text, 'html.parser')
    time.sleep(3)
    standings_table = soup.select('table.stats_table')[0]

    squad_links = [l.get('href') for l in standings_table.find_all('a')]
    squad_links = [l for l in squad_links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in squad_links]

    print("Fetching Premier League data...")
    logging.info("Fetching Premier League data")

    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")

        data = requests.get(team_url)

        if data.status_code != 200:
            print(f"Failed to retrieve data for {team_name} in {current_year}. Status code: {data.status_code}")
            continue
        team_matches = pd.read_html(data.text, match="Scores & Fixtures")

        if not team_matches:
            print(f"No 'Fixtures' table found for {team_name} in {current_year}")
            continue

        team_matches = team_matches[0]

        soup = BeautifulSoup(data.text, 'html.parser')
        time.sleep(3)
        links = [l.get("href") for l in soup.find_all('a')]

        def fetch_table(links, identifier, table_name):
            relevant_links = [l for l in links if l and identifier in l]
            if not relevant_links:
                return None
            data = requests.get(f"https://fbref.com{relevant_links[0]}")
            time.sleep(3)
            try:
                table = pd.read_html(data.text, match=table_name)[0]
                table.columns = table.columns.droplevel() if isinstance(table.columns, pd.MultiIndex) else table.columns
                return table
            except ValueError:
                return None

        shooting = fetch_table(links, "all_comps/shooting/", "Shooting")
        possession = fetch_table(links, "all_comps/possession", "Possession")
        passing = fetch_table(links, "all_comps/passing", "Passing")
        GCA = fetch_table(links, "all_comps/gca", "GCA")
        defense = fetch_table(links, "all_comps/defense", "Defensive Actions")
        misc = fetch_table(links, "all_comps/misc", "Miscellaneous Stats")

        try:
            team_data = team_matches
            if 'Date' not in team_data.columns:
                print(f"Skipping {team_name} in {current_year}: 'Date' column missing.")
                continue
            team_data['Date'] = team_data['Date'].astype(str)
            today = datetime.datetime.now().date()
            last_wednesday = today - datetime.timedelta(days=today.weekday() + 4)
            this_wednesday = last_wednesday + datetime.timedelta(days=7)
            team_data = team_data[(team_data['Date'] >= last_wednesday.strftime('%Y-%m-%d')) & (team_data['Date'] <= this_wednesday.strftime('%Y-%m-%d'))]
            if shooting is not None:
                shooting_columns = ["Date", "Sh", "SoT", "G/Sh", "G/SoT", "Dist", "PK", "PKatt", "xG", "npxG", "npxG/Sh"]
                shooting_columns = [col for col in shooting_columns if col in shooting.columns]
                team_data = team_data.merge(shooting[shooting_columns], on="Date", how="left")
            if possession is not None:
                possession_columns = ["Date", "Touches", "Def Pen", "Def 3rd", "Att 3rd", "Att Pen", "Att", "Succ%", "1/3", "CPA", "Mis", "Dis", "Rec", "PrgR"]
                possession_columns = [col for col in possession_columns if col in possession.columns]
                team_data = team_data.merge(possession[possession_columns], on="Date", how="left")
            if passing is not None:
                passing_columns = ["Date", "Cmp", "Att", "Cmp%", "TotDist", "PrgDist", "Cmp.1", "Att.1", "Cmp%.1", "Cmp.2", "Att.2", "Cmp%.2", "Cmp.3", "Att.3", "Cmp%.3", "Ast", "xAG", "xA", "KP", "1/3.1", "PPA", "CrsPA", "PrgP"]
                passing_columns = [col for col in passing_columns if col in passing.columns]
                team_data = team_data.merge(passing[passing_columns], on="Date", how="left")
            if GCA is not None:
                GCA_columns = ["Date", "SCA", "PassLive", "PassDead", "TO", "Sh", "Fld", "Def", "GCA", "PassLive.1", "PassDead.1", "TO.1", "Sh.1", "Fld.1", "Def.1"]
                GCA_columns = [col for col in GCA_columns if col in GCA.columns]
                team_data = team_data.merge(GCA[GCA_columns], on="Date", how="left")
            if defense is not None:
                defense_columns = ["Date", "Tkl", "TklW", "Def 3rd", "Mid 3rd", "Att 3rd", "Tkl.1", "Att", "Tkl%", "Lost", "Blocks", "Sh", "Pass", "Int", "Tkl+Int", "Clr", "Err"]
                defense_columns = [col for col in defense_columns if col in defense.columns]
                team_data = team_data.merge(defense[defense_columns], on="Date", how="left")
            if misc is not None:
                misc_columns = ["Date", "Recov", "Won", "Lost", "Won%"]
                misc_columns = [col for col in misc_columns if col in misc.columns]
                team_data = team_data.merge(misc[misc_columns], on="Date", how="left")

        except ValueError as e:
            print(f"Error merging data for {team_name} in {current_year}: {e}")
            continue

        team_data = team_data[team_data["Comp"] == "Premier League"]

        team_data["Season"] = current_year
        team_data["Team"] = team_name
        matches.append(team_data)
        time.sleep(3)

    for df in matches:
        if 'Date' in df.columns:
            duplicates = df[df.duplicated(subset='Date', keep=False)]
            if not duplicates.empty:
                print(f"Found duplicates in DataFrame for {df['Team'].iloc[0] if 'Team' in df.columns else 'Unknown Team'} in {df['Season'].iloc[0] if 'Season' in df.columns else 'Unknown Season'}:")
                print(duplicates)
        else:
            print(f"Warning: DataFrame for {df['Team'].iloc[0] if 'Team' in df.columns else 'Unknown Team'} in {df['Season'].iloc[0] if 'Season' in df.columns else 'Unknown Season'} does not have a 'Date' column.")

    all_matches_df = pd.concat(matches, ignore_index=True)
    all_matches_df = all_matches_df.drop_duplicates(subset=['Date', 'Team'], keep='first')
    print("Data fetched successfully")
    logging.info("Data fetched successfully")

    # Additional preprocessing steps
    print("Performing data preprocessing...")
    logging.info("Performing data preprocessing")
    outcome_mapping = {'W': 1, 'D': 2, 'L': 0}
    all_matches_df['Outcome_encoded'] = all_matches_df['Result'].map(outcome_mapping)
    PL_outcomes_cleaned = all_matches_df.drop(['Unnamed: 0','Captain', 'Match Report', 'Notes', 'Comp', 'Result'], axis = 1)
    Big_Six = ["Manchester City", "Arsenal", "Chelsea", "Liverpool", "Tottenham", "Manchester Utd"]
    PL_outcomes_cleaned['Against_Big_Six'] = np.where(PL_outcomes_cleaned['Opponent'].isin(Big_Six), 1, 0)
    PL_outcomes_cleaned.sort_values(by='Date', inplace=True)
    PL_outcomes_cleaned.reset_index(inplace=True, drop=True)
    PL_outcomes_cleaned['Home_Team'] = PL_outcomes_cleaned.apply(lambda row: row['Team'] if row['Venue'] == 'Home' else row['Opponent'], axis=1)
    PL_outcomes_cleaned['Away_Team'] = PL_outcomes_cleaned.apply(lambda row: row['Team'] if row['Venue'] == 'Away' else row['Opponent'], axis=1)
    PL_outcomes_cleaned['GF_Home'] = PL_outcomes_cleaned.apply(lambda row: row['GF'] if row['Venue'] == 'Home' else row['GA'], axis=1)
    PL_outcomes_cleaned['GF_Away'] = PL_outcomes_cleaned.apply(lambda row: row['GF'] if row['Venue'] == 'Away' else row['GA'], axis=1)
    PL_outcomes_cleaned.drop(columns=['GF', 'GA', 'Team', 'Opponent'], inplace=True)
    home_column = PL_outcomes_cleaned.pop('Home_Team')
    PL_outcomes_cleaned.insert(5, 'Home_Team', home_column)
    away_column = PL_outcomes_cleaned.pop('Away_Team')
    PL_outcomes_cleaned.insert(6, 'Away_Team', away_column)
    home_goals = PL_outcomes_cleaned.pop('GF_Home')
    PL_outcomes_cleaned.insert(7, 'GF_Home', home_goals)
    away_goals = PL_outcomes_cleaned.pop('GF_Away')
    PL_outcomes_cleaned.insert(8, 'GF_Away', away_goals)
    def standardize_team_name(team_name):
        return team_name_mapping.get(team_name, team_name)
# Mapping different representations of team names to a single standardized name
    team_name_mapping = {
      'Man City': 'Manchester City',
      'Manchester City': 'Manchester City',
      'Man United': 'Manchester United',
      'Man Utd': 'Manchester United',
      'Manchester Utd': 'Manchester United',
      'Manchester United': 'Manchester United',
      'Tottenham': 'Tottenham Hotspur',
      'Spurs': 'Tottenham Hotspur',
      'West Ham': 'West Ham United',
      'Leicester': 'Leicester City',
      'Brighton': 'Brighton & Hove Albion',
      'Wolves': 'Wolverhampton Wanderers',
      'Sheffield Utd': 'Sheffield United',
      "Nott'ham Forest": 'Nottingham Forest',
      'Brighton and Hove Albion': 'Brighton & Hove Albion',
      'Newcastle Utd': 'Newcastle United',
      'Newcastle United' : 'Newcastle United'
    }
    PL_outcomes_cleaned['Home_Team'] = PL_outcomes_cleaned['Home_Team'].apply(standardize_team_name)
    PL_outcomes_cleaned['Away_Team'] = PL_outcomes_cleaned['Away_Team'].apply(standardize_team_name)
    PL_outcomes_cleaned['Match_ID'] = PL_outcomes_cleaned.apply(lambda row: f"{row['Date']}_{min(row['Home_Team'], row['Away_Team'])}_{max(row['Home_Team'], row['Away_Team'])}", axis=1)
    home_df = PL_outcomes_cleaned[PL_outcomes_cleaned['Venue'] == 'Home']
    away_df = PL_outcomes_cleaned[PL_outcomes_cleaned['Venue'] == 'Away']
    home_df.drop(columns=['Venue'], inplace=True)
    home_df.sort_values(by='Date', inplace=True)
    home_df.reset_index(inplace=True, drop=True)
    away_df.drop(columns=['Venue'], inplace=True)
    away_df.sort_values(by='Date', inplace=True)
    away_df.reset_index(inplace=True, drop=True)
    combined_df = pd.merge(home_df, away_df, on='Match_ID', suffixes=('_home', '_away'), how = "outer")
    columns_to_drop1 = ['Attendance_home', 'Attendance_away', 'Round_away', 'Formation_home', 'Formation_away']
    combined_df.drop(columns=columns_to_drop1, inplace=True)
    combined_df['Round_home'] = combined_df['Round_home'].str.extract('(\d+)').astype(int)
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
    final_columns_to_drop = ['Home_Team_x', 'Away_Team_x', 'Home_Team_y', 'Away_Team_y', 'Date_away', 'Time_away', 'Day_away', 'Referee_away', 'Round_y', 'Season_y', 'Date_y',
                         'Referee_home']
    final_df.drop(columns=final_columns_to_drop, inplace=True)

    print("Data preprocessing completed")
    logging.info("Data preprocessing completed")
    print(final_df.head())
    csv_file = 'final_df_organized.csv'
    print(f"Saving data to {csv_file}...")
    logging.info(f"Saving data to {csv_file}")
    if os.path.isfile(csv_file):
        # If the file exists, read the existing data
        existing_data = pd.read_csv(csv_file)
        
        # Append the new data to the existing data
        updated_data = pd.concat([existing_data, final_df], ignore_index=True)
        
        # Save the updated data to the CSV file
        updated_data.to_csv(csv_file, index=False)
    else:
        # If the file doesn't exist, save the new data to the CSV file
        final_df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")
    logging.info(f"Data saved to {csv_file}")

    logging.info("Premier League data fetch completed")

# Schedule the task to run every Tuesday at 8:00 AM
schedule.every().wednesday.at("10:45").do(fetch_organized_premier_league_data)

while True:
    logging.info("Running pending scheduled tasks")
    schedule.run_pending()
    logging.info("Waiting for the next scheduled task")
    time.sleep(60)  # Check every minute if the scheduled task needs to run# Check every minute if the scheduled task needs to run
