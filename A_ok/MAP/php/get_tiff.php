<?php

//輸入：地圖描述文件
//輸出：contour_geojson

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');

// 請替換成後端的地圖描述文件的get位置
$jsonFile = './mapdiscript.json';


// 讀取所需資料

// 不在地圖描述文件中，需要詢問
$file_path = "./layer/2m_temperature.tif";



// 構建 TIFF 資料
$tiffData = [
    "tiff_name" => $file_path, // 規定的路徑
    "crs" => "EPSG:3857",                      // 固定的投影座標系統
    "min" => 222,                                // 假設的最小值，根據測試數據設置
    "max" => 311                              // 假設的最大值，根據測試數據設置
];

// 回傳 JSON 資料
echo json_encode($tiffData, JSON_PRETTY_PRINT);