from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import os.path

from _SourceCode import Constants

directory = os.path.join(Constants.resources_folder, 'facebook_bart_large_mnli')
# Load model and tokenizer from the saved directory
tokenizer = AutoTokenizer.from_pretrained(directory)
model = AutoModelForSequenceClassification.from_pretrained(directory)
classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

"""
Class for the zero shot model. The labels are given when calling the classify_entity function and
it returns one of the labels based on confidence.
"""


def classify_entity(entity_str, labels):
    result = classifier(entity_str, candidate_labels=labels, multi_label=True)
    if result['labels']:
        return result['labels'][0]  # Return the top classification
    else:
        return None
