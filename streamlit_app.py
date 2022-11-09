import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt
from PIL import Image


# Add error-handling (if any error, just say there's an error, then display random player)

st.set_page_config(layout="wide")


row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.01, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Identifying Professional Soccer Player Styles')
with row0_2:
    st.markdown("You can find the source code in the [GitHub Repository](https://github.com/marcjbaron/soccer_scouting)")
    st.markdown('Streamlit App by [Marc Baron](https://www.linkedin.com/in/marc-j-baron/)')
# row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
# with row3_1:
st.markdown("Over the past 10 years, the analysis of soccer analytics has seen a rapid growth in interest as ever-increasing amounts of data is collected.\
    Today, there are several data companies and professional teams in-house analysts collecting increasingly fine-grained statistics on every match played.") 
st.markdown(" This page attempts to use some of those statistics to group together players with statistically similar play styles.\
    Use the sidebar to choose a player from one of 10 different leagues, and see a list of players who play in a similar style to the chosen player.")
st.markdown(" To see all the player styles and how the styles were determined, go to the bottom of the page.")

#################
### SELECTION ###
#################
df_player = pd.read_csv("data/processed/display_player_data.csv")
df_player.drop(columns=["Unnamed: 0"], inplace=True)
neighbors = pd.read_csv("data/processed/nearest_neighbors.csv")


def get_unique_leagues(df):
    return np.unique(df.League).tolist()
def get_unique_teams(df, league ):
    return np.unique(df[df.League == league].Squad).tolist()
def get_unique_player(df, team):
    return np.unique(df[df.Squad == team].Player).tolist()

def filter_leagues(df_data):
    df_filtered_team = pd.DataFrame()
    if all_leagues_selected == 'Select leagues manually (choose below)':
        df_filtered_team = df_data[df_data['League'].isin(selected_leagues)]
        return df_filtered_team
    return df_data

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
if "player" not in st.session_state:
    st.session_state["player"] = df_player.Player.sample().values[0]
# elif "random_player" not in st.session_state:
    # st.session_state["random_player"] = st.session_state["random_player"] 

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
###  Selecting leagues
with st.form(key='selectbox_league'):
    with st.sidebar:
        unique_leagues = get_unique_leagues(df_player)
        all_leagues_selected = st.sidebar.selectbox('Do you want to only include specific leagues? If so, check the box below and \
            then select the league(s) in the new field.', ['Include all available leagues','Select leagues manually (choose below)'])
        if (all_leagues_selected == 'Select leagues manually (choose below)'):
            selected_leagues = st.sidebar.multiselect("Select and deselect the leagues you would like to include in the analysis. You can \
                clear the current selection by clicking the corresponding x-button on the right", unique_leagues, default = unique_leagues)
        df_data_filtered = filter_leagues(df_player)   

with st.form(key='selectbox_form'):
    with st.sidebar:
        unique_leagues = get_unique_leagues(df_data_filtered)
        prompts = [["Select a league"], ["Select a team"], ["Select a player"]]
        prompts[0].extend(unique_leagues)
        league_selection = st.sidebar.selectbox('To choose a player, use the options below to select a league, team and then player. At the moment, only the 2021-2022 season \
            is included.', prompts[0])
        
        #...and team selection 
        unique_teams = get_unique_teams(df_player, league_selection)
        prompts[1].extend(unique_teams)
        team_selection = st.sidebar.selectbox("Select a team", prompts[1] )

        #...and player selection 
        unique_player = get_unique_player(df_player, team_selection)
        prompts[2].extend(unique_player)
        player_selection_selectbox = st.sidebar.selectbox("Select a player (Players must have played at least 20% of available minutes to \
            be eligible)", options = prompts[2] )
        selectbox_submitted = st.form_submit_button("Submit" )
        if selectbox_submitted:
            st.session_state.player = player_selection_selectbox

# Reset everything after player selection?

### Or text input
# player_name = random_player(df_player)
# that variable changes when anything changes; to fix it, see here: https://docs.streamlit.io/library/advanced-features/session-state
with st.form(key='text_form', clear_on_submit=False):
    with st.sidebar:
        player_selection_text = st.sidebar.text_input('Or type the name of a player below. We\'ve randomly selected a player so you can\
             see how it works. If a player played for multiple teams in that season, only one of the teams will listed', value = st.session_state.player) 
        
        # def new_random_player(df):
            # st.session_state["random_player"] = df.Player.sample().values[0]
            # return 
        textform_submitted = st.form_submit_button("Submit" )
        if textform_submitted:
            st.session_state.player = player_selection_text

###############
### ANALYSIS ###
################

player_selection = st.session_state.player

st.header(f'Player Profile for {player_selection}')

