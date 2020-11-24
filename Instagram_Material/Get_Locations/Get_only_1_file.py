import os
import json
import pandas as pd
import numpy as np
import utm


DIR="Json_locations/"
FILEJSON="../unifiedNew.json"
FILEXML="../unifiedNew.xlsx"

list_of_files = os.listdir(DIR) 
dict_unified={}
for name_file in list_of_files:
	print("Processing file {}".format(name_file))
	fp = open(DIR+name_file, 'r')
	dict_partial = json.load(fp)
	fp.close()
	keys=["lat","lng"]
	keys_to_eliminate=[]
	for key in keys:
		#First elimination --> eliminate keys with coordinates 'outside of the range' or None
		if key=="lat":
			keys_to_eliminate+=[el for el in list(dict_partial.keys()) if dict_partial[el][key]==None or dict_partial[el][key]<44.95 or dict_partial[el][key]>45.15]
		elif key=="long":
			keys_to_eliminate+=[el for el in list(dict_partial.keys()) if dict_partial[el][key]==None or dict_partial[el][key]<7.51 or dict_partial[el][key]>7.85]
		values=[]
		for el in list(dict_partial.values()):
			if el[key]!=None:
				values.append(el[key])
		average=np.mean(values)
		stdv=np.std(values)
		#Maintaining only 95% of data
		for el in list(dict_partial.keys()):
			if el not in keys_to_eliminate:
				value=dict_partial[el][key]
				if (value-average)/stdv>=2.58 or (value-average)/stdv<=-2.58:
					keys_to_eliminate.append(el)
	for key in list(dict_partial.keys()):
		if key not in keys_to_eliminate:
			dict_unified[key]=dict_partial[key]

print("At the end we have {} locations id!".format(len(list(dict_unified.keys()))))
#THIS NEW FILE WILL OVERWRITE THE PREVIOUS 
#KEEP THE ORIGINALS SAFE!
with open(FILEJSON, "w+") as write_file:
    json.dump(dict_unified, write_file)
#xls = ExcelFile(FILEXML)
df = pd.DataFrame()
listOfFields=["name","slug","has_public_page","lat","lng"]
df["idLocation"]=list(dict_unified.keys())
for el in listOfFields:
	df[el]=[value[el] for value in list(dict_unified.values())]
for it in range(len(df["idLocation"])):
	u=utm.from_latlon(df["lat"][it],df["lng"][it])
	df["lat"][it]=str(u[0]).replace(".",",")
	df["lng"][it]=str(u[1]).replace(".",",")
df.to_excel(FILEXML) 
