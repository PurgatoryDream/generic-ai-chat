blockData = {};

document.addEventListener('DOMContentLoaded', function() {
    // Sample data for blocks and their settings
    const blockMenuContent = document.getElementById('blockMenuContent');

    function fetchBlocks() {
        fetch('/pipeline/getblocks')
            .then(response => response.json())
            .then(blocks => {
                blocks.forEach(block => {
                    blockData[block.type] = block;
                    const button = document.createElement('button');
                    button.classList.add('btn', 'btn-secondary', 'btn-block');
                    button.setAttribute('data-type', block.type);
                    button.textContent = block.name;
                    button.onclick = function() { addBlockToPipeline(block); };
                    blockMenuContent.appendChild(button);
                });
            })
            .catch(error => console.error('Error fetching blocks:', error));
    }

    // Selectors for different areas
    const blockMenu = document.querySelector('.block-menu');
    const pipelineArea = document.querySelector('.pipeline-area');
    const settingsArea = document.querySelector('.settings-area');

    // Function to add a block to the pipeline
    function addBlockToPipeline(blockType) {
        const block = document.createElement('div');
        block.classList.add('pipeline-block');
        block.textContent = blockData[blockType].name;
        block.setAttribute('data-type', blockType);
        pipelineArea.appendChild(block);

        // Event Listener for each block in the pipeline
        block.addEventListener('click', function() {
            displayBlockSettings(blockType);
        });
    }

    // Function to display settings for a block
    function displayBlockSettings(blockType) {
        const settings = blockData[blockType].editableSettings;
        settingsArea.innerHTML = `<h3>${blockData[blockType].name} Settings</h3>`;

        for (const key in settings) {
            const settingDiv = document.createElement('div');
            settingDiv.innerHTML = `<label>${key}:</label>`;

            if (Array.isArray(settings[key])) {
                // Dropdown for array-type settings
                const select = document.createElement('select');
                settings[key].forEach(option => {
                    const opt = document.createElement('option');
                    opt.value = option;
                    opt.textContent = option;
                    select.appendChild(opt);
                });
                settingDiv.appendChild(select);
            } else {
                // Text input for string-type settings
                const input = document.createElement('input');
                input.type = 'text';
                input.value = settings[key];
                settingDiv.appendChild(input);
            }

            settingsArea.appendChild(settingDiv);
        }
    }

    // Event Listeners for block menu buttons
    blockMenu.addEventListener('click', function(event) {
        if (event.target.tagName === 'BUTTON') {
            const blockType = event.target.getAttribute('data-type');
            addBlockToPipeline(blockType);
        }
    });

    fetchBlocks();
});