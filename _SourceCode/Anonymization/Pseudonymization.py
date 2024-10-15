import os
import re

from dateutil import parser

from _SourceCode import Constants, WriteToFiles, HelperFunctions
from _SourceCode.AnnotationHelpers.AnnotationReplace import insert_into_annotations
from _SourceCode.Anonymization.pseudonymization_methods.Age_Pseudonymization import pseudonymize_age_labels
from _SourceCode.Anonymization.pseudonymization_methods.Date_Pseudonymization import pseudonymize_date_labels
from _SourceCode.Anonymization.pseudonymization_methods.Email_Pseudonymization import pseudonymize_email_labels
from _SourceCode.Anonymization.pseudonymization_methods.Height_Pseudonymization import pseudonymize_height_labels
from _SourceCode.Anonymization.pseudonymization_methods.ID_Pseudonymization import pseudonymize_id_labels
from _SourceCode.Anonymization.pseudonymization_methods.Location_Pseudonymization import pseudonymize_location_labels
from _SourceCode.Anonymization.pseudonymization_methods.NRP_Pseudonymization import pseudonymize_nrp_labels
from _SourceCode.Anonymization.pseudonymization_methods.Organization_Pseudonymization import \
    pseudonymize_organization_labels
from _SourceCode.Anonymization.pseudonymization_methods.Person_Pseudonymization import pseudonymize_person_labels
from _SourceCode.Anonymization.pseudonymization_methods.Phone_Number_Pseudonymization import \
    pseudonymize_phone_number_labels
from _SourceCode.Anonymization.pseudonymization_methods.SpelledOutItems_Pseudonymization import \
    pseudonymize_spelled_out_items_labels
from _SourceCode.Anonymization.pseudonymization_methods.Spelled_Name_Pseudonymization import \
    pseudonymize_spelled_names_labels
from _SourceCode.Anonymization.pseudonymization_methods.Time_Pseudonymization import pseudonymize_time_labels
from _SourceCode.Anonymization.pseudonymization_methods.URL_Pseudonymization import pseudonymize_url_labels
from _SourceCode.FileDataExtraction import TextExtraction
from _SourceCode.ToolsUtils import PresidioRecognizers

name_mapping = {}
org_mapping = {}
id_mapping = {}


def anonymize(output_directory, json_data):
    global name_mapping, org_mapping
    """
    Go through the hearing files in hearings_txt and pseudonymize
    the annotations data based on label.
    Pseudonymization is done by assigning acronyms to the annotations.
    For example: Person_X, Location_X,...
    with X being a number.
    Same person occurring again will have the same number assigned to them. 
    Same applies for all labels.
    """

    pseudonymization_index_folder = output_directory + '_INDEX'

    # Create output directory if it doesn't exit, otherwise clear it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    else:
        HelperFunctions.clear_directory(output_directory)

    # create index directory if it doesn't exist, otherwise clear it
    if not os.path.exists(pseudonymization_index_folder):
        os.makedirs(pseudonymization_index_folder)
    else:
        HelperFunctions.clear_directory(pseudonymization_index_folder)

    files_pseudonymized_index_map = {}

    print('---------PSEUDONYMIZATION started---------')

    for index, hearing_text_file in enumerate(os.listdir(Constants.hearings_txt_directory)):
        # reset the global maps
        name_mapping = {}
        org_mapping = {}

        if hearing_text_file.lower().endswith(Constants.text_format):

            # find the file and annotation data in the json file
            annotations = []
            annotations_json = [data for data in json_data if hearing_text_file == data['file']]
            if annotations_json:
                annotations = annotations_json[0]

            text = TextExtraction.extract_text_from_txt_file(hearing_text_file)
            if annotations:  # get annotation data for this file from the json

                print('\n')
                print(f'{index + 1} ----- Pseudonymizing {hearing_text_file}')
                annotations = _generate_annotation_replacements(index, annotations['annotations'],
                                                                hearing_text_file,
                                                                pseudonymization_index_folder)

                if text and annotations:
                    pseudonymized_file_name = _get_pseudonymized_file_name(
                        hearing_text_file.replace('.txt', '')) + f'_{index + 1}.txt'
                    files_pseudonymized_index_map[hearing_text_file] = pseudonymized_file_name

                    pseudonymized_text = _replace_in_text(annotations, text)

                    pseudonymized_text_output = os.path.join(output_directory, pseudonymized_file_name)

                    WriteToFiles.write_text_into_file(pseudonymized_text_output, pseudonymized_text)
                    print(index + 1, "----- [PSEUDONYMIZATION] ---", hearing_text_file, "➡", pseudonymized_file_name)
                else:
                    print(index + 1, "----- [PSEUDONYMIZATION] ---", hearing_text_file, " - Nothing to pseudonymize.")

    print('\n---------PSEUDONYMIZATION ended---------')

    # finally write an index file that shows the original file names and their pseudonymized names
    file_index_list = []
    for key, value in files_pseudonymized_index_map.items():
        file_index_list.append(f'{key} ➡ {value}')

    all_files_index_file = os.path.join(pseudonymization_index_folder, 'Index.txt')
    WriteToFiles.write_text_into_file(all_files_index_file, '\n'.join(file_index_list))


