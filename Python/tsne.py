import os
import json
import sys
import fire
import pymysql
import numpy as np
import matplotlib.pyplot as plt
from dbscan import *
from sklearn.manifold import TSNE

DATAFILEROOT = f"../Server/RedutionRes/"
SAVEVECDATAROOT = f"../Server/RedutionRes/"
# DATAFILEROOT = "../FilteredData/"
FILETYPE = ".json"
LIMITNUM = 400000

# mysql连接的配置
mysqlOption = {
  "host": "121.41.27.5",
  "user": "root",
  "password": "ywh",
  "database": "Outsourced",
}

# 提前连接好数据库避免重复连接
db = pymysql.connect( host=mysqlOption["host"], user=mysqlOption["user"], password=mysqlOption["password"], database=mysqlOption["database"] )
cursor = db.cursor()

# 根据user_id 查询商店的信息
def get_shopData(userId,colName="SHOP_SALES_VOLUME"):
  cursor.execute("SELECT "+ colName +" from shop where USER_ID = '" + userId + "'")
  data = cursor.fetchall()
  all_volume_val = [item[0] for item in data]
  avg_data = sum(all_volume_val) / 4
  return avg_data

# 获取需要降维的数据   SHOP_OPEN_DATE
def get_data(filename:str):
  with open(DATAFILEROOT + filename + FILETYPE, 'r', encoding='utf-8') as file:
    data = json.load(file)
    aim_data = [[x["item_price"],x["item_sales_volume"],x["item_fav_num"]
              ,x["total_eval_num"],x["item_stock"]
              ] for x in data]
    data_id = [x['item_id'] for x in data]
    
    # aim_data = list(map(lambda x: [
    #                               x["item_price"],x["item_sales_volume"],
    #                               x["item_fav_num"],
    #                               ], data[:LIMITNUM]))
    # data_id = list(map(lambda x: x["item_id"],data[:LIMITNUM]))
    np_arr = np.array(aim_data)
    return np_arr,data_id

# 对数据进行降维
def reduce_v(data):
  # 嵌入空间的维度为2，即将数据降维成2维
  ts = TSNE(n_components=2)
  ts.fit_transform(data)
  vec_2 = ts.embedding_
  return vec_2

def draw(data):
  X = np.array(data)
  print(len(X),len(X[0]))
  colors = [i//100 * 10 for i in range(len(data))] 
  plt.title("t_sne")
  plt.scatter(X[:, 0], X[:, 1],s= 12, c = colors)
  plt.show()

def saveJsonFile(filename:str,data):
  file = open(SAVEVECDATAROOT + filename + FILETYPE, 'w')
  file.write(json.dumps(data,ensure_ascii=False))

def main(loadFileName="7-CATE_NAME_LV1-其他",savefileName="test4"):
  print(loadFileName,savefileName)
  data,data_id = get_data(loadFileName)
  vec_2_data = reduce_v(data)
  saveJsonFile(savefileName, {"vecData":vec_2_data.tolist(),"gId":data_id})


if __name__ == '__main__':
  fire.Fire()
  #main()
  print("success")