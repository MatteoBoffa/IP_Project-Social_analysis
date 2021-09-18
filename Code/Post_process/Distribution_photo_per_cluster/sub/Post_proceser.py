import dropbox
import os
import random

class Dropbox():
	def __init__(self,get_date_info, OUTPUT_PATH, chosen_cluster, chosen_year):
		self.token = "aRrjQsduclkAAAAAAAAAAYVVcfozeAj3GyFLXcwjwmQK8sK8JqRcntH9iZ8vB7VV"
		self.dropbox_instance = dropbox.Dropbox(self.token)
		self.get_date_info = get_date_info
		self.OUTPUT_PATH = OUTPUT_PATH
		self.chosen_cluster = chosen_cluster
		self.chosen_year = chosen_year

	def donwload_pictures(self, ids_to_download, datasets_output, hot_spots):
		print(f"\n\tWill download pictures for the dates: {ids_to_download}")
		for it, el in enumerate(ids_to_download):
			print(f"\n\tConsidering date {el[0].split('-')[1]}/{el[0].split('-')[0]}")
			date = el[0]
			for dataset in datasets_output.keys():
				print(f"\t\tConsidering dataset {dataset}")
				results = datasets_output[dataset]
				counter = 1 # AT COUNTER = 10 WE STOP!
				random.shuffle(results) #SHUFFLE SO THAT AT EVERY RUN DIFFERENT PICS!
				for result in results:
					year,month,day = self.get_date_info(dataset, result["date_taken"])
					if str(int(month))+"-"+str(int(day)) == date:
						new_folder = f"{dataset}/cluster_{self.chosen_cluster}-year_{self.chosen_year}/{it+1})_{date}/"
						path_new_folder = self.OUTPUT_PATH+"Pic/"+new_folder
						self.create_folders(path_new_folder)
						if dataset == "Flickr_v2":
							print(f"\t\t\tDownloading picture: {result['id_secret']}")
							try:
								with open(path_new_folder+"pic_"+str(counter)+".jpg", "wb+") as f:
								    metadata, res = self.dropbox_instance.files_download(path="/Interdisciplinary Project/Flickr_v2/"+str(result['id_secret']+".jpg"))
								    f.write(res.content)
								    counter+=1
							except Exception as e:
								print(f"\t\t\t{e}")
								print("\t\t\tPicture wasn't downloaded")
						elif dataset == "Instagram_Data":
							lat = result["lat"]
							lng = result["lng"]
							if str(lat)+"_"+str(lng) in [el[0] for el in hot_spots[:4]]: #Only picking pictures of hot spots
								print(f"\t\t\tDownloading picture: {result['id']}")
								try:
									with open(path_new_folder+"pic_"+str(counter)+".jpg", "wb+") as f:
									    metadata, res = self.dropbox_instance.files_download(path="/Interdisciplinary Project/Instagram/"+str(result['id']+".jpeg"))
									    f.write(res.content)
									    counter+=1
								except Exception as e:
									print(f"\t\t\t{e}")
									print("\t\t\tPicture wasn't downloaded")
						if counter == 11:
							break

	def create_folders(self,path):
		try:
			os.makedirs(path,exist_ok=True)
		except Exception as e:
			print("#"*30+" "+e+" "+"#"*30)
			exit()

import pymongo

class Mongo_obj():

	def __init__(self): 
		self.auth = "mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority"
		self.pymongo_instance = pymongo.MongoClient(self.auth)
		self.db_instance = self.pymongo_instance['Images_Data']

	def query_dataset(self, interesting_ids, dataset):
		collection =self.db_instance[dataset]
		#Using both version of lng (Instagram) and lon (Flickr)
		results = list(collection.aggregate([
			{
				"$match": {"id": {"$in": list(interesting_ids)}}
			},
			{
				"$project": {
					"id":1,"id_secret":1,"date_taken":1,"macro_predictions":1,"date_taken":1, "lat":1, "lng":1, "lon":1
				}
			}

			]))
		return results

from tqdm import tqdm
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import math
import json

#Matplotlib settings
font = {'weight' : 'bold',
        'size'   : 18}

plt.rc('font', **font)
plt.rcParams['figure.figsize'] = (15, 10)


