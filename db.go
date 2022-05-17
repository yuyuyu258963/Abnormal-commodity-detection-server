package main

import (
	"database/sql"
	"fmt"
	"strconv"

	_ "github.com/go-sql-driver/mysql"
)

/*
	用于数据库的操作
*/

var db *sql.DB

func init() {
	db = linkMysql()
}

func linkMysql() (db *sql.DB) {
	dsn := "root:ywh@tcp(121.41.27.5:3306)/" + sqlName + "?charset=utf8"
	var err error
	//连接数据集
	db, err = sql.Open("mysql", dsn) //open不会检验用户名和密码
	if err != nil {
		fmt.Printf("dsn:%s invalid,err:%v\n", dsn, err)
	}
	db.SetConnMaxIdleTime(100)
	db.SetConnMaxLifetime(500)
	db.SetMaxOpenConns(100)
	return db
}

func getUnionSchema(y string) (S string) {
	S = "(select * from data_20210" + y + "_1 union all select * from data_20210" + y + "_2 union all select * from data_20210" + y + "_3 union all select * from data_20210" + y + "_4)"
	return S
}

// 获取表中一个数据的个数
func queryData(d *sql.DB, schemaName string, ch chan channelInformation) {
	var data KindInformationGroups
	var rows *sql.Rows
	var err error
	if len(schemaName) != 1 {
		rows, err = d.Query("select count(*) as num,CATE_NAME_LV1 from " + schemaName + " group by CATE_NAME_LV1")
	} else {
		s := getUnionSchema(schemaName)
		// fmt.Println(s)
		rows, err = d.Query("select count(*) as num,d.CATE_NAME_LV1 from " + s + "as d group by d.CATE_NAME_LV1")
	}

	if err != nil {
		fmt.Println("error ", err)
	}
	for rows.Next() {
		var Count int
		var Name string
		err = rows.Scan(&Count, &Name)
		if err != nil {
			fmt.Println(err)
		}
		data = append(data, KindInformation{Count, Name})
	}
	ch <- channelInformation{schemaName, data}
}

// 从列中获取Rows中获取数据
func ReadAllData(rows *sql.Rows) (data ProductGroups) {
	for rows.Next() {
		var (
			ITEM_ID           string
			ITEM_NAME         string
			CATE_NAME_LV2     string
			CATE_NAME_LV3     string
			CATE_NAME_LV4     string
			CATE_NAME_LV5     string
			ITEM_PRICE        float32
			ITEM_SALES_VOLUME float32
			ITEM_SALES_AMOUNT float32
			ITEM_FAV_NUM      int
			TOTAL_EVAL_NUM    int
			ITEM_STOCK        int
			USER_ID           string
		)

		err := rows.Scan(
			&ITEM_ID, &ITEM_NAME,
			&CATE_NAME_LV2, &CATE_NAME_LV3,
			&CATE_NAME_LV4, &CATE_NAME_LV5,
			&ITEM_PRICE, &ITEM_SALES_VOLUME,
			&ITEM_SALES_AMOUNT, &ITEM_FAV_NUM,
			&TOTAL_EVAL_NUM, &ITEM_STOCK,
			&USER_ID,
		)
		// fmt.Println(ITEM_ID)
		if err != nil {
			fmt.Println(err)
			continue
		}
		data = append(data, ProductInformation{ITEM_ID, ITEM_NAME,
			CATE_NAME_LV2, CATE_NAME_LV3,
			CATE_NAME_LV4, CATE_NAME_LV5,
			ITEM_PRICE, ITEM_SALES_VOLUME,
			ITEM_SALES_AMOUNT, ITEM_FAV_NUM,
			TOTAL_EVAL_NUM, ITEM_STOCK,
			USER_ID,
		})
	}
	return data
}

