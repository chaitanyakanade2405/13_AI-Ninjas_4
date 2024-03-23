from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
es = Elasticsearch()

# Elasticsearch index name
INDEX_NAME = 'notes_index'

# Function to create the Elasticsearch index
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)

# Route to render the upload form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        # Extract text from the uploaded file (you'll need to implement this)
        extracted_text = extract_text_from_file(file_path)

        # Index the extracted text in Elasticsearch
        es.index(index=INDEX_NAME, body={'text': extracted_text, 'filename': filename})

        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'No file uploaded'}), 400

# Route to handle search requests
@app.route('/search', methods=['GET'])
def search_notes():
    query = request.args.get('query')
    if query:
        search_results = es.search(index=INDEX_NAME, body={'query': {'match': {'text': query}}})
        hits = search_results['hits']['hits']
        return jsonify({'results': hits}), 200
    else:
        return jsonify({'error': 'No query provided'}), 400

if __name__ == '__main__':
    create_index()  # Create Elasticsearch index
    app.run(debug=True)
