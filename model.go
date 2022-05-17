package main

var dataTransCh = make(chan map[string][]float64)
var dataTransChPrductsId = make(chan map[string][]string)

const dataSetRoot = "../比赛题目使用数据/20210"

// func main() {
// 	colIndex := 5
// 	dataSetName := []string{"6", "7", "8", "9"}
// 	dataItems := make([]map[string][]float64,0)
// 	dataPids := make([]map[string][]string,0)
// 	for _, v := range dataSetName {
// 		go getAllDataMatrix(dataSetRoot+v+".tsv", colIndex)
// 	}

// 	for range dataSetName {
// 		Items := <-dataTransCh
// 		PidGroups := <-dataTransChPrductsId
// 		// fmt.Println("完成 -> ", index)
// 		dataItems = append(dataItems, Items)
// 		dataPids = append(dataPids, PidGroups)
// 	}
// 	fmt.Println("开始 merge")
// 	resData := mergeData(dataItems...)
// 	resIds := mergeidsData(dataPids...)
// 	fmt.Println("完成 merge")
// 	saveJson("./TransedData/price_data.json", resData)
// 	saveJson("./TransedData/price_data2ids.json", resIds)
// }