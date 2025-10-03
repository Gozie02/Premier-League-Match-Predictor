import streamlit as st
import pandas as pd
import joblib
import os
from PIL import Image
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import cloudscraper
from team_features import home_team_features, away_team_features
from goals_calculator import poisson_probs, derive_probabilities

# -----------------------------
# Load models and dataset
# -----------------------------
outcome_model = joblib.load('finalized_model2.pkl')
home_goals_model = joblib.load('home_goals_model.pkl')
away_goals_model = joblib.load('away_goals_model.pkl')

all_data = pd.read_csv('final_df_features.csv')

home_teams = [col.replace("home_", "") for col in all_data.columns if col.startswith("home_")]
away_teams = [col.replace("away_", "") for col in all_data.columns if col.startswith("away_")]
all_teams = sorted(set(home_teams + away_teams))

model_feature_names = all_data.columns.tolist()

# -----------------------------
# Utility functions
# -----------------------------
def get_logo_path(team_name):
    return os.path.join("team_logos", f"{team_name}.png")

def resize_logo(logo_path, size):
    logo = Image.open(logo_path)
    logo = logo.resize(size)
    return logo

def set_background_and_text_color(color1, color2, text_color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(to bottom, {color1}, {color2});
            color: {text_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def prepare_input_data(home_team, away_team):
    match_features = {}
    for team in all_teams:
        match_features[f"home_{team}"] = 1 if home_team == team else 0
    for team in all_teams:
        match_features[f"away_{team}"] = 1 if away_team == team else 0
    
    home_features = home_team_features.get(home_team, {})
    away_features = away_team_features.get(away_team, {})
    match_features.update(home_features)
    match_features.update(away_features)
    
    column_names = list(match_features.keys())
    match_data = pd.DataFrame([match_features], columns=column_names)
    return match_data

# -----------------------------
# Prediction logic
# -----------------------------
def predict_match(home_team, away_team):
    match_data = prepare_input_data(home_team, away_team)
    match_data = match_data[match_data.columns.intersection(model_feature_names)]
    match_data = match_data.reindex(columns=model_feature_names)

    prediction = outcome_model.predict(match_data)
    goals_df = match_data.drop(['GF_Home_home', 'GF_Away_home'], axis=1, errors="ignore")
    home_goals_pred = home_goals_model.predict(goals_df)[0]
    away_goals_pred = away_goals_model.predict(goals_df)[0]
    prob_dict = derive_probabilities(home_goals_pred, away_goals_pred)

    return prediction[0], home_goals_pred, away_goals_pred, prob_dict

# -----------------------------
# Fixture scraping
# -----------------------------
def get_upcoming_fixtures(league_url, days_ahead=7):
    scraper = cloudscraper.create_scraper(
    browser={'custom': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/127.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = scraper.get(league_url)
    soup = BeautifulSoup(r.text, "html.parser")

    fixtures_table = soup.find("table", id="sched_2025-2026_9_1")
    rows = fixtures_table.find("tbody").find_all("tr")

    fixtures = []
    today = datetime.today()

    for row in rows:
        date_cell = row.find("td", {"data-stat": "date"})
        date_str = date_cell.text.strip()
        if not date_str:  # skip separators
            continue
        try:
            # If it's already ISO-like: 2024-08-17
            match_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                # FBRef often uses: Sat Aug 17, 2024
                match_date = datetime.strptime(date_str, "%a %b %d, %Y")
            except ValueError:
                print(f"⚠️ Skipping unrecognized date format: {date_str}")
                continue
        if today <= match_date <= today + timedelta(days=days_ahead):
            home = row.find("td", {"data-stat": "home_team"}).text.strip()
            away = row.find("td", {"data-stat": "away_team"}).text.strip()
            score = row.find("td", {"data-stat": "score"})
            
            if not score or score.text.strip() == "":  # upcoming only
                fixtures.append((match_date.date(), home, away))
    return fixtures

# -----------------------------
# Streamlit UI
# -----------------------------
chromatic_color = "#6505a6"
dull_color = "#25023d"
text_color = "#e0d1ff"
set_background_and_text_color(chromatic_color, dull_color, text_color)

header_color = "#ff8c00"
st.markdown(f"<h1 style='color: {header_color};'>Football Match Outcome Predictor</h1>", unsafe_allow_html=True)
st.write("##")

logo_size = (120, 120)
col1, col2, col3 = st.columns([1, 0.5, 1])

with col1:
    home_team = st.selectbox("Select Home Team", sorted(all_teams))
    home_logo_path = get_logo_path(home_team)
    if os.path.exists(home_logo_path):
        st.image(resize_logo(home_logo_path, logo_size), use_container_width=True)

with col2:
    st.write("##")
    st.write("**VS**")
    st.write("##")

with col3:
    away_team = st.selectbox("Select Away Team", sorted(all_teams))
    away_logo_path = get_logo_path(away_team)
    if os.path.exists(away_logo_path):
        st.image(resize_logo(away_logo_path, logo_size), use_container_width=True)

st.write("##")

if st.button("Predict Match Outcome"):
    prediction, home_goals_pred, away_goals_pred, prob_dict = predict_match(home_team, away_team)

    if prediction == 1:
        st.write(f"Nostradamus predicts that <span style='color: #00ff00;'>{home_team}</span> will win against <span style='color: red;'>{away_team}</span>.", unsafe_allow_html=True)
    elif prediction == 2:
        st.write(f"Nostradamus predicts a <span style='color: grey;'>draw</span> between {home_team} and {away_team}.", unsafe_allow_html=True)
    else:
        st.write(f"Nostradamus predicts that <span style='color: #00ff00;'>{away_team}</span> will win against <span style='color: red;'>{home_team}</span>.", unsafe_allow_html=True)

    st.subheader("Goals Expectation")
    st.write(f"{home_team}: {home_goals_pred:.2f} | {away_team}: {away_goals_pred:.2f}")

    st.subheader("Outcome Probabilities (from Poisson)")
    st.write(f"🏠 {home_team} Win: {prob_dict['p_home_win']:.2%}")
    st.write(f"🤝 Draw: {prob_dict['p_draw']:.2%}")
    st.write(f"🛫 {away_team} Win: {prob_dict['p_away_win']:.2%}")

    st.subheader("Over/Under Probabilities")
    st.write(f"Over 1.5: {prob_dict['over_1.5']:.2%} | Under 1.5: {prob_dict['under_1.5']:.2%}")
    st.write(f"Over 2.5: {prob_dict['over_2.5']:.2%} | Under 2.5: {prob_dict['under_2.5']:.2%}")
    st.write(f"Over 3.5: {prob_dict['over_3.5']:.2%} | Under 3.5: {prob_dict['under_3.5']:.2%}")

# -----------------------------
# Automated batch predictions (only runs outside Streamlit)
# -----------------------------
if __name__ == "__main__":
    fixtures = get_upcoming_fixtures(
        "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures",
        days_ahead=7
    )
    results = []
    for date, home, away in fixtures:
        prediction, hg, ag, probs = predict_match(home, away)
        results.append({
            "date": date,
            "home": home,
            "away": away,
            "prediction": prediction,
            "home_goals": hg,
            "away_goals": ag,
            **probs
        })
    pd.DataFrame(results).to_csv("upcoming_predictions.csv", index=False)
    print("Saved upcoming predictions to upcoming_predictions.csv")
