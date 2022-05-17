import numpy as np
from sklearn.cluster import KMeans,OPTICS, Birch, MeanShift, estimate_bandwidth
from sklearn.mixture import GaussianMixture as GMM

X = np.array([[0,2],[0,0],[1,0],[5,0],[5,2]])

def runKMeans_add(data=X, n_clusters = 3):
  clf = KMeans(data, n_clusters=n_clusters, init="k-means++").fit(data)
  return clf.labels_

def runKMeans(data=X,n_clusters= 2):
  clf = KMeans(n_clusters=n_clusters).fit(data)
  return clf.labels_

def runMeanShift(data=X):
  bandwidth = estimate_bandwidth(data, quantile=0.2, n_samples=3)
  clf = MeanShift(bandwidth=bandwidth, bin_seeding=True).fit(data)
  return clf.labels_

def gmm(data=X):
  gmm = GMM(n_components=3).fit(data) #指定聚类中心个数为4
  labels = gmm.predict(data)
  return labels

def birch(data,n_clusters=2):
  birch = Birch(n_clusters=n_clusters).fit(data)
  labels = birch.predict(data)
  return labels

def optics(data=X):
  """
    DBSCAN 的改进算法
  """
  clf = OPTICS(min_samples=2)
  clf.fit(data)
  return clf.labels_

if __name__ == '__main__':
  lables = gmm(X)
  print(lables)
  pass
