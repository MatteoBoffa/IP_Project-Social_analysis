import pandas as pd 
import math 

INPUT_PATH = "./Weekends_Only/"

files = [INPUT_PATH+"Flickr_final.xls", INPUT_PATH+"Instagram_final.xls"]
columns = ["ids", "predictions", "lat", "lng", "CLUSTER_ID"]
for file in files:

	to_modify = pd.read_csv(file).drop(["field_1"], axis = 1)
	labels = set(to_modify["label"])
	clusters = [x for x in set(to_modify["CLUSTER_ID"]) if not math.isnan(x)]
	max_cluster = max(clusters)
	most_numerous_label = ""
	for label,cluster in zip(to_modify["label"],to_modify["CLUSTER_ID"]):
		if not math.isnan(cluster):
			most_numerous_label = label
	labels.remove(most_numerous_label)
	dict_labels = {}
	for additive_index, label in enumerate(labels):
		dict_labels[label] = max_cluster+additive_index+1

	for index, row in to_modify.iterrows():
		if row["label"] in dict_labels.keys():
			to_modify.at[index,'CLUSTER_ID'] = dict_labels[row["label"]]


	to_modify.drop("label", axis = 1, inplace = True)
	to_modify.to_csv(file, columns = columns, index = False) 
	print(f" ******** {file} modified and saved ********")