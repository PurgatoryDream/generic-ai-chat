const recognition = new webkitSpeechRecognition() || new SpeechRecognition();
var recognizing = false;

function generateMessage(message, role) {
    var time = new Date();
    var hour = time.getHours();
    var minute = time.getMinutes();
    var stringTime = hour + ":" + minute;
    return "<div class='message " + role + "'><p>" + message + "</p><span class=\"message-time\">" + stringTime + "</span></div>";
}

function addMessageToChat(message, role) {
    var chatBox = $("#chatBox");
    chatBox.append(generateMessage(message, role));
    chatBox.scrollTop(chatBox[0].scrollHeight);
}

$(document).ready(function() {
    // When the send button is clicked, send the message to the server.
    $("#sendButton").click(function() {
        if ($("#inputText").val() == "") {
            return;
        }

        addMessageToChat($("#inputText").val(), "sent");

        // Construct the message to send to the server.
        message = $("#inputText").val(); 
        var data = new FormData();
        data.append('message', message);
        $("#inputText").val("");

        // Send the message to the server.
        $.ajax({
            url: '/chat',
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function(data) {
                addMessageToChat(data, "received");
            }
        });
    });

    $("#clearButton").click(function() {
        $("#chatBox").empty();
    });

    $("#retryLastButton").click(function() {
        if ($("#chatBox").children().length == 0) {
            return;
        }

        // Delete the last received message and send a request to the server to retry it with the last sent message.
        $("#chatBox").children().last().remove();
        lastMessage = $("#chatBox").children().last();
        message = lastMessage.children().first().text();
        var data = new FormData();
        data.append('message', message);
        
        $.ajax({
            url: '/chat',
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function(data) {
                addMessageToChat(data, "received");
            }
        });
    });

    $("#speech-button").click(function() {
        if (recognizing) {
            recognition.stop();
            console.log('Speech recognition stopped.');
            recognizing = false;
            return;
        }

        const outputField = document.getElementById('inputText');
        recognition.interimResults = true;
        recognition.continuous = true;
        recognition.start();
        recognizing = true;

        recognition.onresult = event => {
            const result = event.results[event.results.length - 1][0].transcript;
            outputField.value = result;
        };

        recognition.onerror = event => {
            console.error('Speech recognition error:', event.error);
        };

        recognition.onnomatch = () => {
            console.log('No speech was recognized.');
        };
    });
});