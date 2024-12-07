<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// 接收 POST 數據
$json = file_get_contents('php://input');
$data = json_decode($json, true);

// 簡單的回應，用於測試
$response = [
    'status' => 'success',
    'message' => 'Variables processed successfully',
    'received_data' => $data  // 回傳接收到的數據，方便前端確認
];

echo json_encode($response);
?>