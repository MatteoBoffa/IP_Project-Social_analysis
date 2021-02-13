import pandas as pd 
import json
import os
"""
Remember:
- 1 - Palaces/historical_monuments/cultural_properties
- 2 - Objects/miscellaneous	
- 3 - Food	
- 4 - Facilities	
- 5 - Natural_views/flora
- 6 - Animals	
- 7 - Shopping/shops/clothing/merchandising	
- 8 - Transportation	
- 9 - Urbanscape	
- 10 - Exhibits/Sculptures/Museum	
- 11 - Religion	
- 12 - Residence	
- 13 - Entertainment	
- 14 - People
"""
set_subclasses = set()
PATH_TXT = "./Txt_files/"
for file in os.listdir(PATH_TXT):
	if file.split(".")[-1]=="txt":
		with open(PATH_TXT+file) as f:
			for line in f:
				set_subclasses.add(line.strip().lower())

print(f"The original list contained {len(set_subclasses)}\n")

dict_to_save = {}
PATH = "./Raw_files/"
for file in os.listdir(PATH):
	if file.split(".")[-1]=="xlsx":
		counter_subclass = 0
		cat = pd.read_excel(PATH+file)
		for index, column in enumerate(cat.columns):
			for subclass in cat[column]:
				if not pd.isna(subclass):
					dict_to_save[subclass.lower().strip()] = index+1
					counter_subclass+=1

		print(f"On file {file}, {counter_subclass} categories were analysed")
		print(f"There are {len(dict_to_save.keys())} keys until now\n")

print(f"The difference between the original list and the re-labeled classes is: ")
print(f"\tOriginal - re-labeled: {set_subclasses.difference(dict_to_save.keys())}")
print(f"\tRe-labeled - original: {set(dict_to_save.keys()).difference(set_subclasses)}")

exit()
with open("classes.json",'w+') as outfile:
	json.dump(dict_to_save, outfile)