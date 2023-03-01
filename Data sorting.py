import tkinter as tk
from tkinter import filedialog
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import onenote

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Define a function to extract and organize the data
def extract_data(text, categories=None):
    # Initialize an empty dictionary to store the data
    data = {}

    # Parse the text using spaCy
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

# Define a function to handle UI input
def handle_ui_input():
    # Create a Tkinter file dialog to choose a file to open
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    # If a file was selected, read the file and extract the data
    if file_path:
        with open(file_path, 'r') as f:
            text = f.read()

        # Extract the data
        data = extract_data(text)

        # Add the data to OneNote
        notebook_name = "My Notebook"
        section_name = "My Section"
        page_name = "My Page"
        on = onenote.OneNote()
        on.navigate_to(notebook_name=notebook_name, section_name=section_name, page_name=page_name)

        for category in data:
            on.create_page(notebook_name=notebook_name, section_name=section_name, page_name=category)
            for item in data[category]:
                on.add_page_content(notebook_name=notebook_name, section_name=section_name, page_name=category, content=item)

# Call the UI input function
handle_ui_input()
