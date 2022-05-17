package main

import (
	"fmt"
)

/*
	主程序的入口文件
*/

// 查询数据
func test() {
	go queryData(db, "data_202106_1", ch)
	go queryData(db, "data_202106_2", ch)

	for i := range ch {
		channelNum--
		i.data.saveJson(i.ChannelName)
		fmt.Println(i.ChannelName,"--kindNum: ", i.data.Len())

		if channelNum == 0 {
			close(ch)
		}
	}
}

func GetData() {
	AllColName := []string{"运动户外", "家用电器", "数字阅读", "手机数码", "其他",
												"家居建材", "其他商品", "文化玩乐", "服装鞋包", "母婴用品", "汽配摩托", "游戏话费", "生活服务", "百货食品", "盒马", "美妆饰品",""}
	defer fmt.Println("main end")
	// test()
	// go queryOneschema(db, "data_202109_4", "CATE_NAME_LV1","家用电器")
	for _, v := range AllColName {
		queryDatamutiChan(db, "9", "CATE_NAME_LV1",v)
		fmt.Println(v)
		// i := <-ch
		// i.data.saveJson(i.ChannelName)
	}
	// for i := range ch {
	// 	channelNum--
	// 	i.data.saveJson(i.ChannelName)
	// 	fmt.Println(i.data.Len())
	// 	if channelNum==0 {
	// 		close(ch)
	// 		break
	// 	}
	// }

}

func GetSelectedData(aimColName string, v string)(aimD []SendProductsType, maxInfo [][]interface{}) {
	go queryDatamutiChan(db, "6", aimColName,v)
	i := <-ch
	return i.data.getLineChartData(false,0,"")
}

func main() {
	// GetSelectedData("CATE_NAME_LV1", "家用电器")
	// GetData()
	// queryShopInformation("USER_ID","1000280746")
	ServerUnion()
}