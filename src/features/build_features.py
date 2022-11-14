import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

###### Function Definitions #####
def common_preprocess(df, scale):
    '''Preprocessing that is common to all statistical tables
    Parameters:
        - df: dataframe of tables from soccersite
        - scale: type of table - either team data or individual data
    Returns:
        - games: games played by team'''

    df.drop(columns=['Unnamed: 0'], inplace=True)
    # Function to divide relevant columns by games played
    games = df['90s']
    
    if scale == 'team': 
        df.drop(columns=['# Pl'], inplace=True)

    if scale == 'individual':
        df['Pos']= df['Pos'].str.split(',',expand=True)[0] # If multiple positions listed, take first (not scientific, but mostly for validation anyway)
        df['Nation'] = df['Nation'].str.split(' ', expand=True)[1] #Gives only 3-letter country abbreviation
        df.drop(columns=['Rk' , 'Age', 'Matches'], inplace=True)
    return games

def shooting_preprocess(df, scale):
    '''Preprocess 'Shooting' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns
        - df: processed dataframe'''

    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    # Drop dead-ball opportunities
    df.drop(columns=['FK', 'PK', 'PKatt', 'xG', 'G-xG'], inplace=True) 

    # Drop columns that are already per 90
    df.drop(columns=['Sh', 'SoT'], inplace=True) 

    # executing the function
    df[["Gls", "npxG", "np:G-xG"]] = df[["Gls", "npxG", "np:G-xG"]].apply(lambda x: x/games)

    return df

def passing_preprocess(df, scale):
    '''Preprocess 'Passing' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns
        - df: processed dataframe'''
    
    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    # executing the per-90 function on relevant stats.
    df[["Cmp", "Att", "TotDist", "PrgDist", "Cmp.1", "Att.1", "Cmp.2", "Att.2", "Cmp.3", "Att.3",
        "Ast", "xA", "KP", "1/3", "PPA", "CrsPA", "Prog" ]] = df[["Cmp", "Att", "TotDist", "PrgDist", "Cmp.1", 
        "Att.1", "Cmp.2", "Att.2", "Cmp.3", "Att.3",
        "Ast", "xA",  "KP", "1/3", "PPA", "CrsPA", "Prog" ]].apply(lambda x: x/games)
    
    # Normalize distances so they are 'distances per pass'
    df["TotDist"]= df["TotDist"]/df["Cmp"]
    df.rename(columns={"TotDist": "TotDist/pass"}, inplace=True)

    df["PrgDist"] = df["PrgDist"]/df["Cmp"]
    df.rename(columns={"PrgDist": "PrgDist/Pass"}, inplace=True)

    # Rename short/medium/long
    df.rename(columns = {"Att.1": "ShortAtt", "Cmp%.1": "Short%", "Att.2": "MedAtt", "Cmp%.2": "Med%","Att.3": "LongAtt", "Cmp%.3": "Long%"}, inplace=True)

    # Find proportion of total passes that are short ( <5 yds), medium (5-15 yds) or long (> 15 yds)
    df["PropShort"] = df["ShortAtt"]/df["Att"]
    df["PropMed"] = df["MedAtt"]/df["Att"]
    df["PropLong"]= df["LongAtt"]/df["Att"]

    # Make % between 0-1
    df[["Short%", "Med%", "Long%"]] = df[["Short%", "Med%", "Long%"]].apply(lambda x: x/100)

    # As above, but with other passing stats
    df["PropAssistShots"] = df["KP"]/df["Cmp"]
    df["PropFinalThirdPasses"]= df["1/3"]/df["Cmp"]
    df["PropPassinPA"]= (df["PPA"] - df['CrsPA'])/df["Cmp"]
    df["PropCrossinPA"]= df["CrsPA"]/df["Cmp"]

    # Drop columns we won't need anymore
    df.drop(columns=['Cmp', 'Att', 'ShortAtt', 'MedAtt', 'LongAtt', 'Cmp%', 'Cmp.1', 'Cmp.2', 'Cmp.3', 'KP', '1/3', 'PPA', 'CrsPA','Prog'], inplace=True) 
    
    return df

 