if selectbox_submitted:
    display, cluster = selectbox_similar_players(player_selection, df_player, neighbors, team_selection)
else:
    try:
        display, cluster = textbox_similar_players(player_selection, df_player, neighbors )
    except IndexError:
        st.error("Please enter a valid player; check the spelling or for special characters in the player's name, and make sure there are no spaces!")
        st.stop()
if (cluster == 1):
    st.subheader(f'Cluster 1 - {find_cluster_size(df_player, 1):.1f}% of players')
    st.markdown("*Exemplars: Erling Haaland (Dortmund), Robert Lewandowski (Bayern Munich), Karime Benzema (Real Madrid), Javier (Chico) Hernández (LA Galaxy)*, Jonathan David (Lille)")
    st.markdown(" Traditional forwards, and the least common role; dangerous finishers close to goal, but tend to contribute mainly at the end of chains of possession, either \
    through their dangerous shooting or by turning the ball over. More effective dribblers, and are thus more likely to be fouled in dangerous areas. Don't touch or pass the ball much, relative to \
    their teammates.")
if (cluster == 2):
    st.subheader(f'Cluster 2 - {find_cluster_size(df_player, 2):.1f}% of players')
    st.markdown("*Exemplars: Lorenzo Insigne (Napoli), Kevin De Bruyne (Manchester City), Kylian Mbappé (Paris S-G), Thomas Müller (Bayern Munich),  Alejandro Pozuelo (Inter Miami)*")
    st.markdown("Traditional attacking midfielders and wingers; this player is adept at creating goal-scoring opportunities, either by dribbling or passing into the opposing team's penalty area. \
        They tend to play shorter passes (perhaps because they are mostly found in the final third), and do not contribute as much defensively.")
if (cluster == 3):
    st.subheader(f'Cluster 3 - {find_cluster_size(df_player, 3):.1f}% of players')
    st.markdown("*Exemplars: Raphina (Leeds United), Luka Modrić (Real Madrid), Sergio Busquets (Barcelona), Joshua Kimmich (Bayern Munich), Marten de Roon (Atalanta)* ")
    st.markdown("This player tends to control the midfield, both offensively and defensively. They possess the ball more than any other \
    player profile, and are accurate passers. They are skilled at dispossessing opposing players, mostly in the midfield. ")
if (cluster == 4):
    st.subheader(f'Cluster 4 - {find_cluster_size(df_player, 4):.1f}% of players')
    st.markdown("*Exemplars: Alphonso Davies (Bayern Munich), Trent Alexander-Arnold (Liverpool), João Cancelo (Manchester City), Kai Wagner (Philadelphia Union)*")
    st.markdown("Traditional fullbacks and wide midfielders. Players who look to make long, progressive passes from deep or central areas. Also effective at dispossessing players in the \
    defensive third. Much more likely to take throw-ins, confirming the wider roles they play.")
if (cluster == 5):
    st.subheader(f'Cluster 5 - {find_cluster_size(df_player, 5):.1f}% of players')
    st.markdown("*Exemplars: Virgil van Dijk (Liverpool),  Matthijs de Ligt (Juventus), Lewis Dunk (Brighton), Pau Torres (Villareal), Gerard Piqué (Barcelona)*") 
    st.markdown("Traditional centre-backs. More likely to possess the ball in their own 3rd of the pitch, and therefore more likely to make accurate, longer passes (*i.e.* greater than 10 yards). \
    They are hard to dispossess and will win most balls on the ground and in the air.")

st.header(f'Similar Players to {player_selection}')
st.markdown("The chosen player will be listed first, followed by the most statistically similar players.")
st.table(display.style.format({'Minutes\nPlayed (%)': "{:.1f}", 'onxG': "{:.2f}", 'onxGA': "{:.2f}"}))
st.markdown("*Table Legend*")
st.caption("**Pos** (player positions): FW - Forward; MF - Midfielder; DF - Defender (no goalkeepers here; sorry keepers!)")
st.caption("**Player Type**: Cluster the player is part of; see next section for details")
st.caption("**Minutes Played (%)**: What proportion of the team's minutes that player played. 100% would mean they played every minute of every game")
st.caption("**onxG**: A measure of the quality of a team's goal-scoring chances when that player is on the pitch. A score above *1.00* implies \
    the team has better goal-scoring chances when the player is playing; a score below *1.00* implies better goal-scoring chances when the player is \
        not playing.")
st.caption("**onxGA**: A measure of the quality of the opposing team's goal-scoring chances when that player is on the pitch. A score above *1.00* implies \
    the opposing team has better goal-scoring chances when the player is playing; a score below *1.00* implies better goal-scoring chances when the player is \
        not playing.")

