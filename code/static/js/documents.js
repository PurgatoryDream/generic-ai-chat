function toggleAddGroupForm() {
    const form = document.querySelector('.add-group-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function openFileSelector(groupName) {
    document.getElementById('file-input-' + groupName).click();
}

function submitNewGroup() {
    const nameInput = document.getElementById('new-group-name');
    const descriptionInput = document.getElementById('new-group-description');
    console.log('Creating new group:', nameInput.value, descriptionInput.value);
    var data = new FormData();
    data.append('name', nameInput.value);
    data.append('description', descriptionInput.value);

    // Send the message to the server.
    $.ajax({
        url: '/documents/creategroup',
        type: 'POST',
        data: data,
        processData: false,
        contentType: false,
        success: function(data) {
            window.location.reload();
        }
    });
}

function handleGroupCheckboxChange(checkbox) {
    const groupName = checkbox.dataset.groupName;
    const isChecked = checkbox.checked;
    console.log('Group checkbox changed:', groupName, isChecked);
    var data = new FormData();
    data.append('group_name', groupName);
    data.append('is_checked', isChecked);
    $.ajax({
        url: '/documents/selectgroup',
        type: 'POST',
        data: data,
        processData: false,
        contentType: false,
        success: function(data) {
            console.log(data["checkres"]);
            console.log(data["value"]);
        }
    });
}

function uploadFile(inputElement, groupName) {
    const inputFile = inputElement.files[0];
    if (!inputFile) return;

    const data = new FormData();
    data.append('file', inputFile);
    data.append('group_name', groupName);

    // Enviar el archivo al servidor Flask
    $.ajax({
        url: '/documents/upload',
        type: 'POST',
        data: data,
        processData: false,
        contentType: false,
        success: function(data) {
            window.location.reload();
        }
    });
}