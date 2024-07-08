from aiplayground import llms, vectorialdataset, embeddings, aiaudio, imagesai

#################################################################################
########################## Block templates: #####################################
# The blocks will have the following structure to be displayed in the frontend:
# {
#     "type": "type of block",
#     "name": "default name",
#     "description": "default description",
#     "editableSettings": { The settings that can be edited by the user in the frontend }
#     "backgroundColor": "color in hexadecimal for the background of the block",
#     "input": [ The input parameters of the block ],
#     "output": [ The output parameters of the block ]
# }
#################################################################################
block = {
    "type": "",
    "name": "",
    "description": "",
    "editableSettings": {},
    "backgroundColor": "#ffffff",
    "input": "",
    "output": ""
}

# Return a JSON object with the block types and their parameters from the models of the other scripts:
def get_blocks():
    blocks = []
    blocks.append(generateTextBlock())
    blocks.append(generateLLMBlock())
    return blocks

def generateLLMBlock():
    optionsdata = ["N/A"]
    optionsdata.extend(vectorialdataset.get_group_names())
    
    block = {
        "type": "llm",
        "name": "Language Model",
        "description": "Answer a prompt with a language model.",
        "editableSettings": {
            "model": {
                "type": "select",
                "options": llms.get_models()
            },
            "data": {
                "type": "select",
                "options": optionsdata
            }
        },
        "backgroundColor": "#ffffff",
        "input": [
            {
                "type": "text",
                "name": "query"
            }
        ],
        "output": [
            {
                "type": "text",
                "name": "response"
            }
        ]
    }
    return block


def generateTextBlock():
    block = {
        "type": "text",
        "name": "Text",
        "description": "Editable text field.",
        "editableSettings": {
            "text": {
                "type": "text",
                "options": ""
            }
        },
        "backgroundColor": "#ffffff",
        "input": [],
        "output": [
            {
                "type": "text",
                "name": "text"
            }
        ]
    }

    return block


#################################################################################
########################### Blocks to Execution: ################################
# The pipeline blocks will have the following structure:
# {
#     "type": "type of block",
#     "options": {
#         ...
#     } 
# }
#################################################################################
def validate_blocks(blocks):
    # Check if the blocks are valid:
    for block in blocks:
        if block["type"] not in ["llm", "text"]:
            return False, "Invalid block type."
        
    return True, "Valid blocks."

def execute_blocks(blocks):
    for i in range(len(blocks) - 1):
        # Get the output of the first block:
        if i == 0:
            output, message = execute_block(blocks[i])
        # Get the output of the rest of the blocks:
        output, message = execute_block(blocks[i + 1], output)

    return output, message

def execute_block(block, input={}):
    if block["type"] == "llm":
        return execute_llm_block(block, input)
    elif block["type"] == "text":
        return execute_text_block(block, input)
    
    return {}, "Invalid block type."

def execute_llm_block(block, input={}):
    if "text" not in input:
        return {}, "Invalid input."
    


    # Get the settings:
    model = "gpt-4-1106-preview"
    dataSource = "N/A"
    if "model" in block["options"]:
        model = block["options"]["model"]

    if "data" in block["options"]:
        dataSource = block["options"]["data"]

    # Get the data from the database:
    data = []
    if dataSource != "N/A":
        embed_question = embeddings.get_embedding_question(input["text"])
        result = vectorialdataset.search_document(dataSource, embed_question)
        for r in result:
            data.append(r["text"])
    
    # Return the output:
    return {
        "text": llms.answer_prompt(input["query"], data, model)
    }, ""

def execute_text_block(block, input={}):
    # Get the settings:
    text = block["options"]["text"]
    
    # Return the output:
    return {
        "text": text
    }, ""