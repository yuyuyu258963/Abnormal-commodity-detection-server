package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"os"
	"reflect"
)

/*
	用于存放各种类型的定义以及对应的方法的
*/

// 用于查询到的数据类型
type KindInformation struct {
	Count int    `json:"count"`
	Name  string `json:"name"`
}

// 保存一个商品查到的一些信息
type ProductInformation struct {
	ITEM_ID 						string 			`json:"item_id"`
	ITEM_NAME 					string 			`json:"item_name"`
	CATE_NAME_LV2 			string 			`json:"cate_name_lv2"`
	CATE_NAME_LV3 			string 			`json:"cate_name_lv3"`
	CATE_NAME_LV4 			string 			`json:"cate_name_lv4"`
	CATE_NAME_LV5 			string 			`json:"cate_name_lv5"`
	ITEM_PRICE 					float32 		`json:"item_price"`
	ITEM_SALES_VOLUME 	float32 		`json:"item_sales_volume"`
	ITEM_SALES_AMOUNT 	float32 		`json:"item_sales_amount"`
	ITEM_FAV_NUM 				int 				`json:"item_fav_num"`
	TOTAL_EVAL_NUM 			int 				`json:"total_eval_num"`
	ITEM_STOCK 					int 				`json:"item_stock"`
	USER_ID							string			`json:"user_id"`
}

// 存储每个店铺的信息
type ShopInformation struct {
	DATA_MONTH 					int 			 	 `json:"data_month"`
	SHOP_NAME 					string 			 `json:"shop_name"`
	SHOP_SALES_VOLUME 	int 				 `json:"shop_sales_volume"`
	SHOP_SALES_AMOUNT 	string 			 `json:"shop_sales_amount"`
	MAIN_BUSINESS 			string 			 `json:"main_business"`
	ITEMDESC_SCORE 			float32 		 `json:"itemdesc_score"`
	SERVICE_SCORE 			float32 		 `json:"service_score"`
	DELIVERY_SCORE 			float32 		 `json:"delivery_score"`
}

// 用于返回给前端的上坪的数据类型
type SendProductsType struct {
	ITEM_PRICE 					float32 		`json:"item_price"`
	ITEM_SALES_VOLUME 	float32 		`json:"item_sales_volume"`
	ITEM_FAV_NUM 				int 				`json:"item_fav_num"`
	TOTAL_EVAL_NUM 			int 				`json:"total_eval_num"`
	ITEM_STOCK 					int 				`json:"item_stock"`
	ITEM_NAME 					string 			`json:"item_name"`
	ITEM_ID 						string 			`json:"item_id"`
	USER_ID							string			`json:"user_id"`
	// CATE_NAME_LV1				string			`json:"cate_name_lv1"`
	// CATE_NAME_LV2       string			`json:"cate_name_lv2"`
	// CATE_NAME_LV3       string			`json:"cate_name_lv3"`
}

// 用于接收得到的聚类参数
type ClusterDataType struct {
	ProductionData    		SendProductsData  	`json:"productionData"`
	ClusterMethodName 		string 			 				`json:"methodName"`
	ClusterNumber 				string 			 				`json:"clusterNumber"`
}

// 前端携带的运行模型的数据类型
type RunModelDataType struct {
	ITEM_PRICE 					float32 		`json:"item_price"`
	ITEM_SALES_VOLUME 	float32 		`json:"item_sales_volume"`
	ITEM_ID 						string 			`json:"item_id"`
}

type RunModelTokenJsonType struct {
	Data     						[]RunModelDataType  `json:"data"`
	SelectedDataMonth		string  						`json:"selectedDataMonth"`
	SelectedMethodName	string  						`json:"selectedDataName"`
}

type KindInformationGroups []KindInformation
type ProductGroups []ProductInformation
type SendProductsData []SendProductsType

// 用于泛华通道中查询到数据的类型
type ChannelDataType interface {
	Len() int
	saveJson(filename string)
	show()
	getLineChartData(filterAble bool,aimColId int,aimVal string)(aimData SendProductsData, maxInfo [][]interface{})
}

// 用于多线程查询到的数据的类型
type channelInformation struct {
	ChannelName 			string
	data 							ChannelDataType
	
}
// 逐行展示信息
func (k KindInformationGroups) show() {
	for _, v := range k {
		fmt.Printf("%+v\n", v)
	}
}

// 返回节点数据格式
type NodesType struct {
	X 							float64 			`json:"x"`
	Y 							float64				`json:"y"`
	ClassId 				int  					`json:"classId"`
	Id 							string				`json:"id"`
}

// 聚类后保存的数据格式
type ClusteredSaveDataType struct {
	X 							float64 			`json:"x"`
	Y 							float64				`json:"y"`
	ClassId 				int  					`json:"classId"`
	Id 							string				`json:"id"`
	ItemPrice 			float64 			`json:"item_price"`
	ItemSaleVolume 	float64 			`json:"item_sales_volume"`
}

