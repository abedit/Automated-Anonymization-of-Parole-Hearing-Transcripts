import re

from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity

id_count = 1  # the main count to add next to the ID_ part


def pseudonymize_id_labels(annotations, id_map):
    """
    Filters the annotations to only hold the ID label.
    IDs are then pseudonymized and saved in a map so that if the same ID value is occurred again,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.

    Parameters:
        annotations (list): The list of Annotation items
        id_map (dict): Map original IDs to their pseudonymized versions

    Returns:
        List of NameEntity for ID values with the 'replacement' variable filled.
    """
    global id_count
    id_count = 1
    ids = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in annotations if
           item.label == Constants.LABEL_ID]

    # IDs usually look like a letter or 2 followed by numbers
    digit_pattern = r'\d+'

    for id_entity in ids:
        pseudo_id = ""

        # get the number part of the ID and pseudonymize it
        numbers = re.findall(digit_pattern, id_entity.name)
        numbers = ''.join(numbers)

        if numbers:
            if numbers not in id_map:
                id_map[numbers] = _get_pseudo_value()
            pseudo_id += id_map[numbers]

        id_entity.name_replacement = '[' + pseudo_id + ']'

    return ids


def _get_pseudo_value():
    """
    Return a value under the form of ID_X with X being a counter.
    Increment the counter
    """
    global id_count

    pseudonymized_id = 'ID_' + str(id_count)
    id_count += 1
    return pseudonymized_id
