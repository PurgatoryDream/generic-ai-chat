import json
import os
from transcription import transcriptmain as tr
from werkzeug.utils import secure_filename
from aiplayground import llms, vectorialdataset, embeddings, aiaudio, imagesai, pipeline
from tenacity import retry, stop_after_attempt, wait_random_exponential
from openai import OpenAI
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Initialize the Flask application:
app = Flask(__name__)
groups = []

# Configuration:
config = {
    "model" : "gpt-4-1106-preview",
}

# Load settings:
def load_theme():
    with open('settings/theme.json') as theme_file:
        return json.load(theme_file)
    
def save_theme(theme):
    with open('settings/theme.json', 'w') as theme_file:
        json.dump(theme, theme_file)

# Basic routes for the different pages:
@app.route('/')
def index():
    theme = load_theme()
    return render_template('chat.html', theme=theme)

@app.route('/documents')
def documents():
    theme = load_theme()
    groupsVect = vectorialdataset.get_groups()
    for groupVect in groupsVect:
        groupVect['files'] = vectorialdataset.get_filenames(groupVect['group_name'])
        groupVect['checked'] = groupVect['group_name'] in groups
    print(groups)
    print(groupsVect)
    return render_template('documents.html', theme=theme, groups=groupsVect)

@app.route('/settings')
def settings():
    theme = load_theme()
    models = llms.get_models()
    return render_template('settings.html', theme=theme, models=models, config=config)

@app.route('/transcribe')
def transcribe():
    theme = load_theme()
    return render_template('whisper.html', theme=theme)

@app.route('/images')
def images():
    theme = load_theme()
    return render_template('images.html', theme=theme)

@app.route('/pipeline')
def pipeline_page():
    theme = load_theme()
    return render_template('pipeline.html', theme=theme)

# Routes for handling requests:
@app.route('/chat', methods=['POST'])
def chat():
    # Get the message from the request:
    if request.method == 'POST':
        message = request.form['message']

        # If there's a group selected, get the data from it:
        data = []
        for group in groups:
            embed_question = embeddings.get_embedding_question(message)
            result = vectorialdataset.search_document(group, embed_question)
            for r in result:
                data.append(r["text"])

        response = llms.answer_prompt(message, data, config["model"])
        return response
    else:
        return redirect(url_for('index'))

# Create a new document group:
@app.route('/documents/creategroup', methods=['POST'])
def creategroup():
    # Get the message from the request:
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        vectorialdataset.create_group(name, description)
        return "Success!"
    else:
        return redirect(url_for('documents'))
    
# Upload a document to a group:
@app.route('/documents/upload', methods=['POST'])
def upload():
    # Get the message from the request:
    if request.method == 'POST':
        file = request.files.get('file')
        group_name = request.form['group_name']
        if not file:
            return jsonify({'error': 'No file provided'}), 400
    
        # If path to group doesn't exist, create it:
        filename = file.filename
        filename_secure = secure_filename(filename)
        if not os.path.exists(os.path.join('files', group_name)):
            os.makedirs(os.path.join('files', group_name))

        # Save the file:
        save_path = os.path.join('files', group_name, filename_secure)
        file.save(save_path)

        # Read the file and get the text:
        text = ""
        text = tr.transcript_file(save_path)
        if text == "File type not supported." or len(text) == 0:
            return jsonify({'error': 'File not supported.'}), 400
        else:
            # Upload the document to the group:
            data = embeddings.loadDataObject(filename, text)
            for d in data:
                embed_data = embeddings.get_embedding_data(d)
                vectorialdataset.upload_document(group_name, embed_data, text, filename_secure)
            return "Success!"
    else:
        return redirect(url_for('documents'))

# Select or deselect group:
@app.route('/documents/selectgroup', methods=['POST'])
def selectgroup():
    # Get the message from the request:
    if request.method == 'POST':
        group_name = request.form['group_name']
        is_checked = request.form['is_checked']
        if (group_name in groups):
            groups.remove(group_name)
        if (group_name not in groups) and is_checked == "true":
            groups.append(group_name)
        return jsonify({'checkres': groups, 'value' : is_checked }), 200
    else:
        return redirect(url_for('documents'))
    
# Settings updates:
@app.route('/settings/update-ui', methods=['POST'])
def settingsupdateui():
    # Get the message from the request:
    if request.method == 'POST':
        theme = {}
        for key in request.form:
            theme[key] = request.form[key]
        save_theme(theme)
        return "Success!"
    else:
        return redirect(url_for('settings'))
    
@app.route('/settings/update-model', methods=['POST'])
def settingsupdatemodel():
    # Get the message from the request:
    if request.method == 'POST':
        model = request.form['model']
        openai_apikey = request.form['openai_apikey']
        config["model"] = model

        # Save the OpenAI API key:
        if openai_apikey != "":
            config["openai_apikey"] = openai_apikey
            os.environ["OPENAI_API_KEY"] = openai_apikey

        # Save the Google App credentials:
        if not request.files.get('googleapp_creds', None):
            return "Success!"

        # If there is a file, save it:
        googleapp_creds = request.files["googleapp_creds"]
        config["googleapp_creds"] = googleapp_creds.filename
        save_path = os.path.join('settings', 'googleapp_creds.json')
        googleapp_creds.save(save_path)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = save_path

        return "Success!"
    else:
        return redirect(url_for('settings'))
    

# Get the blocks:
@app.route('/pipeline/getblocks', methods=['GET'])
def getblocks():
    blocks = pipeline.get_blocks()
    return jsonify(blocks)

# Execute pipeline of blocks:
@app.route('/pipeline/execute', methods=['POST'])
def executepipeline():
    # Get the message from the request:
    if request.method == 'POST':
        blocks = request.json
        valid, message = pipeline.validate_blocks(blocks)
        if valid:
            output, message = pipeline.execute_blocks(blocks)
            return jsonify(output)
        else:
            return jsonify(message)
    else:
        return redirect(url_for('pipeline'))

# Whisper:
@app.route('/transcribe/audio', methods = ['POST'])
def transcribe_audio_file():
   if request.method == 'POST':
      audio = request.files['file']
      filename = secure_filename(audio.filename)
      filename = os.path.join('recordings', filename) 
      audio.save(filename)
      file = open(os.path.join('.', filename), 'rb')
      transcript = aiaudio.audio_to_text(file, "whisper-1", {})
      os.remove(filename)
      return jsonify({"text": transcript})

@app.route('/transcribe/text', methods = ['POST'])
def extract_text_from_file():
   if request.method == 'POST':
      text_file = request.files['file']
      filename = secure_filename(text_file.filename)
      text_file.save(filename)
      text = tr.transcript_file(filename)
      os.remove(filename)
      return jsonify({"text": text})
   
# Image generation:
@app.route('/images/generate', methods = ['POST'])
def generate_image():
   if request.method == 'POST':
      text = request.form['text']
      image_url = imagesai.text_to_image(text, "dall-e-3", {})
      return jsonify({"image_url": image_url})
   

# Run the app:
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")