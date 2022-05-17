package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"math"
	"os"
	"strconv"
)

var matrixData map[string][][]float64
var matrixSaleVolunmData map[string][][]float64
var elemInformation map[string][]string

func init() {
	readDataCh := make(chan int)
	// 用于读取价格矩阵数据
	go func() {
		jsonFile1, err := os.Open("./TransedData/res_price_data.json")
		if err != nil {
			fmt.Println(err)
		}
		defer jsonFile1.Close()
		byteValue, _ := ioutil.ReadAll(jsonFile1)
		err = json.Unmarshal([]byte(byteValue), &matrixData)
		if err != nil {
			fmt.Println(err)
		}
		readDataCh <- 1
	}()
	
	// 用于读取销量矩阵数据
	go func() {
		jsonFile1, err := os.Open("./TransedData/res_saleVolunm_data.json")
		if err != nil {
			fmt.Println(err)
		}
		defer jsonFile1.Close()
		byteValue, _ := ioutil.ReadAll(jsonFile1)
		err = json.Unmarshal([]byte(byteValue), &matrixSaleVolunmData)
		if err != nil {
			fmt.Println(err)
		}
		readDataCh <- 1
	}()

	// 用于读取数数据id
	go func() {
		jsonFile2, err := os.Open("./TransedData/res_price_data2ids.json")
		if err != nil {
			fmt.Println(err)
		}
		defer jsonFile2.Close()
		byteValue, _ := ioutil.ReadAll(jsonFile2)
		err = json.Unmarshal([]byte(byteValue), &elemInformation)
		if err != nil {
			fmt.Println(err)
		}
		readDataCh <- 1
	}()
	

	
	<-readDataCh
	<-readDataCh
}

// 读取json文件的基础方法
func basicReadJson(fileName string) ([]byte) {
	filePath := FileRoot + fileName + ".json"
	jsonFile, err := os.Open(filePath)
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)

	return byteValue
}

// 读取JSON格式的数据
func readJson(fileName string,filterAble bool,aimColId int,aimVal string) (aimData SendProductsData,maxInfo [][]interface{}) {
	var dat ProductGroups
	byteValue := basicReadJson(fileName)
	json.Unmarshal([]byte(byteValue), &dat)
	aimData,maxInfo = dat.getLineChartData(filterAble,aimColId,aimVal)
	return aimData,maxInfo
}

// 用于保存JSON格式的数据
func SaveFilterJsonData(filename string,data interface{}) {
	f, err := os.Create(FilteredDataFileRoot + filename + FileType)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer f.Close()
	// jsonData, err := json.Marshal(data)
	jsonData, err := json.MarshalIndent(data, "", "\t")
	// err = json.Indent(&jsonData,"","\t")
	
	if err != nil {
		fmt.Println(err)
	}
	f.Write(jsonData)
}

// 获取文件保存目录下的文件长度
func GetFileListLen(fileRoot string) (l string ) {
	files, _ := ioutil.ReadDir(FilteredDataFileRoot)
	le := len(files)
	l = strconv.Itoa(le)
	return l
}

// 读取保存的向量数据
func Get2vecData(filename string) (NodesGroups,[]string) {
	const vecFileRoot string = "./RedutionRes/"
	filePath := vecFileRoot + filename + ".json"
	jsonFile, err := os.Open(filePath)
	var res vecIdData
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)
	json.Unmarshal([]byte(byteValue), &res)

	// fmt.Printf("%+v",dat[0])
	return res.VecData,res.GId
}


// 读取tsv 或者 csv文件
func readCsvFile(filename string, split rune) [][]string {
	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	reader := csv.NewReader(file)
	reader.Comma = split

	data, err := reader.ReadAll()
	if err != nil {
		log.Fatal(err)
	}
	// fmt.Println(data[0])
	return data
}

// 获取所有的shopId
func getAllShopUserId(fileName string) []string {
	data := readCsvFile(fileName, '\t')
	var res []string
	var recode = make(map[string]bool,len(data) / 2)
	for _, v := range data {
		if _, ok := recode[v[1]]; !ok { 
			recode[v[1]] = true
			res = append(res, v[1])
		}
	}
	return res
}

