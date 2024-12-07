<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// 獲取選擇的變量
$variable = $_GET['variable'] ?? '';

// 模擬不同變量的高度資料
$heightData = [
    '2m_temperature' => [],
    'geopotential' => [1000, 900, 800, 500, 300],
    'other1' => [600, 300, 100],
    'other2' => [900, 500, 300]
];

// 返回對應變量的高度列表
if (isset($heightData[$variable])) {
    echo json_encode($heightData[$variable]);
} else {
    echo json_encode([]);
}
?>