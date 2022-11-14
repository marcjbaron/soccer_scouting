Clustering Professional Soccer Players by Play Style
=======================================================================

An attempt to compare similar players and playing styles using event-based data in 10 professional soccer leagues. There were two goals:

1. Given a selected player, find a list of players who are most similar in terms of play-style (as determined by the gathered statistics).

2. Create clusters (groups) of players who play with a similar play-style, and identify that play-style in an intuitive way.

Data was gathered from a football statistics website and various unsupervised learning algorithms were used to create the clusters of players with similar statistical profiles. Also created a [Streamlit web application](https://marcjbaron-soccer-scouting-streamlit-app-n4gmux.streamlit.app/) which allows you to search for a player in the included leagues and find players who are similar to that player. 

The project is similar in scope to [The Athletic's player roles](https://theathletic.com/3473297/2022/08/10/player-roles-the-athletic/), which also used 
similar techniques. 


This project was initially built as the final project in the Data Science bootcamp at Lighthouse Labs.

## Using this repo

See the *Environment_Instructions.txt* file for details about how to set-up your environent. 

* Collect the data from the website with the file *src/data/collect_data.py*. (*The urls have been changed due to data usage reasons*)

* Data clean-up happens with the file *src/features/build_features*. Exploration of this data-set happens in *notebooks/Data_Exploration_and_Normalization.ipynb* 

* Use Sci-kit learn standardizers in *src/features/transform_features.py*

* Exploration of different dimensionality reduction algorithms (including final model) in *notebooks/PtII-Dimensionality_reduction.ipynb*

* Analysis of different clustering algorithms in *notebooks/PtIII-Cluster_analysis.ipynb*

## Results

The final clusters looked like the following:

![Clusters without pressing data](https://github.com/marcjbaron/soccer_scouting/blob/main/reports/figures/cluster_map_opta_annotated.png)

The clusters are, for the most part, delineated into the most common location of that player on the pitch:

![Player cluster map](https://github.com/marcjbaron/soccer_scouting/blob/main/reports/figures/clusters_pitch.png "Explanatory purposes only; this wasn't determined through analysis")


With a different dataset that included player pressing data, there were small changes to the shape of the clusters, and more clusters were identified:

![Clusters with pressing data](https://github.com/marcjbaron/soccer_scouting/blob/main/reports/figures/cluster_map_annotated_sb.png)

The final clusters were determined by taking around 50 event-based statistical actions and reducing those actions to a 2-dimensional graph using a technique called [UMAP](https://umap-learn.readthedocs.io/en/latest/clustering.html). The resulting data was then organized into\
clusters using a technique called [spectral clustering](https://www.kaggle.com/code/vipulgandhi/spectral-clustering-detailed-explanation). Other techniques were considered, but these gave (i) the best scores on various clustering metrics (Silhouette Score, Davies-Boulding Score, Calinsko-Harabasz), and (ii) gave intuitive results that could be related to knowledge of what a player actually does on the pitch. 


## Future Work

* Use player tracking data to see where actions are taken on the pitch to see if there are finer-grained clusters that can be found (*e.g.* a player who makes a majority of their on-ball actions in one area of the pitch, but a majority of their defensive actions take place elsewhere).
* Create initial clusters based on location-based statistics only, then cluster again based on locationless events 
* Add player contract information 




