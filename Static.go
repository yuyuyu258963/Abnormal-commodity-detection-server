package main

// 用于设置项目中的全局变量


const (
	FileRoot             = "./Datasets/"
	FilteredDataFileRoot = "./FilteredData/"
	AttrDataFileRoot     = "./col1_classfy_data"
	SaveModelUsedDataRoot = "./RedutionRes/"
	FileType             = ".json"
	sqlName              = "Outsourced"
)

var (
	channelNum = 17
	ch = make(chan channelInformation)
)
