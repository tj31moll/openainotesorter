import tkinter as tk
from tkinter import filedialog
import spacy
import cleanlab

# Load the spacy model
nlp = spacy.load('en_core_web_sm')

# Define a function to extract and organize the data
def extract_data(text, categories=None):
    # Initialize an empty dictionary to store the data
    data = {}

    # Parse the text using spacy
    doc = nlp(text)

    # If categories were not specified, determine them automatically using cleanlab
    if categories is None:
        # Use cleanlab to get the best categories based on the predicted labels
        true_labels = [ent.label_ for ent in doc.ents]
        confident_joint = cleanlab.latent_estimation.estimate_joint(
            true_labels=true_labels, 
            predicted_labels=true_labels, 
            psx=None, 
            confident_joint=None, 
            calibrate=False, 
            verbose=False
        )
        categories = cleanlab.latent_estimation.estimate_latent(
            confident_joint=confident_joint, 
            n_classes=len(set(true_labels))
        )

    # Loop through the entities in the document
    for ent in doc.ents:
        # Extract the entity text and label
        text = ent.text.strip()
        label = ent.label_

        # Determine the appropriate category for the entity
        for category in categories:
            if category.lower() in label.lower():
                category_label = category
                break
        else:
            # If the label doesn't match any category, skip this entity
            continue

        # Add the item to the appropriate category
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

        # Extract the data and print it to the console
        data = extract_data(text)
        print(data)


# Call the UI input function
handle_ui_input()
