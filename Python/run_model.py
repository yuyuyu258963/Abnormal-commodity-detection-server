# coding:utf-8
import fire
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
# pyod的包
from pyod.models.abod import ABOD
from pyod.models.cblof import CBLOF
# from pyod.models.feature_bagging import FeatureBagging
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from scipy import stats
from pyod.models.knn import KNN
from pyod.models.mcd import MCD
from pyod.models.pca import PCA


def box(data, cols):  # 箱线图初筛和终筛
    error = []
    error_may = []
    for col in cols:
        des = data[col].describe()
        Q1 = des.loc["25%"]
        Q3 = des.loc["75%"]
        IQR = Q3 - Q1

        I_L = Q1 - 1.5 * IQR
        I_U = Q3 + 1.5 * IQR

        O_L = Q1 - 3 * IQR
        O_U = Q3 + 3 * IQR

        error.append(O_U)
        error_may.append(I_U)

    def ruler(x):
        flag_err = 0
        flag_may = 0
        for i in range(len(cols)):
            if x[cols[i]] < error_may[i]:  # 如果此数据正确跳过
                continue
            if x[cols[i]] >= error[i]:  # 如果此数据大于错误的线
                flag_err += 1
            else:  # 否则就是落入可能错误的区域
                flag_may += 1
        if flag_err == len(cols):
            return -1
        elif flag_may == 0:
            return 1
        else:
            return 0

    return error, error_may


def outlier_detection(model, data, cols, flag):  # 模型寻找异常值并保存文件
    Y = pd.DataFrame()
    for col in cols:
        Y[col] = (data[col] - data[col].mean()) / data[col].std()
        Y[col] = data[col]
    model.fit(Y)

    y = model.predict(Y)
    data["label"] = y
    print("----------")
    # print(str(model))
    if flag == "pyod":
        error = data[data["label"] == 1]
        error = error.drop(columns=["label"])
        # print("检测出的异常数为", len(error))
        # print("检测正常值为", len(data[data["label"] == 0]))
        return error
    else:
        error = data[data["label"] == -1]
        error = error.drop(columns=["label"])
        print("检测出的异常数为", len(error))
        print("检测正常值为", len(data[data["label"] == 1]))
        return error

    # plt.scatter(data[cols[0]], data[cols[1]], c=y)  # 样本点的颜色由y值决定
    # plt.show()


def check_price(price_error_path):  # 查看价格异常数情况
    """
        查看价格异常数情况
    """
    sum = 0
    data = pd.DataFrame()

    for file in Path(price_error_path).rglob("*"):
        d = pd.DataFrame()
        f = pd.read_csv(file, sep="\t")
        num = len(f)
        print(file, num)
        print(f["ITEM_PRICE"].describe())
        sum += num
        d["DATA_MONTH"] = f["DATA_MONTH"]
        d["ITEM_ID"] = f["ITEM_ID"]
        data = data.append(d)
    print("总数", sum)
    return data


def check_sale(sale_error_path):  # 查看销量异常数情况
    """
        查看销量异常数情况
    """
    sum = 0
    data = pd.DataFrame()

    for file in Path(sale_error_path).rglob("*"):
        d = pd.DataFrame()
        f = pd.read_csv(file, sep="\t")
        num = len(f)
        print(file, num)
        print(f["ITEM_SALES_VOLUME"].describe())
        sum += num
        d["DATA_MONTH"] = f["DATA_MONTH"]
        d["ITEM_ID"] = f["ITEM_ID"]
        data = data.append(d)
    print("总数", sum)
    return data


