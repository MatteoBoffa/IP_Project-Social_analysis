import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn.cluster as clus
import time 
from scipy.spatial.distance import cdist
from sklearn.metrics import silhouette_samples, silhouette_score
from pyproj import Transformer
from sklearn.preprocessing import StandardScaler

if __name__ == '__main__':

	base_dataFrame=pd.read_csv("flickr_points_filtered.csv")
	base_dataFrame=base_dataFrame.drop(["Unnamed: 0"],axis=1)
	
	transformer = Transformer.from_crs("epsg:4326", "epsg:3003")
	for i in range(0,len(base_dataFrame)):
		x,y=transformer.transform(base_dataFrame.iloc[i][1],base_dataFrame.iloc[i][0])
		base_dataFrame.iloc[i][1]=x
		base_dataFrame.iloc[i][0]=y

	plt.figure()
	plt.plot(base_dataFrame["lat"], base_dataFrame["lon"], 'o', markerfacecolor="green",
			markeredgecolor='k', markersize=8)
	plt.title("Map with outliers")
	plt.show()

	#PART DONE TO FIND OPTIMUM VALUE OF eps
	#print("Done 1")
	base_dataFrame = base_dataFrame.sort_values(by=['lat','lon'])
	#print("Done 2")
	base_dataFrame=base_dataFrame.to_numpy()

	base_dataFrame_scaled = StandardScaler().fit_transform(base_dataFrame)
	"""
	df2= pd.DataFrame(columns = ["index","distance"])
	for i in range(0,len(base_dataFrame)-1):
		dist=np.linalg.norm(base_dataFrame[i]-base_dataFrame[i+1])
		df2 = df2.append({"index":str(i),"distance":dist}, ignore_index=True)
	print("Done 3")

	df2=df2.sort_values(by=['distance'])
	print("Done 4")

	plt.scatter(df2["index"],df2["distance"])
	plt.show()
	"""
	
	print("***DBSCAN***\n")
	#Parameters used to test outliers (too big and too small)
	e_t=[0.5]#np.arange(0.25,0.66,0.05) #THESE ARE DEGREES
	M_t=[45]#np.arange(5,60,5)

	silhouettes=[]
	params=[]
	for e in e_t:
		for M in M_t:
			print("\nResult with e="+str(e)+" and M="+str(M)+":")
			db_clusters=clus.DBSCAN(eps=e, min_samples=M).fit(base_dataFrame_scaled)
			lab=db_clusters.labels_
			core_samples_mask = np.zeros_like(lab, dtype=bool)
			core_samples_mask[db_clusters.core_sample_indices_] = True
			silhouette_avg = silhouette_score(base_dataFrame,lab)
			n_clusters_ = len(set(lab)) - (1 if -1 in lab else 0)
			n_noise_ = list(lab).count(-1)
			#silhouettes.append(silhouette_avg)
			print(f"\tAverage silhouette: {silhouette_avg}\n\tN° of clusters: {len(set(lab))}\
				\n\tNumber of outliers: {list(lab).count(-1)}")
			silhouettes.append(silhouette_avg)
			params.append((e,M))

	print(f"The maximum value of silhouette is: {max(silhouettes)}\n\
		With params {params[silhouettes.index(max(silhouettes))]}")

	
	unique_labels = set(lab)
	colors = [plt.cm.Spectral(each)
			  for each in np.linspace(0, 1, len(unique_labels))]

	xs=[]
	ys=[]
	labels=[]

	for k, col in zip(unique_labels, colors):
		if k == -1:
			# Black used for noise.
			col = [0, 0, 0, 1]

		class_member_mask = (lab == k)
		
		xy = base_dataFrame[class_member_mask & core_samples_mask]
		if k==2 or k==0:
			listx=list(xy[:,1])
			print(f"X-Appended new {len(listx)} elements")
			xs+=listx
			listy=list(xy[:,0])
			ys+=listy
			print(f"Y-Appended new {len(listy)} elements")

			listLabels=[lab[it] for it in range(len(lab)) if lab[it]==k and\
						core_samples_mask[it]==True]
			labels+=listLabels
			print(f"L-Appended new {len(listLabels)} elements")
			print()
		
		plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
				 markeredgecolor='k', markersize=14)

		"""
		xy = base_dataFrame[class_member_mask & ~core_samples_mask]
		plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
				 markeredgecolor='k', markersize=6)
		"""
	plt.title('Estimated number of clusters: %d' % n_clusters_)
	plt.show()

	transformer = Transformer.from_crs("epsg:3003","epsg:4326")
	for i in range(0,len(xs)):
		lon,lat=transformer.transform(xs[i],ys[i])
		xs[i]=lon
		ys[i]=lat

	excel_file={
	"lng":xs,
	"lat":ys,
	"label":labels
	}

	df2=pd.DataFrame(excel_file,columns=["lat","lng","label"])
	df2.to_excel("Results/labeled_points.xlsx")
