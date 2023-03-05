import tkinter as tk
from tkinter import filedialog
import onenote
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from flask import Flask, render_template, request

# Load the spacy model
nlp = spacy.load('en_core_web_sm')

# Define a function to extract and organize the data
def extract_data(text, categories=None):
    # Initialize an empty dictionary to store the data
    data = {}

    # Parse the text using spacy
    doc = nlp(text)

    # If categories were not specified, determine them automatically using Scikit-learn
    if categories is None:
        # Extract the entity text and label
        X = [ent.text.strip() for ent in doc.ents]

        # Use Scikit-learn to train a Naive Bayes classifier to predict the category
        vectorizer = CountVectorizer()
        X_train = vectorizer.fit_transform(X)
        y_train = [ent.label_ for ent in doc.ents]
        clf = MultinomialNB()
        clf.fit(X_train, y_train)

        # Use the trained classifier to predict the category of each entity
        categories = clf.predict(X_train)

    # Loop through the entities in the document
    for i, ent in enumerate(doc.ents):
        # Extract the entity text and label
        text = ent.text.strip()
        label = ent.label_

        # Add the item to the appropriate category
        category_label = categories[i]
        if category_label not in data:
            data[category_label] = []
        data[category_label].append(text)

    # Return the organized data
    return data

# # Define a function to create a OneNote notebook and section
def create_notebook(api_key, notebook_name, category_labels):
    # Create a OneNote client using the API key
    client = onenote.OneNoteClient(api_key)

    # Create a new notebook
    notebook = client.create_notebook(notebook_name)

    # Create a new section in the notebook
    section = client.create_section(notebook['id'], 'Section 1')

    # Create subpages for each category in the section
    category_ids = {}
    for label in category_labels:
        page = client.create_page(section['id'], label)
        category_ids[label] = page['id']

    # Return the notebook and category IDs
    return notebook['id'], category_ids

# Initialize the Flask application
# Initialize the Flask application
app = Flask(__name__)

# Define the home page route
@app.route('/')
def home():
    return render_template('home.html')

# Define the upload page route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']

        # Read the file and extract the data
        text = file.read().decode('utf-8')
        data = extract_data(text)

        # Create a new OneNote page for each category and append the items to the page
        api_key = 'YOUR_API_KEY'
        notebook_name = 'Entity Recognition Data'
        notebook_id, section_id = create_notebook(api_key, notebook_name, data.keys())
        for category, items in data.items():
            page_title = category
            page_content = '<ul>' + ''.join([f'<li>{item}</li>' for item in items]) + '</ul>'
            onenote.create_page(api_key, page_title, page_content, section_id[category])

        return 'Data uploaded successfully!'

    # If the request method is GET, show the upload form
    return render_template('upload.html')

if __name__ == '__main__':
    app.run()

