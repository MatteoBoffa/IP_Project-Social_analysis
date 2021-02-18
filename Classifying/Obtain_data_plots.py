import pandas as pd 
import numpy as np

UNDER_STUDY = "Weekends_Only"

INPUT_PATH = "./After_elaboration/"+UNDER_STUDY+"/Modified/"
files = ["Flickr_final.xls", "Instagram_final.xls"]

list_convertor = ["Palaces","Miscellaneous","Food","Facilities","Natural_views",\
					"Animals","Shopping","Transportation","Urbanscape",\
					"Exhibits","Religion","Residence","Entertainment","People"]

dict_traslator = {}
for it in range(len(list_convertor)):
	dict_traslator[it+1]=list_convertor[it]

dict_classes = {}
dict_tot_photos = {}

for file in files:
	to_analyse = pd.read_csv(INPUT_PATH+file).to_numpy()
	for point in to_analyse:
		id_point = point[0]
		label = point[-1]
		try:
			predictions = point[1].split(",")
			if label not in list(dict_classes.keys()):
				dict_classes[label] = {}
				dict_tot_photos[label] = 1
			else:
				dict_tot_photos[label] += 1
			for pred in predictions:
				main_class = pred.split(":")[0].strip()
				prob = float(pred.split(":")[1].strip())
				if main_class not in dict_classes[label]:
					dict_classes[label][main_class] = prob
				else:
					dict_classes[label][main_class] += prob
		except:
			print(f"No prob available for id {id_point}")

tot_per_zone = {}
for zone in dict_classes.keys():
	sum_class = 0
	for main_class in dict_classes[zone].keys():
		sum_class += dict_classes[zone][main_class]
	tot_per_zone[zone] = sum_class	

	
to_export = {
	"lat":[],
	"lng":[],
	"id":[],
	"cluster_id":[],
	"[photos]":[]
}

for el in list_convertor:
	to_export[el]=[]

to_analyse = pd.read_csv(INPUT_PATH+files[0]).to_numpy()

for point in to_analyse:
	to_export["id"].append(point[0])
	to_export["cluster_id"].append(point[-1])
	to_export["lat"].append(point[2])
	to_export["lng"].append(point[3])
	for it, main_class in enumerate(list_convertor):
		try:
			to_export[main_class].append(dict_classes[point[-1]][str(it+1)])
		except:
			to_export[main_class].append(0)

	to_export["[photos]"].append(dict_tot_photos[point[-1]])

output_dataframe = pd.DataFrame.from_dict(to_export)
output_dataframe.to_csv("./To_Plot/"+UNDER_STUDY+"/summary.csv", index = False)



