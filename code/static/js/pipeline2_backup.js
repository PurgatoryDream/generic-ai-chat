let availableBlockTypes = [];
let tempConfig = {};

$(document).ready(function() {
    // Obtener los tipos de bloques del servidor
    $.getJSON('/pipeline/getblocks', function(blocks) {
        availableBlockTypes = blocks;
    });

    $('#save-config').click(function() {
        applyBlockConfiguration(tempConfig);
        $('#block-config-panel').css('transform', 'translateX(100%)');
    });

    $('#cancel-config').click(function() {
        $('#block-config-panel').css('transform', 'translateX(100%)');
    });
});

function addNewBlock() {
    if (availableBlockTypes.length === 0) {
        console.error("No block types available");
        return;
    }

    // Use the first available block type as the default type
    const defaultBlockType = availableBlockTypes[0].type;
    const blockId = 'block-' + Date.now();
    const $newBlock = $('<div>').addClass('block').attr('id', blockId).text(blockId + ' (' + defaultBlockType + ')');

    // Store the block type in the block's data
    $newBlock.attr('data-type', defaultBlockType);
    $newBlock.attr('data-text', "");
    $newBlock.click(function() {
        configureBlock(this);
    });

    $('#blocks-container').append($newBlock);
}

function configureBlock(blockElement) {
    const $block = $(blockElement);
    const blockId = $block.attr('id');
    const blockType = $block.attr('data-type');
    tempConfig = { id: blockId, type: blockType, name: '', settings: {} };

    // Get settings from all data attributes except for data-type
    var data = $block.data();
    var keys = $.map(data, function (value, key) {
        return key;
    });
    for (i = 0; i < keys.length; i++) {
        if (keys[i] !== 'type') {
            tempConfig.settings[keys[i]] = data[keys[i]];
        }
    }

    // Populate the config panel
    const $configPanel = $('#block-config-content');
    const $dynamicOptionsContainer = $('#dynamic-options-container').empty();
    
    // Block name input
    const $nameInput = $('<input>')
        .attr('type', 'text')
        .addClass('form-control mb-2')
        .val($block.text().split(' (')[0]) // Get current name
        .on('change', function() {
            tempConfig.name = $(this).val();
        });

    // Block type selector
    const $typeSelect = $('<select>').addClass('form-control mb-2');
    availableBlockTypes.forEach(function(availableblockType) {
        const $option = $('<option>').val(availableblockType.type).text(availableblockType.name);
        console.log(availableblockType.type, blockType);
        if (availableblockType.type == blockType) {
            $option.attr('selected', true);
        }
        $typeSelect.append($option);
    });
    $typeSelect.change(function() {
        tempConfig.type = $(this).val();
        updateConfigOptions($('#dynamic-options-container'), $(this).val(), true);
    })

    // Populate the dynamic options for the current type
    updateConfigOptions($dynamicOptionsContainer, tempConfig.type, false);
    $configPanel.empty()
        .append($('<div>').text('Nombre del Bloque:'), $nameInput)
        .append($('<div>').text('Tipo de Bloque:'), $typeSelect)
        .append($dynamicOptionsContainer);

    $('#block-config-panel').css('transform', 'translateX(0)');
}

function updateConfigOptions($container, blockType, changedType) {
    const blockData = availableBlockTypes.find(block => block.type === blockType);
    if (!blockData) return;

    $container.empty();
    tempConfig.settings = {};
    for (let setting in blockData.editableSettings) {
        let settingDef = blockData.editableSettings[setting];
        const $settingElement = createEditableSetting(setting, settingDef, changedType);
        $settingElement.find('input, select').change(function() {
            tempConfig.settings[setting] = $(this).val();
        });
        $container.append($settingElement);
    }
}

function createEditableSetting(name, settingDef, changedType) {
    const $settingContainer = $('<div>').addClass('mb-2');
    const $label = $('<label>').text(name);
    let $input;

    if (settingDef.type === 'select') {
        $input = $('<select>').addClass('form-control');
        settingDef.options.forEach(option => {
            if (option === settingDef[0]) {
                tempConfig.settings[name] = option;
            }
            $input.append($('<option>').val(option).text(option));
        });
    } else if (settingDef.type === 'text') {
        tempConfig.settings[name] = "";
        $input = $('<input>').attr('type', 'text').addClass('form-control').val(settingDef.options);
    }

    return $settingContainer.append($label).append($input);
}

function applyBlockConfiguration(config) {
    const $block = $('#' + config.id);

    // Update block name and type
    const blockName = config.name || config.id;
    $block.text(blockName + ' (' + config.type + ')');

    // Remove all data- attributes
    var data = $block.data();
    var keys = $.map(data, function (value, key) {
        return key;
    });
    for (i = 0; i < keys.length; i++) {
        $("div").removeAttr("data-" + keys[i]);
    }

    // Set new data- attributes
    $block.attr('data-type', config.type)
    $.each(config.settings, function(key, value) {
        $block.attr('data-' + key, value);
        $block.data(key, value);
    });
}