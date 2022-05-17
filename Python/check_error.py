import sys
import fire
import os
import numpy as np
from statsmodels.stats.stattools import medcouple
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import simplejson as json

# 获取文件所在的真实路径
# FILEROOT = os.path.dirname(os.path.realpath(sys.argv[0])) + f"\\"

#  改进的箱线图
def boxplot_plus(data : pd.DataFrame, cols : list):
    limit = []
    for col in cols:
        if len(data[col]) > 10000:  # 大于10000就抽样计算估计数据的MC
            samples = data[col].sample(n=10000)
        else:
            samples = data[col]

        MC = medcouple(samples)
        # print(col, "medcouple:", MC)
        des = data[col].describe()

        Q1 = des.loc["25%"]
        Q3 = des.loc["75%"]
        IQR = Q3 - Q1

        L = 0
        U = 0
        if MC >= 0:
            L = Q1 - 1.5 * np.exp(-3.5 * MC) * IQR
            U = Q3 + 1.5 * np.exp(4 * MC) * IQR
        else:
            L = Q1 - 1.5 * np.exp(-4 * MC) * IQR
            U = Q3 + 1.5 * np.exp(3.5 * MC) * IQR

        # print(col, "boxplot_plus异常值界限：", U)

        error = data[(data[col] > U)]  # 只取高的异常值
        # error.to_csv(col + "error.tsv", sep="\t", index=0)
        if len(error) == 0:
            limit.append(-1)
            # print("未检测出异常值")
        else :
            limit.append(U)
        # limit.append(U)
        # else:
        #     print("检测出的异常值数量为", len(error))
        
    return limit

# MADe法
# def MADe(data, cols):
#     limit = []
#     for col in cols:
#         X = data
#         M = X[col].median()
#         MAD = (np.abs(X[col] - X[col].median())).median()
#         down = M - 3 * MAD * 1.483
#         up = M + 3 * MAD * 1.483
#         limit.append(up)
#         error = X[(X[col] > up)]
#         print(col, "-----------")
#         print("MADe上界", up)
#         if len(error) == 0:
#             print("此方法未检测出异常值")
#         else:
#             print("检测出", len(error))
#     return limit

# # 训练数据包含异常值
# def outlier_detection(model, data, cols):
#     Y = pd.DataFrame()
#     for col in cols:
#         # Y[col] = (data[col] - data[col].mean()) / data[col].std()
#         Y[col] = data[col]
#     model.fit(Y)
#     y = model.fit_predict(Y)
#     data["label"] = y
#     print("----------")
#     print(str(model))
#     print("检测出的异常数为", len(data[data["label"] == -1]))
#     print("检测正常值为", len(data[data["label"] == 1]))

#     plt.scatter(data[cols[0]], data[cols[1]], c=y)  # 样本点的颜色由y值决定
#     plt.show()
#     return data[data["label"] == -1]

# # 训练数据晒过异常值，用于寻找训练数据外的数据里的异常值
# def novelty_detection(model, train_data, pre_data, cols):
#     X = pd.DataFrame()
#     Y = pd.DataFrame()
#     for col in cols:
#         # X[col] = (train_data[col] - train_data[col].mean()) / train_data[col].std()
#         # Y[col] = (pre_data[col] - pre_data[col]) / pre_data[col].std()
#         X[col] = train_data[col]
#         Y[col] = pre_data[col]

#     model.fit(X)
#     y = model.predict(Y)
#     print("----------")
#     print(str(model))
#     pre_data["label"] = y
#     print("检测出的异常数为", len(pre_data[pre_data["label"] == -1]))
#     print("检测正常值为", len(pre_data[pre_data["label"] == 1]))

#     plt.scatter(pre_data[cols[0]], pre_data[cols[1]], c=y)  # 样本点的颜色由y值决定
#     # plt.show()
#     return pre_data[pre_data["label"] == -1]

