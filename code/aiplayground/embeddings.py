import tiktoken
import datetime
from tenacity import retry, stop_after_attempt, wait_random_exponential
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Check the length of a tokenized text:
def checkLength(text, embedding_encoding="cl100k_base"):
    tokenizer = tiktoken.get_encoding(embedding_encoding)
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

# Generate the text splitter:
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,
    length_function=checkLength,
    separators=["\n\n", "\n", " ", ""]
)

# Put the data from the transcripts into a data object:
def loadDataObject(filename, text, date=datetime.date.today().strftime("%B %d, %Y")):
    textChunks = splitter.split_text(text)
    data = []
    data.extend([{
        'filename': filename,
        'text': chunk,
        'date': date
    } for chunk in textChunks])
    return data

# Print the data object:
def printDataObject(data):
    print(f"Filename: {data['filename']}")
    print(f"Text: {data['text']}")
    print(f"Date: {data['date']}")
    print("\n")

# Get the embedding of a data object:
def get_embedding_data(data, model="text-embedding-ada-002"):
    text = data['text']
    text = text.replace("\n", " ")
    filename = ".".join(data["filename"].split(".")[:-1])
    input_text = " || ".join([filename, data["date"], text])
    
    # Get the embedding, waiting if it fails to avoid the rate limit:
    res = ""
    if model == "text-embedding-ada-002":
        res = get_embedding_data_openai(input_text, model)
    return res

# Get the embedding of a question:
def get_embedding_question(question, model="text-embedding-ada-002"):
    res = ""
    if model == "text-embedding-ada-002":
        res = get_embedding_data_openai(question, model)
    return res

# Get the embedding of a data text with OpenAI:
@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=60))
def get_embedding_data_openai(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    
    # Get the embedding, waiting if it fails to avoid the rate limit:
    client_openai = OpenAI()
    return client_openai.embeddings.create(input=[text], model=model).data[0].embedding