# Showing bar plot of percentiles (comment out for now)
# col1, col2, col3 = st.columns([1.5,6,1])
# with col1:
#     st.write("")
# with col2:
#     action_map = Image.open(f"reports/figures/cluster_{cluster}_action_profile.png")
#     st.image(action_map )
# with col3:
#     st.write("")

with st.form(key='allclusters_form'):
        prompts = ["Hide all player profiles and methodology", "Show all player profiles and methodology"]
        general_selection = st.selectbox('All player profles and methodology', prompts)
        all_selectbox_submitted = st.form_submit_button("Submit" )

if all_selectbox_submitted:
    st.header('All Player Type Profiles')

    st.subheader('Details of the Player Styles')
    st.subheader(f'Cluster 1 - {find_cluster_size(df_player, 1):.1f}% of players')
    st.markdown("*Exemplars: Erling Haaland (Dortmund), Robert Lewandowski (Bayern Munich), Karime Benzema (Real Madrid), Javier (Chico) Hernández (LA Galaxy)*, Jonathan David (Lille)")
    st.markdown(" Traditional forwards, and the least common role; dangerous finishers close to goal, but tend to contribute mainly at the end of chains of possession, either \
    through their dangerous shooting or by turning the ball over. More effective dribblers, and are thus more likely to be fouled in dangerous areas. Don't touch or pass the ball much, relative to \
        their teammates.")
    st.subheader(f'Cluster 2- {find_cluster_size(df_player, 2):.1f}% of players')
    st.markdown("*Exemplars: Lorenzo Insigne (Napoli), Kevin De Bruyne (Manchester City), Kylian Mbappé (Paris S-G), Thomas Müller (Bayern Munich),  Alejandro Pozuelo (Inter Miami)*")
    st.markdown("Traditional attacking midfielders and wingers; this player is adept at creating goal-scoring opportunities, either by dribbling or passing into the opposing team's penalty area. \
        They tend to play shorter passes (perhaps because they are mostly found in the final third), and do not contribute as much defensively.")
    st.subheader(f'Cluster 3- {find_cluster_size(df_player, 3):.1f}% of players')
    st.markdown("*Exemplars: Raphina (Leeds United), Luka Modrić (Real Madrid), Sergio Busquets (Barcelona), Joshua Kimmich (Bayern Munich), Marten de Roon (Atalanta)* ")
    st.markdown("This player tends to control the midfield, both offensively and defensively. They possess the ball more than any other \
    player profile, and are accurate passers. They are skilled at dispossessing opposing players, mostly in the midfield. ")
    st.subheader(f'Cluster 4- {find_cluster_size(df_player, 4):.1f}% of players')
    st.markdown("*Exemplars: Alphonso Davies (Bayern Munich), Trent Alexander-Arnold (Liverpool), João Cancelo (Manchester City), Kai Wagner (Philadelphia Union)*")
    st.markdown("Traditional fullbacks and wide midfielders. Players who look to make long, progressive passes from deep or central areas. Also effective at dispossessing players in the \
    defensive third. Much more likely to take throw-ins, confirming the wider roles they play.")
    st.subheader(f'Cluster 5- {find_cluster_size(df_player, 5):.1f}% of players')
    st.markdown("*Exemplars: Virgil van Dijk (Liverpool),  Matthijs de Ligt (Juventus), Lewis Dunk (Brighton), Pau Torres (Villareal), Gerard Piqué (Barcelona)*") 
    st.markdown("Traditional centre-backs. More likely to possess the ball in their own 3rd of the pitch, and therefore more likely to make accurate, longer passes (*i.e.* greater than 10 yards). \
        They are hard to dispossess and will win most balls on the ground and in the air.")

    st.subheader('Details of the Methodology')
    st.markdown('The play styles were determined by taking around 50 event-based statistical actions collected by [Opta](https://www.statsperform.com/opta/), and reducing those actions to a 2-dimensional\
        graph using a technique called [UMAP](https://umap-learn.readthedocs.io/en/latest/clustering.html). The resulting data was then organized into\
        clusters using a technique called [spectral clustering](https://www.kaggle.com/code/vipulgandhi/spectral-clustering-detailed-explanation). The resulting graph, along \
        with an interpretation of the axes, is shown below.')
    st.markdown("\'*Position*' is the position on the pitch where most of that player's actions take place. \'*Skill in possession*\' is how good they are with the ball at their feet, \
        whether passing , dribbling or holding on to the ball. ")

    col1, col2, col3 = st.columns([1,6,1])
    with col1:
        st.write("")
    with col2:
        cluster_map = Image.open("reports/figures/cluster_map_opta_annotated.png")
        st.image(cluster_map )
    with col3:
        st.write("")
