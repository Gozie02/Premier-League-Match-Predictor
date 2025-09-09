import time
import requests
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import numpy as np
import logging
import lxml
import datetime
import html5lib
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Starting update_premier_league_data.py script")
logging.info("Starting Premier League data fetch")
today = datetime.date.today()
offset = (today.weekday() - 1) % 7
last_tuesday = today - datetime.timedelta(days=offset)

if today.weekday() == 1:  # If today is a Wednesday
    last_tuesday -= datetime.timedelta(days=7)
this_tuesday = last_tuesday + datetime.timedelta(days=7)  # Upcoming Wednesday
# Convert to string format (YYYY-MM-DD) for comparison
last_tuesday_str = last_tuesday.strftime('%Y-%m-%d')
this_tuesday_str = this_tuesday.strftime('%Y-%m-%d')
current_year = 2025  # Update this to the current Premier League season
PL_History = "https://fbref.com/en/comps/9/Premier-League-Stats"
matches = []

scraper = cloudscraper.create_scraper(
    browser={'custom': 'chrome', 'platform': 'windows', 'desktop': True}
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
seasons = scraper.get(PL_History, headers=headers)
soup = BeautifulSoup(seasons.text, 'html.parser')
time.sleep(3)
standings_table = soup.select('table.stats_table')[0]

squad_links = [l.get('href') for l in standings_table.find_all('a')]
squad_links = [l for l in squad_links if '/squads/' in l]
team_urls = [f"https://fbref.com{l}" for l in squad_links]

print("Fetching Premier League data...")
logging.info("Fetching Premier League data")

try:
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
    all_matches_df['Date'] = all_matches_df['Date'].astype(str)
    all_matches_df = all_matches_df[(all_matches_df['Date'] >= last_tuesday_str) & (all_matches_df['Date'] < this_tuesday_str)]
    def rename_duplicate_columns(df):
        columns = df.columns.tolist()
        column_counts = {}
        for i, col in enumerate(columns):
            if col in column_counts:
                column_counts[col] += 1
                new_col_name = f"{col}.{column_counts[col]}"
                columns[i] = new_col_name
            else:
                column_counts[col] = 0  # First occurrence, no suffix needed
        df.columns = columns
        return df
    all_matches_df = rename_duplicate_columns(all_matches_df)
    print("Data fetched successfully")
    logging.info("Data fetched successfully")
    
    # Additional preprocessing steps
    print("Performing data preprocessing...")
    logging.info("Performing data preprocessing")
    outcome_mapping = {'W': 1, 'D': 2, 'L': 0}
    all_matches_df['Outcome_encoded'] = all_matches_df['Result'].map(outcome_mapping)
    PL_outcomes_cleaned = all_matches_df.drop(['Captain', 'Match Report', 'Notes', 'Comp', 'Result', 'Opp Formation'], axis = 1)
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
    combined_df = combined_df.dropna()
    combined_df = combined_df.astype({'GF_Home_home': 'int', 'GF_Away_home': 'int', 'GF_Home_away': 'int', 'GF_Away_away': 'int'})
    columns_to_drop1 = ['Attendance_home', 'Attendance_away', 'Round_away', 'Formation_home', 'Formation_away']
    combined_df.drop(columns=columns_to_drop1, inplace=True)
    combined_df['Round_home'] = combined_df['Round_home'].str.extract(r'(\d+)').astype(int)
    combined_csv_file = 'ELO_df.csv'
    print(f"Saving data to {combined_csv_file}...")
    logging.info(f"Saving data to {combined_csv_file}")

    if os.path.isfile(combined_csv_file):
        print(f"{combined_csv_file} already exists. Appending new data...")
        logging.info(f"{combined_csv_file} already exists. Appending new data.")
        
        # Read the existing data from the CSV file
        existing_data = pd.read_csv(combined_csv_file)
        
        # Append the new data to the existing data
        updated_data = pd.concat([existing_data, combined_df], ignore_index=True)
        
        # Save the updated data back to the CSV file
        updated_data.to_csv(combined_csv_file, index=False, mode='w', header=True)
    else:
        # If the file doesn't exist, create a new file and save the data
        combined_df.to_csv(combined_csv_file, index=False)
    
    print(f"Data saved to {combined_csv_file}")
    logging.info(f"Data saved to {combined_csv_file}")

except Exception as e:
    logging.error(f"Failed to fetch Premier League data: {e}")

logging.info("Premier League data fetch completed")

def run_script():
    exec(open("auto_update_match_df.py").read())

schedule.every().tuesday.at("09:30").do(run_script)

