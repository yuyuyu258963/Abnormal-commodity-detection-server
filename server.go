package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

/*
	用于服务器的操作
*/

var FilterDataCh = make(chan []byte)

// 开启默认的页面
func geDefaltPage(c *gin.Context) {
	c.HTML(http.StatusOK, "index.html", nil)
}


// 中间件解决跨域问题
func Cors() gin.HandlerFunc {
	return func(c *gin.Context) {
			method := c.Request.Method
							origin := c.Request.Header.Get("Origin")

			if origin != "" {
					c.Header("Access-Control-Allow-Origin", "*")  // 可将将 * 替换为指定的域名
					c.Header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE, UPDATE")
					c.Header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization")
					c.Header("Access-Control-Expose-Headers", "Content-Length, Access-Control-Allow-Origin, Access-Control-Allow-Headers, Cache-Control, Content-Language, Content-Type")
					c.Header("Access-Control-Allow-Credentials", "true")
			}
			if method == "OPTIONS" {
					c.AbortWithStatus(http.StatusNoContent)
			}
			c.Next()
	}
}

// 用于请求数据的
func GetKindData(c *gin.Context) {
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Methods","POST,GET,OPTIONS")
	
	jsonParams := make(map[string]string)
	c.BindJSON(&jsonParams)
	selectedMonth := jsonParams["selectedMonth"]
	selected := jsonParams["selected"]
	sendfielNam := jsonParams["fileName"]
	selectedPathId := jsonParams["selectedPathId"]
	NumSelectedPathId,_ := strconv.Atoi(selectedPathId)
	// aimColName := "cate_name_lv" + selectedPathId
	fileName := selectedMonth + "-CATE_NAME_LV1-" + sendfielNam
	filterAble :=  NumSelectedPathId > 1
	// fmt.Println(aimColName, selected)
	// dat,maxInfo := GetSelectedData(aimColName ,selected)
	fmt.Println(NumSelectedPathId)
	dat,maxInfo := readJson(fileName,filterAble,NumSelectedPathId,selected)

	errDataLine := runBoxCheck(fileName)
	// classedData, MaxMinData := runDBSCAN(dat)

	fmt.Printf("data:%v\n", jsonParams)
	c.JSON(200, gin.H{
		"status":  				"posted",
		"LineChartData": 	dat,
		"DataLen":				len(dat),
		"maxInfo": 				maxInfo,
		"errDataLine":		errDataLine,
		// "classedData": 		classedData,
		// "MaxMinData" : 		MaxMinData,
	})
}

// 保存异常数据
func SaveData(c *gin.Context) {
	jsonParams := make(map[string]interface{})
	c.BindJSON(&jsonParams)
	filterData := jsonParams["filterData"]
	// jsonData, err := json.Marshal(filterData)
	jsonData, err := json.MarshalIndent(filterData, "", "\t")
	
	fmt.Println("成功保存文件")
	FilterDataCh <- jsonData
	if err != nil {
		fmt.Println(err)
	}
	// SaveFilterJsonData("test",filterData)

	c.JSON(200, gin.H {
		"status":"ok",
	})
}

// 实现文件下载
func Upload(c *gin.Context) {
	fmt.Println("请求保存文件")
	byteValue := <- FilterDataCh
	month := c.Query("month")
	attr 	:= c.Query("attr")

	c.Writer.WriteHeader(http.StatusOK)
	c.Header("Content-Type", "*")
  c.Header("Content-Disposition", "attachment; filename="+ "20210" + month +"-" + attr +"-异常数据.json")
	c.Header("Accept-Length", fmt.Sprintf("%d", len(byteValue)))
	c.Writer.Write(byteValue)
}

// 用于请求一个商店的信息
func GetShopData(c *gin.Context) {
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Methods","POST,GET,OPTIONS")
	
	jsonParams := make(map[string]string)
	c.BindJSON(&jsonParams)
	userId := jsonParams["userId"]
	shopData := queryShopInformation("USER_ID",userId)
	// matrix := readMatrix(userId)

	fmt.Printf("data:%v\n", jsonParams)
	c.JSON(200, gin.H{
		"status":  "posted",
		"shopData": shopData,
		// "matrix":		matrix,
	})
}

// 用于请求商品对应商店的数据
func GetProductsInShop(c *gin.Context) {
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Methods","POST,GET,OPTIONS")
	
	jsonParams := make(map[string]string)
	c.BindJSON(&jsonParams)
	userId := jsonParams["userId"]
	go queryDatamutiChan(db,"7","USER_ID",userId)
	chData := <- ch
	// chData.data
	dat,maxInfo := chData.data.getLineChartData(false,1,"-1")
	
	// classedData, MaxMinData := runDBSCAN(dat)

	fmt.Printf("data:%v\n", jsonParams)
	c.JSON(200, gin.H{
		"status":  				"posted",
		"LineChartData": 	dat,
		"DataLen":				len(dat),
		"maxInfo": 				maxInfo,
		// "classedData" : 	classedData,
		// "MaxMinData" : 		MaxMinData,
	})
}

// 运行进行聚类
func Cluster(c *gin.Context) {
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Methods","POST,GET,OPTIONS")

	var jsonParams ClusterDataType
	c.BindJSON(&jsonParams)
	dat 					:= jsonParams.ProductionData
	clusterMethod := jsonParams.ClusterMethodName
	clusterNumber := jsonParams.ClusterNumber

	aimData := runClusterUnion(dat, clusterMethod, clusterNumber)

	c.JSON(200, gin.H{
		"status":  						"200",
		"classedData" : 			 aimData,
	})
}

// 运行模型的接口
func RunModel(c *gin.Context) {
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Methods","POST,GET,OPTIONS")
	
	var jsonParams RunModelTokenJsonType
	c.BindJSON(&jsonParams)
	data := jsonParams.Data
	// fmt.Println(data)
	SelectedDataMonth := jsonParams.SelectedDataMonth
	SelectedMethodName := jsonParams.SelectedMethodName
	fmt.Println(SelectedMethodName)
	checkedPriceErr,checkedSaleErr := runPythonModel(SelectedDataMonth, SelectedMethodName, data)
	c.JSON(200, gin.H{
		"status":  						"200",
		"priceErr": 				 checkedPriceErr,
		"saleErr":					 checkedSaleErr,
	})
}


// 获取数字矩阵的信息
func GetMaticData(c *gin.Context) { 
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Methods","POST,GET,OPTIONS")
	userid := c.Query("userid")
	priceMatrix, saleVolunmMatrix,matrixId := readMatrix(userid)
	c.JSON(200, gin.H{
		"status":  											"posted",
		"priceMatrix" : 								priceMatrix,
		"saleVolunmMatrix" : 						saleVolunmMatrix,
		"matrixId" : 										matrixId,
	})
}

// 用于开启服务器
func ServerUnion() {
	r := gin.Default()
	r.Use(Cors())
	// r.LoadHTMLFiles("./static/index.html")
	// r.StaticFile("/umi.js","./static/umi.js")
	// r.StaticFile("/umi.css","./static/umi.css")
	r.POST("/getData", GetKindData)
	r.POST("/GetProductsInShop",GetProductsInShop)
	r.POST("/getShopData",GetShopData)
	r.POST("/saveData", SaveData)
	r.POST("/cluster", Cluster)
	r.POST("/runModel", RunModel)
	r.GET("/upload", Upload)
	r.GET("/getmatrixdata", GetMaticData)

	r.GET("/", geDefaltPage)
	r.Run(":250")
}
