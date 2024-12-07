$(document).ready(function() {
  // 初始狀態下不顯示任何模態框
  $('#dimension-modal').hide();
  $('#variables-modal').hide();

  // ===================== Step 1: 檔案上傳 =====================
  $('#start-mapping').click(function() {
    var file = $('#nc-file')[0].files[0];

    if (file) {
      var formData = new FormData();
      formData.append('nc-file', file);

      // 顯示載入畫面
      $('#loading-overlay').show();

      // 上傳檔案
      $.ajax({
        url: 'php/upload.php',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          console.log('File uploaded successfully!');
          // 檔案上傳成功後，開始 Step 2
          requestDimensions();
        },
        error: function(xhr, status, error) {
          console.error('Error uploading file:', error);
          $('#loading-overlay').hide();
          alert('File upload failed: ' + error);
        }
      });
    } else {
      alert('Please select a file to upload.');
    }
  });

  // ===================== Step 2: 維度選擇 =====================
  // 請求維度列表
  function requestDimensions() {
    $.ajax({
      url: 'php/dimensions.php',
      type: 'GET',
      dataType: 'json',
      success: function(dimensions) {
        // 隱藏載入畫面
        $('#loading-overlay').hide();
        // 準備維度選擇模態框
        prepareDimensionModal(dimensions);
      },
      error: function(xhr, status, error) {
        console.error('Error fetching dimensions:', error);
        $('#loading-overlay').hide();
        alert('Failed to fetch dimensions: ' + error);
      }
    });
  }

  // 準備維度選擇模態框
  function prepareDimensionModal(dimensions) {
    var dimensionModal = $('#dimension-modal');
    var longitudeSelect = $('#longitude-select');
    var latitudeSelect = $('#latitude-select');
    var heightSelect = $('#height-select');
    var timeSelect = $('#time-select');

    // 清空先前的選項
    [longitudeSelect, latitudeSelect, heightSelect, timeSelect].forEach(function(select) {
      select.empty().append($('<option>', {
        value: '',
        text: 'Select a dimension'
      }));
    });

    // 為每個維度添加選項
    dimensions.forEach(function(dimension) {
      [longitudeSelect, latitudeSelect, heightSelect, timeSelect].forEach(function(select) {
        select.append($('<option>', {
          value: dimension,
          text: dimension
        }));
      });
    });

    // 顯示維度選擇模態框
    dimensionModal.show();
  }

  // 關閉維度選擇模態框的按鈕
  $('#close-dimension-modal').click(function() {
    $('#dimension-modal').hide();
  });

  // 確認選擇維度的按鈕
  $('#confirm-dimensions').click(function() {
    // 獲取選中的維度
    var selectedDimensions = {
      longitude: $('#longitude-select').val(),
      latitude: $('#latitude-select').val(),
      height: $('#height-select').val(),
      time: $('#time-select').val()
    };
    
    // 驗證是否所有維度都已選擇
    var allDimensionsSelected = Object.values(selectedDimensions).every(dim => dim !== '');
    
    if (allDimensionsSelected) {
      // 顯示載入畫面
      $('#loading-overlay').show();
      
      // 將選擇的維度傳送給後端
      $.ajax({
        url: 'php/process_dimensions.php',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(selectedDimensions),
        success: function(response) {
          $('#loading-overlay').hide();
          $('#dimension-modal').hide();
          console.log('Dimensions processed:', response);
          // Step 2 完成後，開始 Step 3
          prepareVariableModal();
        },
        error: function(xhr, status, error) {
          $('#loading-overlay').hide();
          alert('Failed to process dimensions: ' + error);
        }
      });
    } else {
      alert('Please select all dimensions before confirming.');
    }
  });

  // ===================== Step 3: 變量選擇 =====================
  // 準備變量選擇模態框
  function prepareVariableModal() {
    $('#loading-overlay').show();
    
    $.ajax({
      url: 'php/get_variables.php',
      type: 'GET',
      dataType: 'json',
      success: function(variables) {
        $('#loading-overlay').hide();
        
        // 填充變量選擇器
        var shadingVariable = $('#shading-variable');
        var contourVariable = $('#contour-variable');
        
        // 清空現有選項
        shadingVariable.empty().append($('<option>', {
          value: '',
          text: 'Select a variable'
        }));
        
        contourVariable.empty().append($('<option>', {
          value: 'None',
          text: 'None'
        }));
        
        // 添加變量選項
        variables.forEach(function(variable) {
          shadingVariable.append($('<option>', {
            value: variable,
            text: variable
          }));
          
          contourVariable.append($('<option>', {
            value: variable,
            text: variable
          }));
        });

        // 初始化 height 選擇器
        $('#shading-height').empty().append($('<option>', {
          value: '',
          text: 'Select height'
        }));

        $('#contour-height').empty().append($('<option>', {
          value: 'None',
          text: 'None'
        }));
        
        // 顯示變量選擇模態框
        $('#variables-modal').show();
      },
      error: function(xhr, status, error) {
        $('#loading-overlay').hide();
        alert('Failed to fetch variables: ' + error);
      }
    });
  }

  // 變量選擇改變時的處理函數
  function handleVariableChange(variableSelectId, heightSelectId) {
    const selectedVariable = $(`#${variableSelectId}`).val();
    const heightSelect = $(`#${heightSelectId}`);

    // 如果選擇了 None 或空值
    if (!selectedVariable || selectedVariable === 'None') {
      heightSelect.empty().append($('<option>', {
        value: 'None',
        text: 'None'
      }));
      heightSelect.prop('disabled', true);
      return;
    }

    // 顯示載入指示器
    $('#loading-overlay').show();

    // 向後端請求高度列表
    $.ajax({
      url: 'php/get_heights.php',
      type: 'GET',
      data: { variable: selectedVariable },
      dataType: 'json',
      success: function(heights) {
        // 清空並填充高度選擇器
        heightSelect.empty();

        // 如果是空數組，禁用高度選擇
        if (heights.length === 0) {
          heightSelect.append($('<option>', {
            value: '',
            text: 'No height parameter'
          }));
          heightSelect.prop('disabled', true);
        } else {
          heightSelect.prop('disabled', false);
          heightSelect.append($('<option>', {
            value: '',
            text: 'Select height'
          }));
          heights.forEach(function(height) {
            heightSelect.append($('<option>', {
              value: height,
              text: height + ' hPa'
            }));
          });
        }
        
        // 隱藏載入指示器
        $('#loading-overlay').hide();
      },
      error: function(xhr, status, error) {
        console.error('Error fetching heights:', error);
        $('#loading-overlay').hide();
        alert('Failed to fetch height options: ' + error);
      }
    });
  }

  // 監聽 Shading Variable 的變化
  $('#shading-variable').change(function() {
    handleVariableChange('shading-variable', 'shading-height');
  });

  // 監聽 Contour Variable 的變化
  $('#contour-variable').change(function() {
    handleVariableChange('contour-variable', 'contour-height');
  });

  // 關閉變量選擇模態框的按鈕
  $('#close-variables-modal').click(function() {
    $('#variables-modal').hide();
  });

  // 確認變量選擇的按鈕
  $('#confirm-variables').click(function() {
    var selectedVariables = {
      shading: {
        variable: $('#shading-variable').val(),
        height: $('#shading-height').val()
      },
      contour: {
        variable: $('#contour-variable').val(),
        height: $('#contour-height').val()
      }
    };
    
    // 驗證 shading layer 的選擇
    if (!selectedVariables.shading.variable) {
      alert('Please select a shading variable.');
      return;
    }

    // 只有當高度選單可用且為必填時，才需讓使用者選擇高度
    if (!$('#shading-height').prop('disabled') && !selectedVariables.shading.height) {
      alert('Please select a height for the shading variable.');
      return;
    }

    // 如果選擇了 contour 變量但未選擇高度
    if (selectedVariables.contour.variable && 
      selectedVariables.contour.variable !== 'None' && 
      !$('#contour-height').prop('disabled') && 
      !selectedVariables.contour.height) {
      alert('Please select a height for the contour variable.');
      return;
    }
    
    // 發送選擇結果到後端
    $('#loading-overlay').show();
    
    $.ajax({
      url: 'php/process_variables.php',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(selectedVariables),
      success: function(response) {
        $('#loading-overlay').hide();
        $('#variables-modal').hide();
        console.log('Variables processed:', response);
      },
      error: function(xhr, status, error) {
        $('#loading-overlay').hide();
        alert('Failed to process variables: ' + error);
      }
    });
  });
});