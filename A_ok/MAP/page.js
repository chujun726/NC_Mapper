// 切換顯示/隱藏圖層



document.addEventListener('DOMContentLoaded', function () { // 確保資源加載完畢

    $(document).ready(function () {
        // 使用 AJAX 獲取資料
        $.ajax({
          url: './php/get_select_para.php', // 指向後端 PHP 文件
          method: 'GET',
          dataType: 'json',
          success: function (response) {
            // 確保資料正確
            if (response.shading_title) {
              // 更新前端的 span 元素文字
              $('#contour-layer-title').text(response.shading_title);
            } else {
              console.error('未找到 shading_title 資料');
            }

            // 確保資料正確
            if (response.contour_title) {
                // 更新前端的 span 元素文字
                $('#shading-layer-title').text(response.contour_title);
                } else {
                console.error('未找到 shading_title 資料');
                }
          },
          error: function (xhr, status, error) {
            console.error('AJAX 請求失敗:', error);
          }
        });
      });

});