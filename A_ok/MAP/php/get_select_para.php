<?php

//輸入：地圖描述文件
//輸出：contour_geojson

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');


// 讀取所需資料





// 構建 TIFF 資料
$paraData = [

    "shading_title"=> "geopotential_300",   //格式：類型_level
    "contour_title"=> "2m_temperature"  //格式：類型_level
];

echo json_encode($paraData, JSON_PRETTY_PRINT);
?>

