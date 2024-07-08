// Preview audio file
function previewAudio(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        
        reader.onload = function(e) {
            $('#audioPlayer').attr('src', e.target.result);
        }
        
        reader.readAsDataURL(input.files[0]); // convert to base64 string
    }
}

// Using jQuery for AJAX requests
$('form').on('submit', function (event) {
    event.preventDefault();
    var action = $(this).attr('action');

    $.ajax({
        type: $(this).attr('method'),
        url: $(this).attr('action'),
        data: new FormData(this),
        contentType: false,
        cache: false,
        processData: false,
        success: function (data) {
            if (action == '/transcribe/audio') {
                text = data.text;
                console.log(data);
                $('#transcript').text(text);
            } else if (action == '/transcribe/text') {
                text = data.text;
                console.log(data);
                $('#text').text(text);
            }
        },
    });
});

function compare() {
    var dmp = new diff_match_patch();
    var transcript = $('#transcript').val();
    var text = $('#text').val();
    var diffs = dmp.diff_main(transcript, text);
    dmp.diff_cleanupSemantic(diffs);
    $('#comparison').html(diffToHtml(diffs));
}

function diffToHtml(diffs) {
    var html = [];
    var sumErrores = 0;
    var sumText = 0;
    for (var i = 0; i < diffs.length; i++) {
        var operation = diffs[i][0];  // Operation (insert, delete, equal)
        var text = diffs[i][1];  // Text of change.
        if (operation === -1) {
            sumErrores += text.length;
            sumText += text.length;
        } else if (operation === 0) {
            sumText += text.length;
        }
        var color = operation === -1 ? '#ffa6a6' : operation === 1 ? '#aeff7e' : '#e8f5e6';
        html.push('<span style="background:' + color + '">' + escapeHtml(text) + '</span>');
    }

    var porcentaje = (sumText - sumErrores) / sumText * 100;
    html.push('<br><br><span style="font-size: 20px;">Accuracy: ' + porcentaje.toFixed(2) + '%</span>');

    return html.join('');
}

function escapeHtml(text) {
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

$(document).ready(function(){
    $('#infoButton').popover({
        title: "Comparison functionality.",
        content: "Comparison is made through the diff_match_patch algorithm. If a portion of text is only in Upload Audio, it'll be marked in red (wrong). If it is in the real text, it'll be marked in green (correction).",
        placement: "top"
    });
});