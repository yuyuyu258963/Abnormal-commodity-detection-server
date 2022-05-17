import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import IsolationForest        # 这里尝试sklearn的包

def Isolation_Forest(file, target, n_estimators = 100):
    for i in target:
        file_for_this = file.dropna(axis=0, how='any', subset=["ITEM_FAV_NUM"])
        clf = IsolationForest(n_estimators=n_estimators)
        clf.fit(file_for_this[file.columns[i]].values.reshape(-1, 1))    # 训练=>靠reshap变成2维一列的数据
        xx = np.linspace(file_for_this[file.columns[i]].min(), file_for_this[file.columns[i]].max(), len(file_for_this)).reshape(-1, 1)    # 序列生成器生成序列，均匀一下差值
        anomaly_score = clf.decision_function(xx)       # 分类器的一种方法，看是在分类器超平面的左右哪边 => 算是打出了一个异常得分
        outlier = clf.predict(xx)           # 预测，看看谁是异常的
        plt.figure(figsize=(20, 10))
        plt.plot(xx, anomaly_score, color='r', linewidth=1, label='anomaly score')
        plt.fill_between(xx.T[0], np.min(anomaly_score), np.max(anomaly_score),
                         alpha=0.4, where=outlier == -1,
                         label='outlier_region')        # 很神奇，这里可以直接写outlier == -1
        plt.legend()
        plt.ylabel('anomaly score')
        plt.xlabel(file.columns[i])
        print(file.columns[i], "的异常值范围是：", np.min(anomaly_score), "----", np.max(anomaly_score))
        plt.show()



def main():
    df = pd.read_csv(r"../data_202106_head.tsv", encoding="utf-8", sep="\t")
    target = [5, 6, 7, 13, 14, 15]
    # target是目标列，n_estimators是估算器数量
    Isolation_Forest(df, target, n_estimators=101)

if __name__ == '__main__':
    main()