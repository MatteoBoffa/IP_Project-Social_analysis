import pandas as pd 
import numpy as np
import os
import matplotlib.pyplot as plt
from haversine import haversine,Unit
np.seterr('raise')

#GLOBAL VARIABLES
################################################################################
list_convertor = ["Palaces","Miscellaneous","Food","Facilities","Natural_views",\
					"Animals","Shopping","Transportation","Urbanscape",\
					"Exhibits","Religion","Residence","Entertainment","People"] 
list_culturals = ["Palaces","Exhibits","Religion"]
list_attractions = ["Palaces","Exhibits","Religion","Food","Shopping"]
list_cadastre = ["Palaces", "Shopping", "Transportation", "Natural_view"]
dict_traslator = {}
for it in range(len(list_convertor)):
	dict_traslator[it+1]=list_convertor[it]
	#EACH CLASS WILL HAVE AN IDENTIFYING NUMBER (i.e: 'Palaces' = 1)

#FIELDS TO EXPORT AND PLOT ON QGIS
to_export = {
	"lat":[],
	"lng":[],
	"cluster_id":[],
	"[photos_per_coordinates]":[],
	"[photos_per_cluster]":[],
	"cultural":[],
	"turist_attr":[],
	"cadastre":[]
} 
for el in list_convertor:
	to_export[el]=[]

colors = ["#7D0000","#FF0000","#FB7756","gold","#1AC0C6",\
			"#1A1B4B","#3E4491","#3A9EFD","#8C61FF","#DDACF5",\
			"steelblue","#454D66","#58B368","#DAD873"]
dict_color = {} #WANT TO ASSIGN A UNIQUE COLOR FOR EACH CLASS
for color, main_class in zip(colors,list_convertor):
	dict_color[main_class] = color

################################################################################

#FUNCTIONS
################################################################################
def obtain_perception(file, perception_zones, points_per_zone):
	to_analyse = pd.read_csv(file).to_numpy()
	for point in to_analyse:
		id_point = point[0]
		cluster_id = point[-1] 
		lat = point[-4]
		lng = point[-3]
		try: #Some point might be missing the prediction
			predictions = point[1].split(",")
			if cluster_id not in list(perception_zones.keys()): 
			#if that zone was never considered, configure an instance
				perception_zones[cluster_id] = {}
				points_per_zone[cluster_id] = {
				"lats":[],
				"lngs":[]
				}
			points_per_zone[cluster_id]["lats"].append(lat)
			points_per_zone[cluster_id]["lngs"].append(lng)
			#Since we kept the best three, now it's time to analyse them!
			for pred in predictions:
				main_class = pred.split(":")[0].strip()
				prob = float(pred.split(":")[1].strip())
				#Again, consider whether that macro_class has been already used or not
				if main_class not in perception_zones[cluster_id]:
					perception_zones[cluster_id][main_class] = prob
				else:
					perception_zones[cluster_id][main_class] += prob
		except Exception as e:
			#print(e)
			print(f"No prob available for id {id_point}")	
	return perception_zones,points_per_zone	

def plot_results(perception_zones, points_per_zone, OUTPUT_PICTURE):
	fig, ax= plt.subplots()
	#Variables useful for creating the graph	
	list_bars_per_zone = []
	list_total_per_zone = []
	zones = [int(el) for el in list(perception_zones.keys())]
	for it,zone in enumerate(zones):
		#USEFUL TO GET THE BARS ORDERED EQUALLY (SAME ORDER OF CLASSES)
		#(since cannot order dictionary...)
		perception_per_zone = perception_zones[zone]
		list_classes_ordered = [(key,value) for key,value in zip(perception_per_zone.keys(), perception_per_zone.values())]
		list_classes_ordered.sort(key = lambda x:int(x[0])) #From class 1 (palaces) to 14
		tot_score_zone = np.sum(list(perception_zones[zone].values()))
		left = 0 #PARAMETER WHICH ALLOWS THE REPRESENTATION (SPACE ON THE LEFT OF EACH BAR)

		for tuple in list_classes_ordered:
			main_class = tuple[0]
			score_class = tuple[1]
			#Normalizing over the total score
			probability_class = score_class/tot_score_zone*100 
			#Creating the horizontal bar
			bar = ax.barh(zone, probability_class,\
			 left = left, color = dict_color[dict_traslator[int(main_class)]])
			#If probability > 10%, also annotating the bar!
			if probability_class > 10:
				for r in bar:
					width, height =r.get_width(),r.get_height()
					x=r.get_x()+width/2
					y=r.get_y()+height/2
					ax.annotate('{:.1f}%'.format(probability_class), \
						xy=(x,y), \
						xytext=(0, 0), \
						textcoords="offset points", \
						ha='center', va='center', color = "w", size=10, weight='bold')
			left = left + probability_class
		if it == 0: #If it is the first zone we are considering
			list_bars_per_zone.append(len(perception_zones[zone].keys()))
		else:
			last_el = list_bars_per_zone[-1]
			list_bars_per_zone.append(last_el+len(perception_zones[zone].keys()))	
		#Saving total number of pictures on a list (will be useful later)			
		list_total_per_zone.append(len(points_per_zone[zone]["lats"]))  
	#AIMS AT ADDING THE TOTAL NUMBER OF PICTURES INFO
	it_list_bars = 0
	for it,p in enumerate(ax.patches):
		if (it+1) % list_bars_per_zone[it_list_bars] == 0:
			percentage ='{}'.format(list_total_per_zone[it_list_bars]).rjust(5,"\t").replace("\t","  ")
			width, height =p.get_width(),p.get_height()
			x=p.get_x()+width+0.5
			y=p.get_y()+height/2
			ax.annotate(percentage,(x,y), ha='left', va='center', size=16)
			it_list_bars+=1
	#DEFINING AXES AND LEGEND
	plt.legend(dict_traslator.values(), ncol=7,	
	loc='upper center', bbox_to_anchor=(0.5, 1.125), fontsize = 10)
	ax2 = ax.twinx()
	ax2.set_ylabel('[Photo taken]', fontsize = 20)
	ax.tick_params(labelsize=16)
	ax.set_xlabel("Percentages [%]", fontsize = 20)
	ax.set_ylabel("Zones", fontsize = 20)
	ax.set_yticks([x for x in range(len(zones))])
	ax2.margins(0.1)
	plt.setp(ax2.get_yticklabels(), visible=False)
	plt.savefig(OUTPUT_PICTURE)

