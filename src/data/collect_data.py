
# URL changed for data usage reasons

import requests
import pandas as pd


#### Function Definitions ####

def get_dataframe(league, stat, year):
  '''Store data soccerstats data into Pandas dataframe for a specific category of statistic.
  Parameters:
    stat: the specific category of statistic 
      - Options: shooting, passing, passing_types, gca, defense, possession, playingtime, misc

    league: 
      - options: Big5, La-Liga, Premier-League, Ligue-1, Bundesliga, Serie-A, Major-League-Soccer
      Liga MX, EFL Championship, Eredivisie, Primeira Liga (Portugal)

    
    year: 
      - should be over 2 years for the big 5 leagues, and a single year for MLS; if chosen over 2 years,
      latter season will be taken for MLS (e.g. if 2021-2022 chosen, 2022 MLS data will be used)
      - if "year" chosen, will choose the current season 

      ***Advanced data only available after 2017-2018
  Return:
    df: Dataframe containing table of stats from the given soccerstats page
  '''

  #Leagues have specific number codes in URL; add that code if user wants specific league
  if (league == 'Big-5-European-Leagues'):
    league_num = 'Big5' 
    # Big 5 stats have a different URL to individual leagues
    url = f'https://soccerstats.com/en/comps/{league_num}/{year}/{stat}/players/{year}-{league}-Stats'
    if (year == 'current'):
      url = f'https://soccerstats.com/en/comps/{league_num}/{stat}/players/{league}-Stats'
  else:
    if (league == 'La-Liga'):
      league_num = '12'
    if (league == 'Premier-League'):
      league_num = '9'
    if (league == 'Ligue-1'):
      league_num = '13'
    if (league == 'Bundesliga'):
      league_num = '20'
    if (league == 'Serie-A'):
      league_num = '11'
    if (league == 'Eredivisie'):
      league_num = '23'
    if (league == 'Primeira-Liga'):
      league_num = '32'
    if (league == 'Championship'):
      league_num = '10'
    if (league == 'Liga-MX'):
      league_num = '31'
    if (league == 'Major-League-Soccer'):
      if (year != 'current'):
        year = year.split('-')[1] # MLS takes place in a single calendar year
      league_num = '22'
    else:
      print('League not found')
  
    url = f'https://soccerstats.com/en/comps/{league_num}/{year}/{stat}/{year}-{league}-Stats'
    
    if (year == 'current'): #MLS page redirects to this page for current season
      url = f'https://soccerstats.com/en/comps/{league_num}/{stat}/{league}-Stats'

    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    list_df = pd.read_html(html_content)

  # 'df' has 3 tables within it: df[0] is team data, df[1] is against opposition data and 
  # df[2] is individual data. We don't care about df[1].
    list_df[0].columns = list_df[0].columns.droplevel(0) # drop top header row
    list_df[2].columns = list_df[2].columns.droplevel(0) # drop top header row
    list_df[2] = list_df[2][list_df[2]['Rk'].ne('Rk')].reset_index(drop=True) # remove mid-table header rows 
      
    print(f"{year} {league} {stat} data successfully stored.")
  return list_df[0], list_df[2]

stats = ['shooting', 'passing', 'passing_types', 'gca', 'possession', 'defense', 'playingtime', 'misc']
# We can download all Big 5 European leagues at once, but if we do league individually, it gives us team 
# stats (which we will wantto extract for by-team normalizing)
leagues = ['La-Liga', 'Premier-League', 'Ligue-1', 'Bundesliga',  'Serie-A']
mls = 'Major-League-Soccer'
year = '2021-2022'

for stat in stats:
        for league in leagues:
                 team_df, ind_df = get_dataframe(league, stat, year)
                 team_df.to_csv(f'../data/raw/team/{league}-{year}-team-{stat}.csv') #Assumes location of 'data' folder
                 ind_df.to_csv(f'../data/raw/individual/{league}-{year}-individual-{stat}.csv') #Assumes location of 'data' folder
        
        # Taken while current MLS season is on, so do it separately
        team_df, ind_df = get_dataframe(mls, stat, 'current')
        team_df.to_csv(f'../data/raw/team/{mls}-2022-team-{stat}.csv') #Assumes location of 'data' folder
        ind_df.to_csv(f'../data/raw/individual/{mls}-2022-individual-{stat}.csv') #Assumes location of 'data' folder

