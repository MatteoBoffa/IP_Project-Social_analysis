"""
TO_ANALYSE
2017:
45.07	7.7	DONE
45.07	7.71 DONE
45.06	7.71 DONE
45.06	7.7	DONE
45.08	7.77 ERROR?
2019:
45.02	7.67 DONE
45.06	7.65
"""
import sys
import pymongo
import matplotlib.pyplot as plt
import dropbox
import random
import os

#assert len(sys.argv) == 3, "Attenton: three parameters are required to run this script (lat, lng, year)"
"""
lat = sys.argv[1]
lng = sys.argv[2]
year = sys.argv[3]
"""

def get_turning_month(sort_orders):
	#Function that returns the array index in which the month changes -> in order to know where to represent it on the x-axis!

	months = {1:"Jan",2:"Feb",3:"March",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sept",10:"Oct",11:"Nov",12:"Dec"} 		#mapping dictionary
	days_index = [0]
	current_month = [(1,"Jan")] 
	for it,el in enumerate(sort_orders):
		if int(el[0].split("-")[0]) != current_month[-1][0]:
			days_index.append(it)
			current_month.append((int(el[0].split("-")[0]),months[int(el[0].split("-")[0])]))

	return days_index, current_month

chosen_lat = 45.08
chosen_lng = 7.77	
chosen_year = 2017

print(f"\nDownloading info from mongo...")

auth = "mongodb+srv://vincenzo:Ict@cluster0.qvgo1.mongodb.net/Images_Data?retryWrites=true&w=majority"
pymongo_instance = pymongo.MongoClient(auth)
db_instance = pymongo_instance['Images_Data']

collection = db_instance["Flickr_v2"]

results = list(collection.aggregate([
	{
		"$project": {
			"id":1,"id_secret":1,"date_taken":1,"latitude":1, "longitude":1
		}
	}

]))
dict_period = {}
dict_id = {}
for r in results:
	date = r["date_taken"].split(" ")[0]
	year,month,day = date.split("-")
	if int(year) == chosen_year:
		if round(float(r["latitude"]),2) == chosen_lat and round(float(r["longitude"]),2) == chosen_lng:
			key = str(month)+"-"+str(day)
			if key not in dict_period.keys():
				dict_period[key] = 0
				dict_id[key] = []
			dict_period[key] += 1
			dict_id[key].append(r["id_secret"])

saving_path = "./Output/Trend/"
print(f"\nPlotting some useful stats...")
sort_orders = sorted(dict_period.items(), key=lambda x: (int(x[0].split("-")[0]), int(x[0].split("-")[1])), reverse=False)
days_index, current_month = get_turning_month(sort_orders)
plt.figure()
plt.plot([el[0] for el in sort_orders],[el[1] for el in sort_orders])
plt.scatter([el[0] for el in sort_orders],[el[1] for el in sort_orders], color = "k")
plt.grid()
plt.title(f"[pictures] trend on lat-lon {chosen_lat}-{chosen_lng} during {chosen_year}")
plt.xlabel("Year")
plt.ylabel("[picures]")
plt.xticks(days_index, [el[1] for el in current_month], rotation = 45)
plt.savefig(saving_path+f"lat:{chosen_lat}_lon:{chosen_lng}_year:{chosen_year}.png")

sort_n_ids = sorted(dict_id.items(), key=lambda x: (len(x[1])), reverse=True)
best_4 = sort_n_ids[:4] #Keeping only some of them to reduce n° pictures
print(f"\nNow downloading the pictures from dropbox...")
token = "aRrjQsduclkAAAAAAAAAAYVVcfozeAj3GyFLXcwjwmQK8sK8JqRcntH9iZ8vB7VV"
dropbox_instance = dropbox.Dropbox(token)
saving_path = "./Output/Downloaded_Pic/"
for it,best in enumerate(best_4):
	print(f"\tDownloading date {it+1}...")
	fold = f"lat:{chosen_lat}_lon:{chosen_lng}_year:{chosen_year}/"
	try:
		os.makedirs(saving_path+fold,exist_ok=True)
	except Exception as e:
		print(e)
		exit()
	list_ids = best[1]
	key = best[0]
	random.shuffle(list_ids)
	counter = 1
	for id in list_ids:
		print(f"\t\tId_secret:{id}")
		try:
			with open(saving_path+fold+"pic_"+str(counter)+f"_{key}.jpg", "wb+") as f:
				try:
					metadata, res = dropbox_instance.files_download(path="/Interdisciplinary Project/Flickr_v2/"+str(id)+".jpg")
				except:
					metadata, res = dropbox_instance.files_download(path="/Interdisciplinary Project/Flickr/"+str(id)+".jpg")
				f.write(res.content)
				counter+=1
		except Exception as e: 
			print(f"\t\t\tFailed - {e}!!")
			pass
		if counter==6:
			break
	