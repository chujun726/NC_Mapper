<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// 暫時返回固定的變量列表
$variables = [
    '2m_temperature', 
    'geopotential', 
    'other1', 
    'other2'
];

echo json_encode($variables);
?>