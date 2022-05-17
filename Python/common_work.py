# coding:utf-8
import pandas as pd
import simplejson as json


def read_dic(dic_file):
    with open(dic_file) as f:
        f = json.load(f)
    return f


def save_dic(dic_file, data):
    info_json = json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '))
    f = open(dic_file, 'w')
    f.write(info_json)


def single_mean_feature_rate_extraction(data, group_by_cols, primary_key, feature):
    '''
    该函数的功能是在data的同一group_by_cols的情况下，求出feature的均值记为mean_feature，然后计算出data中feature/mean_feature
    例如data有[ID, 价格, 产地, 类别],其中ID为识别每个商品的唯一标识
    现在需要求 new_feature = 商品的价格/同一产地和类别情况下的平均价格,（如果值很大，可能就是异常值了）
    传入参数为：
    data : dataframe([ID, 价格, 产地, 类别])
    group_by_cols : [产地, 类别]
    primary_key : [ID]
    feature : [价格]
    return : dataframe([ID, new_feature])
    如果计算时有缺失值无法计算则返回-1
    :param data:dataframe 传入的需要分析的数据
    :param group_by_cols:[col1, col2..] 若干列名组成的列表
    :param primary_key: [key1, key2..] 若干列名组成的列表
    :param feature: str 需要计算平均比例的列名，字符串形式
    :return: dataframe[key1, key2,.. feature_rate]
    '''
    new_data = pd.DataFrame()
    for p in primary_key:
        new_data[p] = data[p]

    dic = {}
    new_feature_name = "same-" + "-".join(group_by_cols) + "-mean-" + feature
    dic_name = new_feature_name + "-mean-dic.json"
    group_data = data.groupby(by=group_by_cols)[feature].mean()
    group_data.to_csv(new_feature_name+"-mean.tsv", sep="\t")  # 分组计算出的均值保存
    key = list(group_data.index)
    value = list(group_data)
    if len(group_by_cols) > 1:
        for ks, v in zip(key, value):
            con_k = []
            for k in ks:
                con_k.append(k)
            con_k = "-".join(con_k)
            dic[con_k] = v
    else:
        for k, v in zip(key, value):
            dic[k] = v
    # save_dic(dic_name, dic)  # 保存字典，数据量大再次计算可以减少计算量

    for key, value in zip(dic.keys(), dic.values()):
        print(key, value)

    def get_rate(x):
        keys = []
        for c in group_by_cols:
            keys.append(str(x[c]))
        keys = "-".join(keys)
        try:
            return x[feature] / dic[keys]
        except:
            return -1
    new_feature_name += "-rate"
    new_data[new_feature_name] = data.apply(lambda x: get_rate(x), axis=1)
    new_data.to_csv(new_feature_name + ".tsv", sep="\t", index=0)


def main():
    f = pd.read_csv("D:\\pcham\\服务外包比赛\\202106_10000.tsv", sep="\t")
    s = pd.read_csv("D:\\pcham\\服务外包比赛\\比赛题目使用数据\\shop.tsv", sep="\t")
    con_data = pd.merge(f, s, how="left", on=["USER_ID", "DATA_MONTH"])
    group_by_cols = ["CATE_NAME_LV1", "SHOP_DELIVERY_PROVINCE"]
    primary_key = ["ITEM_ID"]
    feature = "ITEM_PRICE"
    single_mean_feature_rate_extraction(con_data, group_by_cols, primary_key, feature)


if __name__ == '__main__':
    main()
