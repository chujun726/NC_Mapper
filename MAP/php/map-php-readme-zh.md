# PHP 文件說明

## 概述
本文件涵蓋 地圖處理相關的php腳本，負責對於後端、起始頁面進行資料載入

## 檔案結構
```
php/
├── get_contour.php     # 從地圖描述文件讀取contour資料
├── get_tiff.php        # 從地圖描述文件讀取tiff參數、檔案位置
├── get_select_para.php # 從起始頁面讀取使用者的渲染設定，呈現在layer panel中 

mapdiscript.json # 地圖描述文件的模擬資料，請替換為實際匯出描述文件的php
```

## 詳細檔案說明

### 1.get_contour.php
**用途**：從地圖描述文件讀取contour資料
**狀態**：可直接參考
**預期輸入**：
- GET 請求，檔案資料來源未定，暫時以map_descript.json取代

**預期輸出**：JSON 回應
```json
{
    "contour_layer": { 
         "data": null,
         "contour_geojson": "geojson資料"
}
```

### 2. get_tiff.php
**用途**：從地圖描述文件解析tiff設定檔
**預期輸入**：
- GET 請求，檔案資料來源未定，暫時以map_descript.json取代

(以下為節錄)

```json 
{

"shading_layer":{
    "crs" : "地理座標",
    "value_color_dict": "色彩與色票的映射"
},
"file_path": "../layer/contour_3857.tif"
},

}
```

**預期輸出**：tiff相關參數
```json
{
"tiff_path": "./layer/contour_3857.tif", //可以直接讀取的路徑 規定在./layer/檔名.tiff
"crs": "EPSG:3857", //投影座標系統
"min": 0, //資料範圍最小值
"max": 1100, // 資料範圍最大值
} 

```

### 3. get_select_para.php
**用途**：處理使用者的維度選擇
**預期輸入**：
- GET 請求，前端地圖參數的設置
```json
{ // 與process_variables.php的輸入相同
  
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
    "shading_title": "wind_700", //類型_level
    "contour_title": "2m_temperature_700",//類型_level
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
1. 等待地圖描述文件產生
2.  `get_contour.php` 解析地圖描述文件，擷取等高線資料
3.  `get_tiff` 解析地圖描述文件，擷取tiff參數資料
4. `get_select_para.php` 從起始頁面讀取使用者的渲染設定
5.  等待相關檔案寫入與載入完畢
6. 執行地圖渲染