def _generate_annotation_replacements(loop_index, annotations, hearing_text_file, pseudonymization_index_folder):
    """
    Fill replacements for the annotations with pseudonymized data
    """

    # set the replacement in the main annotations list
    insert_into_annotations(
        annotations=annotations,
        names=pseudonymize_person_labels(annotations, name_mapping),
        spelled_names=pseudonymize_spelled_names_labels(annotations, name_mapping),
        organizations=pseudonymize_organization_labels(annotations, org_mapping),
        locations=pseudonymize_location_labels(annotations),
        urls=pseudonymize_url_labels(annotations),
        emails=pseudonymize_email_labels(annotations),
        nrps=pseudonymize_nrp_labels(annotations),
        dates=pseudonymize_date_labels(annotations),
        times=pseudonymize_time_labels(annotations),
        ids=pseudonymize_id_labels(annotations, id_mapping),
        ages=pseudonymize_age_labels(annotations),
        heights=pseudonymize_height_labels(annotations),
        phone_numbers=pseudonymize_phone_number_labels(annotations),
        spelled_out_items=pseudonymize_spelled_out_items_labels(annotations)
    )

    # Save in a folder called PSEUDONYMIZED_INDEX which contains
    # the original values and their pseudonymized values
    file = os.path.join(pseudonymization_index_folder,
                        hearing_text_file.replace(".txt", "_PSEUDONYMIZATION_INDEX.txt"))
    if not os.path.exists(pseudonymization_index_folder):
        os.makedirs(pseudonymization_index_folder)

    anonymizations = set([f'{ann.label} | {ann.preview}  ➡  {ann.replacement}'
                          for ann in annotations
                          ])

    if anonymizations:
        WriteToFiles.write_text_into_file(file, '\n'.join(anonymizations))
        print(loop_index + 1, "----- Index written in", file)
    return annotations


def _replace_in_text(annotations, text):
    """
    Replace the annotations with the 'replacement'
    """
    annotations.sort(key=lambda x: int(x.start), reverse=True)
    for ann in annotations:
        start = int(ann.start)
        end = int(ann.end)
        replacement = ann.replacement if ann.replacement else ann.preview
        text = text[:start] + replacement + text[end:]

    return text


def _get_pseudonymized_file_name(file_name):
    """
    Pseudonymize the file name by using the maps that we have so that the data in the file name
    is consistent with the content inside
    """

    file_name_parts = re.findall(Constants.split_string_pattern_for_file, file_name)

    id_changed = False
    simple_date_format = r'\d{4}-\d{1,2}-\d{1,2}'  # look for yyyy-mm-dd format

    for index, part in enumerate(file_name_parts):

        # conditions for if the current part is an ID
        is_id_conditions = [
            part.isalnum(),
            not part.isalpha(),
            _matches_patterns(part, PresidioRecognizers.IDRecognizer.patterns),
            not id_changed
        ]

        # Person name in the file name
        if part.isalpha() and not id_changed:
            # if pseudonymized name in map, use it. Otherwise write '[PERSON]' as placeholder
            if part in name_mapping:
                file_name_parts[index] = name_mapping[part]
            else:
                # see if the same name exists in the map under difference case
                different_case_map_key = [item for item in name_mapping.keys() if item.lower() == part.lower()]
                if different_case_map_key:
                    file_name_parts[index] = name_mapping[different_case_map_key[0]]
                else:
                    file_name_parts[index] = '[PERSON]'

        elif all(is_id_conditions):
            file_name_parts[index] = '[ID]'

        elif re.fullmatch(simple_date_format, part):
            # Generalize the date part
            file_name_parts[index] = "[DATE]"

    return ''.join(file_name_parts)


def _find_date_in_map(date_dict, target_date):
    """
    Look for a specific date inside the date_dict.
    Using the parser will help us look for the target_date under a different format

    """
    target_date = parser.parse(target_date).date()  # turn to date object
    for key, value in date_dict.items():
        try:
            key_date = parser.parse(key).date()
            value_date = parser.parse(value).date()

            # Compare dates to the target date
            if key_date == target_date:
                return value_date.strftime('%Y-%m-%d')
            if value_date == target_date:
                return value_date.strftime('%Y-%m-%d')
        except (ValueError, OverflowError):
            continue
    return None


def _matches_patterns(text, patterns):
    """
    get a list of regex patterns and see if the text matches one of them
    """
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False
