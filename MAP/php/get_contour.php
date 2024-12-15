<?php

//輸入：地圖描述文件
//輸出：contour_geojson

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');

// 請替換成後端的地圖描述文件的get位置
$jsonFile = './mapdiscript.json';

// 通過 GET 方法請求遠端 JSON 資料
/*
$jsonFile = file_get_contents($remoteUrl);

*/

//....


// 讀取文件 可以直接沿用
if (file_exists($jsonFile)) {
    $jsonContent = file_get_contents($jsonFile);
    $data = json_decode($jsonContent, true);

    // 確認是否有 contour_geojson
    if (!empty($data['contour_layer']['contour_geojson'])) {
        // 輸出 GeoJSON
        echo $data['contour_layer']['contour_geojson'];
    } else {
        echo json_encode(["error" => "未找到 contour_geojson 資料"]);
    }
} else {
    echo json_encode(["error" => "JSON 文件不存在"]);
}
?>

