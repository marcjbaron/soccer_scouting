import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt
from PIL import Image


# Add error-handling (if any error, just say there's an error, then display random player)

st.set_page_config(layout="wide")


row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.01, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Identifying Professional Soccer Player Profiles')
with row0_2:
    st.markdown("You can find the source code in the [GitHub Repository](https://github.com/marcjbaron/soccer-scounting)")
    st.markdown('Streamlit App by [Marc Baron](https://www.linkedin.com/in/marc-j-baron/)')
# row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
# with row3_1:
st.markdown("Over the past 10 years, as more and more data is collectedsoccer has seen a rapid growth in interest.\
    Today, there are several data companies and professional teams collecting increasingly fine-grained statistics on every match played.") 
st.markdown(" This page attempts to use some of those statistics to group together players with statistically similar play styles.\
    Keep scrolling to get into the details, or just use the sidebar to choose a player and get a list of 10 players who play in a similar style.")
    # st.markdown("If you are interested in how this app was developed check out my [Medium article](https://tim-denzler.medium.com/is-bayern-m%C3%BCnchen-the-laziest-team-in-the-german-bundesliga-770cfbd989c7)")

#################
### SELECTION ###
#################
df_player = pd.read_csv("../data/processed/display_player_data.csv")
df_player.drop(columns=["Unnamed: 0"], inplace=True)
neighbors = pd.read_csv("../data/processed/nearest_neighbors.csv")


def get_unique_leagues(df):
    return np.unique(df.League).tolist()
def get_unique_teams(df, league ):
    return np.unique(df[df.League == league].Squad).tolist()
def get_unique_player(df, team):
    return np.unique(df[df.Squad == team].Player).tolist()

def selectbox_similar_players(player_selection, player_data, neighbor_data, team):
    idx = player_data[(player_data['Player'] == player_selection) & (player_data['Squad'] == team)].index[0]
    neighbors_idx = np.array(neighbor_data.iloc[idx, :]) # Find neighbors of player from array
    similar_players = player_data.iloc[neighbors_idx, :]
    display_df = similar_players[1:].reset_index(drop=True)
    cluster = player_data['Player Type'][player_data['Player'] == player_selection].values[0]
    return display_df, cluster 

def textbox_similar_players(player_selection, player_data, neighbor_data):
    idx = player_data[(player_data['Player'] == player_selection)].index[0]
    neighbors_idx = np.array(neighbor_data.iloc[idx, :]) # Find neighbors of player from array
    similar_players = player_data.iloc[neighbors_idx, :]
    display_df = similar_players[1:].reset_index(drop=True)
    cluster = player_data['Player Type'][player_data['Player'] == player_selection].values[0]
    return display_df, cluster

def find_cluster_size(df, cluster):
    clusters = np.array(df['Player Type'])
    num_unique_clusters, counts = np.unique(clusters, return_counts=True)
    cluster_counts = dict(zip(num_unique_clusters, (counts/len(clusters))*100))
    return cluster_counts[cluster]

# Display a random player in the text box as an example
# Check if session state object exists
if "random_player" not in st.session_state:
    st.session_state["random_player"] = df_player.Player.sample().values[0]
elif "random_player" not in st.session_state:
    st.session_state["random_player"] = st.session_state["random_player"] 

# def player_callback():
#     st.session_state["prev_random_player"] = st.session_state["random_player"]
#     st.session_state["random_player"] = st.session_state["random_player"]   

# for key in st.session_state.keys():
    # del st.session_state[key]


# textbox_default = df_player.Player.sample().values[0]


st.sidebar.text('')
st.sidebar.text('')
st.sidebar.text('')

##Sidebar options

