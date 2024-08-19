import streamlit as st
import pandas as pd
import joblib
from team_features import home_team_features, away_team_features

# Load the trained model and the dataset
model = joblib.load('finalized_model.pkl')
all_data = pd.read_csv('final_df_features.csv')

# Streamlit App
st.title("Football Match Outcome Predictor")

# Sidebar for team selection
st.sidebar.header("Select Teams")
home_team = st.sidebar.selectbox("Home Team", [col.replace("home_", "") for col in all_data.columns if col.startswith("home_")])
away_team = st.sidebar.selectbox("Away Team", [col.replace("away_", "") for col in all_data.columns if col.startswith("away_")])

# Function to extract and prepare the input data
def get_team_features(team):
    home_features = home_team_features.get(team, {})
    away_features = away_team_features.get(team, {})
    
    # Merge the feature values from both dictionaries
    team_features = {}
    for feature in home_features.keys() | away_features.keys():
        home_value = home_features.get(feature, 0)
        away_value = away_features.get(feature, 0)
        team_features[feature] = (home_value + away_value) / 2
    
    return team_features

# Predict Button
if st.button("Predict Match Outcome"):
    # Prepare the input data using the selected teams
    # Retrieve combined feature values for the inputted teams
        home_features = get_team_features(home_team)
        away_features = get_team_features(away_team)
        
        # Combine the feature values of both teams
        match_features = {**home_features, **away_features}
        prediction = model.predict(match_features)
        # Interpret and display prediction
        if prediction == 1:
            st.write(f"The model predicts that **{home_team}** will win against **{away_team}**.")
        elif prediction == 2:
            st.write(f"The model predicts a **draw** between **{home_team}** and **{away_team}**.")
        elif prediction == 0:
            st.write(f"The model predicts that **{away_team}** will win against **{home_team}**.")
else:
  st.write("No data available for the selected teams.")
