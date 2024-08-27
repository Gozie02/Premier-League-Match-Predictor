import streamlit as st
import pandas as pd
import joblib
from team_features import home_team_features, away_team_features
import sklearn
import os
from PIL import Image

# Load the trained model and the dataset
model = joblib.load('finalized_model2.pkl')
all_data = pd.read_csv('final_df_features.csv')

# Extract unique team names from the dataset
home_teams = [col.replace("home_", "") for col in all_data.columns if col.startswith("home_")]
away_teams = [col.replace("away_", "") for col in all_data.columns if col.startswith("away_")]
all_teams = sorted(set(home_teams + away_teams))

# Get the list of feature names used during training
model_feature_names = all_data.columns.tolist()

# Streamlit App
st.title("Football Match Outcome Predictor")

# Sidebar for team selection
st.sidebar.header("Select Teams")
home_team = st.sidebar.selectbox("Home Team", all_teams)
away_team = st.sidebar.selectbox("Away Team", all_teams)

def get_logo_path(team_name):
    return os.path.join("team_logos", f"{team_name}.png")

def resize_logo(logo_path, max_size):
    logo = Image.open(logo_path)
    logo.thumbnail(max_size)
    return logo

# Function to prepare the input data with one-hot encoding and additional features
def prepare_input_data(home_team, away_team):
    match_features = {}
    
    # Perform one-hot encoding for the home team
    for team in all_teams:
        match_features[f"home_{team}"] = 1 if home_team == team else 0
    
    # Perform one-hot encoding for the away team
    for team in all_teams:
        match_features[f"away_{team}"] = 1 if away_team == team else 0
    
    # Include additional features from home_team_features and away_team_features
    home_features = home_team_features.get(home_team, {})
    away_features = away_team_features.get(away_team, {})
    
    match_features.update(home_features)
    match_features.update(away_features)
    
    # Create the DataFrame with explicit column names
    column_names = list(match_features.keys())
    match_data = pd.DataFrame([match_features], columns=column_names)
    
    return match_data

max_size = (180, 180)

col1, col2, col3 = st.columns(3)

with col1:
    home_logo_path = get_logo_path(home_team)
    if os.path.exists(home_logo_path):
        home_logo = resize_logo(home_logo_path, max_size)
        st.image(home_logo, use_column_width=True)
    else:
        st.write(f"Logo not found for {home_team}")
    st.write(f"**{home_team}**")

with col2:
    st.write("##")
    st.write("##")
    st.write("**VS**")

with col3:
    away_logo_path = get_logo_path(away_team)
    if os.path.exists(away_logo_path):
        away_logo = resize_logo(away_logo_path, max_size)
        st.image(away_logo, use_column_width=True)
    else:
        st.write(f"Logo not found for {away_team}")
    st.write(f"**{away_team}**")
    
# Predict Button
if st.button("Predict Match Outcome"):
    # Prepare the input data using the selected teams
    match_data = prepare_input_data(home_team, away_team)
    
    # Remove columns that don't appear in the BaggingClassifier's training data
    match_data = match_data[match_data.columns.intersection(model_feature_names)]
    
    # Reorder the columns in match_data to match the order in model_feature_names
    match_data = match_data.reindex(columns=model_feature_names)
    
    # Make the prediction
    prediction = model.predict(match_data)
    
    # Interpret and display prediction
    if prediction[0] == 1:
        st.write(f"The model predicts that **{home_team}** will win against **{away_team}**.")
    elif prediction[0] == 2:
        st.write(f"The model predicts a **draw** between **{home_team}** and **{away_team}**.")
    elif prediction[0] == 0:
        st.write(f"The model predicts that **{away_team}** will win against **{home_team}**.")
else:
    st.write("Please select the home and away teams and click the 'Predict Match Outcome' button.")
