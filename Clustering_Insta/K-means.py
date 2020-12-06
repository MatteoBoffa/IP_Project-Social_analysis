import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.spatial.distance import cdist
from pyproj import Transformer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

dfs = pd.read_excel("./Results/labeled_points.xlsx")
counters=dfs["counters"].to_numpy()
lat=dfs["lat"].to_numpy()
lng=dfs["lng"].to_numpy()

transformer = Transformer.from_crs("epsg:4326","epsg:3003")
for i in range(0,len(lat)):
	x,y=transformer.transform(lng[i],lat[i])
	lng[i]=x
	lat[i]=y

plt.plot()
plt.title('Dataset')
plt.plot(lat,lng, 'o', markerfacecolor="green",
		markeredgecolor='k', markersize=8)
plt.show()

#11 BEST
X = np.array(list(zip(lat, lng))).reshape(len(lat), 2)
X = StandardScaler().fit_transform(X)

distortions = []
silhouette_coefficients=[]
K = [2,10,13]
for k in K:
	print(f"Doing k:{k}")
	kmeanModel = KMeans(n_clusters=k).fit(X,counters)
	label=kmeanModel.fit_predict(X)
	distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_, 'euclidean'), axis=1)) / X.shape[0])
	score = silhouette_score(X, kmeanModel.labels_)
	silhouette_coefficients.append(score)
	u_labels=np.unique(label)
	for i in u_labels:
		plt.scatter(lat[label == i], lng[label == i], label=i)
	plt.legend()
	plt.title(
	f"k-means\nN_Cluster: {k}", fontdict={"fontsize": 12}
	)
	plt.show()
	
plt.plot(K, distortions, 'bx-')
plt.xlabel('k')
plt.ylabel('Distortion')
plt.title('The Elbow Method showing the optimal k')
plt.show()

plt.style.use("fivethirtyeight")
plt.plot(range(2, 30), silhouette_coefficients)
plt.xticks(range(2, 30))
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Coefficient")
plt.show()
