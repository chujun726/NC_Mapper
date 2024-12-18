<?php
// 設定回應標頭
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// 接收 POST 數據
$json = file_get_contents('php://input');
$dimensions = json_decode($json, true);

// 驗證數據
if (!$dimensions || 
    !isset($dimensions['longitude']) || 
    !isset($dimensions['latitude']) || 
    !isset($dimensions['height']) || 
    !isset($dimensions['time'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid dimensions data']);
    exit;
}

// 儲存選項
file_put_contents('dimensions.json', json_encode($dimensions, JSON_PRETTY_PRINT));

// 回傳處理結果，會在console.log顯示
$response = [
    'status' => 'success',
    'message' => 'Dimensions processed successfully',
    'data' => $dimensions
];

echo json_encode($response);
?>