from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import os.path

from _SourceCode import Constants

directory = "_Resources\\facebook_bart_large_mnli\\pytorch_model.bin"

if not os.path.exists(directory):
    print(f"\nThe BART model file was not found in the '_Resources\\facebook_bart_large_mnli'"
          f"directory.\n"
          f"The anonymization of the NRP and Location entities will use a generic label.\n")
    classifier = None
else:
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
    if classifier is None:
        return None

    result = classifier(entity_str, candidate_labels=labels, multi_label=True)
    if result['labels']:
        return result['labels'][0]  # Return the top classification
    else:
        return None
