<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// 執行 Python 腳本獲取維度列表
$pythonPath = realpath('../python/envs/ncmapper/python.exe');  // 指定python環境路徑
// $pythonPath = 'C:\\Users\\user\\anaconda3\\envs\\ncmapper\\python.exe';  // local環境
$scriptPath = realpath('../python/analyze_nc.py'); // pyton脚本
$dataPath = realpath('../uploads/data.nc'); // 要處理的nc檔

$command = "\"$pythonPath\" \"$scriptPath\" \"$dataPath\" variables 2>&1";
// 輸出陣列
exec($command, $variables);

echo json_encode($variables);
?>