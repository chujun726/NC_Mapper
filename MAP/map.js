console.log("map.js");

document.addEventListener('DOMContentLoaded', function () {  // 確保資源加載完畢

  // OpenLayers 地圖初始化
  const map = new ol.Map({
    target: 'map', // 將地圖綁定到 map-container
    layers: [
      // 基本圖層：OpenStreetMap 圖層
      new ol.layer.Tile({
        source: new ol.source.OSM(),
      }),
    ],
    view: new ol.View({
      center: ol.proj.fromLonLat([0, 0]), // 地圖中心（經度, 緯度）
      zoom: 2, // 初始縮放級別
    }),
  });

  /////  加入Grid圖層 + 控制樣式的函數   /////
  function initializeGridLayer() {
    let graticule;

    // 獲取控制元素
    const colorInput = document.querySelector('#grid-color-input');
    const widthInput = document.querySelector('#grid-width-input');
    const intervalInput = document.querySelector('#grid-interval-input');

    // 更新格網線樣式的函數
    function updateGridStyle() {
        const color = colorInput.value;
        const width = parseFloat(widthInput.value);
        const interval = parseFloat(intervalInput.value);

        // 如果已存在格網，先移除它
        if (graticule) {
            map.removeLayer(graticule);
        }

        // 創建新的格網線圖層
        graticule = new ol.layer.Graticule({
            // 基本樣式設置
            strokeStyle: new ol.style.Stroke({
                color: color,
                width: width
            }),
            showLabels: true,
            wrapX: false,
            
            // 間隔相關設置
            intervals: [interval],         // 固定間隔
            maxLines: 500,                // 增加最大線條數量
            minDistance: 20,              // 降低最小間距（像素）
            targetSize: 50,               // 降低目標大小（像素）
            
            // 標籤相關設置
            lonLabelPosition: 0,        // 經度標籤位置
            latLabelPosition: 1,        // 緯度標籤位置
            /*lonLabelFormatter: function(lon) {  // 自定義經度標籤格式
                return lon.toFixed(1) + '°';
            },
            latLabelFormatter: function(lat) {  // 自定義緯度標籤格式
                return lat.toFixed(1) + '°';
            }*/
        });

        // 添加新的格網到地圖
        map.addLayer(graticule);
    }

     // 添加事件監聽器
     colorInput.addEventListener('input', updateGridStyle);
     colorInput.addEventListener('change', updateGridStyle);
     widthInput.addEventListener('input', updateGridStyle);
     widthInput.addEventListener('change', updateGridStyle);
     intervalInput.addEventListener('input', updateGridStyle);
     intervalInput.addEventListener('change', updateGridStyle);
 
     // 設置初始樣式
     updateGridStyle();
   }
   initializeGridLayer();


   /////  創建line圖層 + 控制樣式的函數  /////
   function initializeLayersAndStyles() {
    // 創建 coastline、countries 圖層
    const coastline_Layer = new ol.layer.Vector({
      source: new ol.source.Vector({
        url: './basemap/coastline.geojson', // 海岸線位置
        format: new ol.format.GeoJSON()
      })
    });
    
    const countries_Layer = new ol.layer.Vector({
      source: new ol.source.Vector({
        url: './basemap/countries.geojson', // 國界位置
        format: new ol.format.GeoJSON()
      })
    });
    map.addLayer(coastline_Layer);
    map.addLayer(countries_Layer);

    // 獲取控制元素
    const colorInput = document.querySelector('#line-color-input');
    const widthInput = document.querySelector('#line-width-input');

    // 更新樣式的函數
    function updateStyles() {
      const color = colorInput.value;
      const width = parseFloat(widthInput.value);

      // 設置 coastline 樣式
      coastline_Layer.setStyle(new ol.style.Style({
        fill: new ol.style.Fill({
          color: 'rgba(255, 165, 0, 0)'
        }),
        stroke: new ol.style.Stroke({
          color: color,
          width: width
        })
      }));

      // 設置 countries 樣式
      countries_Layer.setStyle(new ol.style.Style({
        fill: new ol.style.Fill({
          color: 'rgba(255, 165, 0, 0)'
        }),
        stroke: new ol.style.Stroke({
          color: color,
          width: width / 3
        })
      }));
    }

    // 添加事件監聽器
    colorInput.addEventListener('change', updateStyles);
    colorInput.addEventListener('input', updateStyles);
    widthInput.addEventListener('change', updateStyles);
    widthInput.addEventListener('input', updateStyles);

    // 設置初始樣式
    updateStyles();
  }
  // 初始化圖層和樣式
  initializeLayersAndStyles();


   ///// 將 contour layer 圖層添加到地圖  ///// 

   // contourline 代表線
   // contourLayer 代表等高線標籤
   
   // layerpanel控制
  function initializeContourline(contourLayer) {


      // 獲取控制面板元素
      const colorInput = document.querySelector('#contourline-color-input');
      const widthInput = document.querySelector('#contourline-width-input');

      // 更新樣式 適用於contourline
      function updateContourlineStyle() {
        const color = colorInput.value; // 獲取選擇的顏色
        const width = parseFloat(widthInput.value); // 獲取線寬

        // 檢查是否有 contourLayer
        if (contourLayer) {
          contourLayer.setStyle(
            new ol.style.Style({
              stroke: new ol.style.Stroke({
                color: color,
                width: width
              })
            })
          );
          console.log('樣式已更新：', { color, width });
        } else {
          console.error('contourLayer 未定義');
        }
      }

          // 添加事件監聽器，動態更新樣式
      colorInput.addEventListener('change', updateContourlineStyle);
      colorInput.addEventListener('input', updateContourlineStyle);
      widthInput.addEventListener('change', updateContourlineStyle);
      widthInput.addEventListener('input', updateContourlineStyle);

      // 初始化樣式
      updateContourlineStyle();
  }

    

    // 1. ajax載入資料

    $.ajax({
      url: './test_contour.php', // 更換為最終 PHP 文件的位置
      method: 'GET',
      dataType: 'json',
      success: function (geojsonData) {
            // 解析 GeoJSON，轉換為 OpenLayers Feature


      const features = new ol.format.GeoJSON().readFeatures(geojsonData, {
        featureProjection: 'EPSG:3857' // 投影轉換至 Web Mercator
      });

      const features_line = new ol.format.GeoJSON().readFeatures(geojsonData, {
        featureProjection: 'EPSG:3857' // 投影轉換至 Web Mercator
      });


      // 標籤 載入等高線 只需執行一次

      features.forEach(feature => {
        const value = feature.get('value'); // 獲取等高線的值
        feature.setStyle(
          new ol.style.Style({
            /*stroke: new ol.style.Stroke({
              color: 'blue', // 等高線顏色
              width: 1       // 線條寬度
            }),
            */
            text: new ol.style.Text({
              text: value ? value.toFixed(0) : '', // 轉換值為文字，保留兩位小數
              font: '12px Arial',
              fill: new ol.style.Fill({
                color: '#000000' // 黑色文字
              }),
              stroke: new ol.style.Stroke({
                color: '#ffffff', // 白色描邊
                width: 3
              }),
              placement: 'line', // 沿著線條顯示文字
              overflow: true // 允許文字溢出線條邊界
            })
          })
        );
      });

            // 創建圖層並添加 Feature
      const contourLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
          features: features // 將解析後的 Feature 添加到 Source
        })
      });  
      
      const contourline = new ol.layer.Vector({
        source: new ol.source.Vector({
          features: features_line // 將解析後的 Feature 添加到 Source
        }),
        style: new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: '#0000ff', // 預設藍色
            width: 1 // 預設線寬
          })
        })
      });

      map.addLayer(contourline);
      map.addLayer(contourLayer);
      console.log('等高線圖層已添加');
      initializeContourline(contourline); // 初始化等高線相關邏輯

    },

      error: function (error) {
        // 請求失敗
        console.error('無法獲取 GeoJSON 資料:', error);
      }
    });


  
  // 這裡預計改為ajax讀取tiff資料
  
  let tiff_url = './layer/contour_3857.tif' //tiff路徑
  let ovr_url = './layer/contour_3857.tif.ovr' //overview圖磚路徑
  let tiff_min = 0 //tiff最小值
  let tiff_max = 1100 //tiff最大值
  let bandIndex = [0]
  let opacity = 1

  // colormap

  async function loadRasterLayer(tiff_url,ovr_url = '',tiff_min,tiff_max,bandIndex = [0],opacity = 1) {
    try {
      const raster_Layer = new ol.layer.WebGLTile({
        source: new ol.source.GeoTIFF({
          sources: [{
            url: tiff_url,  // 替換成你的檔案路徑
            overviews: [ovr_url], // 可以為空
            min: tiff_min, 
            max: tiff_max,
            //width: 512, // 降低解析度
            //height: 512,
          }],
          bands: bandIndex,
          
        }),
        opacity: opacity  // 可調整透明度
      });
        // 錯誤處理
      raster_Layer.getSource().on('error', function(event) {
        console.error('Raster 載入錯誤:', event.error);
      });

      // 監聽載入狀態
      raster_Layer.getSource().on('change', function() {
        console.log('Raster 載入狀態:', this.getState());
      });
     // 添加圖層到地圖
      map.addLayer(raster_Layer);

    } catch (error) {
      console.error('讀取 GeoTIFF 數據範圍時發生錯誤:', error);
      throw error; // 向外傳播錯誤
    }

  }
  // 載入raster圖層主程式
  raster_layer = loadRasterLayer(tiff_url,ovr_url,tiff_min,tiff_max,bandIndex,opacity)
  
  


  // 控制工具（比例尺等）
  map.addControl(new ol.control.ScaleLine());

});