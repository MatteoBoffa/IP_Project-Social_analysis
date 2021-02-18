import pandas as pd 
import math 

INPUT_PATH = "./Weekends_Only/Not_Modified/"
OUTPUT_PATH = "./Weekends_Only/Modified/"

files = ["Flickr_final.xls", "Instagram_final.xls"]
columns = ["ids", "predictions", "lat", "lng", "label", "CLUSTER_ID"]

for file in files:
	to_modify = pd.read_csv(INPUT_PATH+file).drop(["field_1"], axis = 1)
	labels = set(to_modify["label"])
	clusters = [x for x in set(to_modify["CLUSTER_ID"]) if not math.isnan(x)]
	max_cluster = max(clusters)
	most_numerous_label = ""
	for label,cluster in zip(to_modify["label"],to_modify["CLUSTER_ID"]):
		if not math.isnan(cluster):
			most_numerous_label = label
			break
	labels.remove(most_numerous_label)
	labels.remove(-1)

	dict_labels = {}
	for additive_index, label in enumerate(labels):
		dict_labels[label] = max_cluster+additive_index+1

	for index, row in to_modify.iterrows():
		if row["label"] in dict_labels.keys():
			to_modify.at[index,'CLUSTER_ID'] = dict_labels[row["label"]]
		elif row["label"] == -1:
			to_modify.drop(index, inplace=True)

	to_modify.to_csv(OUTPUT_PATH+file, columns = columns, index = False) 
	print(f" ******** {OUTPUT_PATH+file} modified and saved ********")