import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
import pandas as pd

cluster = pymongo.MongoClient("mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority")
db = cluster['Images_Data'] #(db)
collection =db['Flickr_v2']
years=[2017,2018,2019]
lat_lim=[45.00,45.15]
lon_lim=[7.576,7.7724]
data={}
for year in years:
	data[year]={
	"lat":[],
	"lon":[]
	}

results=list(collection.aggregate([
		{'$project':{
			"date_taken":1,
			"latitude":1,
			"longitude":1
		}}
	]))


for el in results:
	date=el["date_taken"]
	lat=float(el["latitude"])
	lng=float(el["longitude"])
	if lat>=lat_lim[0] and lat<=lat_lim[1] and lng>=lon_lim[0] and lng<=lon_lim[1]:
		data[datetime.strptime(date, '%Y-%m-%d %H:%M:%S').year]["lat"].append(lat)
		data[datetime.strptime(date, '%Y-%m-%d %H:%M:%S').year]["lon"].append(lng)

for year in data.keys():
	data_for_year=data[year]
	df2=pd.DataFrame(data[year],columns=["lat","lon"])
	df2.to_csv(f"./Raw_data/points_year_{year}.csv")