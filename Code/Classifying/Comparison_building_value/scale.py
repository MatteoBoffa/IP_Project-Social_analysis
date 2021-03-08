import pandas as pd 
import numpy as np

to_analyse = pd.read_csv("centroidi.csv")
dict_cluster_1 = {}
for price,cluster in zip(to_analyse["Avg_price"], to_analyse["cluster_id"]):
	if cluster not in dict_cluster_1.keys():
		dict_cluster_1[cluster] = [price]
	else:
		dict_cluster_1[cluster].append(price)
avg_cluster={}
for key in dict_cluster_1.keys():
	avg_cluster[key] = np.mean(dict_cluster_1[key])

mini = np.min(list(avg_cluster.values()))
maxi = np.max(list(avg_cluster.values()))
mean = np.mean(list(avg_cluster.values()))
std = np.std(list(avg_cluster.values()))

list_to_sort = []
for key in dict_cluster_1.keys():
	avg_cluster[key] = (avg_cluster[key] - mean)/(std)
	list_to_sort.append((key,avg_cluster[key]))
list_to_sort.sort(key = lambda x: x[1])
for el in list_to_sort:
	print(el[0],el[1])
"""
mini = np.min(list(avg_cluster.values()))
maxi = np.max(list(avg_cluster.values()))

for key in dict_cluster.keys():
	avg_cluster[key] = (avg_cluster[key] - mini)/(maxi-mini)
	print(key, avg_cluster[key])
"""
print()
to_analyse = pd.read_csv("vince.csv")
dict_cluster = {}
for score,cluster in zip(to_analyse["cadastre"], to_analyse["cluster"]):
	if cluster in dict_cluster_1.keys():
		dict_cluster[cluster] = score

mean = np.mean(list(dict_cluster.values()))
std = np.std(list(dict_cluster.values()))
list_to_sort = []
for key in dict_cluster.keys():
	dict_cluster[key] = (dict_cluster[key] - mean)/(std)
	list_to_sort.append((key,dict_cluster[key]))
list_to_sort.sort(key = lambda x: x[1])
for el in list_to_sort:
	print(el[0],el[1])

"""
mini = np.min(list(dict_cluster.values()))
maxi = np.max(list(dict_cluster.values()))
for key in dict_cluster.keys():
	dict_cluster[key] = (dict_cluster[key] - mini)/(maxi-mini)
	print(key, dict_cluster[key])
"""