<?php
// 設定回應標頭
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// 設定上傳檔案的基本參數
$uploadDir = '../uploads/';  // 上傳目錄
$maxFileSize = 100 * 1024 * 1024;  // 最大檔案大小 (100MB)

try {
    // 檢查是否有檔案上傳
    if (!isset($_FILES['nc-file'])) {
        throw new Exception('No file uploaded');
    }

    $file = $_FILES['nc-file'];
    error_log("Received file: " . print_r($file, true));

    // 檢查檔案上傳是否出錯
    if ($file['error'] !== UPLOAD_ERR_OK) {
        throw new Exception('File upload error: ' . $file['error']);
    }

    // 檢查檔案大小
    if ($file['size'] > $maxFileSize) {
        throw new Exception('File size exceeds maximum limit of 100MB');
    }

    // 檢查檔案類型（.nc 檔案）
    $fileExt = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if ($fileExt !== 'nc') {
        throw new Exception('Invalid file type. Only .nc files are allowed');
    }

    // 確保上傳目錄存在
    if (!file_exists($uploadDir)) {
        if (!mkdir($uploadDir, 0777, true)) {
            throw new Exception('Failed to create upload directory');
        }
    }

    // 固定使用 data.nc 作為檔名 (目前以僅處理一個檔案爲主，暫不考量多人使用)
    $uploadPath = $uploadDir . 'data.nc';

    // 如果檔案已存在，先刪除它
    if (file_exists($uploadPath)) {
        if (!unlink($uploadPath)) {
            throw new Exception('Failed to remove existing file');
        }
    }

    // 移動上傳的檔案
    if (!move_uploaded_file($file['tmp_name'], $uploadPath)) {
        throw new Exception('Failed to move uploaded file');
    }

    // 成功回應
    echo json_encode([
        'status' => 'success',
        'message' => 'File uploaded successfully',
        'data' => [
            'filename' => 'data.nc',
            'size' => $file['size']
        ]
    ]);

} catch (Exception $e) {
    // 錯誤回應
    http_response_code(400);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}