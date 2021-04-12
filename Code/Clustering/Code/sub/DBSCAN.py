import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from haversine import haversine,Unit
from tqdm import tqdm
from kneed import DataGenerator, KneeLocator
from sklearn.metrics import silhouette_samples, silhouette_score
import sklearn.cluster as clus

font = {'weight' : 'bold',
		'size'   : 22}

plt.rc('font', **font)
plt.rcParams['figure.figsize'] = (15, 10)

class DBSCAN():

	"""
	Class useful for a preliminary discrimination of border clusters and noise
	It's aim is generating as output the same input together with the assigned classes

	References",
	"- https://www.kaggle.com/kevinarvai/knee-elbow-point-detection",
	"- https://towardsdatascience.com/machine-learning-clustering-dbscan-determine-the-optimal-value-for-epsilon-eps-python-example-3100091cfbc",
	"- https://geoffboeing.com/2014/08/clustering-to-reduce-spatial-data-set-size/"
	"""
	
	def __init__(self,INPUT_PATH, OUTPUT, chosen_file, dict_stats):

		self.chosen_file = chosen_file
		self.INPUT_PATH = INPUT_PATH
		self.OUTPUT = OUTPUT
		self.kms_per_radian = 6371.0088
		self.dataset = pd.read_csv(INPUT_PATH+"/Flickr_v2.csv").drop(["Unnamed: 0"],axis=1)
		self.dict_stats = dict_stats
		self.prepare_data()


	def prepare_data(self):
		self.plot_preliminary_results()
		self.evaluate_Haversine()
		kneedle = self.find_knee()
		self.plot_kneedle(kneedle)

	def plot_preliminary_results(self):
		plt.figure()
		plt.plot(self.dataset["lat"], self.dataset["lon"],
		'o', markerfacecolor="green", markeredgecolor='k', markersize=14)
		plt.title(f"Map with outliers ({self.chosen_file})")
		plt.savefig(self.OUTPUT+"Preliminary/"+self.chosen_file+".png")

	def evaluate_Haversine(self):
		self.dataset.sort_values(by=['lat','lon'], inplace = True)
		self.coordinates = self.dataset[['lat','lon']]
		array_coordinates=self.coordinates.to_numpy()
		self.df_distances= pd.DataFrame(columns = ["index","distance"])
		print("\tEvaluating Haversine distances...")
		for i in tqdm(range(len(array_coordinates)-1)):
			point_1=array_coordinates[i,:]
			point_2=array_coordinates[i+1,:]
			distance=haversine(point_1,point_2,Unit.KILOMETERS) 
			self.df_distances = self.df_distances.append({"index":str(i),"distance":distance}, ignore_index=True)
		self.df_distances.sort_values(by=["distance"], inplace = True)
	
	def find_knee(self):
		array_distances=self.df_distances.to_numpy(dtype = 'float')
		indexes=array_distances[:,0]
		distances=array_distances[:,1]
		kneedle = KneeLocator(range(1,len(distances)+1), distances, S=1.0, curve="convex", direction="increasing",interp_method='polynomial')
		self.e_t = kneedle.knee_y/self.kms_per_radian
		self.radius = kneedle.knee_y
		self.dict_stats["radius_DBSCAN"] = str(self.radius)
		return kneedle

	def plot_kneedle(self, kneedle):
		plt.figure()
		kneedle.plot_knee()
		plt.title(f"Haversine distances between points with knee ({self.chosen_file})", fontsize = 10)
		plt.ylabel("Distance [km]",fontsize=12)
		plt.xlabel("Index of point", fontsize=12)
		plt.legend(fontsize=10)
		plt.xticks(fontsize=10)
		plt.yticks(fontsize=10)
		plt.savefig(self.OUTPUT+"Stats/"+self.chosen_file+".png")

	def tune(self):
		self.list_of_parameters = list()
		M_t=np.arange(1,41,2)
		radians_coords=np.radians(self.coordinates)
		for it in tqdm(range(len(M_t))):
			M = M_t[it]
			try:
				db_clusters=clus.DBSCAN(eps=self.e_t, min_samples=M, metric='haversine',algorithm='ball_tree').fit(radians_coords)
				lab=db_clusters.labels_
				sil=silhouette_score(radians_coords,lab)
				n_noise_ = list(lab).count(-1)
				params={
				  "silhouette":sil,
				  "e":self.e_t,
				  "M":M,
				  "labels":lab
				}
				self.list_of_parameters.append(params)
			except Exception as e:
				print(e)
				#Eliminating the trials in which only 1 cluster was generated
				pass

	def get_best(self):
		self.list_of_parameters.sort(key=lambda el:el["silhouette"],reverse=True)
		for el in self.list_of_parameters[:5]:
			n_clusters_ = len(set(el["labels"])) - (1 if -1 in el["labels"] else 0)
			n_noise_ = list(el["labels"]).count(-1)
			print("\n\tResult with e="+str(el["e"])+" and M="+str(el["M"])+":") 
			print("\t\tAverage silhouette:"+str(el["silhouette"])+"\n\t\tN° of clusters: "+str(n_clusters_)+\
			"\n\t\tNumber of outliers: "+str(n_noise_))

	def run_best(self):
		self.best_M = self.list_of_parameters[0]["M"]
		self.dict_stats["best_M_DBSCAN"] = str(self.best_M)
		radians_coords=np.radians(self.coordinates)
		db_clusters=clus.DBSCAN(eps=self.e_t,
		min_samples=self.best_M,
		metric='haversine',algorithm='ball_tree').fit(radians_coords)
		self.lab=db_clusters.labels_
		self.dict_stats["[clusters]_DBSCAN"] = str(len(set(self.lab)))
		#These are parameters which will be usefull later on
		self.core_samples_mask = np.zeros_like(self.lab, dtype=bool)
		self.core_samples_mask[db_clusters.core_sample_indices_] = True
		self.plot_best()

	def plot_best(self):
		plt.figure()
		unique_labels = set(self.lab)
		array_coordinates=self.coordinates.to_numpy()
		colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
		for k, col in zip(unique_labels, colors):
			if k == -1:
				col = [0, 0, 0, 1]
			class_member_mask = (self.lab == k)
			xy = array_coordinates[class_member_mask & self.core_samples_mask]  
			plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),markeredgecolor='k', markersize=14)
			xy = array_coordinates[class_member_mask & ~self.core_samples_mask] 
			plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),markeredgecolor='k', markersize=10)
		plt.title(f'Estimated number of clusters: {len(unique_labels)} ({self.chosen_file})')
		plt.savefig(self.OUTPUT+"Result/"+self.chosen_file+".png")

	def save_results(self):
		longitudes=[]
		latitudes=[]
		predictions = []
		ids = []
		cluster=[]
		cores=[]
		unique_labels = set(self.lab)
		colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
		numpy_array = self.dataset.to_numpy()
		for k, col in zip(unique_labels, colors):
		  class_member_mask = (self.lab == k)

		  #Taking the core points first
		  xy = numpy_array[class_member_mask & self.core_samples_mask]
		  longitudes+=list(xy[:,1])
		  latitudes+=list(xy[:,0])
		  ids += list(xy[:,2])
		  predictions+=list(xy[:,3])
		  listLabels=[self.lab[it] for it in range(len(self.lab)) if self.lab[it]==k and it in self.core_samples_mask]
		  cluster+=listLabels
		  cores+=[1 for it in range(len(xy[:,]))]

		  #Then the others
		  xy = numpy_array[class_member_mask & ~self.core_samples_mask]
		  longitudes+=list(xy[:,1])
		  latitudes+=list(xy[:,0])
		  ids += list(xy[:,2])
		  predictions+=list(xy[:,3])
		  listLabels=[self.lab[it] for it in range(len(self.lab)) if self.lab[it]==k and it not in self.core_samples_mask]
		  cluster+=listLabels
		  cores+=[0 for it in range(len(xy[:,]))]

		csv_file={
		"lng":longitudes,
		"lat":latitudes,
		"ids":ids,
		"predictions":predictions,
		"label":cluster,
		"cores":cores
		}
		df=pd.DataFrame(csv_file,columns=["lat","lng","ids","predictions","label","cores"])
		chosen = self.OUTPUT+"Labeled/"+ self.chosen_file+"_labeled"
		df.to_csv(chosen+"_"+str(round(self.radius,2))+"_"+str(self.best_M)+".csv")
		return df
