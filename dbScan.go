package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
)


const (
	NOISE        int = 0
	UNCLASSIFIED int = -1
)

// 判断两个点是否在范围内
func epsNeigh(a NodeType, b NodeType, eps float64) bool {
	return a.dist(b) < eps
}

// 以一个点为初始点寻找周围满足条件的点
func regionQuery(allNodes NodesGroups, rootNode NodeType, eps float64) (seeds []int) {
	for index, node := range allNodes {
		if node.dist(rootNode) < eps {
			seeds = append(seeds, index)
		}
	}
	return seeds
}

// 扩散进行分类
func expandCluster(allNodes NodesGroups, clusterResult []int, pointId int, clusterId int, eps float64, minPts int) bool {

	seeds := regionQuery(allNodes, allNodes[pointId], eps)
	if len(seeds) < minPts {
		clusterResult[pointId] = NOISE
		return false
	} else {
		clusterResult[pointId] = clusterId
		for _, nodeId := range seeds {
			clusterResult[nodeId] = clusterId
		}
	}

	for {
		if len(seeds) <= 0 {
			break
		}
		rootNodeId := seeds[0]
		queryResults := regionQuery(allNodes, allNodes[rootNodeId], eps)
		if len(queryResults) >= minPts {
			for _, nodeId := range queryResults {
				if clusterResult[nodeId] == UNCLASSIFIED {
					seeds = append(seeds, nodeId)
					clusterResult[nodeId] = clusterId
				} else if clusterResult[nodeId] == NOISE {
					clusterResult[nodeId] = clusterId
				}
			}
		}
		seeds = seeds[1:]
	}
	return true
}

// DBscan 入口
func dbScan(data NodesGroups, eps float64, minPts int) []int {
	var RagionClusterId int = 1
	nodesNum := data.Len()
	var clusterResult []int
	for i := 0; i < nodesNum; i++ {
		clusterResult = append(clusterResult, UNCLASSIFIED)
	}

	for i := 0; i < nodesNum; i++ {
		if clusterResult[i] == UNCLASSIFIED {
			res := expandCluster(data, clusterResult, i, RagionClusterId, eps, minPts)
			if res {
				RagionClusterId += 1
			}
		}
	}
	// fmt.Printf("res : %d \n", RagionClusterId-1)
	// fmt.Printf("res : %+v %d \n",clusterResult,RagionClusterId-1)
	return clusterResult
}

// 出发python进行降维
func checkExe2(loadFileName string, saveFilename string) {
	runRootPath, _ := os.Getwd()
	// 服务器上的反斜杠反过来
	cmd := exec.Command(`python`,runRootPath + `/Python/tsne.py`, "main", loadFileName, saveFilename)
	str, err := cmd.CombinedOutput()
	fmt.Println(string(str))
	if err != nil {
		log.Fatalf("cmd.Run() failed with %s\n", err)
	}
}

// 执行DBSCAN算法
func Dbscan(fileName string)([]NodesType, []float64, map[int][]string) {
	x_min, x_max, y_min, y_max := 1000.0, -1000.0, 1000.0, -1000.0
	dat,gId := Get2vecData(fileName)

	resCluster := dbScan(dat, 5.0, 5)
	fmt.Println(len(resCluster))
	var nodesData []NodesType
	var classNumCounter =  make(map[int][]string)
	
	for index,classId := range resCluster {
		nodesData = append(nodesData,NodesType{dat[index][0],dat[index][1],classId,gId[index]})
		if x_min > dat[index][0] {
			x_min = dat[index][0]
		}
		if x_max < dat[index][0] {
			x_max = dat[index][0]
		}
		if y_min > dat[index][1] {
			y_min = dat[index][1]
		}
		if y_max < dat[index][1] {
			y_max = dat[index][1]
		}

		// 进行每个类的统计
		val, ok := classNumCounter[classId]
		if ok {
			classNumCounter[classId] = append(val, gId[index])
		} else {
			classNumCounter[classId] = []string{gId[index]}
		}
	}

	return nodesData,[]float64{x_min, x_max, y_min, y_max},classNumCounter
}

// 先出发python的tsne算法再进行dbscan
func runDBSCAN(dat SendProductsData) (classedData []NodesType, a []float64, classNumCounter map[int][]string) {
	dat.saveJson("preData")
	checkExe2("preData", "res")
	classedData, a, classNumCounter = Dbscan("res")
	return classedData, a, classNumCounter
}

// 用于运行聚类算法
func runClusterUnion(dat SendProductsData, methodName string, clusterNumber string) []ClusteredSaveDataType {
	dat.saveJson("preData")
	runRootPath, _ := os.Getwd()
	// 服务器上的反斜杠反过来
	cmd := exec.Command(`python`,runRootPath + `/Python/Cluster.py`, "main", methodName, clusterNumber)
	str, err := cmd.CombinedOutput()
	fmt.Println(string(str))
	if err != nil {
		log.Fatalf("cmd.Run() failed with %s\n", err)
	}

	jsonFile, err := os.Open("./RedutionRes/clusterRes.json")
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)
	var aim_data []ClusteredSaveDataType
	json.Unmarshal(byteValue, &aim_data)
	return aim_data
}
