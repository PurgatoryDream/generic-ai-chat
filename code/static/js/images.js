document.getElementById('submit-btn').addEventListener('click', function() {
    var textContent = document.getElementById('image-text').value;
    const data = new FormData();
    data.append('text', textContent);
    
    // Example: POST request with textContent
    $.ajax({
        type: 'POST',
        url: '/images/generate',
        data: data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            document.getElementById('image-display').src = data.image_url;
        },
    });
});
