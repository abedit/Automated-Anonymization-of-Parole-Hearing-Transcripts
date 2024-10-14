import os
import json
import shutil

from _SourceCode import Constants, HelperFunctions


def get_data_from_annotation_json():
    """
    Get data from the annotation output json file
    """
    file_path = os.path.join(Constants.output_json_directory, Constants.output_json_file)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data



def write_data_to_json(data):
    """
    Write the data into a json file
    """
    directory = Constants.output_json_directory
    output_file_path = os.path.join(Constants.output_json_directory, Constants.output_json_file)

    if not os.path.exists(directory):
        os.makedirs(directory)
        data = [data]
    else:
        json_file_path = os.path.join(directory, Constants.output_json_file)
        if os.path.exists(json_file_path):  # if file exists, append the data to the already existing file
            data = _update_json_data(json_file_path, data)
        else:  # otherwise, clear the directory for a new json file
            HelperFunctions.clear_directory(directory)
            data = [data]

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def _update_json_data(json_file_path, new_data_dict):
    """
    Update the JSON file by appending new data or replacing annotations for existing files.
    """

    if os.path.exists(json_file_path): # Check if the file exists
        with open(json_file_path, 'r', encoding='utf-8') as f:
            current_json_data = json.load(f)  # get data from the JSON file
    else:
        # If the file doesn't exist, start with an empty list
        current_json_data = []

    file_found = False  # check if the file is already in the JSON data
    new_file_name = new_data_dict['file']

    # Go through the existing data to find if the file already exists
    for entry in current_json_data:
        if entry['file'] == new_file_name:
            # If the file exists, replace the annotations
            entry['annotations'] = new_data_dict['annotations']
            file_found = True
            break

    if not file_found:  # file in json not found, append the new data
        current_json_data.append(new_data_dict)

    return current_json_data