# League selection
with st.form(key='selectbox_form'):
    with st.sidebar:
        unique_leagues = get_unique_leagues(df_player)
        prompts = [["Select a league"], ["Select a team"], ["Select a player"]]
        prompts[0].extend(unique_leagues)
        league_selection = st.sidebar.selectbox('Use the options below to select your desired player. At the moment, only the 2021-2022 season is included.', prompts[0])
        
        #...and team selection 
        unique_teams = get_unique_teams(df_player, league_selection)
        prompts[1].extend(unique_teams)
        team_selection = st.sidebar.selectbox("Select a team", prompts[1] )

        #...and player selection 
        unique_player = get_unique_player(df_player, team_selection)
        prompts[2].extend(unique_player)
        player_selection_selectbox = st.sidebar.selectbox("Select a player", options = prompts[2] )
        selectbox_submitted = st.form_submit_button("Submit" )

# Reset everything after player selection?

### Or text input
# player_name = random_player(df_player)
# that variable changes when anything changes; to fix it, see here: https://docs.streamlit.io/library/advanced-features/session-state
with st.form(key='text_form', clear_on_submit=False):
    with st.sidebar:
        player_selection_text = st.sidebar.text_input('Or type the name of a player below. We\'ve randomly selected a player so you can\
             see how it works. If a player played for multiple teams in that season, only one of the teams will listed', value = st.session_state.random_player) 
        
        # def new_random_player(df):
            # st.session_state["random_player"] = df.Player.sample().values[0]
            # return 
        submitted = st.form_submit_button("Submit" )
        # st.session_state.player = player_selection_text

################
### ANALYSIS ###
################

if selectbox_submitted:
    player_selection = player_selection_selectbox
else:
    player_selection = player_selection_text

st.header(f'{player_selection} Player Profile')


if selectbox_submitted:
    display, cluster = selectbox_similar_players(player_selection, df_player, neighbors, team_selection)
else:
    display, cluster = textbox_similar_players(player_selection, df_player, neighbors )

if (cluster == 1):
    st.markdown("*Exemplars:  Dušan Vlahović (Juventus), Erling Haaland (Dortmund), Sebastián Ferreira (Houston Dynamo), Mohamed Lamine Bayo (Clermont Foot)*")
    st.markdown(" Very attacking players. Dangerous finishers close to goal, but who tend to contribute mainly at the end of chains of possession, either \
    through their dangerous shooting or by turning the ball over. Relatively accurate passers (for attacking players), so a bit more likely to play more towards midfield. ")
if (cluster == 2):
    st.markdown("*Exemplars: Anton Stach (Mainz 05), Nemanja Matić (Manchester United), Sergio Busquets (Barcelona), Joshua Kimmich (Bayern Munich)* ")
    st.markdown("This player tends to control the midfield, both offensively and defensively. They possess the ball more than any other \
    player profile, and are accurate passers. They are skilled at dispossessing opposing players, mostly in the midfield. ")
if (cluster == 3):
    st.markdown("*Exemplars: Alphonso Davies (Bayern Munich), Trent Alexander-Arnold (Liverpool), João Cancelo (Manchester City), Kai Wagner (Philadelphia Union)*")
    st.markdown("Players who look to make long, progressive passes from deep or central areas. Also effective at dispossessing players in the \
    defensive third. Much more likely to take throw-ins, suggesting they play the traditional \"fullback\" role.")
if (cluster == 4):
    st.markdown("*Exemplars:Virgil van Dijk (Liverpool),  Matthijs de Ligt (Juventus), Lewis Dunk (Brighton), Pau Torres (Villareal)*") 
    st.markdown("Defensive-minded players who are able to make a wide variety of accurate passes. Team's focal point in possession in the defensive third, and more likely to advance into the midfield. \
    They hard to dispossess and who will win most balls on the ground and in the air.")
if (cluster == 5):
    st.markdown("*Exemplars: Pietro Ceccaroni (Venezia), Tyrone Mings (Aston Villa), Julien Laporte (Lorient), Andrew Farrell (New England)*") 
    st.markdown("Defensive-minded players who are able to make a wide variety of accurate passes. Not as likely to roam from the defensive third, and are more likely to dribble their way out of trouble. \
    They hard to dispossess and who will win most balls on the ground and in the air.")
