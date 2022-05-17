import json
import pandas as pd
import numpy as np

# 数组合并同时去重
def flatten(arr):
  res = []
  for item in arr:
    res += item
  return list(set(res))

def readJsonData(filename):
  with open(filename, "r", encoding='utf-8') as file:
    data = json.load(file)
    return data

def saveJsonData(filename, data):
  with open(filename, "w", encoding='utf-8') as file:
    file.write(json.dumps(data,ensure_ascii=False))

def dataUnion(dataset , idGroups):
  aim_data_transed = {}
  aim_data2id = {}
  print("开始处理 -> ", end="")
  for k, v in idGroups.items():
    print(k, end="",flush=True)
    print("\b"*len(k), end="", flush=True)
    unionV = flatten(v)
    itemData = dataset[k]
    aim_data = [[
      itemData[index][monthData.index(Pid)] if Pid in monthData else -1  for Pid in unionV
    ] for index,monthData in enumerate(v)]
    aim_data_transed[k] = aim_data
    aim_data2id[k] = unionV
  return aim_data_transed, aim_data2id

def main():
  dataset = readJsonData("./TransedData/price_data.json")
  idGroups = readJsonData("./TransedData/price_data2ids.json")
  # print(idGroups.items())
  aim_data, aim_data2id = dataUnion(dataset, idGroups)
  saveJsonData("./TransedData/res_price_data.json", aim_data)
  saveJsonData("./TransedData/res_price_data2ids.json", aim_data2id)

def viewData():
  data = readJsonData("./TransedData/res_price_data.json")
  # aim_data2id = readJsonData("./TransedData/res_price_data2ids.json")
  # d = max(data.items(), key=lambda x:len(x[0]))
  # print(d)
  for k, v in data.items():
    df = np.array(v)
    print(df.max())
    # sumdf = df.sum(axis=0)
    # print(sumdf)

if __name__ == '__main__':
  # main()
  viewData()
  print("success")
  pass