def price_models(train_data_filepath, two_model_result_path, concat_result_path, save_model_path):  # 价格异常查找模型
    iso_forest = IsolationForest(random_state=1000)
    cb_lof = CBLOF(contamination=0.05, random_state=1000)

    for file in Path(train_data_filepath).rglob("*"):
        f = str(file).split("\\")
        filename = f[-1]
        print(filename)
        data = pd.read_csv(file, sep="\t")
        col_box = ["ITEM_PRICE"]
        # "ITEM_PRICE",
        cols = ["same-CATE_NAME_LV1-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV2-mean-ITEM_PRICE-rate",
                "same-CATE_NAME_LV3-mean-ITEM_PRICE-rate", "same-ITEM_ID-mean-ITEM_PRICE-rate",
                "same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_PRICE-rate-rate",
                "same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_PRICE-rate",
                "same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_PRICE-rate"]
        error, error_may = box(data, col_box)
        # print(error)
        # print(error_may)
        data = data[data["ITEM_PRICE"] >= data["ITEM_PRICE"].describe().loc["50%"]]

        print("data", len(data))

        cols_primary = ["same-CATE_NAME_LV1-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV2-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV3-mean-ITEM_PRICE-rate"]
        for c in cols_primary:
            data = data[data[c] >= data[c].describe().loc["50%"]]
        
        print("train_data", len(data))
        # 孤立森林模型的
        isf_result = outlier_detection(iso_forest, data, cols, "sklearn", f[-1], "price", save_model_path)
        # cblof 的结果
        cb_lof_result = outlier_detection(cb_lof, data, cols, "pyod", f[-1], "price", save_model_path)

        isf_result = isf_result[isf_result["ITEM_PRICE"] > error[0]]
        cb_lof_result = cb_lof_result[cb_lof_result["ITEM_PRICE"] > error[0]]

        isf_result.to_csv(two_model_result_path + "/isf_" + filename, sep="\t", index=0)
        cb_lof_result.to_csv(two_model_result_path + "/cblof_" + filename, sep="\t", index=0)

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
        result_jiao.to_csv(concat_result_path + "/sum_error_jiao_"+filename, sep="\t", index=0)
        # result.to_csv("sum_error_"+filename, sep="\t", index=0)


def sale_models(train_data_filepath, two_model_result_path, concat_result_path, save_model_path):  # 销量异常查找模型
    iso_forest = IsolationForest(random_state=1000)
    cb_lof = CBLOF(contamination=0.05, random_state=1000)


    for file in Path(train_data_filepath).rglob("*"):
        f = str(file).split("\\")
        filename = f[-1]
        print(filename)
        data = pd.read_csv(file, sep="\t")
        col_box = ["ITEM_SALES_VOLUME"]
        # "ITEM_PRICE",
        cols = ["same-CATE_NAME_LV1-mean-ITEM_SALES_VOLUME-rate", "same-CATE_NAME_LV2-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV3-mean-ITEM_SALES_VOLUME-rate", "same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate-rate",
                "same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_SALES_VOLUME-rate",
                "same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_SALES_VOLUME-rate"]
        error, error_may = box(data, col_box)
        print(error)
        print(error_may)
        data = data[data["ITEM_SALES_VOLUME"] >= data["ITEM_SALES_VOLUME"].describe().loc["50%"]]

        print("data", len(data))

        cols_primary = ["same-CATE_NAME_LV1-mean-ITEM_SALES_VOLUME-rate", "same-CATE_NAME_LV2-mean-ITEM_SALES_VOLUME-rate", "same-CATE_NAME_LV3-mean-ITEM_SALES_VOLUME-rate"]
        for c in cols_primary:
            data = data[data[c] >= data[c].describe().loc["50%"]]

        print("train_data", len(data))
        isf_result = outlier_detection(iso_forest, data, cols, "sklearn", f[-1], "sale", save_model_path)
        cb_lof_result = outlier_detection(cb_lof, data, cols, "pyod", f[-1], "sale", save_model_path)

        isf_result = isf_result[isf_result["ITEM_SALES_VOLUME"] > error[0]]
        cb_lof_result = cb_lof_result[cb_lof_result["ITEM_SALES_VOLUME"] > error[0]]

        isf_result.to_csv(two_model_result_path + "/isf_" + filename, sep="\t", index=0)
        cb_lof_result.to_csv(two_model_result_path + "/cblof_" + filename, sep="\t", index=0)

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
        result_jiao.to_csv(concat_result_path + "/sum_error_jiao_" + filename, sep="\t", index=0)
        # result.to_csv("sum_error_"+filename, sep="\t", index=0)


