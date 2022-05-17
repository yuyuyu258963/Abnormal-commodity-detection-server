import numpy as np
import matplotlib.pyplot as plt
import math
import time

UNCLASSIFIED = False
NOISE = 0

def dist(a, b):
	"""
	输入：向量A, 向量B
	输出：两个向量的欧式距离
	"""
	return math.sqrt(np.power(a - b, 2).sum())

def eps_neighbor(a, b, eps):
	"""
	输入：向量A, 向量B
	输出：是否在eps范围内
	"""
	return dist(a, b) < eps

def region_query(data, pointId, eps):
	"""
	输入：数据集, 查询点id, 半径大小
	输出：在eps范围内的点的id
	"""
	nPoints = data.shape[1]
	seeds = []
	for i in range(nPoints):
		if eps_neighbor(data[:, pointId], data[:, i], eps):
			seeds.append(i)
	return seeds

def expand_cluster(data, clusterResult, pointId, clusterId, eps, minPts):
	"""
	输入：数据集, 分类结果, 待分类点id, 簇id, 半径大小, 最小点个数
	输出：能否成功分类
	"""
	seeds = region_query(data, pointId, eps)
	if len(seeds) < minPts: # 不满足minPts条件的为噪声点
		clusterResult[pointId] = NOISE
		return False
	else:
		clusterResult[pointId] = clusterId # 划分到该簇
		for seedId in seeds:
			clusterResult[seedId] = clusterId

		while len(seeds) > 0: # 持续扩张
			currentPoint = seeds[0]
			queryResults = region_query(data, currentPoint, eps)
			if len(queryResults) >= minPts:
				for i in range(len(queryResults)):
					resultPoint = queryResults[i]
					if clusterResult[resultPoint] == UNCLASSIFIED:
						seeds.append(resultPoint)
						clusterResult[resultPoint] = clusterId
					elif clusterResult[resultPoint] == NOISE:
						clusterResult[resultPoint] = clusterId
			seeds = seeds[1:]
		return True

def dbscan(data, eps, minPts):
  """
  输入：数据集, 半径大小, 最小点个数
  输出：分类簇id
  """
  clusterId = 1
  nPoints = data.shape[1]
  clusterResult = [UNCLASSIFIED] * nPoints
  for pointId in range(nPoints):
    # point = data[:, pointId]
    if clusterResult[pointId] == UNCLASSIFIED:
      if expand_cluster(data, clusterResult, pointId, clusterId, eps, minPts):
        clusterId = clusterId + 1
  return clusterResult, clusterId - 1

def plotFeature(data, clusters, clusterNum):
	nPoints = data.shape[1]
	matClusters = np.mat(clusters).transpose()
	fig = plt.figure()
	scatterColors = ['black', 'blue', 'green', 'yellow', 'red', 'purple', 'orange', 'brown']
	ax = fig.add_subplot(111)

	for [x,y],clusterNId in zip(data,clusters):
		ax.scatter(x,y,c = scatterColors[clusterNId % len(scatterColors)], s=50)

def DB_cluster(data):
	# dataSet = trans_data(nodes)

	dataSet = np.mat(data).transpose()
	clusters, clusterNum = dbscan(dataSet, 5, 5)
	print("cluster Numbers = ", clusterNum)
	
	
	# print(clusters)
	# plotFeature(data,clusters,clusterNum)
	# plt.show()

	
	# data = get_aimData(nodes,clusters)
	# print(data)
	# return data

if __name__ == '__main__':
  DB_cluster()
  # plt.show()
# DBSCAN