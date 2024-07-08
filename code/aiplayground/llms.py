from tenacity import retry, stop_after_attempt, wait_random_exponential
from openai import OpenAI
import vertexai
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel

# Map modelsc to their respective functions:
models = {
    "gpt-4-1106-preview": "openai",
    "text-bison@001": "vertexai"
}

# Get list of supported models:
def get_models():
    return list(models.keys())

# Other functions:
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=60))
def answer_prompt(query, data=[], model="gpt-4-1106-preview", settings={}):
    response_text = ""
    if models[model] == "openai":
        response_text = answer_prompt_openai(query, data, model, settings)
    elif models[model] == "vertexai":
        response_text = answer_prompt_vertex(query, data, model, settings)
    return response_text

# Answer a prompt with OpenAI:
def answer_prompt_openai(query, data, model, settings={}):
    # Initialize the OpenAI client:
    client_openai = OpenAI()
    messages = []

    # Introduce the context of the prompt:
    if len(data) > 0:
        messagePrompt = """You are an AI assistant. As an AI assistant, your objective is to help the user with their questions. 
                        You should only use the information provided here, from the first -----------------------------------
                        to the last -----------------------------------."""
        messagePrompt += "\n\n"
        messagePrompt += "-----------------------------------\n"
        for item in data:
            messagePrompt += item + "\n"
        messagePrompt += "\n-----------------------------------\n"
        messagePrompt += query
        messages.append({"role": "system", "content": messagePrompt})

    # Change the message depending on the role:
    if len(data) == 0:
        messages.append({"role": "user", "content": query})

    # Make the request:
    print(messages)
    response = client_openai.chat.completions.create(
        messages=messages,
        model=model
    )

    response_text = response.choices[0].message.content
    return response_text

# Answer a prompt with Google Vertex AI:
def answer_prompt_vertex(query, data, model, settings={}):
    vertexai.init(project="api-chat-playground", location="us-central1")
    parameters = {
        "temperature": 1.0,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40,
    }

    # Introduce the context of the prompt:
    messagePrompt = ""
    if len(data) > 0:
        messagePrompt = """You are an AI assistant. As an AI assistant, your objective is to help the user with their questions. 
                        You should only use the information provided here, from the first -----------------------------------
                        to the last -----------------------------------."""
        messagePrompt += "\n\n"
        messagePrompt += "-----------------------------------\n"
        for item in data:
            messagePrompt += item + "\n"
        messagePrompt += "\n-----------------------------------\n"
        messagePrompt += query

    # Change the message depending on the role:
    if len(data) == 0:
        messagePrompt = query

    # Initialize the model:
    modelgoogle = TextGenerationModel.from_pretrained(model)
    response = modelgoogle.predict(
        messagePrompt,
        **parameters
    )

    return response.text