// 读取矩阵数据 包括了数字矩阵和对应的 并且进行转化
func readMatrix(userId string) ( [][]float64, [][]float64, []string ) {
	var resPriceData [][]float64
	var resSaleVolunmData [][]float64
	resPriceData = matrixData[userId]
	resSaleVolunmData = matrixSaleVolunmData[userId]
	// 按照年份进行排序
	resPriceData = [][]float64{resPriceData[3],resPriceData[0],resPriceData[2],resPriceData[1]}
	resSaleVolunmData = [][]float64{resSaleVolunmData[3],resSaleVolunmData[0],resSaleVolunmData[2],resSaleVolunmData[1]}
	
	var maxPriceData = math.Inf(-1)
	var maxSaleVolunmData = math.Inf(-1)
	for i, v := range resPriceData {
		for j,k := range v {
			if k > maxPriceData {
				maxPriceData = k
			}
			if resSaleVolunmData[i][j] > maxSaleVolunmData {
				maxSaleVolunmData = resSaleVolunmData[i][j]
			}
		}
	}
	for i, v := range resPriceData {
		for j,k := range v {
			if k != -1 {
				resPriceData[i][j] = resPriceData[i][j] * 10 / maxPriceData
			}
			if resSaleVolunmData[i][j] != -1 {
				resSaleVolunmData[i][j] = resSaleVolunmData[i][j] * 10 / maxSaleVolunmData
			}
		}
	}
	
	return resPriceData, resSaleVolunmData, elemInformation[userId]
}


// 获得对应的一年的shop-[]string 中为店铺中所有上商品对应的数据
func getAllDataMatrix(fileName string, colIndex int)  {
	data := readCsvFile(fileName, '\t')
	userId2data := make(map[string][]float64)
	userId2dataId := make(map[string][]string)

	// 去除首行数据
	for _, v := range data[1:] {
		shopId := v[19]    //获得对应店铺的id
		itemId := v[1]    //获得对应商品的id
		dataSet,err := strconv.ParseFloat(v[colIndex], 64)
		if err != nil {
			dataSet = -1
		}
		userId2data[shopId] = append(userId2data[shopId], dataSet)
		userId2dataId[shopId] = append(userId2dataId[shopId], itemId)
	}
	// fmt.Println(userId2data)
	fmt.Println("完成 ->", fileName)
	dataTransCh <- userId2data
	dataTransChPrductsId <- userId2dataId
}

// 将多个map数据进行合并 即四个月对应的数据
func mergeData(args... map[string][]float64) map[string][][]float64 {
	shopId := getAllShopUserId("../比赛题目使用数据/shop.tsv")
	res := make(map[string][][]float64)
	for _, id := range shopId {
		for _, v := range args {
			if _, ok := v[id]; ok {
				res[id] = append(res[id], v[id])
			} else {
				res[id] = append(res[id], []float64{})
			}
		}
	}
	return res
}

// 将多个map数据进行合没有用泛型
func mergeidsData(args... map[string][]string) map[string][][]string {
	shopId := getAllShopUserId("../比赛题目使用数据/shop.tsv")
	res := make(map[string][][]string)
	for _, id := range shopId {
		for _, v := range args {
			if _, ok := v[id]; ok {
				res[id] = append(res[id], v[id])
			} else {
				res[id] = append(res[id], []string{})
			}
		}
	}
	return res
}

// 用于保存JSON格式的数据
func saveJson(filePath string,data interface{}) {
	f, err := os.Create(filePath)
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

// 用于保存tsv文件
func saveTsv(filePath string, newContent [][]string) {
	nfs, err := os.Create(filePath)
	if err != nil {
			log.Fatalf("can not create file, err is %+v", err)
	}
	defer nfs.Close()
	nfs.Seek(0, io.SeekEnd)

	w := csv.NewWriter(nfs)
	w.Comma = '\t'
	w.UseCRLF = true
	w.Flush()

	w.WriteAll(newContent)
}

// 读取保存的 JSON 文件
func ReadAllJson(filePath string,dataSaveObj *interface{}) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		fmt.Println(err)
	}
	json.Unmarshal(data, dataSaveObj)

}


