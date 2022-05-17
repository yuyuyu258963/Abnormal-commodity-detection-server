import sys
import json
import fire
import numpy as np
from sklearn.cluster import KMeans,OPTICS, Birch, MeanShift, estimate_bandwidth
from sklearn.mixture import GaussianMixture as GMM
from tsne import get_data, reduce_v, saveJsonFile

X = np.array([[0,2],[0,0],[1,0],[5,0],[5,2]])

def ReadJson():
  """
    读取约定好的要聚类的数据
  """
  with open("../RedutionRes/preData.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    
    
    return data

def saveJson(data):
  """
    将聚类的结果保存到约定好的文件中
  """
  with open("../RedutionRes/res.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(data))

def runKMeans_add(data=X, n_clusters = 5):
  clf = KMeans(data, n_clusters=n_clusters, init="k-means++").fit(data)
  return clf.labels_

def runKMeans(data=X,n_clusters= 5):
  clf = KMeans(n_clusters=n_clusters).fit(data)
  return clf.labels_

def runMeanShift(data=X):
  bandwidth = estimate_bandwidth(data, quantile=0.2, n_samples=3)
  clf = MeanShift(bandwidth=bandwidth, bin_seeding=True).fit(data)
  return clf.labels_

def gmm(data=X, clusterNumber=5):
  gmm = GMM(n_components=clusterNumber).fit(data) #指定聚类中心个数为4
  labels = gmm.predict(data)
  return labels

def birch(data,n_clusters=5):
  birch = Birch(n_clusters=n_clusters).fit(data)
  labels = birch.predict(data)
  return labels

def optics(data=X, clusterNumber=3):
  """
    DBSCAN 的改进算法
  """
  clf = OPTICS(min_samples=clusterNumber)
  clf.fit(data)
  return clf.labels_

def main(method="GMM", clusterNumber=5):
  data,data_id = get_data("preData")
  nodesData = data.tolist()
  vec_2_data = reduce_v(data)
  print(method)
  if method == "GMM":
    lables = gmm(vec_2_data, clusterNumber)
  elif method == "KMEANS":
    lables = runKMeans(vec_2_data, clusterNumber)
  elif method == "OPTICS":
    lables = optics(vec_2_data, clusterNumber)
  elif method == 'BIRCH':
    lables = birch(vec_2_data, clusterNumber)
  lables = lables.tolist()
  vec_2_data = vec_2_data.tolist()
  aim_data = [{'id':proId,'classId':classLable,'x':x,'y':y,
            "item_price":elem[0],"item_sales_volume":elem[1]}
            for proId,[x,y],classLable,elem in zip(data_id,vec_2_data,lables,nodesData)]
  saveJsonFile('clusterRes', aim_data)

if __name__ == '__main__':
  fire.Fire()
  # lables = gmm(X)
  # print(lables)