import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

sns.set()
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE

data = pd.read_csv(r"C:\Users\ASUS\Desktop\Problem_C_Data\monthdata\total_month.csv", encoding='utf-8')
data = data.T
index = data.index
data = StandardScaler().fit_transform(data)
tsne = TSNE(perplexity=30, n_components=3, init='pca', n_iter=2000, method='exact')
data = tsne.fit_transform(data)

X=data

from sklearn.mixture import GaussianMixture as GMM
gmm = GMM(n_components=2).fit(X) #指定聚类中心个数为4
labels = gmm.predict(X)
plt.scatter(X[:, 0], X[:, 1], c=labels, s=50, cmap='viridis')
X = pd.DataFrame(X)
X["cluster"] = labels
X.index = index
X = X.sort_values(by="cluster")
print(X)
X.to_csv("GMM.csv", encoding="utf-8-sig")

# plt.show()