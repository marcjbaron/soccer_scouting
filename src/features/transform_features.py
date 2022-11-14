import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer
from sklearn.compose import ColumnTransformer

import pickle


df = pd.read_csv("../../data/processed/sb_individual.csv")
player_data = df[['Player', 'League', 'Nation', 'Pos', 'Squad', 'Born', '90s']]

# Drop identifying columns
df.drop(columns = ['Unnamed: 0', 'Player', 'League', 'Nation', 'Pos', 'Squad', 'Born', '90s'], inplace=True)

# Add goal/assist stats to their own df
GA_stats = df[['Gls/90', 'np:G-xG', 
          'xA',  'onG', 'onGA', '+/-',
           'On-Off', 'onxG', 'onxGA', 'xG+/-', 'onG-xG', 'onGA-xGA', 'G-xG+/-' ]]
df.drop(columns = ['Gls/90', 'np:G-xG', 'Sh/90',
          'xA', 'xAG', 'A-xAG',  'onG', 'onGA', '+/-',
           'On-Off', 'onxG', 'onxGA', 'xG+/-', 'onG-xG', 'onGA-xGA', 'G-xG+/-'], inplace=True) # Removing data here is late addition

# Drop these columns in data collection
df.drop(columns = [ 'Mn/Start', 'Ast', 'Past', 'Starts', 'TimesOffside'], inplace=True)


# Stats that are scaled were determined by inspecting initially processed data. Justification for scaling was:
# StandardScaler - Normal-like values with large magnitude 
# Min-MaxScaler - Non-normal relatively even distributions
# RobustScaler - data with large (albeit useful) outliers
stdscale_list = ['AvgShotDist', 'npxG/Sh', 'TotDist/pass', 'PrgDist/Pass', 'PropShort', 'PropMed', "PropLong", 'Long%', "PropFinalThirdPasses", 
    'TotPassAtt',  'TotalTouches', 'Tkl', 'PropTkl Def 3rd', 'PropTkl Mid 3rd', 'DribTkl',  'Blocks', 'Int',  'Fld', 'DribSucc%',
     'Recov', 'DuelWin%', 'DribTkl%', 'Prop Mid 3rd Touches']
minmax_list = ['Fls', 'Prop Def Pen Touches', 'Prop Att 3rd Touches', 'Prop Def 3rd Touches' ]
rbst_list = [] 
power_list = ['npxG/90', 'PropAssistShots', 'PropPassinPA', 'PropCrossinPA', 'Short%', 'Med%', "PropPassBlocked", "Dis",
    'Sw', 'Crs', 'Shot-CreatingSh/90', 'Shot-Creating Drib/90', 'Shot-Creating Pass/90',
     'Prop Att Pen Touches', 'AttDribbles',  'PropPassRecProg', 'PropTkl Att 3rd', 'PropBlockSh','PropBlockPass', 'Clr', 'AerialDuels', 
     'RecPass/Misplayed', 'TI']

## Need way to extract colunmns after transform (new order is transformed columns first, passthrough columns after)
original_df = df.copy()
original_df.drop(columns=stdscale_list, inplace=True)
original_df.drop(columns=minmax_list, inplace=True)
original_df.drop(columns=rbst_list, inplace=True)
original_df.drop(columns=power_list, inplace=True)

# Create list of column names with new order after transformations 
transformed_columns = stdscale_list + minmax_list + rbst_list + power_list + original_df.columns.to_list() 

#Do the transformations
cltr = ColumnTransformer(
    transformers =[('mean_scaling', StandardScaler(),stdscale_list  ),
    ('min-max_scaling', MinMaxScaler(), minmax_list  ),
    ("outlier_scaling", RobustScaler(), rbst_list  ),
    ("frequent_zeros", PowerTransformer(method='yeo-johnson'), power_list  )],
    remainder='passthrough')

df_trans = cltr.fit_transform(df)

# transform_data = {'Columns': transformed_columns, "Data": df_trans}
transform_data = [transformed_columns,  df_trans]
# Save the data to a different file for later reloading (pickle so we can easily extract the list)
pickle.dump(transform_data, open('../models/transformed_opta_data.p', "wb"))
