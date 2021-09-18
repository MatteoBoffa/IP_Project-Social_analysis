import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from kneed import DataGenerator, KneeLocator
from tqdm import tqdm

font = {'weight' : 'bold',
        'size'   : 22}

plt.rc('font', **font)
plt.rcParams['figure.figsize'] = (15, 10)

class KMEANS(): 
	"""
	Class useful for a further dividing the most numerous cluster
	It's aim is outputting the best number of k-clusters as a suggestion for QGIS implementation
	"""
	def __init__(self,df, OUTPUT, chosen_file, dict_stats):
		self.df = df 
		self.OUTPUT = OUTPUT
		self.chosen_file = chosen_file
		self.dict_stats = dict_stats
		self.configure()

	def configure(self):
		self.dbscan_sizes = {}
		for c in self.df['label']:
		    if c not in self.dbscan_sizes.keys():
		        self.dbscan_sizes[c] = 0
		    self.dbscan_sizes[c] += 1

		print("\n\tNumerosity of each DB-SCAN cluster:")
		for key in sorted(self.dbscan_sizes):
		    print(f"\t\t- Cluster {key}: {self.dbscan_sizes[key]}")
		    
		main_cluster = max(self.dbscan_sizes, key=self.dbscan_sizes.get)
		self.dict_stats["main_cluster_KMEANS"] = str(main_cluster)
		print("\t #### Main cluster is: ", main_cluster)
		self.lat=[self.df["lat"][it] for it in range(len(self.df["lat"])) if self.df["label"][it]==main_cluster]
		self.lng=[self.df["lng"][it] for it in range(len(self.df["lng"])) if self.df["label"][it]==main_cluster]
		self.lat_out=[self.df["lat"][it] for it in range(len(self.df["lat"])) if self.df["label"][it]!=main_cluster]
		self.lng_out=[self.df["lng"][it] for it in range(len(self.df["lng"])) if self.df["label"][it]!=main_cluster]
		self.plot_cleaned()
		self.X = np.array(list(zip(self.lat, self.lng))).reshape(len(self.lat), 2)

	def plot_cleaned(self):
		plt.figure()
		plt.title(f'Only central cluster ({self.chosen_file})')
		plt.plot(self.lng,self.lat, 'o', markerfacecolor="green", markeredgecolor='k', markersize=14,label="cleaned")
		plt.plot(self.lng_out,self.lat_out, 'o', markerfacecolor="black", markeredgecolor='k', markersize=12,label="outlier")
		plt.legend()
		plt.savefig(self.OUTPUT+"Preliminary/"+self.chosen_file+".png")

	def tune(self):
		distortions = []
		silhouette_coefficients=[]
		K = range(2,20)
		for k in tqdm(K):
		    kmeanModel = KMeans(n_clusters=k).fit(self.X)
		    label=kmeanModel.fit_predict(self.X)
		    distortions.append(kmeanModel.inertia_)
		    score = silhouette_score(self.X, kmeanModel.labels_)
		    silhouette_coefficients.append(score)

		self.plot_silhouette(silhouette_coefficients, K)

	def plot_silhouette(self,silhouette_coefficients, K):
		plt.figure()
		plt.grid()
		plt.style.use("fivethirtyeight")
		plt.plot(K, silhouette_coefficients)
		plt.title(f"Silhouette coefficient' results ({self.chosen_file})")
		plt.xticks(K)
		plt.xlabel("Number of Clusters")
		plt.xticks(rotation=45)
		plt.ylabel("Silhouette Coefficient")
		self.max_silh = K[np.asarray(silhouette_coefficients).argmax()]
		plt.savefig(self.OUTPUT+"Stats/"+self.chosen_file+".png")

	def best_run(self):
		kmeanModel = KMeans(n_clusters=self.max_silh).fit(self.X)
		self.dict_stats["[clusters]_kmeans"] = str(self.max_silh)
		label=kmeanModel.fit_predict(self.X)
		self.plot_best(label)
		print("\n\t"+"#"*30+f" Suggested number of clusters is {self.max_silh} "+"#"*30)
		self.print_cluster_sizes(label)

	def plot_best(self,label):
		colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(label))]
		plt.figure()
		plt.title(f'Number of cluster: {self.max_silh} ({self.chosen_file})')
		plt.scatter(self.X[:, 1], self.X[:, 0], c=label, edgecolor='black' ,s=200, cmap='viridis')
		plt.savefig(self.OUTPUT+"Result/"+self.chosen_file+".png")

	def print_cluster_sizes(self, label):
		print("\n\tNumerosity of each sub-cluster:")
		clusters_size = {}
		for c in label:
		    if c not in clusters_size.keys():
		        clusters_size[c] = 0
		    clusters_size[c] += 1
		for key in sorted(clusters_size):
		    print(f"\t\tCluster {key}: {clusters_size[key]}")