import streamlit as st
import pandas as pd
import joblib
from team_features import home_team_features, away_team_features, all_teams

# Load the trained model
model = joblib.load('finalized_model.pkl')

# Streamlit App
st.title("Football Match Outcome Predictor")

# Sidebar for team selection
st.sidebar.header("Select Teams")
home_team = st.sidebar.selectbox("Home Team", all_teams)
away_team = st.sidebar.selectbox("Away Team", all_teams)

# Function to prepare the input data with one-hot encoding
def prepare_input_data(home_team, away_team):
    match_features = {}
    
    # Perform one-hot encoding for the home team
    for team in all_teams:
        match_features[f"home_{team}"] = 1 if home_team == team else 0
    
    # Perform one-hot encoding for the away team
    for team in all_teams:
        match_features[f"away_{team}"] = 1 if away_team == team else 0
    
    # Retrieve the home and away team features based on user input
    home_features = home_team_features.get(home_team, {})
    away_features = away_team_features.get(away_team, {})
    
    # Combine the one-hot encoded team features and the additional team features
    match_features.update(home_features)
    match_features.update(away_features)
    
    return pd.DataFrame([match_features])

# Predict Button
if st.button("Predict Match Outcome"):
    # Prepare the input data using the selected teams
    match_data = prepare_input_data(home_team, away_team)
    
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
