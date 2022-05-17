import os
import fire
import json
import string
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

JSONFILEROOT = "./Datasets/"



def getAllelemFilename()->list:
  fileList = os.listdir(JSONFILEROOT[:-1])
  return fileList

def readJson(filename:string)->dict:
  FilePath = JSONFILEROOT+filename if ".json" in filename else JSONFILEROOT+filename+".json"
  with open(FilePath, 'r', encoding='utf-8') as file:
    data = json.load(file)
    print("原始数据长度：：",len(data))
    aim_data = list(filter(lambda x: 0 not in x.values() and x["item_fav_num"] < 1000 and  x["item_fav_num"]!=0 ,data))
    return aim_data

def findFeature(data,end):
  features = ["item_price","item_sales_volume","item_sales_amount","item_fav_num","total_eval_num","item_stock"]
  # features = ["item_price","item_sales_volume","item_sales_amount","item_fav_num","total_eval_num","item_stock"]
  for feat in features:
    sortedData = sorted(data,key=lambda x: x[feat],reverse=True)[:end]
    print(sortedData)

def union():
  data = readJson("6-CATE_NAME_LV1")
  item_price_max = max(data,key=lambda x: x["item_price"])
  item_sales_volume_max = max(data,key=lambda x: x["item_sales_volume"])
  item_sales_amount_max = max(data,key=lambda x: x["item_sales_amount"])
  item_fav_num_max = max(data,key=lambda x: x["item_fav_num"])
  total_eval_num_max = max(data,key=lambda x: x["total_eval_num"])
  item_stock_max = max(data,key=lambda x: x["item_stock"])
  print(item_price_max)
  print(item_sales_volume_max)
  print(item_sales_amount_max)
  print(item_fav_num_max)
  print(total_eval_num_max)
  print(item_stock_max)

def analyze_data(data):
  df = pd.DataFrame(data)
  del df["item_name"]
  print("item_fav_num::",df.item_fav_num.describe())
  plt.subplot(221)
  # sns.distplot(df['item_fav_num'])

  sns.boxplot(x="distance", y="method", data=data,
            whis=[0, 100], width=.6, palette="vlag")
  # plt.figure(figsize=(10,6), dpi=80)
  # sns.regplot(data=df,x="item_fav_num", y="total_eval_num")
  plt.show()

def ceshiZhishu():
  from scipy import stats
  import pandas as pd
  import numpy as np
  # scipy包是一个高级的科学计算库，它和Numpy联系很密切，Scipy一般都是操控Numpy数组来进行科学计算

  data = np.random.exponential(10, size=20)
  data = pd.DataFrame(data)
  # print(data)
  u = data.mean()
  std = data.std()
  p = stats.kstest(data[0], 'expon', (u, std))
  print(p)
  # .kstest方法：KS检验，参数分别是：待检验的数据，检验方法（这里设置成norm正态分布），均值与标准差
  # 结果返回两个值：statistic → D值，pvalue → P值
  # p值大于0.05，为正态分布


if __name__ == '__main__':
  # data = readJson("8-CATE_NAME_LV1-家用电器")
  # # findFeature(data,20)
  # analyze_data(data)
  # # union()
  # print("success")
  ceshiZhishu()