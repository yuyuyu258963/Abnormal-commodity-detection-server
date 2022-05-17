import simplejson as json
import fire
import pymysql
import numpy as np
from sklearn.manifold import TSNE

DATAFILEROOT = f"./RedutionRes/"
SAVEVECDATAROOT = f"./RedutionRes/"

FILETYPE = ".json"
LIMITNUM = 3000

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

# 根据user_id 查询商店的信息
def get_DateNum(userId,colName="SHOP_OPEN_DATE"):
  cursor.execute("SELECT "+ colName +" from shop where USER_ID = '" + userId + "'")
  data = cursor.fetchall()
  yearLen =  2022 - int(data[0][0].split("-")[0])
  return yearLen

# 获取需要降维的数据   SHOP_OPEN_DATE
def get_data(filename:str):
  with open(DATAFILEROOT + filename + FILETYPE, 'r', encoding='utf-8') as file:
    data = json.load(file)
    aim_data = list(map(lambda x: [
                                  x["item_price"],x["item_sales_volume"],
                                  x["item_fav_num"],x["total_eval_num"],
                                  get_shopData(x["user_id"]),get_shopData(x["user_id"],"SHOP_SALES_AMOUNT"),
                                  get_DateNum(x["user_id"]),
                                  ], data[:LIMITNUM]))
    data_id = list(map(lambda x: x["item_id"],data[:LIMITNUM]))
    np_arr = np.array(aim_data)
    return np_arr,data_id

# 对数据进行降维
def reduce_v(data):
  ts = TSNE(n_components=2)
  ts.fit_transform(data)
  vec_2 = ts.embedding_
  return vec_2

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