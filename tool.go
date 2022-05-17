package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
)
var GetModelDataCh = make(chan struct{})

// 用于读取包含衍生数据的结果
func getAttrData(fileName string,preStr string,dataSaveObj *map[string][]string) {
	// Id2AttrData := make(map[string][]string)
	file, err := os.Open(AttrDataFileRoot + preStr + fileName + ".tsv")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	reader := csv.NewReader(file)
	reader.Comma = '\t'
	for {
		row, err := reader.Read()
		if err != nil && err != io.EOF {
				log.Fatalf("can not read, err is %+v", err)
		}
		if err == io.EOF {
				break
		}
		(*dataSaveObj)[row[0] + row[1]] = row
	}
	GetModelDataCh <- struct{}{}
	// return Id2AttrData
}

// 运行去保存模型所需要用到的数据
func runSaveModelUsedData(Month string, Name string, data []RunModelDataType) {
	Id2AttrDataPrice := make(map[string][]string)
	Id2AttrDataSale  := make(map[string][]string)
	go getAttrData(Name, "/", &Id2AttrDataPrice)
	go getAttrData(Name, "_sale/销量_", &Id2AttrDataSale)
	aimDataPrice := make([][]string, len(data) + 1)
	aimDataSale := make([][]string, len(data) + 1)
	aimDataPrice[0] = []string{"DATA_MONTH","ITEM_ID",	"ITEM_PRICE",	"CATE_NAME_LV1",	"CATE_NAME_LV2",	"CATE_NAME_LV3",	"same-CATE_NAME_LV1-mean-ITEM_PRICE-rate",	
					"same-CATE_NAME_LV2-mean-ITEM_PRICE-rate", "same-CATE_NAME_LV3-mean-ITEM_PRICE-rate",	"same-ITEM_ID-mean-ITEM_PRICE-rate",	"USER_ID",	"same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_PRICE-rate-rate", "same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_PRICE-rate",	
					"same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_PRICE-rate",	"same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_PRICE-rate"}
	aimDataSale[0] = []string {
		"DATA_MONTH",	"ITEM_ID",	"ITEM_SALES_VOLUME",	"CATE_NAME_LV1",	"CATE_NAME_LV2",	"CATE_NAME_LV3",	"USER_ID",	
		"same-CATE_NAME_LV1-mean-ITEM_SALES_VOLUME-rate",	"same-CATE_NAME_LV2-mean-ITEM_SALES_VOLUME-rate",	
		"same-CATE_NAME_LV3-DATA_MONTH-mean-same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate-rate",	
		"same-CATE_NAME_LV3-mean-ITEM_SALES_VOLUME-rate",	
		"same-ITEM_ID-mean-ITEM_SALES_VOLUME-rate",	"same-CATE_NAME_LV1-BRAND_ID-mean-ITEM_SALES_VOLUME-rate",	
		"same-CATE_NAME_LV2-BRAND_ID-mean-ITEM_SALES_VOLUME-rate","same-CATE_NAME_LV3-BRAND_ID-mean-ITEM_SALES_VOLUME-rate",
	}

	<- GetModelDataCh
	<- GetModelDataCh
	for i, v := range data {
		aimDataPrice[i + 1] = Id2AttrDataPrice["20210" + Month + v.ITEM_ID]
		aimDataSale[i + 1] 	= Id2AttrDataSale["20210" + Month + v.ITEM_ID]
	}
	saveTsv(SaveModelUsedDataRoot + "sendUseModelPriceData.tsv", aimDataPrice)
	saveTsv(SaveModelUsedDataRoot + "sendUseModelSaleData.tsv", aimDataSale)
}

// 运行python脚本
func runPythonModel(Month string, Name string, data []RunModelDataType) (interface{}, interface{}) {
	runSaveModelUsedData(Month, Name, data)
	runRootPath, _ := os.Getwd()
	cmd := exec.Command(`python`,runRootPath + `/Python/main.py`, "main")
	str, err := cmd.CombinedOutput()
	fmt.Println(string(str))
	if err != nil {
		log.Fatalf("cmd.Run() failed with %s\n", err)
	}

	return ReadResData()
}

// 用于读取保存的错误的数据
func ReadResData() (interface{}, interface{}) {
	var readResCh = make(chan struct{})
	fileNames := []string{"sumPrice_error_jiaoData.json", 
												"sumSale_error_jiaoData.json"}
	
	// checkedPriceErr := make([]string, 0)
	// checkedSaleErr 	:= make([]string, 0)

	var checkedPriceErr interface{}
	var checkedSaleErr interface{}

	readResCsvFun := func(filename string, saveObj *interface{}) {
		// file, err := os.Open("./RedutionRes/" + filename)
		// if err != nil {
		// 	log.Fatal(err)
		// }
		// defer file.Close()
		// reader := csv.NewReader(file)
		// reader.Comma = '\t'
		// counter := 0
		// for {
		// 	row, err := reader.Read()
		// 	if counter == 0 {
		// 		counter ++;
		// 		continue
		// 	}
		// 	if err != nil && err != io.EOF {
		// 			log.Fatalf("can not read, err is %+v", err)
		// 	}
		// 	if err == io.EOF {
		// 			break
		// 	}
		// 	*saveObj = append(*saveObj, row[1])
		// }

		data, err := ioutil.ReadFile("./RedutionRes/" + filename)
		if err != nil {
			fmt.Println(err)
		}
		json.Unmarshal(data, saveObj)
		
		readResCh <- struct{}{}
	}
	go readResCsvFun(fileNames[0], &checkedPriceErr)
	go readResCsvFun(fileNames[1], &checkedSaleErr)
	<-readResCh
	<-readResCh
	return checkedPriceErr, checkedSaleErr
}



// func main() {
// 	// getAttrData("盒马")
// 	saveTsv(SaveModelUsedDataRoot + "test.tsv",[][]string{})
// }