// 查找一个表中的数据限定一个一列的属性
func queryOneschema(d *sql.DB, schemaName string, aimColName string, aimColValue string) {
	var data ProductGroups
	var rows *sql.Rows
	var err error
	rows, err = d.Query("select ITEM_ID,ITEM_NAME,ITEM_PRICE,ITEM_SALES_VOLUME,ITEM_SALES_AMOUNT,ITEM_FAV_NUM,TOTAL_EVAL_NUM,ITEM_STOCK,USER_ID from " + schemaName + " where " + aimColName + " = '" + aimColValue + "'")

	if err != nil {
		fmt.Println("error ", err)
	}
	fmt.Println("开始查找")
	data = ReadAllData(rows)
	fmt.Println("退出")
	ch <- channelInformation{schemaName + "-" + aimColName + "-" + aimColValue, data}
}

// 用多线程的方式同时读取一年对应的所有数据
func queryDatamutiChan(d *sql.DB, year string, aimColName string, aimColValue string) {
	var data ProductGroups
	mCh := make(chan []ProductInformation)
	mChNum := 4
	var schemaNames []string
	for i := 1; i < 5; i++ {
		schemaNames = append(schemaNames, "data_20210"+year+"_"+strconv.Itoa(i))
	}
	for chId, schemaName := range schemaNames {
		sc := schemaName
		fmt.Println("开启ch：：", chId)
		go func() {
			// rows, err := d.Query("select ITEM_ID,ITEM_NAME,ITEM_PRICE,ITEM_SALES_VOLUME,ITEM_SALES_AMOUNT,ITEM_FAV_NUM,TOTAL_EVAL_NUM,ITEM_STOCK from "+sc+" where "+aimColName+" = '"+aimColValue+"'")
			rows, err := d.Query("select ITEM_ID,ITEM_NAME,CATE_NAME_LV2,CATE_NAME_LV3,CATE_NAME_LV4,CATE_NAME_LV5,ITEM_PRICE,ITEM_SALES_VOLUME,ITEM_SALES_AMOUNT,ITEM_FAV_NUM,TOTAL_EVAL_NUM,ITEM_STOCK,USER_ID from " + sc + " where " + aimColName + " = '" + aimColValue + "'")
			if err != nil {
				fmt.Println("err::", err)
			}
			elemData := ReadAllData(rows)
			mCh <- elemData
		}()
	}
	for c := range mCh {
		data = append(data, c...)
		mChNum--
		if mChNum == 0 {
			close(mCh)
			break
		}
	}
	// fmt.Println("线程退出")
	i := channelInformation{year + "-" + aimColName + "-" + aimColValue, data}
	i.data.saveJson(i.ChannelName)
	// return
	// ch <- channelInformation{year+"-"+aimColName+"-"+aimColValue,data}
}

// 根据信息查找出shop中的店铺信息
func queryShopInformation(aimColName string, aimColValue string) (data []ShopInformation) {
	rows, err := db.Query("select DATA_MONTH,SHOP_NAME,SHOP_SALES_VOLUME,SHOP_SALES_AMOUNT,MAIN_BUSINESS,ITEMDESC_SCORE,SERVICE_SCORE,DELIVERY_SCORE from shop where " + aimColName + " = '" + aimColValue + "'")
	if err != nil {
		fmt.Println("err::", err)
	}
	for rows.Next() {
		var (
			DATA_MONTH        int
			SHOP_NAME         string
			SHOP_SALES_VOLUME int
			SHOP_SALES_AMOUNT string
			MAIN_BUSINESS     string
			ITEMDESC_SCORE    float32
			SERVICE_SCORE     float32
			DELIVERY_SCORE    float32
		)

		err := rows.Scan(
			&DATA_MONTH,
			&SHOP_NAME,
			&SHOP_SALES_VOLUME,
			&SHOP_SALES_AMOUNT,
			&MAIN_BUSINESS,
			&ITEMDESC_SCORE,
			&SERVICE_SCORE,
			&DELIVERY_SCORE,
		)
		if err != nil {
			fmt.Println(err)
			continue
		}
		data = append(data, ShopInformation{
			DATA_MONTH,
			SHOP_NAME,
			SHOP_SALES_VOLUME,
			SHOP_SALES_AMOUNT,
			MAIN_BUSINESS,
			ITEMDESC_SCORE,
			SERVICE_SCORE,
			DELIVERY_SCORE,
		})
	}
	fmt.Println(data)
	return data
}
