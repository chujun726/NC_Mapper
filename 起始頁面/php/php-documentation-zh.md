# PHP 文件說明

## 概述
本文件涵蓋 NC Mapper 網頁應用程式所需的所有 PHP 文件。這些文件負責處理檔案上傳、資料維度處理和變量管理。

## 檔案結構
```
php/
├── upload.php              # 處理 NC 檔案上傳
├── dimensions.php          # 回傳維度列表
├── process_dimensions.php  # 處理所選維度
├── get_variables.php       # 回傳可用變量
├── get_heights.php        # 回傳特定變量的高度列表
└── process_variables.php   # 處理所選變量和高度
```

## 詳細檔案說明

### 1. upload.php
**用途**：處理 NetCDF 檔案的上傳
**預期輸入**：
- POST 請求，檔案資料在 `nc-file` 欄位中

**預期輸出**：JSON 回應
```json
{
    "status": "success",
    "message": "檔案上傳成功"
}
```

### 2. dimensions.php
**用途**：回傳已上傳 NC 檔案中可用的維度列表
**預期輸入**：
- GET 請求

**預期輸出**：維度名稱的 JSON 陣列
```json
["longitude", "latitude", "level", "time", "other1", "other2"]
```

### 3. process_dimensions.php
**用途**：處理使用者的維度選擇
**預期輸入**：
- POST 請求，包含維度選擇的 JSON 資料
```json
{
    "longitude": "選擇的維度_1",
    "latitude": "選擇的維度_2",
    "height": "選擇的維度_3",
    "time": "選擇的維度_4"
}
```

**預期輸出**：JSON 回應
```json
{
    "status": "success",
    "message": "維度處理成功",
    "received_data": {
        // 回傳接收到的選擇
    }
}
```

### 4. get_variables.php
**用途**：回傳可用於繪圖的變量列表
**預期輸入**：
- GET 請求

**預期輸出**：變量名稱的 JSON 陣列
```json
["2m_temperature", "geopotential", "other1", "other2"]
```

### 5. get_heights.php
**用途**：回傳特定變量可用的高度層級
**預期輸入**：
- GET 請求，包含變量參數
- 範例：`get_heights.php?variable=geopotential`

**預期輸出**：高度值的 JSON 陣列
```json
[1000, 900, 800, 500, 300]  // geopotential 的範例
[]                          // 地表變量如 2m_temperature 的空陣列
```

### 6. process_variables.php
**用途**：處理使用者的變量和高度選擇
**預期輸入**：
- POST 請求，包含選擇的 JSON 資料
```json
{
    "shading": {
        "variable": "選擇的變量_1",
        "height": "選擇的高度_1"
    },
    "contour": {
        "variable": "選擇的變量_2",
        "height": "選擇的高度_2"
    }
}
```

**預期輸出**：JSON 回應
```json
{
    "status": "success",
    "message": "變量處理成功",
    "received_data": {
        // 回傳接收到的選擇
    }
}
```

## 所有 PHP 檔案的共同要求

1. **Headers 設定**：
   ```php
   header('Content-Type: application/json');
   header('Access-Control-Allow-Origin: *');
   ```

2. **錯誤處理**：
   - 所有檔案都應回傳適當的 HTTP 狀態碼
   - 錯誤回應應遵循此格式：
   ```json
   {
       "status": "error",
       "message": "錯誤描述"
   }
   ```

## 開發注意事項
1. 目前使用預設回應進行測試
2. 需要實作實際的 NC 檔案處理
3. 考慮對頻繁存取的資料實作快取機制
4. 考慮實作檔案處理的工作階段管理

## 使用流程範例
1. 使用者透過 `upload.php` 上傳 NC 檔案
2. 系統透過 `dimensions.php` 取得維度
3. 使用者選擇維度，由 `process_dimensions.php` 處理
4. 系統透過 `get_variables.php` 取得變量
5. 使用者選擇變量，系統透過 `get_heights.php` 取得高度
6. 最終選擇由 `process_variables.php` 處理
