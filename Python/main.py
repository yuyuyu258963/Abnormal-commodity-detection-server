import os
import os
import sys
import fire
import json
import sklearn
import threading
import numpy as np
import pandas as pd
import numpy as np
from pyod.models.cblof import CBLOF
from sklearn.ensemble import IsolationForest

from run_model import box, outlier_detection


# 前端保存的需要检测的数据的文件路径
TRAIN_FILE_ROOT = "./RedutionRes/"
PRICE_SAVED_DATA_FILE_NAME = "sendUseModelPriceData.tsv"
SALE_SAVED_DATA_FILE_NAME = "sendUseModelSaleData.tsv"


def saveJson(data, fileName):
  """
    保存json文件
  """
  with open(fileName, 'w', encoding='utf-8') as file:
    file.write(json.dumps(data, ensure_ascii=False))
    

def getBoxErr(data,col_box="ITEM_PRICE"):
  error, error_may = box(data, col_box)
  return error


def run_priceModels():
  """
    运行模型寻找价格异常
  """
  iso_forest = IsolationForest(random_state=1000)
  # cb_lof = CBLOF(contamination=0.05, random_state=1000)
  data = pd.read_csv(TRAIN_FILE_ROOT + PRICE_SAVED_DATA_FILE_NAME, sep="\t")

  shop_data = pd.read_csv("./RedutionRes/价格结果.csv", index_col=0)
  check_data = pd.merge(shop_data, data, how="left", on=["DATA_MONTH", "USER_ID"])

  all = len(check_data)
  some = len(check_data[~check_data["ITEM_ID"].isnull()])
  print("shop", some / all)
  contamination = 0.03 + 0.01 * some / all
  cb_lof = CBLOF(contamination=contamination, random_state=1000)
  
  perDataLen = data.shape[0]
  # "ITEM_PRICE",
  cols = ["same-CATE_NAME_LV1-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV2-mean-ITEM_PRICE-rate",
          "same-CATE_NAME_LV3-mean-ITEM_PRICE-rate", "same-ITEM_ID-mean-ITEM_PRICE-rate",
          "same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_PRICE-rate-rate",
          "same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_PRICE-rate",
          "same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_PRICE-rate"]
  row_data = data
  data = data[data["ITEM_PRICE"] >= row_data["ITEM_PRICE"].describe().loc["75%"]]

  cols_primary = ["same-CATE_NAME_LV1-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV2-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV3-mean-ITEM_PRICE-rate"]
  for c in cols_primary:

    data = data[data[c] >= row_data[c].describe().loc["75%"]]

  isf_result = outlier_detection(iso_forest, data, cols, "sklearn")
  # cblof 的结果
  cb_lof_result = outlier_detection(cb_lof, data, cols, "pyod")

  col_box = ["ITEM_PRICE"]
  error = getBoxErr(data,col_box)
  
  result = pd.DataFrame()
  result = result.append(isf_result)
  result = result.append(cb_lof_result)
  result = result.drop_duplicates()

  part = pd.DataFrame()
  col_con = ["ITEM_ID", "ITEM_PRICE", "DATA_MONTH", "USER_ID"]
  for c in col_con:
    part[c] = cb_lof_result[c]

  result_jiao = pd.merge(isf_result, part, how="inner", on=col_con)
  print("isf", len(isf_result), "cblof", len(cb_lof_result), "sum", len(result), "jiao", len(result_jiao))

  filteredJiao = result_jiao[result_jiao["ITEM_PRICE"] > error[0]]
  data = np.array(filteredJiao["ITEM_ID"]).tolist()
  
  
  resData = {
    "data":                     data,
    "isf_name":                 "ISOF",
    "isf_resultLen":            len(isf_result),
    "isf_res_mean":             round(isf_result["ITEM_PRICE"].describe().loc["mean"],3),
    "isf_percent":              str(round(100 * len(isf_result) / perDataLen,3))[:6] + "%",
    "cblof_name":               "CBLOF",
    "cblof_resultLen":          len(cb_lof_result),
    "cblof_res_mean":           round(cb_lof_result["ITEM_PRICE"].describe().loc["mean"],3),
    "cblof_percent":            str(round(len(100 * cb_lof_result) / perDataLen,3))[:6] + "%",
    "jiao_resultLen":           len(result_jiao),
    "jiao_res_mean":            round(result_jiao["ITEM_PRICE"].describe().loc["mean"],3),
    "jiao_percent":             str(round(100 * len(result_jiao) / perDataLen,3))[:6] + "%",
    "filteredJiao_resultLen":   len(filteredJiao),
    "filteredJiao_res_mean":    round(filteredJiao["ITEM_PRICE"].describe().loc["mean"],3),
    "filteredJiao_percent":     str(round(100 * len(filteredJiao) / perDataLen,3))[:6] + "%",
    "filteredJiao_percentNum":  round(100 * len(filteredJiao) / perDataLen,3),
    "errLine":         error[0],
  }
  saveJson(resData, TRAIN_FILE_ROOT + "/sumPrice_error_jiaoData.json")
  
  result_jiao.to_csv(TRAIN_FILE_ROOT + "/sumPrice_error_jiaoData.tsv", sep="\t", index=0)

