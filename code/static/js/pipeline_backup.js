function renderBlocks(blocks) {
    blocks.forEach(block => {
        let $block = $('#block-template').clone().removeAttr('id');

        // Set block type and function
        $block.data('type', block.type).data('function', block.function);
        
        // Set the background color
        $block.css('background-color', block.backgroundColor);
        
        // Set the block description and title
        $block.find('.block-title').text(block.type);
        $block.find('.block-description').text(block.description);

        // Append input buttons with labels
        block.input.forEach((input, index) => {
            let $inputContainer = createIOButton('input', input.name);
            $block.append($inputContainer);
        });
    
        // Append output buttons with labels
        block.output.forEach((output, index) => {
            let $outputContainer = createIOButton('output', output.name);
            $block.append($outputContainer);
        });
        
        // Create editable settings based on the block definition
        for (let setting in block.editableSettings) {
            let settingDef = block.editableSettings[setting];
            $block.find('.block-options').append(createEditableSetting(setting, settingDef));
        }

        // Append the new block to the blocks container
        $('#blocks-container').append($block.show());
    });
}

function createBlockElement(blockData) {
    let $block = $('#block-template').clone().removeAttr('id');

    // Set block type and function
    $block.data('type', blockData.type).data('function', blockData.function);
    
    // Set the background color
    $block.css('background-color', blockData.backgroundColor);
    
    // Set the block description and title
    $block.find('.block-title').text(blockData.type);
    $block.find('.block-description').text(blockData.description);

    // Append input buttons with labels
    blockData.input.forEach((input, index) => {
        let $inputContainer = createIOButton('input', input.name);
        $block.append($inputContainer);
    });

    // Append output buttons with labels
    blockData.output.forEach((output, index) => {
        let $outputContainer = createIOButton('output', output.name);
        $block.append($outputContainer);
    });
    
    // Create editable settings based on the block definition
    for (let setting in blockData.editableSettings) {
        let settingDef = blockData.editableSettings[setting];
        $block.find('.block-options').append(createEditableSetting(setting, settingDef));
    }

    return $block;
}


function createEditableSetting(name, settingDef) {
    let $setting;
    if (settingDef.type === 'select') {
        $setting = $('<select>').addClass('block-setting-select');
        settingDef.options.forEach(option => {
            $setting.append($('<option>').val(option).text(option));
        });
    } else if (settingDef.type === 'text') {
        $setting = $('<input>').attr('type', 'text').addClass('block-setting-text').val(settingDef.options);
    }

    return $('<div>').addClass('block-setting').append(
        $('<label>').text(name),
        $setting
    );
}

// Add an input or output button to the block
function createIOButton(name, type) {
    const $ioContainer = $('<div>').addClass('io-container ' + (type === 'input' ? 'io-input' : 'io-output'));
    const $button = $('<button>').addClass('io-button').data('name', name);
    const $label = $('<span>').addClass('io-label').text(name);
    
    $ioContainer.append($button);
    $ioContainer.append($label);
    return $ioContainer;
}

function placeBlockOntoCanvas(blockData) {
    const $block = createBlockElement(blockData); // createBlockElement similar to previous examples
    $block.css({
        position: 'absolute',
        left: '10px', // Starting position on the canvas
        top: '10px'
    });
    $block.draggable({ // Make the block draggable
        containment: '#pipeline-canvas'
    });
    $('#pipeline-canvas').append($block);
}

// Simulate fetching block data
$(document).ready(function() {
    if ($.ui) {
        console.log("jQuery UI is loaded");
    } else {
        console.log("jQuery UI is not loaded");
    }

    $.ajax({
        url: '/pipeline/getblocks',
        type: 'GET',
        success: function(data) {
            blocks = data;
            console.log(blocks);
            blocks.forEach(block => {
                const $blockTypeItem = $('<li>').text(block.type).data('block-data', block);
                $blockTypeItem.on('click', function() {
                    placeBlockOntoCanvas($(this).data('block-data'));
                });
                $('#block-types-list').append($blockTypeItem);
            });
        }
    });

    $('#pipeline-canvas').droppable({
        drop: function(event, ui) {
            $(this).append(ui.draggable);
        }
    });
});
