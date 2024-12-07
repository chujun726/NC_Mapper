<?php
// 設定允許跨域請求（如果需要）
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// 暫時返回固定的維度列表
$dimensions = [
    'longitude', 
    'latitude', 
    'level', 
    'time', 
    'other1', 
    'other2'
];

// 回傳 JSON 格式的維度列表
echo json_encode($dimensions);
?>