if (cluster == 6):
    st.markdown("*Exemplars: Andy Delort (Nice), Robert Lewandowski (Bayern Munich), Ciro Immobile (Lazio), Javier (Chico) Hernández (LA Galaxy)*")
    st.markdown(" The least common role. Extremely attacking players. Dangerous finishers close to goal, but who tend to contribute mainly at the end of chains of possession, either \
     through their dangerous shooting or by turning the ball over. More effective dribblers, and are thus more likely to be fouled in dangerous areas. ")
if (cluster == 7):
    st.markdown("*Exemplars: Son Heung-min (Tottenham), Kylian Mbappé (Paris S-G), Bukayo Saka (Arsenal), Marco Reus (Dortmund)*") 
    st.markdown("This player is adept at creating goal-scoring opportunities, either by passing or shooting in the opposing team's penalty area. \
        They tend to play shorter passes (perhaps because they are mostly found in the final third), and do not contribute as much defensively.")
if (cluster == 8):
    st.markdown("*Exemplars: Lorenzo Insigne (Napoli), Kevin De Bruyne (Manchester City), Thomas Müller (Bayern Munich),  Alejandro Pozuelo (Inter Miami)*")
    st.markdown(" The most common role. This player is adept at creating goal-scoring opportunities, either by dribbling or passing into the opposing team's penalty area. \
        They tend to play shorter passes (perhaps because they are mostly found in the final third), and do not contribute as much defensively.")


st.header('Similar Players')
st.table(display.style.format({'Minutes Played (%)': "{:.1f}", 'onxG': "{:.2f}", 'onxGA': "{:.2f}"}))
st.markdown("*Table Legend*")
st.markdown("**Pos** (player positions): FW - Forward; MF - Midfielder; DF - Defender (no goalkeepers here; sorry keepers!)")
st.markdown("**Player Type**: Cluster the player is part of; see next section for details")
st.markdown("**Min Pld (%)**: What proportion of the team's minutes that player played. 100% would mean they played every minute of every game")
st.markdown("**onxG**: A measure of the quality of a team's goal-scoring chances when that player is on the pitch. A score above *1.00* implies \
    the team has better goal-scoring chances when the player is playing; a score below *1.00* implies better goal-scoring chances when the player is \
        not playing.")
st.markdown("**onxGA**: A measure of the quality of the opposing team's goal-scoring chances when that player is on the pitch. A score above *1.00* implies \
    the opposing team has better goal-scoring chances when the player is playing; a score below *1.00* implies better goal-scoring chances when the player is \
        not playing.")
# st.markdown("**onxGA**: A measure of the quality of the opposing team's goal-scoring chances when that player is on the pitch. A score above *1.00* implies\
    # the opposing team has better goal-scoring chances when the player is playing; a score below *1.00* implies better goal-scoring chances when the player is\
        # not playing.")
# Define player types

action_map = Image.open(f"../reports/figures/cluster_{cluster}_action_profile.png")
st.image(action_map )

st.header('All Player Type Profiles')

st.subheader('Details of the Player Styles')
st.markdown('The play styles were determined by taking around 70 event-based statistical actions collected by [StatsBomb](https://statsbomb.com/what-we-do/soccer-data/), and reducing those actions to a 2-dimensional\
    graph using a technique called [UMAP](https://umap-learn.readthedocs.io/en/latest/clustering.html). The resulting data was then organized into\
    clusters using a technique called [spectral clustering](https://www.kaggle.com/code/vipulgandhi/spectral-clustering-detailed-explanation). The resulting graph, along \
    with an interpretation of the axes, is shown below.')
st.markdown("\'*Position*' is the position on the pitch where most of that player's actions take place. \'*Composure with ball*\' is how good they are with the ball at their feet, \
    whether passing or holding on to the ball.")
cluster_map = Image.open("../reports/figures/cluster_map_annotated.png")
st.image(cluster_map )