def passing_types_preprocess(df, scale):
    '''Preprocess 'Pass Type' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns
        - df: processed dataframe'''
    
    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    # Some stats here are redundant from the "Passing" stat, so we'll drop them
    # Also some we just don't care about: dead balls, "Other" passes (which is likely keeper throwing it)
    df.drop(columns = ['Att', 'Dead', 'CK', 'In', 'Out', 'Str'], inplace=True)

    # Offsides could be interesting, as it suggests through/attacking balls, but it is only like 2% of passes, so let's drop
    df.drop(columns = ['Off'], inplace=True)

    # executing the per-90 function on relevant stats
    df[["Live", "FK", "TB", "Sw", "Crs", "TI", "Cmp", "Blocks" ]] = df[["Live", "FK", "TB", "Sw", "Crs", "TI", "Cmp", "Blocks" ]].apply(lambda x: x/games)
    
    # Normalize certain stats to be per pass
    # 'TB' (completed pass b/w back two defenders into open space) has a max of 0.63-per-90, so don't normalize
    live_passes = df['Live'][0]
    df[["Sw", "Crs", "Blocks"]] = df[["Sw", "Crs", "Blocks"]].apply(lambda x: x/live_passes)
    df.rename(columns ={"Blocks": "PropPassBlocked"}, inplace=True)

    ####### These commands are outdated after the data update, but keep if you use another data provider
    # For "Height", it includes dead-ball kicks (which we don't care about). We'll do a sill trick:
    # Assume 10% of Dead ball kicks are 'low', 20% 'ground' and 70% are 'high'. Then subtract those amounts from the height stats
    # df["Ground"] = df["Ground"] - 0.1*df["FK"]
    # df["Low"] = df["Low"] - 0.2*df["FK"]
    # df["High"] = df["High"] - 0.7*df["FK"]

    # Then, find the proportion of each height...
    # df["Ground"] = df["Ground"]/df["Live"]
    # df["Low"] = df["Low"]/df["Live"]
    # df["High"] = df["High"]/df["Live"]
    # df.rename(columns={"Ground": "PropPassGround", "Low": "PropPassLow", "High": "PropPassHigh"}, inplace=True)

     #...and the proportion from each body part (no normalization from dead balls though)
    # df["Left"] = df["Left"]/df["Live"]
    # df["Right"] = df["Right"]/df["Live"]
    # df["Head"] = df["Head"]/df["Live"]
    ###########

    df.rename(columns={"Live": "TotPassAtt", }, inplace=True)

    # Drop columns we won't need anymore
    df.drop(columns=[ 'Cmp', 'TB',  'FK'], inplace=True) 
    
    return df

def gca_preprocess(df, scale):
    '''Preprocess 'Goal and shot creation' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns
        - df: processed dataframe
        '''
    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    # SCA, GCA already per-90'ed
    df.drop(columns = ['SCA', 'GCA'], inplace=True)

    # Dead ball things to drop
    df.drop(columns = ['PassDead', 'Fld', 'PassDead.1', 'Fld.1', 'PassLive.1', 'Drib.1', 'Sh.1', 'Fld.1', 'Def.1'], inplace=True)

    # executing the per-90 function on relevant stats
    df[["PassLive", "Drib", "Sh", "Def", ]] = df[["PassLive", "Drib", "Sh", "Def"]].apply(lambda x: x/games)
    df.rename(columns ={"PassLive": "Shot-Creating Pass/90", "Drib": "Shot-Creating Drib/90",  "Sh": "Shot-CreatingSh/90", "Def": "Shot-Creating Def/90"}, inplace=True)

    # Drop certain GC stats:low numbers, and seems irrelevant (adding here so it can potentially be commented out) 
    df.drop(columns=['GCA90'], inplace=True) 
    
    return df 


