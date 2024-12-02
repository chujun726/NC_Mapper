$(document).ready(function() {
  // Handle "Start Mapping" button click
  $('#start-mapping').click(function() {
    // Get the selected file
    var file = $('#nc-file')[0].files[0];

    // Check if a file is selected
    if (file) {
      // Create a new FormData object
      var formData = new FormData();
      formData.append('nc-file', file);

      // Use AJAX to send the file to the server
      $.ajax({
        url: 'upload.php',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          console.log('File uploaded successfully!');
          // Handle the server response as needed
        },
        error: function(xhr, status, error) {
          console.error('Error uploading file:', error);
          // Handle the error
        }
      });
    } else {
      alert('Please select a file to upload.');
    }
  });
});