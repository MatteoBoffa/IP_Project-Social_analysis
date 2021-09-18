import pandas as pd 
import math 
import os
import sys

interesting_files = ["Flickr_final.csv", "Instagram_final.csv"]
columns_input = ["ids", "predictions", "lat", "lng", "label", "CLUSTER_ID"] #ORDER CRUCIAL!
columns_to_modify = {"lon":"lng","id":"ids"}

DIRECTORY_TO_ANALYSE = os.getcwd()

for directory in os.listdir(DIRECTORY_TO_ANALYSE):
	if directory!=sys.argv[0] and directory!="Center":
		INPUT_PATH = DIRECTORY_TO_ANALYSE+"/"+directory+"/Not_Modified/"
		OUTPUT_PATH = DIRECTORY_TO_ANALYSE+"/"+directory+"/Modified/"
		if not os.path.exists(OUTPUT_PATH):
			os.makedirs(OUTPUT_PATH)
		files = os.listdir(INPUT_PATH)
		for file in files:
			if file in interesting_files:
				to_modify = pd.read_csv(INPUT_PATH+file)
				for column in to_modify.columns:
					if column in columns_to_modify.keys():
						to_modify = to_modify.rename({column: columns_to_modify[column]}, axis=1)
				for column in to_modify.columns:
					if column not in columns_input:
						to_modify.drop(column, axis=1, inplace=True)
				labels = set(to_modify["label"])
				if -1 in labels:
					labels.remove(-1) #Remove noise
				clusters = [x for x in set(to_modify["CLUSTER_ID"]) if not math.isnan(x)]
				max_cluster = max(clusters)
				most_numerous_label = ""
				for label,cluster in zip(to_modify["label"],to_modify["CLUSTER_ID"]):
					if not math.isnan(cluster):
						most_numerous_label = label
						break
				labels.remove(most_numerous_label)

				dict_labels = {}
				for additive_index, label in enumerate(labels):
					dict_labels[label] = max_cluster+additive_index+1

				for index, row in to_modify.iterrows():
					if row["label"] in dict_labels.keys():
						to_modify.at[index,'CLUSTER_ID'] = dict_labels[row["label"]]
					elif row["label"] == -1:
						to_modify.drop(index, inplace=True)

				to_modify.to_csv(OUTPUT_PATH+file, columns = columns_input, index = False) 
				
				print(f" ******** {OUTPUT_PATH+file} modified and saved ********")
				