def export_file(file_input, perception_zones, points_per_zone, density_per_zone, file_output):
	to_analyse = pd.read_csv(file_input).to_numpy()
	#tot_per_zone = find_total_score(perception_zones) #IN CASE WE WANT TO USE WEIGHTED SCORES
	dict_point = obtain_stats_coordinate(to_analyse,perception_zones,density_per_zone,points_per_zone)
	to_export = create_dataframe_export(dict_point)
	output_dataframe = pd.DataFrame.from_dict(to_export)
	output_dataframe.to_csv(file_output, index = False)

def create_dataframe_export(dict_point):
	for key in dict_point.keys():
		lat = key.split(" ")[0]
		lng = key.split(" ")[1]
		to_export["lat"].append(lat)
		to_export["lng"].append(lng)
		to_export["[photos_per_coordinates]"].append(dict_point[key]["[photos_per_coordinates]"])
		to_export["[photos_per_cluster]"].append(dict_point[key]["[photos_per_cluster]"])
		to_export["cluster_id"].append(dict_point[key]["cluster_id"])	
		for main_class in list_convertor:	
			to_export[main_class].append(dict_point[key][main_class])
		to_export["cultural"].append(dict_point[key]["cultural"])
		to_export["turist_attr"].append(dict_point[key]["turist_attr"])
		to_export["cadastre"].append(dict_point[key]["cadastre"])

	return to_export

def obtain_stats_coordinate(to_analyse,perception_zones, density_per_zone,points_per_zone):
	dict_point = {} #each point with the same coordinates will be counted only once
	for point in to_analyse:
		lat = point[2]
		lng = point[3]
		key = str(lat)+" "+str(lng)
		if key not in dict_point.keys():
			dict_point[key] = {}
			dict_point[key]["[photos_per_coordinates]"] = 1
			dict_point[key]["cluster_id"] = point[-1]
			#NOW EVALUATING FEATURES WHICH REGARDS THE CLUSTER TO WHICH THE POINT IS ASSIGNED
			score_cultural = 0 
			score_attr = 0
			score_cadastre = 0
			for it, main_class in enumerate(list_convertor): #CONSIDERING EACH MAIN CLASS'S SCORES
				try:
					#EXTRACTING THE IT+1 MAIN CLASS SCORE OF THE CLUSTER TO WHICH THE POINT BELONGS
					score = perception_zones[point[-1]][str(it+1)]/density_per_zone[point[-1]]
				except Exception as e: #IF THAT CLASS IS NOT PRESENT IN THE CLUSTER
					score = 0
				dict_point[key][main_class] = score
				if main_class in list_culturals:
					score_cultural+=score
				if main_class in list_attractions:
					score_attr+=score
				if main_class in list_cadastre:
					score_cadastre+=score
			dict_point[key]["[photos_per_cluster]"] = len(points_per_zone[point[-1]]["lats"])
			dict_point[key]["cultural"] = score_cultural
			dict_point[key]["turist_attr"] = score_attr
			dict_point[key]["cadastre"] = score_cadastre
		else:
			dict_point[key]["[photos_per_coordinates]"]+=1
	return dict_point

def find_total_score(perception_zones):
	tot_per_zone = {}
	for zone in perception_zones.keys():
		sum_class = 0
		for main_class in perception_zones[zone].keys():
			sum_class += dict_classes[zone][main_class]
		tot_per_zone[zone] = sum_class
	return tot_per_zone	
	
def process_data(perception_zones, points_per_zone):
	#INDEX TO WEIGHT HOW CONFIDENT WE ARE WITH THE ZONES PREDICTION -> INTER-ZONAL COMPARISON!
	density_per_zone = evaluate_density(perception_zones, points_per_zone) 
	return density_per_zone


def evaluate_density(perception_zones, points_per_zone):
	density_per_zone = {}
	for zone in points_per_zone.keys():
		#UNIQUE SET OF POINTS 
		#	NOT CONSIDERING REPETITIONS SINCE THE COORDINATES ARE THE SAME -> NOT HELPFUL TO EXPLORE DENSITY
		points = set() 
		for lat,lng in zip(points_per_zone[zone]["lats"],points_per_zone[zone]["lngs"]):
		    points.add((float(lat),float(lng)))
		if len(points)!=1:
			points = sorted(points, key = lambda x: (x[0], x[1])) #ORDERING ON LATITUDE AND LONGITUDE
			distances = []
			for i in range(len(points)-1): 
				point_1=points[i]
				point_2=points[i+1]
				distance=haversine(point_1,point_2,Unit.KILOMETERS) #DISTANCE BETWEEN A POINT AND ITS CLOSEST NEIGHBOUR
				distances.append(distance)
		else:
			print(f"Only one point in cluster {zone}!")
			distances.append(0.01)
		density_per_zone[zone] = np.std(distances)
		#THE HIGHER THIS INDEX, THE SPARSER THE DISTRIBUTION OF POINTS
	return density_per_zone