st.subheader(f'Cluster 2 - {find_cluster_size(df_player, 2):.1f}% of players')
st.markdown("*Exemplars: Anton Stach (Mainz 05), Nemanja Matić (Manchester United), Sergio Busquets (Barcelona), Joshua Kimmich (Bayern Munich)* ")
st.markdown("This player tends to control the midfield, both offensively and defensively. They possess the ball more than any other \
player profile, and are accurate passers. They are skilled at dispossessing opposing players, mostly in the midfield. ")
st.subheader(f'Cluster 8- {find_cluster_size(df_player, 8):.1f}% of players')
st.markdown("*Exemplars: Lorenzo Insigne (Napoli), Kevin De Bruyne (Manchester City), Thomas Müller (Bayern Munich),  Alejandro Pozuelo (Inter Miami)*")
st.markdown(" The most common role. This player is adept at creating goal-scoring opportunities, either by dribbling or passing into the opposing team's penalty area. \
    They tend to play shorter passes (perhaps because they are mostly found in the final third), and do not contribute as much defensively.")
st.subheader(f'Cluster 7- {find_cluster_size(df_player, 7):.1f}% of players')
st.markdown("*Exemplars: Son Heung-min (Tottenham), Kylian Mbappé (Paris S-G), Bukayo Saka (Arsenal), Marco Reus (Dortmund)*") 
st.markdown("This player is adept at creating goal-scoring opportunities, either by passing or shooting in the opposing team's penalty area. \
    They tend to play shorter passes (perhaps because they are mostly found in the final third), and do not contribute as much defensively.")
st.subheader(f'Cluster 6- {find_cluster_size(df_player, 6):.1f}% of players')
st.markdown("*Exemplars: Andy Delort (Nice), Robert Lewandowski (Bayern Munich), Ciro Immobile (Lazio), Javier (Chico) Hernández (LA Galaxy)*")
st.markdown(" The least common role. Extremely attacking players. Dangerous finishers close to goal, but who tend to contribute mainly at the end of chains of possession, either \
 through their dangerous shooting or by turning the ball over. More effective dribblers, and are thus more likely to be fouled in dangerous areas. ")
st.subheader(f'Cluster 1- {find_cluster_size(df_player, 1):.1f}% of players')
st.markdown("*Exemplars:  Dušan Vlahović (Juventus), Erling Haaland (Dortmund), Sebastián Ferreira (Houston Dynamo), Mohamed Lamine Bayo (Clermont Foot)*")
st.markdown(" Very attacking players. Dangerous finishers close to goal, but who tend to contribute mainly at the end of chains of possession, either \
through their dangerous shooting or by turning the ball over. Relatively accurate passers (for attacking players), so a bit more likely to play more towards midfield. ")

st.subheader(f'Cluster 3- {find_cluster_size(df_player, 3):.1f}% of players')
st.markdown("*Exemplars: Alphonso Davies (Bayern Munich), Trent Alexander-Arnold (Liverpool), João Cancelo (Manchester City), Kai Wagner (Philadelphia Union)*")
st.markdown("Players who look to make long, progressive passes from deep or central areas. Also effective at dispossessing players in the \
defensive third. Much more likely to take throw-ins, suggesting they play the traditional \"fullback\" role.")
st.subheader(f'Cluster 5- {find_cluster_size(df_player, 5):.1f}% of players')
st.markdown("*Exemplars: Pietro Ceccaroni (Venezia), Tyrone Mings (Aston Villa), Julien Laporte (Lorient), Andrew Farrell (New England)*") 
st.markdown("Defensive-minded players who are able to make a wide variety of accurate passes. Not as likely to roam from the defensive third, and are more likely to dribble their way out of trouble. \
They hard to dispossess and who will win most balls on the ground and in the air.")
st.subheader(f'Cluster 4- {find_cluster_size(df_player, 4):.1f}% of players')
st.markdown("*Exemplars:Virgil van Dijk (Liverpool),  Matthijs de Ligt (Juventus), Lewis Dunk (Brighton), Pau Torres (Villareal)*") 
st.markdown("Defensive-minded players who are able to make a wide variety of accurate passes. Team's focal point in possession in the defensive third, and more likely to advance into the midfield. \
They hard to dispossess and who will win most balls on the ground and in the air.")
