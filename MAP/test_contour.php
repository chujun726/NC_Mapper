<?php

//輸入：地圖描述文件
//輸出：contour_geojson

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// 替換為 JSON 檔案
$jsonFile = './map_description/WithoutArray_WithGeojson.json';

// 讀取文件
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

