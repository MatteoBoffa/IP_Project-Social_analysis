import pandas as pd 
import numpy as np

to_analyse = pd.read_csv("Centroids_census.csv")
dict_cluster_1 = {}
for price,cluster in zip(to_analyse["U_MED"], to_analyse["cluster_id"]):
	if cluster not in dict_cluster_1.keys():
		dict_cluster_1[cluster] = [price]
	else:
		dict_cluster_1[cluster].append(price)
avg_cluster={}
for key in dict_cluster_1.keys():
	avg_cluster[key] = np.mean(dict_cluster_1[key])
	print(f"{key}){np.mean(dict_cluster_1[key])}")