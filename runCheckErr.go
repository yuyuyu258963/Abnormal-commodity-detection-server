package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
)

// 运行用于运行检查箱线图的数据
func runBoxCheck(fileName string) (dat []float64) {
	fmt.Println("runBoxCheck:", fileName)
	runRootPath, _ := os.Getwd()
	cmd := exec.Command(`python`, runRootPath+`/Python/check_error.py`, "main", fileName)
	str, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println("runBoxCheck-err ",err)
	}
	json.Unmarshal(str, &dat)

	return dat
}

// func main() {
// 	runBoxCheck("6-CATE_NAME_LV1-其他.json")
// }