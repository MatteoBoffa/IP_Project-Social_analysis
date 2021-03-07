import json
import pandas as pd
#from pyproj import Transformer

cursors=["cursors_[torino_photogroup].json","cursors_[torinodascoprire].json",
"cursors_[torinofoodporn].json","cursors_[torinomusei].json","cursors_final.json",
"cursors_[openhousetorino].json"]

locations=["location_id_[torino_photogroup].json","location_id_[torinodascoprire].json",
"location_id_[torinofoodporn].json","location_id_[torinomusei].json","unifiedNew.json",
"location_id_[openhousetorino].json"]

cursorMap={}

for cursor in cursors:
	with open("../Download_Pictures_Instagram/Cursors/{}".format(cursor)) as json_file:
		cursorMap.update(json.load(json_file))
for key in list(cursorMap.keys()):
	cursorMap[key]=cursorMap[key]
	cursorMap[key]["current_cursor"]=cursorMap[key]["cursor_int"]

map_info={}		
for location in locations:
	with open("./Json_locations/{}".format(location)) as json_file:
		map_info.update(json.load(json_file))

#transformer = Transformer.from_crs("epsg:4326", "epsg:3003")
cursor_keys=list(cursorMap.keys())
location_keys=list(map_info.keys())

points={}
for key in cursor_keys:
	if key in location_keys:
		#u1,u2=transformer.transform(map_info[key]["lng"], map_info[key]["lat"])
		if cursorMap[key]["cursor_int"]!=0:
			if map_info[key]["lat"]>44.985 and map_info[key]["lat"]<45.15 and map_info[key]["lng"]>7.6 and map_info[key]["lng"]<7.8:
				points[key]={
					"cursor_init":cursorMap[key]["cursor_int"],
					"current_cursor":cursorMap[key]["current_cursor"],
					"lat":map_info[key]["lat"],\
					"lng":map_info[key]["lng"],
					"name":map_info[key]["name"],
					}

with open("../Results/joined_results.json","w+") as f:
	json.dump(points,f,indent=4,sort_keys=True,default="ftr")

df = pd.DataFrame()
df["id_insta"]=list(points.keys())
df["name"]=[point["name"] for point in points.values()]
df["Lat"]=[point["lat"] for point in points.values()]
df["Lng"]=[point["lng"] for point in points.values()]
df.to_excel("../To_plot/Joined_file/joined_results.xlsx")
print("Done")