from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

models = {
    "dall-e-3": "openai",
    "dall-e-2": "openai"
}

# Get list of supported models:
def get_image_models():
    return list(models.keys())

# Other functions:
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=60))
def text_to_image(text, model="dall-e-3", settings={}):
    image_url = ""
    if models[model] == "openai":
        image_url = text_to_image_openai(text, model, settings)
    return image_url

# Answer a prompt with OpenAI:
def text_to_image_openai(text, model, settings={}):
    # Initialize the OpenAI client:
    client_openai = OpenAI()

    # Make the request:
    image = client_openai.images.generate(
        model=model,
        prompt=text
    )

    image_url = image.data[0].url
    return image_url