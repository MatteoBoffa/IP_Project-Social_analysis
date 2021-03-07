import pymongo
from pymongo import MongoClient
import json
import requests
import matplotlib.pyplot as plt
import numpy as np
import time

cluster = pymongo.MongoClient("mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority")
db = cluster['Images_Data'] #(db)
collection =db['Instagram_Data']
LINK_INSTA="https://www.instagram.com/explore/locations/{0}/?__a=1&max_id={1}"
LOCATION_AND_CURSORS="../Results/joined_results.json"
with open(LOCATION_AND_CURSORS) as json_file: #Uploading the location I want to study
	locations_and_cursors = json.load(json_file)
with open("./n_pic.json") as json_file:
	dict_pictures_per_location=json.load(json_file)

for key in list(locations_and_cursors.keys())[:65]:
	print(locations_and_cursors[key]["name"])
	total_pictures_per_loc=dict_pictures_per_location[key]
	
	if total_pictures_per_loc>1000:
		results=list(collection.aggregate([
			{
				"$match":{
					"location_id":key
				}
			},
			{
				"$project":{
					"id":1,
					"year": { "$year": "$date_taken" },
					"month": { "$month": "$date_taken" },
					"day": { "$dayOfMonth": "$date_taken" }
				}
			}
			]))
		results.sort(key=lambda x:(x["year"],x["month"],x["day"]), reverse=True)
		if len(results)>500:
			resultsToUse=results[:500].copy()
		else:
			resultsToUse=results.copy()

		if total_pictures_per_loc>20000:
			step=24
		elif total_pictures_per_loc>10000 and total_pictures_per_loc<=20000:
			step=12
		elif total_pictures_per_loc<=10000 and total_pictures_per_loc>5000:
			step=6
		elif total_pictures_per_loc<=5000 and total_pictures_per_loc>1000:
			step=3
		
		list_to_update=[]
		for it in range(1,len(resultsToUse)):
			if it%step!=0: 
				id_picture=resultsToUse[it]["id"]
				list_to_update.append(id_picture)

		collection.update_many(
			{ "id": {"$in":list_to_update} },
			{ "$set":
				{
				"to_take": False,
				}
			}
		)
	
