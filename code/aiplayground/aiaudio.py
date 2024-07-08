from openai import OpenAI
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_random_exponential

#################################################################################
################################ Audio to text ##################################
#################################################################################
models = {
    "whisper-1": "openai"
}

# Get list of supported models:
def get_audio_models():
    return list(models.keys())

# Other functions:
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=60))
def audio_to_text(audio, model="whisper-1", settings={}):
    response_text = ""
    if models[model] == "openai":
        response_text = audio_to_text_openai(audio, model, settings)
    return response_text

# Answer a prompt with OpenAI:
def audio_to_text_openai(audio, model, settings={}):
    # Initialize the OpenAI client:
    client_openai = OpenAI()

    # Make the request:
    transcript = client_openai.audio.transcriptions.create(
        model=model,
        file=audio,
    )

    response_text = transcript.text
    return response_text


#################################################################################
############################# Text to audio #####################################
#################################################################################
models_tts = {
    "tts-1": "openai"
}

# Get list of supported models:
def get_tts_models():
    return list(models_tts.keys())

# Other functions:
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=60))
def text_to_audio(text, model="tts-1", settings={}):
    audio_file = ""
    if models_tts[model] == "openai":
        audio_file = text_to_audio_openai(text, model, settings)
    return audio_file

# Answer a prompt with OpenAI:
def text_to_audio_openai(text, model, settings={}):
    # Initialize the OpenAI client:
    client_openai = OpenAI()
    speech_file_path = Path(__file__).parent / "speech.mp3"

    # Make the request:
    audio = client_openai.audio.speech.create(
        model=model,
        input=text
    )

    audio.stream_to_file(speech_file_path)
    return speech_file_path