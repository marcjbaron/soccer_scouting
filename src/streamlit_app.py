import streamlit as st
import numpy as np
import pandas as pd
import pickle
import time
import matplotlib.pyplot  as plt
from  matplotlib.ticker import FuncFormatter
import seaborn as sns


row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('BuLiAn - Bundesliga Analyzer')
with row0_2:
    st.text("")
    st.subheader('Streamlit App by [Tim Denzler](https://www.linkedin.com/in/tim-denzler/)')
row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
with row3_1:
    st.markdown("Hello there! Have you ever spent your weekend watching the German Bundesliga and had your friends complain about how 'players definitely used to run more' ? However, you did not want to start an argument because you did not have any stats at hand? Well, this interactive application containing Bundesliga data from season 2013/2014 to season 2019/2020 allows you to discover just that! If you're on a mobile device, I would recommend switching over to landscape for viewing ease.")
    st.markdown("You can find the source code in the [BuLiAn GitHub Repository](https://github.com/tdenzl/BuLiAn)")
    st.markdown("If you are interested in how this app was developed check out my [Medium article](https://tim-denzler.medium.com/is-bayern-m%C3%BCnchen-the-laziest-team-in-the-german-bundesliga-770cfbd989c7)")

unique_seasons = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                   columns=['a', 'b', 'c'])
#################
### SELECTION ###
#################
# df_stacked = stack_home_away_dataframe(df_database)

st.sidebar.text('')
st.sidebar.text('')
st.sidebar.text('')


### TEAM SELECTION ###
unique_leagues = get_unique_leagues()
unique_teams = get_unique_teams(df_data_filtered_matchday)
unique_player = get_unique_player(df_data_filtered_matchday)
unique_teams = unique_seasons 
all_teams_selected = st.sidebar.selectbox('Use the options below to select your desired player. At the moment, only the 2021-2022 season is included',
 ['Select a league', 'Major League Soccer', 'English Premier League', 'Bundesliga', 'Ligue 1', 'Serie A', 'La Liga'])
if all_teams_selected == 'Select a league':
    selected_league = st.sidebar.selectbox("Select and deselect the teams you would like to include in the analysis. You can clear the current selection by clicking the corresponding x-button on the right", unique_teams, default = unique_teams)
# df_data_filtered = filter_teams(df_data_filtered_matchday)        
df_data_filtered = unique_teams 
### SEE DATA ###
row6_spacer1, row6_1, row6_spacer2 = st.columns((.2, 7.1, .2))
with row6_1:
    st.subheader("Currently selected data:")