def possession_preprocess(df, scale):
    '''Preprocess 'Possession' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns
        - df: processed dataframe
        '''
    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    if scale == 'team': 
        # Make % between 0-1
        df[["Poss"]] = df[["Poss"]].apply(lambda x: x/100)
        df['OppPoss'] = 1 - df['Poss']

    # Make % between 0-1
    df[["Succ%"]] = df[["Succ%"]].apply(lambda x: x/100)
    df.rename(columns={"Succ%": "DribSucc%"}, inplace=True)
    
    
    # Stats to drop (either taken into account, irrelevant or too small to matter)
    df.drop(columns = ["Touches", "Live" ], inplace=True)

    # executing the per-90 function on relevant stats
    df[['Succ', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen', 'Att',
     'Mis', 'Dis', 'Rec',]] = df[['Succ', 'Def Pen', 'Def 3rd',
      'Mid 3rd', 'Att 3rd', 'Att Pen', 'Att', 'Mis', 'Dis',  'Rec']].apply(lambda x: x/games)


    # Touches per area don't add up to total touches stat. Add them up, then normalize so it's
    # proportion of actions at each location; Also think "Pen" touches are taken from that third, 
    # so subtract "Pen" touches from that area.
    # (Dead ball touches is included in here? 

    total_touches = df['Def 3rd'] + df['Mid 3rd'] + df['Att 3rd']
    df["Def 3rd"] = df["Def 3rd"] - df["Def Pen"] 
    df["Att 3rd"] = df["Att 3rd"] - df["Att Pen"]
    df[['Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen']] =  df[['Def Pen', 'Def 3rd', 
    'Mid 3rd', 'Att 3rd', 'Att Pen']].apply(lambda x: x/total_touches)
    df.rename(columns={'Def Pen': 'Prop Def Pen Touches', 'Def 3rd': 'Prop Def 3rd Touches', 'Mid 3rd': 'Prop Mid 3rd Touches', 
    'Att 3rd': 'Prop Att 3rd Touches', 'Att Pen': 'Prop Att Pen Touches'},inplace=True)
    df['TotalTouches'] = total_touches

    df['Mis'] = df['Rec']/df['Mis'] 
    df.rename(columns={'Mis': 'RecPass/Misplayed'},inplace=True)
    
    # And some receiving normalizing
    df['Prog'] = df['Prog']/df['Rec'] 
    df.rename(columns={'Prog.1': 'PropPassProg', 'Att': 'AttDribbles', 'Prog':'PropPassRecProg'},inplace=True)
    # Drop columns we won't need anymore
    df.drop(columns=['Succ', 'Rec'], inplace=True) 
    
    return df
 
def defense_preprocess(df, scale):
    '''Preprocess 'Defensive actions' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns￼￼
        - df: processed dataframe
        '''
    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    # Stats to drop (either taken into account, or too small to matter)
    df.drop(columns = [], inplace=True)

    # executing the per-90 function on relevant stats
    df[["Tkl", "TklW", "Def 3rd", "Mid 3rd", "Att 3rd", "Att",  "Blocks", "Sh", "Pass", "Int", "Clr"]] = df[["Tkl", "TklW", "Def 3rd", "Mid 3rd", "Att 3rd", 
    "Att", "Blocks", "Sh", "Pass", "Int", "Clr"]].apply(lambda x: x/games)

    # Find proportion of actions at each location
    df['TklW'] = df['TklW']/df['Tkl']
    df['Def 3rd'] = df['Def 3rd']/df['Tkl']
    df['Mid 3rd'] = df['Mid 3rd']/df['Tkl']
    df['Att 3rd'] = df['Att 3rd']/df['Tkl']
    
    # Make between 0-1
    df[["Tkl%"]] = df[["Tkl%"]].apply(lambda x: x/100)
    
    # Find proportions of each type of block (either pass or shot)
    df["Pass"] = df["Pass"]/df["Blocks"]
    df["Sh"] = df["Sh"]/df["Blocks"]
    
    df.rename(columns ={"TklW": "Tkl%", "Def 3rd": "PropTkl Def 3rd", "Mid 3rd": "PropTkl Mid 3rd", "Att 3rd": "PropTkl Att 3rd",
     "Att": "DribTkl", "Tkl%": "DribTkl%",  "Sh": "PropBlockSh", "Pass": "PropBlockPass"}, inplace=True)
    
    # Drop columns we won't need anymore
    df.drop(columns=['Tkl+Int', 'Tkl.1',  'Err'], inplace=True) 
    
    return df 

def playingtime_preprocess(df, scale):
    '''Preprocess 'Playing time' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns￼￼
        - df: processed dataframe
        '''

    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    # executing the per-90 function on relevant stats
    df[["onG", "onGA", "onxG", "onxGA"]] = df[["onG", "onGA", "onxG", "onxGA"]].apply(lambda x: x/games)
    
    # Find g-xg diff
    df["onG-xG"] = df['onG'] - df['onxG']
    df["onGA-xGA"] = df['onGA'] - df['onxGA']
    df["G-xG+/-"] = df['+/-'] - df['xG+/-']

    # Stats to drop (either taken into account, or too small to matter)
    df.drop(columns = ['MP', 'Min', 'Mn/MP', 'Min%', 'Compl',
    'Subs', 'Mn/Sub', 'unSub', 'PPM', '+/-', 'xG+/-'], inplace=True)

    # All stats are per-90 normalized, so remove that from label
    df.rename(columns={'+/-90': '+/-', 'xG+/-90': 'xG+/-'}, inplace=True)

    if scale == 'individual':
        df.drop(columns={'On-Off.1'}, inplace=True)

    return df 