// python运行t-sne后保存的json数据的格式
type vecIdData struct {
	VecData NodesGroups 	`json:"vecData"`
	GId			[]string			`json:"gId"`
}


func (k ProductGroups) show() {
	for _, v := range k {
		fmt.Printf("%+v\n", v)
	}
}

// 前面使用了interface 为了获取对应的数据长度所以添加了一个获取长度的方法
func (a KindInformationGroups) Len() int {return len(a)}
func (a ProductGroups) Len() int {return len(a)}

// 将数据进行保存
func (data KindInformationGroups) saveJson(filename string) {
	f, err := os.Create(FileRoot + filename + FileType)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer f.Close()
	jsonData, err := json.Marshal(data)
	if err != nil {
		fmt.Println(err)
	}
	f.Write(jsonData)
}

// 存储查询到的商品的一些信息
func (data ProductGroups) saveJson(filename string) {
	f, err := os.Create(FileRoot + filename + FileType)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer f.Close()
	jsonData, err := json.Marshal(data)
	if err != nil {
		fmt.Println(err)
	}
	f.Write(jsonData)
}

func (data KindInformationGroups) getLineChartData(filterAble bool,aimColId int,aimVal string)(aimData SendProductsData, maxInfo [][]interface{}) {
	return aimData,maxInfo
}

//  filterAble = False 的话就是不过滤的
func (data ProductGroups) getLineChartData (filterAble bool,aimColId int,aimVal string)(aimData SendProductsData, maxInfo [][]interface{}) {
	var priceMax float32 = 0.0
	var itemSaleValueMax float32 = 0.0
	var itemSaleAmountMax float32 = 0.0
	itemFavNumMax := 0
	totalEvalNumMax := 0
	totalEvalNumMaxitemStockMax := 0
	
	for _,v := range data {
		objV := reflect.ValueOf(v).Field(aimColId).Interface()
		if filterAble && aimVal != objV {
			// fmt.Println("过滤掉了")
			continue
		}
		// fmt.Println(objV)
		if priceMax<v.ITEM_PRICE {
			priceMax = v.ITEM_PRICE
		}
		if itemSaleValueMax<v.ITEM_SALES_VOLUME {
			itemSaleValueMax = v.ITEM_SALES_VOLUME
		}
		if itemSaleAmountMax<v.ITEM_SALES_AMOUNT {
			itemSaleAmountMax = v.ITEM_SALES_AMOUNT
		}
		if itemFavNumMax<v.ITEM_FAV_NUM {
			itemFavNumMax = v.ITEM_FAV_NUM
		}
		if totalEvalNumMax<v.TOTAL_EVAL_NUM {
			totalEvalNumMax = v.TOTAL_EVAL_NUM
		}
		if totalEvalNumMaxitemStockMax<v.ITEM_STOCK {
			totalEvalNumMaxitemStockMax = v.ITEM_STOCK
		}
		item := SendProductsType{v.ITEM_PRICE ,v.ITEM_SALES_VOLUME, v.ITEM_FAV_NUM, v.TOTAL_EVAL_NUM, v.ITEM_STOCK,v.ITEM_NAME,v.ITEM_ID, v.USER_ID,}
		aimData = append(aimData, item)
	}
	return aimData, [][]interface{}{{0,priceMax}, {0,itemSaleValueMax}, {0,itemFavNumMax}, {0,totalEvalNumMax}, {0,totalEvalNumMaxitemStockMax}}
}

type NodeType []float64
type NodesGroups []NodeType
type ClusteredDataType map[int]NodesGroups

// 计算向量的维度
func (n NodeType) Len() int { return len(n) }
func (n NodesGroups) Len() int { return len(n) }

// 计算欧式距离
func (a NodeType) dist(b NodeType)(dis float64) {
	if a.Len() != b.Len() {
		fmt.Println("两向量维度不同")
		return -1
	}
	dis = 0.0
	for i := 0; i < a.Len(); i++ {
		c := a[i] - b[i]
		dis += c * c
	}
	
	return math.Sqrt(dis)
}

// 存储查询到的商品的一些信息
func (data ClusteredDataType) saveJson(filename string) {
	f, err := os.Create("./RedutionRes/" + filename + FileType)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer f.Close()
	jsonData, err := json.Marshal(data)
	if err != nil {
		fmt.Println(err)
	}
	f.Write(jsonData)
}

// 将发送的数据进行保存
func (data SendProductsData) saveJson(filename string) {
	f, err := os.Create("./RedutionRes/" + filename + FileType)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer f.Close()
	jsonData, err := json.Marshal(data)
	if err != nil {
		fmt.Println(err)
	}
	f.Write(jsonData)
}