""" 
def main():
    np.random.seed(0)
    goods_words = ['其他', '其他商品', '家居建材', '家用电器', '手机数码', '数字阅读', '文化玩乐', '服装鞋包', '母婴用品', '汽配摩托', '游戏话费', '生活服务', '百货食品',
                '盒马', '美妆饰品', '运动户外']
    cols = ["item_price", "item_sales_volume"]
    # cols = ["ITEM_PRICE", "ITEM_SALES_VOLUME", "ITEM_SALES_AMOUNT"]
    path = "../比赛题目使用数据/"
    file = path + "202106.tsv"
    file_data = pd.read_csv(file, sep="\t")

    for good in goods_words[:1]:
        f = file_data[file_data["CATE_NAME_LV1"] == good]
        print("数据总数为:", len(f))
        # limit为各个特征的异常上界
        limit1 = boxplot_plus(f, cols)
        # limit2 = MADe(f, cols)

        # # 模型需要调参，支持向量机训练时间长的令人发指，注释掉了。
        # LOF_novelty_model = LocalOutlierFactor(novelty=True)
        # # OCS_novelty_model = OneClassSVM()

        # LOF_outlier_model = LocalOutlierFactor()
        # # OCS_outlier_model = OneClassSVM()
        # ISF_outlier_model = IsolationForest()

        # # 孤立森林直接寻找异常点
        # ISF_outlier_result = outlier_detection(ISF_outlier_model, f, cols)
        # # LOF直接寻找异常点
        # LOF_outlier_result = outlier_detection(LOF_outlier_model, f, cols)
        # # OSC_outlier_result = outlier_detection(OCS_outlier_model, f, cols)
        
        # # MADe筛出异常值后的数据LOF训练，然后筛出MADe筛出的异常值的数据
        # LOF_novelty_result = novelty_detection(LOF_novelty_model, f[f[cols[0]] <= limit2[0]], f[f[cols[0]] >= limit2[0]], cols)
        # # OSC_novelty_result = novelty_detection(OCS_novelty_model, f[f[cols[0]] <= limit2[0]], f[f[cols[0]] >= limit2[0]], cols)

        # # 价格高于箱线图异常值水平的
        # LOF_novelty_result = LOF_novelty_result[LOF_novelty_result["ITEM_PRICE"] > limit1[0]]
        # # 改变dataframe列顺序
        # new_col_order = ["ITEM_PRICE", "ITEM_SALES_VOLUME", "ITEM_SALES_AMOUNT","DATA_MONTH","ITEM_ID","ITEM_NAME","BRAND_ID","BRAND_NAME","CATE_NAME_LV1","CATE_NAME_LV2","CATE_NAME_LV3","CATE_NAME_LV4","CATE_NAME_LV5","ITEM_FAV_NUM","TOTAL_EVAL_NUM","ITEM_STOCK","ITEM_DELIVERY_PLACE","ITEM_PROD_PLACE","ITEM_PARAM","USER_ID", "SHOP_NAME","label"]
        # LOF_novelty_result = LOF_novelty_result[new_col_order]
        # LOF_novelty_result.to_csv("MADe_LOF.tsv", sep="\t", index=0)
        
        # # 只计算一种类别
        # break
"""



def ReadJSON(filename="6-CATE_NAME_LV1-其他")-> pd.DataFrame:
    """
        用于读取json格式的数据并转化格式
    """
    DATASETROOT = "./Datasets/"
    aimColNames = ["item_id","item_price","item_sales_volume"]
    with open(DATASETROOT + filename + ".json", "r", encoding="utf-8") as file:
        data = json.load(file)
        attributes = [ [item[colName] for colName in aimColNames] for item in data ]
        df = pd.DataFrame(attributes, columns=aimColNames)
        # print(df)
        return df

def findDiffData(df):
    cols = ["item_price", "item_sales_volume"]
    limit = boxplot_plus(df, cols)
    print(limit)

def main(filename="6-CATE_NAME_LV1-其他"):
    df = ReadJSON(filename)
    findDiffData(df)

if __name__ == '__main__':
    fire.Fire()
    # main("7-CATE_NAME_LV1-数字阅读")
