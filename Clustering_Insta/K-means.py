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

#distortions = []
#silhouette_coefficients=[]
K = [2,9,12]

for k in K:
	xs=[]
	ys=[]
	labels=[]
	print(f"Doing k:{k}")
	kmeanModel = KMeans(n_clusters=k)
	label=kmeanModel.fit_predict(X,counters)
	"""
	distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_, 'euclidean'), axis=1)) / X.shape[0])
	score = silhouette_score(X, kmeanModel.labels_)
	silhouette_coefficients.append(score)
	"""
	u_labels=np.unique(label)
	for i in u_labels:
		plt.scatter(lat[label == i], lng[label == i], label=i)
		xs+=list(lng[label == i])
		ys+=list(lat[label==i])
		labels+=list([i for it in range(len(lat[label==i]))])
	plt.legend()
	plt.title(
	f"k-means\nN_Cluster: {k}", fontdict={"fontsize": 12}
	)
	plt.show()
	transformer = Transformer.from_crs("epsg:3003","epsg:4326")
	for i in range(0,len(xs)):
		x,y=transformer.transform(xs[i],ys[i])
		xs[i]=x
		ys[i]=y

	excel_file={
	"lng":xs,
	"lat":ys,
	"label":labels
	}

	df2=pd.DataFrame(excel_file,columns=["lat","lng","label"])
	df2.to_excel(f"Results/Clusters_{k}_for_QGis.xlsx")
"""
plt.plot(K, distortions, 'bx-')
plt.xlabel('k')
plt.ylabel('Distortion')
plt.title('The Elbow Method showing the optimal k')
plt.show()

plt.style.use("fivethirtyeight")
plt.plot(range(2, 31), silhouette_coefficients)
plt.xticks(range(2, 31))
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Coefficient")
plt.show()
"""