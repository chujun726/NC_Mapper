<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// 設定路徑
$pythonPath = realpath('../python/envs/ncmapper/python.exe');  // 指定python環境路徑
// $pythonPath = 'C:\\Users\\user\\anaconda3\\envs\\ncmapper\\python.exe';  // local環境
$scriptPath = realpath('../python/analyze_nc.py');
$dataPath = realpath('../uploads/data.nc');

// 獲取請求的變量
$variable = $_GET['variable'] ?? '';

// 先獲取所有變量
$command = "\"$pythonPath\" \"$scriptPath\" \"$dataPath\" variables 2>&1";
exec($command, $variables);

// 初始化 heightData 陣列
$heightData = [];

// 對每個變量獲取其高度列表
foreach ($variables as $var) {
    $command = "\"$pythonPath\" \"$scriptPath\" \"$dataPath\" heights \"$var\" 2>&1";
    unset($heights); // 清除前一次的結果
    exec($command, $heights);
    $heightData[$var] = $heights;
}

// 返回對應變量的高度列表
if (isset($heightData[$variable])) {
    echo json_encode($heightData[$variable]);
} else {
    echo json_encode([]);
}
?>