import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from numpy import percentile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pyod.models.iforest import IForest


def IForest_test(data, contamination=0.1):
    clf = IForest(contamination=contamination, random_state=0)
    clf.fit(data)
    scores_pred = clf.decision_function(data) * -1
    y_pred = clf.predict(data)
    n_inliers = len(y_pred) - np.count_nonzero(y_pred)  # 统计数组中非零元素的个数 => 非异常值
    n_outliers = np.count_nonzero(y_pred == 1)  # 计算异常值个数
    X1 = data
    X1['outlier'] = y_pred.tolist()
    print('OUTLIERS: ', n_outliers, 'INLIERS: ', n_inliers)  # 输出异常值数量
    threshold = np.percentile(scores_pred, 100 * contamination)  # 输出这个百分比之下的数字，相当于求多少分位数
    draw(clf, X1, threshold)


def draw(clf, X1, threshold):         # 画图
    xx, yy = np.meshgrid(np.linspace(-0.1, 1.1, 120), np.linspace(-0.1, 1.1, 120))
    inliers_sales = np.array(X1['ITEM_PRICE'][X1['outlier'] == 0]).reshape(-1, 1)  # 暂时可视化这几个
    inliers_amount = np.array(X1['ITEM_SALES_AMOUNT'][X1['outlier'] == 0]).reshape(-1, 1)  # 暂时你俩
    outliers_sales = X1['ITEM_PRICE'][X1['outlier'] == 1].values.reshape(-1, 1)
    outliers_amount = X1['ITEM_SALES_AMOUNT'][X1['outlier'] == 1].values.reshape(-1, 1)
    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()]) * -1  # ravel多维变一维，靠np._c连接两个矩阵 => 计算图上每个点的
    Z = Z.reshape(xx.shape)     # 是为了画那个蓝色区域
    plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), threshold, 7), cmap=plt.cm.Blues_r)     # plt.coutour用来画等高线的
    a = plt.contour(xx, yy, Z, levels=[threshold], linewidths=2, colors='red')  # 红线表示阈值
    plt.contourf(xx, yy, Z, levels=[threshold, Z.max()], colors='orange')       # 异常值到最大异常值得分的地方画橙色
    b = plt.scatter(inliers_sales, inliers_amount, c='white', s=20, edgecolor='k')
    c = plt.scatter(outliers_sales, outliers_amount, c='black', s=20, edgecolor='k')
    plt.axis('tight')
    plt.legend([a.collections[0], b, c], ['learned decision function', 'inliers', 'outliers'],
               prop=matplotlib.font_manager.FontProperties(size=20), loc='lower right')
    plt.xlim((-0.1, 1.1))
    plt.ylim((-0.1, 1.1))
    plt.title('Isolation Forest')
    plt.show()

def normalize(file, group):
    min_max = MinMaxScaler(feature_range=(0, 1))
    ret = file
    ret[file.columns[group]] = min_max.fit_transform(file[file.columns[group]])
    return ret

def main():
    df = pd.read_csv(r"../data_202106_head.tsv", encoding="utf-8", sep="\t")
    # 筛选无缺失的
    df1 = df.dropna(axis=0, how='any', subset=["ITEM_FAV_NUM", "TOTAL_EVAL_NUM", "ITEM_STOCK"])
    # 有缺失的
    df2 = df[df[["ITEM_FAV_NUM", "TOTAL_EVAL_NUM", "ITEM_STOCK"]].isnull().T.any()]
    df1 = normalize(df1, [5, 6, 7, 13, 14, 15])
    normalize(df2, [5, 6, 7])
    IForest_test(df1[df1.columns[[5, 6, 7, 13, 14, 15]]], contamination=0.05)
    IForest_test(df2[df2.columns[[5, 6, 7]]], contamination=0.05)

if __name__ == '__main__':
    main()