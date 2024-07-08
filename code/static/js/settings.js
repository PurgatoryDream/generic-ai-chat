function showColors() {
    var collapisble = $('#color-collapsible');
    collapisble.toggleClass('active-collapsible');

    var content = $('#color-palette-container');
    if (content.css('display') == 'none') {
        content.css('display', 'block');
    } else {
        content.css('display', 'none');
    }
}

function updateUISettings() {
    const inputs = document.getElementsByTagName('input');
    var data = new FormData();
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type == 'color') {
            data.append(inputs[i].id, inputs[i].value);
        }
    }

    $.ajax({
        url: '/settings/update-ui',
        type: 'POST',
        data: data,
        processData: false,
        contentType: false,
        success: function(data) {
            window.location.reload();
        }
    });
}

function updateModelSettings() {
    const model = document.getElementById('llm_chat');
    var modeltext = model.options[model.selectedIndex].text;
    var openai_apikey = document.getElementById('openai_apikey').value;
    var googleapp_creds = document.getElementById('googleapp_creds').files[0];

    var data = new FormData();
    data.append('model', modeltext);
    data.append('openai_apikey', openai_apikey);
    data.append('googleapp_creds', googleapp_creds);

    $.ajax({
        url: '/settings/update-model',
        type: 'POST',
        data: data,
        processData: false,
        contentType: false,
        success: function(data) {
            window.location.reload();
        }
    });
}