def misc_preprocess(df, scale):
    '''Preprocess 'Miscellaneous' stat from soccersite
    Parameters:
        - df: dataframe of Statsbomb statistical data taken from soccersite 
    Returns￼￼
        - df: processed dataframe
        '''
    
    # Processing that is common to all dataframes 
    games = common_preprocess(df, scale)

    # Stats to drop (either taken into account, or too small to matter)
    # OG could be interesting, but there are so few that it could skew results
    df.drop(columns = ['2CrdY', 'CrdR', 'Crs', 'Int', 'TklW', 'OG'], inplace=True)
    
    # executing the per-90 function on relevant stats
    df[["Fls", "Fld", "Off", "PKwon", "PKcon", "Recov", "Won", "Lost", ]] = df[["Fls", "Fld", "Off", "PKwon", 
    "PKcon", "Recov", "Won", "Lost"]].apply(lambda x: x/games)
    df.rename(columns={"Off": "TimesOffside"}, inplace=True) #Change stat name that comes up repeateedly 
    
    # Turn % into number between 0-1
    df[["Won%"]] = df[["Won%"]].apply(lambda x: x/100)
    df.rename(columns={"Won%": "DuelWin%"}, inplace=True)

    # Find total number of aerial duels
    df['AerialDuels'] = df['Won'] + df['Lost'] 

    # Stats to drop (either taken into account, or too small to matter)
    df.drop(columns = ['Won', 'Lost'], inplace=True)
    
    # All stats are per-90 normalized, so remove that from label
    df.rename(columns={'+/-90': '+/-', 'xG+/-90': 'xG+/-'}, inplace=True)

    return df


##### Data Processing #####
# Need to process for each scale, league and stat...
scales = ['team', 'individual']
leagues = ['La-Liga', 'Premier-League', 'Ligue-1', 'Bundesliga',  'Serie-A', 'Major-League-Soccer', 'Eredivisie', 'Primeira-Liga', 'Championship', 'Liga-MX']
stats = ['shooting', 'passing', 'passing_types', 'gca', 'possession', 'defense', 'playingtime', 'misc']

scale_frames = []
for scale in scales:
    league_frames = []
    for league in leagues: 
        stat_frames = []
        for stat in stats:
            # Below, account for MLS being in one calendar year. Only using one year of data, so not generalizing
            if (league == 'Major-League-Soccer'):   
                df = pd.read_csv(f"../../data/raw/{scale}/{league}-2022-{scale}-{stat}.csv")
            else:
                df = pd.read_csv(f"../../data/raw/{scale}/{league}-2021-2022-{scale}-{stat}.csv")
            func = 'processed_df = '+stat+'_preprocess(df, scale)' # Allows us to call unique function for each stat
            exec(func)
            # Add league to the dataframe
            processed_df.insert(1, 'League', league)
            stat_frames.append(processed_df)
        if (scale == 'team'):
            league_df = stat_frames[0].merge(stat_frames[1], on =['Squad', 'League', '90s' ]).merge(stat_frames[2], on = ['Squad', 'League', '90s' ])\
                .merge(stat_frames[3], on = ['Squad', 'League', '90s' ]).merge(stat_frames[4], on = ['Squad', 'League', '90s' ]).merge(stat_frames[5], on = ['Squad', 'League', '90s' ])\
                    .merge(stat_frames[6], on = ['Squad', 'League', '90s' ]).merge(stat_frames[7], on = ['Squad', 'League', '90s' ])
        elif (scale == 'individual'): 
            league_df = stat_frames[0].merge(stat_frames[1], on =['Player', 'Nation', 'Pos', 'Squad', 'Born', '90s', 'League' ]).merge(stat_frames[2], on =['Player', 'Nation', 'Pos', 'Squad', 'Born', '90s', 'League' ])\
                .merge(stat_frames[3], on =['Player', 'Nation', 'Pos', 'Squad', 'Born', '90s', 'League' ]).merge(stat_frames[4], on =['Player', 'Nation', 'Pos', 'Squad', 'Born', '90s', 'League' ])\
                .merge(stat_frames[5], on =['Player', 'Nation', 'Pos', 'Squad', 'Born', '90s', 'League' ]).merge(stat_frames[6], on =['Player', 'Nation', 'Pos', 'Squad', 'Born', '90s', 'League' ])\
                .merge(stat_frames[7], on =['Player', 'Nation', 'Pos', 'Squad', 'Born', '90s', 'League' ])
        league_frames.append(league_df)
        final_df = pd.concat(league_frames, ignore_index=True, sort=False)
    scale_frames.append(final_df) # This will be a list with two elements: team data and individual data

team_df = scale_frames[0]
ind_df = scale_frames[1]
team_df.to_csv("../../data/processed/processed_team_data.csv")
ind_df.to_csv("../../data/processed/processed_ind_data.csv")
