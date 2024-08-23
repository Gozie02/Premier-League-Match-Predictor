##Final DF Grouping
import pandas as pd
final_df12 = pd.read_csv('final_df_organized.csv')
final_df12 = final_df12.drop(['GF_Home_away', 'Outcome_encoded_away', 'GF_Away_away'], axis = 1)
# Group the data by home team and aggregate the features
last_value_columns = ['Round_x', 'Home_Team_Avg_GF_Home_home_Last_7', 'Home_Team_Avg_GF_Away_home_Last_7',
 'Home_Team_Avg_xG_x_home_Last_7', 'Home_Team_Avg_xGA_home_Last_7',
 'Home_Team_Avg_Poss_home_Last_7', 'Home_Team_Avg_Sh_x_home_Last_7',
 'Home_Team_Avg_SoT_home_Last_7', 'Home_Team_Avg_G/Sh_home_Last_7',
 'Home_Team_Avg_G/SoT_home_Last_7', 'Home_Team_Avg_Dist_home_Last_7',
 'Home_Team_Avg_PK_home_Last_7', 'Home_Team_Avg_PKatt_home_Last_7',
 'Home_Team_Avg_xG_y_home_Last_7', 'Home_Team_Avg_npxG_home_Last_7',
 'Home_Team_Avg_npxG/Sh_home_Last_7', 'Home_Team_Avg_Touches_home_Last_7',
 'Home_Team_Avg_Def Pen_home_Last_7', 'Home_Team_Avg_Def 3rd_x_home_Last_7',
 'Home_Team_Avg_Att 3rd_x_home_Last_7', 'Home_Team_Avg_Att Pen_home_Last_7',
 'Home_Team_Avg_Att_x_home_Last_7', 'Home_Team_Avg_Succ%_home_Last_7',
 'Home_Team_Avg_1/3_home_Last_7', 'Home_Team_Avg_CPA_home_Last_7',
 'Home_Team_Avg_Mis_home_Last_7', 'Home_Team_Avg_Dis_home_Last_7',
 'Home_Team_Avg_Rec_home_Last_7', 'Home_Team_Avg_PrgR_home_Last_7',
 'Home_Team_Avg_Cmp_home_Last_7', 'Home_Team_Avg_Cmp.1_home_Last_7',
 'Home_Team_Avg_Cmp.2_home_Last_7', 'Home_Team_Avg_Cmp.3_home_Last_7',
 'Home_Team_Avg_Att_y_home_Last_7', 'Home_Team_Avg_Att_y.1_home_Last_7',
 'Home_Team_Avg_Att_y.2_home_Last_7', 'Home_Team_Avg_Att_y.3_home_Last_7',
 'Home_Team_Avg_Cmp%_home_Last_7', 'Home_Team_Avg_Cmp%.1_home_Last_7',
 'Home_Team_Avg_Cmp%.2_home_Last_7', 'Home_Team_Avg_Cmp%.3_home_Last_7',
 'Home_Team_Avg_TotDist_home_Last_7', 'Home_Team_Avg_PrgDist_home_Last_7',
 'Home_Team_Avg_Ast_home_Last_7', 'Home_Team_Avg_xAG_home_Last_7',
 'Home_Team_Avg_xA_home_Last_7', 'Home_Team_Avg_KP_home_Last_7',
 'Home_Team_Avg_PPA_home_Last_7', 'Home_Team_Avg_CrsPA_home_Last_7',
 'Home_Team_Avg_PrgP_home_Last_7', 'Home_Team_Avg_SCA_home_Last_7',
 'Home_Team_Avg_PassLive_home_Last_7',
 'Home_Team_Avg_PassLive.1_home_Last_7',
 'Home_Team_Avg_PassDead_home_Last_7',
 'Home_Team_Avg_PassDead.1_home_Last_7', 'Home_Team_Avg_TO_home_Last_7',
 'Home_Team_Avg_TO.1_home_Last_7', 'Home_Team_Avg_Sh_y_home_Last_7',
 'Home_Team_Avg_Sh_y.1_home_Last_7', 'Home_Team_Avg_Fld_home_Last_7',
 'Home_Team_Avg_Fld.1_home_Last_7', 'Home_Team_Avg_Def_home_Last_7',
 'Home_Team_Avg_Def.1_home_Last_7', 'Home_Team_Avg_GCA_home_Last_7',
 'Home_Team_Avg_Tkl_home_Last_7', 'Home_Team_Avg_Tkl.1_home_Last_7',
 'Home_Team_Avg_TklW_home_Last_7', 'Home_Team_Avg_Def 3rd_y_home_Last_7',
 'Home_Team_Avg_Mid 3rd_home_Last_7', 'Home_Team_Avg_Att 3rd_y_home_Last_7',
 'Home_Team_Avg_Att_home_Last_7', 'Home_Team_Avg_Tkl%_home_Last_7',
 'Home_Team_Avg_Lost_x_home_Last_7', 'Home_Team_Avg_Blocks_home_Last_7',
 'Home_Team_Avg_Sh_home_Last_7', 'Home_Team_Avg_Pass_home_Last_7',
 'Home_Team_Avg_Int_home_Last_7', 'Home_Team_Avg_Tkl+Int_home_Last_7',
 'Home_Team_Avg_Clr_home_Last_7', 'Home_Team_Avg_Err_home_Last_7',
 'Home_Team_Avg_Recov_home_Last_7', 'Home_Team_Avg_Won_home_Last_7',
 'Home_Team_Avg_Lost_y_home_Last_7', 'Home_Team_Avg_Won%_home_Last_7',
 'Home_Team_Avg_Season_home_Last_7',
 'Home_Team_Avg_Outcome_encoded_home_Last_7',
 'Home_Team_Avg_Against_Big_Six_home_Last_7',
 'Away_Team_Avg_GF_Home_away_Last_7', 'Away_Team_Avg_GF_Away_away_Last_7',
 'Away_Team_Avg_xG_x_away_Last_7', 'Away_Team_Avg_xGA_away_Last_7',
 'Away_Team_Avg_Poss_away_Last_7', 'Away_Team_Avg_Referee_away_Last_7',
 'Away_Team_Avg_Sh_x_away_Last_7', 'Away_Team_Avg_SoT_away_Last_7',
 'Away_Team_Avg_G/Sh_away_Last_7', 'Away_Team_Avg_G/SoT_away_Last_7',
 'Away_Team_Avg_Dist_away_Last_7', 'Away_Team_Avg_PK_away_Last_7',
 'Away_Team_Avg_PKatt_away_Last_7', 'Away_Team_Avg_xG_y_away_Last_7',
 'Away_Team_Avg_npxG_away_Last_7', 'Away_Team_Avg_npxG/Sh_away_Last_7',
 'Away_Team_Avg_Touches_away_Last_7', 'Away_Team_Avg_Def Pen_away_Last_7',
 'Away_Team_Avg_Def 3rd_x_away_Last_7',
 'Away_Team_Avg_Att 3rd_x_away_Last_7', 'Away_Team_Avg_Att Pen_away_Last_7',
 'Away_Team_Avg_Att_x_away_Last_7', 'Away_Team_Avg_Succ%_away_Last_7',
 'Away_Team_Avg_1/3_away_Last_7', 'Away_Team_Avg_CPA_away_Last_7',
 'Away_Team_Avg_Mis_away_Last_7', 'Away_Team_Avg_Dis_away_Last_7',
 'Away_Team_Avg_Rec_away_Last_7', 'Away_Team_Avg_PrgR_away_Last_7',
 'Away_Team_Avg_Cmp_away_Last_7', 'Away_Team_Avg_Cmp.1_away_Last_7',
 'Away_Team_Avg_Cmp.2_away_Last_7', 'Away_Team_Avg_Cmp.3_away_Last_7',
 'Away_Team_Avg_Att_y_away_Last_7', 'Away_Team_Avg_Att_y.1_away_Last_7',
 'Away_Team_Avg_Att_y.2_away_Last_7', 'Away_Team_Avg_Att_y.3_away_Last_7',
 'Away_Team_Avg_Cmp%_away_Last_7', 'Away_Team_Avg_Cmp%.1_away_Last_7',
 'Away_Team_Avg_Cmp%.2_away_Last_7', 'Away_Team_Avg_Cmp%.3_away_Last_7',
 'Away_Team_Avg_TotDist_away_Last_7', 'Away_Team_Avg_PrgDist_away_Last_7',
 'Away_Team_Avg_Ast_away_Last_7', 'Away_Team_Avg_xAG_away_Last_7',
 'Away_Team_Avg_xA_away_Last_7', 'Away_Team_Avg_KP_away_Last_7',
 'Away_Team_Avg_PPA_away_Last_7', 'Away_Team_Avg_CrsPA_away_Last_7',
 'Away_Team_Avg_PrgP_away_Last_7', 'Away_Team_Avg_SCA_away_Last_7',
 'Away_Team_Avg_PassLive_away_Last_7',
 'Away_Team_Avg_PassLive.1_away_Last_7',
 'Away_Team_Avg_PassDead_away_Last_7',
 'Away_Team_Avg_PassDead.1_away_Last_7', 'Away_Team_Avg_TO_away_Last_7',
 'Away_Team_Avg_TO.1_away_Last_7', 'Away_Team_Avg_Sh_y_away_Last_7',
 'Away_Team_Avg_Sh_y.1_away_Last_7', 'Away_Team_Avg_Fld_away_Last_7',
 'Away_Team_Avg_Fld.1_away_Last_7', 'Away_Team_Avg_Def_away_Last_7',
 'Away_Team_Avg_Def.1_away_Last_7', 'Away_Team_Avg_GCA_away_Last_7',
 'Away_Team_Avg_Tkl_away_Last_7', 'Away_Team_Avg_Tkl.1_away_Last_7',
 'Away_Team_Avg_TklW_away_Last_7', 'Away_Team_Avg_Def 3rd_y_away_Last_7',
 'Away_Team_Avg_Mid 3rd_away_Last_7', 'Away_Team_Avg_Att 3rd_y_away_Last_7',
 'Away_Team_Avg_Att_away_Last_7', 'Away_Team_Avg_Tkl%_away_Last_7',
 'Away_Team_Avg_Lost_x_away_Last_7', 'Away_Team_Avg_Blocks_away_Last_7',
 'Away_Team_Avg_Sh_away_Last_7', 'Away_Team_Avg_Pass_away_Last_7',
 'Away_Team_Avg_Int_away_Last_7', 'Away_Team_Avg_Tkl+Int_away_Last_7',
 'Away_Team_Avg_Clr_away_Last_7', 'Away_Team_Avg_Err_away_Last_7',
 'Away_Team_Avg_Recov_away_Last_7', 'Away_Team_Avg_Won_away_Last_7',
 'Away_Team_Avg_Lost_y_away_Last_7', 'Away_Team_Avg_Won%_away_Last_7',
 'Away_Team_Avg_Season_away_Last_7',
 'Away_Team_Avg_Outcome_encoded_away_Last_7',
 'Away_Team_Avg_Against_Big_Six_away_Last_7', 'Home_Team_Elo_Before',
 'Away_Team_Elo_Before', 'Home_Team_Elo_After', 'Away_Team_Elo_After']  # Add more as needed

grouping_columns = ['Home_Team_home', 'Away_Team_home']
# Create a dictionary with all columns set to 'mean' by default
agg_dict = {col: 'mean' for col in final_df12.columns if col not in grouping_columns and final_df12[col].dtype != 'object'}

# Update the dictionary for columns that need 'last' aggregation
for col in last_value_columns:
    if col in agg_dict:  # Ensure the column exists in the DataFrame
        agg_dict[col] = 'last'

# Group by 'Home_Team_home' and apply the aggregation
home_team_features_df = final_df12.groupby('Home_Team_home').agg(agg_dict).reset_index()

# Group the data by away team and aggregate the features
away_team_features_df = final_df12.groupby('Away_Team_home').agg(agg_dict).reset_index()


# Convert the DataFrames to dictionaries
home_team_features = home_team_features_df.set_index('Home_Team_home').to_dict('index')
away_team_features = away_team_features_df.set_index('Away_Team_home').to_dict('index')