class Post_Proceser():

	def __init__(self, files, id_name, chosen_cluster, chosen_year, datasets, OUTPUT_PATH, INPUT_PATH):
		self.files = files
		self.id_name = id_name
		self.chosen_cluster = int(chosen_cluster)
		self.chosen_year = str(chosen_year)
		self.datasets = datasets
		self.OUTPUT_PATH = OUTPUT_PATH
		self.INPUT_PATH = INPUT_PATH
		self.mongo_object = Mongo_obj()
		self.dbx = Dropbox(self.get_date_info, self.OUTPUT_PATH,chosen_cluster, chosen_year)
		self.get_ids()

	def get_ids(self):
		self.interesting_ids = set()
		for it,file in enumerate(self.files):
			table = pd.read_csv(self.INPUT_PATH+file)
			ids = list(table[self.id_name[it]])
			clusters = list(table["CLUSTER_ID"])
			for id,cluster in zip(ids,clusters):
				if not math.isnan(cluster): 
					if int(cluster) == self.chosen_cluster: 
						self.interesting_ids.add(str(id))

	def get_daily_info(self):
		self.dic_photo_date = {} #The key will be a string "month-day" while the value will be the [photo]
		self.tot_pic = {} #Number of pictures per year per dataset in the chosen cluster
		self.datasets_output = {}
		for dataset in self.datasets:
			self.tot_pic[dataset] = 0 #Initializing number of pictures
			results = self.mongo_object.query_dataset(self.interesting_ids,dataset)
			if dataset == "Instagram_Data":
				#Later on, while downloading, we want to pic significative pictures
				self.get_hot_spots(results, self.chosen_year, dataset)
			self.datasets_output[dataset] = results.copy()
			for it in tqdm(range(len(results))):
				result = results[it]
				year,month,day = self.get_date_info(dataset, result["date_taken"])
				if str(year) == self.chosen_year: #Only want to consider the chosen year
					#Cast the month and day information -> eliminates the 0d notations (i.e. 01)
					month = int(month)
					day = int(day)
					key = str(month)+"-"+str(day)
					if key not in self.dic_photo_date.keys():
						self.dic_photo_date[key] = 0
					self.tot_pic[dataset]+=1
					self.dic_photo_date[key] += 1

	def get_hot_spots(self, results, chosen_year, dataset):
		counter_lat_lng = {}
		for result in results:
			year,month,day = self.get_date_info(dataset, result["date_taken"])
			if str(year) == chosen_year:
				lat = result["lat"]
				lng = result["lng"]
				if str(lat)+"_"+str(lng) not in counter_lat_lng.keys():
					counter_lat_lng[str(lat)+"_"+str(lng)] = 0
				counter_lat_lng[str(lat)+"_"+str(lng)] += 1
		self.hot_spots = sorted(counter_lat_lng.items(), key=lambda x: (int(x[1])), reverse=True)

	def get_date_info(self, dataset, date):
		if dataset == "Flickr_v2": #On such a case is threaten as a string
			date = date.split(" ")[0]
			year,month,day = date.split("-")
		else: #Otherwise is already a datetime object
			year,month,day = date.year, date.month, date.day
		return year,month,day


	def plot_trend(self):
		#Order observations in chronological order -> using the information on the month and day!
		sort_orders = sorted(self.dic_photo_date.items(), key=lambda x: (int(x[0].split("-")[0]), int(x[0].split("-")[1])), reverse=False)
		#Get "the turning point" for each month for a nice representation
		index_month, month = self.get_turning_month(sort_orders)
		plt.figure()
		plt.plot([el[0] for el in sort_orders],[el[1] for el in sort_orders])
		plt.scatter([el[0] for el in sort_orders],[el[1] for el in sort_orders], color = "k")
		plt.grid()
		plt.title(f"[pictures] trend on cluster {self.chosen_cluster} during {self.chosen_year}")
		plt.xlabel("Year")
		plt.ylabel("[picures]")
		plt.xticks(index_month, [el[1] for el in month], rotation = 45)
		plt.savefig(self.OUTPUT_PATH+f"Trends/cluster_{self.chosen_cluster}-year_{self.chosen_year}.png")

	def get_turning_month(self, sort_orders):
		#Function that returns the array index in which the month changes -> in order to know where to represent it on the x-axis!

		months = {1:"Jan",2:"Feb",3:"March",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sept",10:"Oct",11:"Nov",12:"Dec"} 		#mapping dictionary
		days_index = [0]
		current_month = [(1,"Jan")] 
		for it,el in enumerate(sort_orders):
			if int(el[0].split("-")[0]) != current_month[-1][0]:
				days_index.append(it)
				current_month.append((int(el[0].split("-")[0]),months[int(el[0].split("-")[0])]))

		return days_index, current_month

	def best_print(self):
		sort_orders = sorted(self.dic_photo_date.items(), key=lambda x: int(x[1]), reverse=True)
		for it,element in enumerate(sort_orders[:10]):
			print(f"\t{it+1})\tOn date {element[0].split('-')[1]}/{element[0].split('-')[0]}/{self.chosen_year}: {element[1]}")

	def get_stats(self):

		values = list(np.sum(self.dic_photo_date.values()))

		tot_number = float(np.sum(values))
		mean = float(np.mean(values))
		st_dev = float(np.std(values))
		third_interquantile = float(np.percentile(values,75))
		(min_date, min_value) = (min(self.dic_photo_date, key=self.dic_photo_date.get),float(min(values)))
		(max_date, max_value) = (max(self.dic_photo_date, key=self.dic_photo_date.get),float(max(values)))
		#'*8' since we want to enhance the concept of outliers (only want to take peaks!)
		list_outliers = [(key,val) for key, val in zip(self.dic_photo_date.keys(),self.dic_photo_date.values()) if val>third_interquantile*8]
		list_outliers.sort(key=lambda x: x[1],reverse = True)

		stats = {
		"tot_pictures":tot_number,
		"mean(picture/day)":mean,
		"stdv(picture/day)":st_dev,
		"third_interquantile(picture/day)":third_interquantile,
		"min_date-min_value":(min_date, min_value),
		"max_date-max_value":(max_date, max_value),
		"outliers":list_outliers
		}

		with open(self.OUTPUT_PATH+f"Stats/cluster_{self.chosen_cluster}-year_{self.chosen_year}.json", "w+") as f:
			json.dump(stats,f, indent=4)
		return list_outliers

	def save_pictures_peaks(self, list_outliers):
		#Considering only 5 peaks (hyperparameter)
		self.dbx.donwload_pictures(list_outliers, self.datasets_output, self.hot_spots)

