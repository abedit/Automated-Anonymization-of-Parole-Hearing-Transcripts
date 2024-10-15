import os

from _SourceCode import Constants
from _SourceCode.Anonymization import Pseudonymization
from _SourceCode.JsonFunctions import get_data_from_annotation_json
from _SourceCode.ModelClasses.Annotation import Annotation


def anonymization_entry_point():
    """
    Entry point for anonymization 
    """

    # Get the json file and the data inside of it
    json_file = os.path.join(Constants.output_json_directory, Constants.output_json_file)

    if not os.path.exists(json_file):
        print(f'The file {json_file} does not exist. Please run GatherAnnotations.py.')
        return

    json_data = convert_dict_to_annotation(get_data_from_annotation_json())

    if json_data is None:
        print(f'The file {json_file} does not have any data. Cannot proceed.')
        return

    output_directory = Constants.output_anonymization + Constants.PSEUDONYMIZATION
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Call the appropriate Pseudonymization method
    Pseudonymization.anonymize(output_directory, json_data)


def convert_dict_to_annotation(json_data):
    """
    Convert json data to Annotation data and return it as list of Annotation data with the file name
    """
    output = []

    for data in json_data:
        file = data['file'] + Constants.text_format
        annotations_dict = data['annotations']
        annotations_list = [Annotation(
            start=item['start'],
            end=item['end'],
            label=item['label'],
            preview=item['preview'],
            source=item['source']) for item in annotations_dict]

        output.append({
            'file': file,
            'annotations': annotations_list
        })
    return output