def run_saleModels():
  """
    运行模型寻找销量异常
  """
  iso_forest = IsolationForest(random_state=1000)
  # cb_lof = CBLOF(contamination=0.05, random_state=1000)
  data = pd.read_csv(TRAIN_FILE_ROOT + SALE_SAVED_DATA_FILE_NAME, sep="\t")
  perDataLen = data.shape[0]
  shop_data = pd.read_csv("./RedutionRes/销量结果.csv", index_col=0)
  check_data = pd.merge(shop_data, data, how="left", on=["DATA_MONTH", "USER_ID"])

  all = len(check_data)
  some = len(check_data[~check_data["ITEM_ID"].isnull()])
  print("shop", some / all)
  contamination = 0.03 + 0.01 * some / all
  cb_lof = CBLOF(contamination=contamination, random_state=1000)
  
  
  cols = ["same-CATE_NAME_LV1-mean-ITEM_SALES_VOLUME-rate", "same-CATE_NAME_LV2-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV3-mean-ITEM_SALES_VOLUME-rate", "same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate-rate",
                "same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_SALES_VOLUME-rate"]
  row_data = data
  data = data[data["ITEM_SALES_VOLUME"] >= row_data["ITEM_SALES_VOLUME"].describe().loc["75%"]]

  cols_primary = ["same-CATE_NAME_LV1-mean-ITEM_SALES_VOLUME-rate", "same-CATE_NAME_LV2-mean-ITEM_SALES_VOLUME-rate", "same-CATE_NAME_LV3-mean-ITEM_SALES_VOLUME-rate"]
  for c in cols_primary:
      data = data[data[c] >= row_data[c].describe().loc["75%"]]

  isf_result = outlier_detection(iso_forest, data, cols, "sklearn")
  # cblof 的结果
  cb_lof_result = outlier_detection(cb_lof, data, cols, "pyod")

  col_box = ["ITEM_SALES_VOLUME"]
  error = getBoxErr(data,col_box)
  
  # isf_result = isf_result[isf_result["ITEM_SALES_VOLUME"] > error[0]]
  # cb_lof_result = cb_lof_result[cb_lof_result["ITEM_SALES_VOLUME"] > error[0]]

  result = pd.DataFrame()
  result = result.append(isf_result)
  result = result.append(cb_lof_result)
  result = result.drop_duplicates()

  part = pd.DataFrame()
  col_con = ["ITEM_ID", "ITEM_SALES_VOLUME", "DATA_MONTH", "USER_ID"]
  for c in col_con:
    part[c] = cb_lof_result[c]

  result_jiao = pd.merge(isf_result, part, how="inner", on=col_con)

  print("isf", len(isf_result), "cblof", len(cb_lof_result), "sum", len(result), "jiao", len(result_jiao))

  # data = np.array(result_jiao["ITEM_ID"]).tolist()

  filteredJiao = result_jiao[result_jiao["ITEM_SALES_VOLUME"] > error[0]]
  data = np.array(filteredJiao["ITEM_ID"]).tolist()

  
  resData = {
    "data":                     data,
    "isf_name":                 "ISOF",
    "isf_resultLen":            len(isf_result),
    "isf_percent":              str(round(100 * len(isf_result) / perDataLen,3))[:6] + "%",
    "isf_res_mean":             round(isf_result["ITEM_SALES_VOLUME"].describe().loc["mean"],3),
    "cblof_name":               "CBLOF",
    "cblof_resultLen":          len(cb_lof_result),
    "cblof_res_mean":           round(cb_lof_result["ITEM_SALES_VOLUME"].describe().loc["mean"],3),
    "cblof_percent":            str(round(100 * len(cb_lof_result) / perDataLen,3))[:6] + "%",
    "jiao_resultLen":           len(result_jiao),
    "jiao_res_mean":            round(result_jiao["ITEM_SALES_VOLUME"].describe().loc["mean"],3),
    "jiao_percent":             str(round(100 * len(result_jiao) / perDataLen,3))[:6] + "%",
    "filteredJiao_resultLen":   len(filteredJiao),
    "filteredJiao_res_mean":    round(filteredJiao["ITEM_SALES_VOLUME"].describe().loc["mean"],3),
    "filteredJiao_percent":     str(round(100 * len(filteredJiao) / perDataLen,3))[:6] + "%",
    "filteredJiao_percentNum":  round(100 * len(filteredJiao) / perDataLen,3),
    "errLine":            error[0],
  }
  saveJson(resData, TRAIN_FILE_ROOT + "/sumSale_error_jiaoData.json")
  result_jiao.to_csv(TRAIN_FILE_ROOT + "/sumSale_error_jiaoData.tsv", sep="\t", index=0)

def main():
  
  # run_priceModels()
  # run_saleModels()
  
  t1 = threading.Thread(target=run_priceModels)
  t2 = threading.Thread(target=run_saleModels)
  t1.start()
  t2.start()
  t1.join()
  t2.join()


if __name__ == '__main__':
  main()
  pass