def concat():
    error = pd.DataFrame()
    file_id = []
    file_name = []
    price_error_path = "D:\pcham\服务外包比赛\check_outer\price_error"
    ALL_DATA_path = "D:\pcham\服务外包比赛\比赛题目使用数据\ALL_DATA.tsv"
    price_error_detail_path = "D:\pcham\服务外包比赛\check_outer\price_error\error_detail"
    sale_error_path = "D:\pcham\服务外包比赛\check_outer\sale_error\sale_error"
    sale_error_detail_path ="D:\pcham\服务外包比赛\check_outer\sale_error\error_detail"

    for i, file in enumerate(Path(price_error_path).rglob("*")):
        print(file)
        f = pd.read_csv(file, sep="\t")
        name = str(file).split("\\")[-1]
        f["file"] = i
        error = error.append(f)
        file_id.append(i)
        file_name.append(name)

    print("read")
    data = pd.read_csv(ALL_DATA_path, sep="\t")
    detail = pd.merge(error, data, how="left", on=["ITEM_ID", "DATA_MONTH", "ITEM_PRICE", "USER_ID"])

    for id, name in zip(file_id, file_name):
        print(name)
        f = detail[detail["file"] == id]
        f = f.sort_values(by=["ITEM_PRICE"])
        col = "DATA_MONTH	ITEM_ID	CATE_NAME_LV1	CATE_NAME_LV2	CATE_NAME_LV3	ITEM_PRICE	ITEM_SALES_VOLUME	ITEM_NAME	ITEM_PARAM	SHOP_NAME	same-CATE_NAME_LV1-mean-ITEM_PRICE-rate	same-CATE_NAME_LV2-mean-ITEM_PRICE-rate	same-CATE_NAME_LV3-mean-ITEM_PRICE-rate	same-ITEM_ID-mean-ITEM_PRICE-rate	USER_ID	same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_PRICE-rate-rate	same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_PRICE-rate	same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_PRICE-rate	same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_PRICE-rate	file"
        col = col.split("\t")
        f = f[col]
        f.to_csv(price_error_detail_path + "/error_detail"+name, sep="\t", index=0)

    # sale
    error = pd.DataFrame()
    file_id = []
    file_name = []
    for i, file in enumerate(Path(sale_error_path).rglob("*")):
        print(file)
        f = pd.read_csv(file, sep="\t")
        name = str(file).split("\\")[-1]
        f["file"] = i
        error = error.append(f)
        file_id.append(i)
        file_name.append(name)
    detail = pd.merge(error, data, how="left", on=["ITEM_ID", "DATA_MONTH", "ITEM_SALES_VOLUME", "USER_ID"])

    for id, name in zip(file_id, file_name):
        print(name)
        f = detail[detail["file"] == id]
        f = f.sort_values(by=["ITEM_SALES_VOLUME"])
        col = "DATA_MONTH	ITEM_ID	CATE_NAME_LV1	CATE_NAME_LV2	CATE_NAME_LV3	ITEM_PRICE	ITEM_SALES_VOLUME	ITEM_NAME	ITEM_PARAM	SHOP_NAME	same-CATE_NAME_LV1-mean-ITEM_SALES_VOLUME-rate	same-CATE_NAME_LV2-mean-ITEM_SALES_VOLUME-rate	same-CATE_NAME_LV3-mean-ITEM_SALES_VOLUME-rate	same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate	USER_ID	same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate-rate	same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_SALES_VOLUME-rate	same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_SALES_VOLUME-rate	same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_SALES_VOLUME-rate	file"
        col = col.split("\t")
        f = f[col]
        f.to_csv(sale_error_detail_path + "/error_detail"+name, sep="\t", index=0)


def check(price_error_path, sale_error_path):
    d1 = check_sale(price_error_path)
    d2 = check_price(sale_error_path)
    d3 = d1.append(d2)
    d3 = d3.drop_duplicates()
    print("sale", len(d1), "price", len(d2), len(d3))


def main():
    # 模型保存路径
    save_model_path = "./Model/"

    # 价格训练数据文件路径
    price_train_data_filepath = "D:\pcham\服务外包比赛\品牌处理\col1_classfy_data"
    # 两个模型分别保存的路径
    price_two_model_result_path = "D:\pcham\服务外包比赛\check_outer\price_error\model_error"
    # 价格异常结果路径
    price_error_path = "D:\pcham\服务外包比赛\check_outer\price_error\price_error"

    sale_train_data_filepath = "D:\pcham\服务外包比赛\品牌处理\col1_classfy_data_sale"
    sale_two_model_result_path = "D:\pcham\服务外包比赛\check_outer\sale_error\model_error"
    sale_error_path = "D:\pcham\服务外包比赛\check_outer\sale_error\sale_error"

    # 价格异常识别
    price_models(price_train_data_filepath, price_two_model_result_path, price_error_path, save_model_path)
    # 查看价格异常数
    # check_price(price_error_path)

    sale_models(sale_train_data_filepath, sale_two_model_result_path, sale_error_path, save_model_path)
    # check_sale(sale_error_path)

    # check(price_error_path, sale_error_path)
    # concat()


if __name__ == "__main__":
    fire.Fire()
    # main()

