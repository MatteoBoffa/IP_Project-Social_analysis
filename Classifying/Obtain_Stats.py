
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from string import *


INPUT_PATH = "./After_elaboration/Weekends_Only/Modified/"
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

fig, ax= plt.subplots()
zones = [int(el) for el in list(dict_classes.keys())]
#"#FDFA66"
colors = ["#7D0000","#FF0000","#FB7756","gold","#1AC0C6",\
			"#1A1B4B","#3E4491","#3A9EFD","#8C61FF","#DDACF5",\
			"steelblue","#454D66","#58B368","#DAD873"]

dict_color = {}
for color, main_class in zip(colors,list_convertor):
	dict_color[main_class] = color

list_bars_per_zone = []
list_total_per_zone = []

for it,zone in enumerate(zones):

	print(f"\nFor zone {zone} the stats says:")

	to_order = []
	left = 0
	sum_class = 0
	list_classes_ordered = []

	for main_class in dict_classes[zone].keys():
		sum_class += dict_classes[zone][main_class]
		list_classes_ordered.append((int(main_class),dict_classes[zone][main_class]))

	list_classes_ordered.sort(key = lambda x:x[0])

	for it2, el in enumerate(list_classes_ordered):
		rect = ax.barh(zone, el[1]/sum_class*100, left = left, color = dict_color[dict_traslator[int(el[0])]])
		if el[1]/sum_class*100 > 10:
			for r in rect:
				width, height =r.get_width(),r.get_height()
				x=r.get_x()+width/2
				y=r.get_y()+height/2
				ax.annotate('{:.1f}%'.format(el[1]/sum_class*100), \
					xy=(x,y), \
					xytext=(0, 0), \
					textcoords="offset points", \
					ha='center', va='center', color = "w", size=10, weight='bold')

		to_order.append((el[0],el[1]))
		left = left + el[1]/sum_class*100

	if it != 0:
		last_el = list_bars_per_zone[-1]
		list_bars_per_zone.append(last_el+len(list_classes_ordered))
	else:
		list_bars_per_zone.append(len(list_classes_ordered))

	list_total_per_zone.append(dict_tot_photos[zone])	

	to_order.sort(key=lambda x: x[1], reverse=True)	
	for it2,el in enumerate(to_order[:8]):
		print(f"\t{it2+1}) class {dict_traslator[int(el[0])]} : {el[1]/sum_class*100}")

it_list_bars = 0

for it,p in enumerate(ax.patches):
	if (it+1) % list_bars_per_zone[it_list_bars] == 0:
		percentage ='{}'.format(list_total_per_zone[it_list_bars]).rjust(5,"\t").replace("\t","  ")
		width, height =p.get_width(),p.get_height()
		x=p.get_x()+width+0.5
		y=p.get_y()+height/2
		ax.annotate(percentage,(x,y), ha='left', va='center', size=16)
		it_list_bars+=1

plt.legend(list_convertor, ncol=7, loc='upper center', bbox_to_anchor=(0.5, 1.125), fontsize = 10)
ax2 = ax.twinx()
ax2.set_ylabel('[Photo taken]', fontsize = 20)
ax.tick_params(labelsize=16)
ax.set_xlabel("Percentages [%]", fontsize = 20)
ax.set_ylabel("Zones", fontsize = 20)
ax.set_yticks([x for x in range(len(zones))])
ax2.margins(0.1)
plt.setp(ax2.get_yticklabels(), visible=False)

plt.show()
