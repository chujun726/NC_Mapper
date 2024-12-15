// 切換顯示/隱藏圖層

document.addEventListener('DOMContentLoaded', function () { // 確保資源加載完畢
  // 點選首頁左上角的ICON，跳轉到 index.html 
  document.querySelector('.header-content').addEventListener('click', function () {
    window.location.href = '../起始頁面/index.html'; 
  });
    

  
  
  // 1. 控制圖層渲染顏色 變數為newColor

    // 顏色選取器
    document.querySelectorAll('.color-display').forEach((span) => {
        // 點擊顏色顯示值 (#AAA)
        span.addEventListener('click', function () {
        // 找到對應的顏色輸入框
        const colorInput = this.nextElementSibling.nextElementSibling;
        if (colorInput) {
            // 觸發顏色選擇器的點擊事件
            colorInput.click();
        }
        });
    });
    
    // 使用者選擇顏色後更新顯示值
    document.querySelectorAll('.color-input').forEach((input) => {
      
        input.addEventListener('input', function () {
        // 找到對應的顏色顯示元素
        const colorDisplay = this.previousElementSibling.previousElementSibling;
        if (colorDisplay) {
            // 更新顯示的顏色值
            const newColor = this.value.toUpperCase(); // 獲取新顏色值
            colorDisplay.textContent = newColor; // 更新文字
            colorDisplay.style.color = newColor; // 更新背景色
          
        }
        });
    });


     // 2. 改變線的寬度(width)大小  變數為value


    // 顯示width的輸入選單
  document.querySelectorAll('.width-display').forEach((span) => {
    span.addEventListener('click', function () {
      const input = this.nextElementSibling.nextElementSibling; // 找到對應的輸入框
      if (input) {
        input.style.display = 'inline-block'; // 顯示輸入框
        this.style.display = 'none'; // 隱藏文字顯示框
        input.focus(); // 自動聚焦到輸入框
      }
    });
  });

  //選擇與紀錄width，並限制範圍在0-50px之間
  document.querySelectorAll('.width-input').forEach((input) => {
    input.addEventListener('blur', function () {
      const span = this.previousElementSibling.previousElementSibling; // 找到對應的文字框
      if (span) {
        let value = this.value || '2'; // 如果輸入框為空，默認為 7
              // 新增範圍檢查，輸入小於 5 或大於 50 時默認為 7
        if (value < 0 || value > 50) {
          value = '2';
        }


        span.textContent = `${value}`; // 更新文字框的值
        span.style.display = 'inline-block'; // 顯示文字框
        this.style.display = 'none'; // 隱藏輸入框
      }
    });

  // 處理用戶按 Enter 確認
  input.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      this.blur(); // 模擬失去焦點，執行相同邏輯
    }
  });
});


  // 3. 改變隔線間距大小(interval)  變數為interval_value

  // 顯示interval的輸入選單
document.querySelectorAll('.interval-display').forEach((span) => {
  span.addEventListener('click', function () {
    const input = this.nextElementSibling.nextElementSibling; // 找到對應的輸入框
    if (input) {
      input.style.display = 'inline-block'; // 顯示輸入框
      this.style.display = 'none'; // 隱藏文字顯示框
      input.focus(); // 自動聚焦到輸入框
    }
  });
});

  // 選擇與紀錄interval，並限制範圍在0-90度之間
  document.querySelectorAll('.interval-input').forEach((input) => {
    input.addEventListener('blur', function () {
      const span = this.previousElementSibling.previousElementSibling; // 找到對應的文字框
      if (span) {
        let interval_value = this.value || '30'; // 如果輸入框為空，默認為 30

        // 範圍檢查，輸入小於 0 或大於 90 時默認為 30
        if (interval_value < 0 || interval_value > 90) {
          interval_value = '30';
        }

        span.textContent = `${interval_value}°`; // 更新文字框的值
        span.style.display = 'inline-block'; // 顯示文字框
        this.style.display = 'none'; // 隱藏輸入框
      }
    });

    // 處理用戶按 Enter 確認
    input.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        this.blur(); // 模擬失去焦點，執行相同邏輯
      }
    });
  });

   // 4. 改變解析度(resolution)  變數為res_value

  // 顯示resolution的輸入選單
document.querySelectorAll('.resolution-display').forEach((span) => {
  span.addEventListener('click', function () {
    const input = this.nextElementSibling.nextElementSibling; // 找到對應的輸入框
    if (input) {
      input.style.display = 'inline-block'; // 顯示輸入框
      this.style.display = 'none'; // 隱藏文字顯示框
      input.focus(); // 自動聚焦到輸入框
    }
  });
});

   // 選擇與紀錄resolution，並限制範圍在0公尺以上
  document.querySelectorAll('.resolution-input').forEach((input) => {
    input.addEventListener('blur', function () {
      const span = this.previousElementSibling.previousElementSibling; // 找到對應的文字框
      if (span) {
        let res_value = this.value || '50'; // 如果輸入框為空，默認為 50

        // 範圍檢查，輸入小於 0 時默認為 50
        if (res_value < 0) {
          res_value = '50';
        }

        span.textContent = `${res_value}m`; // 更新文字框的值
        span.style.display = 'inline-block'; // 顯示文字框
        this.style.display = 'none'; // 隱藏輸入框
      }
    });

    // 處理用戶按 Enter 確認
    input.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        this.blur(); // 模擬失去焦點，執行相同邏輯
      }
    });
  });

    
  // 5. 改變解析度(level)  變數為lev_value

  // 點擊顯示數字輸入框
  document.querySelectorAll('.level-display').forEach((span) => {
    span.addEventListener('click', function () {
      const input = this.nextElementSibling.nextElementSibling; // 找到對應的輸入框
      if (input) {
        input.style.display = 'inline-block'; // 顯示輸入框
        this.style.display = 'none'; // 隱藏文字顯示框
        input.focus(); // 自動聚焦到輸入框
      }
    });
  });

  // 顯示level的輸入選單，並限制高程在0公尺以上
  document.querySelectorAll('.level-input').forEach((input) => {
    input.addEventListener('blur', function () {
      const span = this.previousElementSibling.previousElementSibling; // 找到對應的文字框
      if (span) {
        let lev_value = this.value || '700'; // 如果輸入框為空，默認為 700

        // 檢查範圍：如果輸入小於 0，重設為 700
        if (lev_value < 0) {
          lev_value = '700';
        }

        span.textContent = `${lev_value}m`; // 更新文字框的值
        span.style.display = 'inline-block'; // 顯示文字框
        this.style.display = 'none'; // 隱藏輸入框
      }
    });

    // 處理用戶按 Enter 確認
    input.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        this.blur(); // 模擬失去焦點，執行相同邏輯
      }
    });
  });


});