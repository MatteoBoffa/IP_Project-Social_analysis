import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

common_path = "./Data/"
paths = ["2017/2017-01-01_to_2017-12-31_11_1111_labeled_1.29_31.csv",
		 "2019/2019-01-01_to_2019-12-31_11_1111_labeled_0.5_39.csv"]
dics = []

def round_nearest(x, a):
    return round(x / a) * a

for file in paths:
	dic_lat_lng = {}
	file = common_path+file
	table = pd.read_csv(file).drop(["Unnamed: 0"],axis = 1)
	for lat, lng in zip(table["lat"], table["lng"]):
		#lat, lng = round_nearest(lat,0.005),round_nearest(lng,0.005)
		lat,lng = round(lat,2),round(lng,2)
		if (lat,lng) not in dic_lat_lng.keys():
			dic_lat_lng[(lat,lng)] = 0
		dic_lat_lng[(lat,lng)] += 1
	dics.append(dic_lat_lng)

difference_2017_2019 = {}
for key in dics[0].keys(): #2017 points
	if key not in dics[1].keys():
		difference_2017_2019[key] = dics[0][key]
	else:
		difference_2017_2019[key] = dics[0][key] - dics[1][key]

print(np.mean(list(difference_2017_2019.values())), np.std(list(difference_2017_2019.values())))
plt.hist(difference_2017_2019.values(), bins = 50)
plt.show()
csv_file={
"lng":[el[1] for el in difference_2017_2019.keys()],
"lat":[el[0] for el in difference_2017_2019.keys()],
"val":[el for el in difference_2017_2019.values()]
}
df=pd.DataFrame(csv_file,columns=["lat","lng","val"])
df.to_csv("Sparse_files/difference.csv")

csv_file={
"lng":[el[1] for el in dics[0].keys()],
"lat":[el[0] for el in dics[0].keys()],
"val":[el for el in dics[0].values()]
}
df=pd.DataFrame(csv_file,columns=["lat","lng","val"])
df.to_csv("Sparse_files/2017.csv")

csv_file={
"lng":[el[1] for el in dics[1].keys()],
"lat":[el[0] for el in dics[1].keys()],
"val":[el for el in dics[1].values()]
}
df=pd.DataFrame(csv_file,columns=["lat","lng","val"])
df.to_csv("Sparse_files/2019.csv")