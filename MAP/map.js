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

  // 加入格網線（可選）
  const graticule = new ol.layer.Graticule({
    strokeStyle: new ol.style.Stroke({
      color: 'rgba(211, 211, 211, 0.9)', // 格網線顏色
      width: 1,
    }),
    showLabels: true, // 顯示經緯度標籤
    wrapX: false,
  });
  map.addLayer(graticule);

    // 將 GeoTIFF 圖層添加到地圖
    map.addLayer(geoTiffLayer);
  



  // 控制工具（比例尺等）
  map.addControl(new ol.control.ScaleLine());

});