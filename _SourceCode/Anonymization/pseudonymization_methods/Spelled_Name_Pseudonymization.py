from _SourceCode import HelperFunctions, Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity


def pseudonymize_spelled_names_labels(annotations, name_mapping):
    """
    Filters the annotations to only hold the SPELLED_NAMES label.
    Spelled names are then pseudonymized and saved in a map so that if the same Spelled name value _is occurred more than once,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.
    The process is to look into name_mapping and then get the pseudonymized name then
    the pseudonymized value would be SPELLED_NAME_PERSON_ followed by the corresponding person's acronym.
    Example: SPELLED_NAME_PERSON_2 just means that this is the spelled name of Person_2
    the characters.
    Parameters:
        annotations (list): The list of Annotation items
        name_mapping (dict): The name dictionary with original name and their pseudonymized name
    Returns:
        List of NameEntity for Spelled names values with the 'replacement' variable filled.
    """

    spelled_names = list(
        set([item for item in annotations if item.label == Constants.LABEL_SPELLED_NAME]))
    spelled_names = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in spelled_names]

    for spelled_name in spelled_names:
        normal_name = HelperFunctions.clean_name(_normalized_name(spelled_name.name).title())
        if normal_name in name_mapping:
            pseudo_name = name_mapping[normal_name]
        else:
            pseudo_name = ""

        if not pseudo_name:  # if for some reason it's not in the name_mapping, don't proceed
            spelled_name.name_replacement = "[SPELLED_NAME]"  # it's still sensitive info so just add this as replacement
            continue

        spelled_pseudo_name = pseudo_name.lower().replace('person', 'SPELLED_NAME_PERSON')

        if spelled_pseudo_name.endswith('-'):
            spelled_pseudo_name = spelled_pseudo_name[:-1]

        spelled_name.name_replacement = spelled_pseudo_name

    return spelled_names


def _normalized_name(spelled_name):
    """
    Spelled names are spelled with dashes in between, so we just remove the dashes and reconstruct the name.
    Reconstruction is done keeping in mind that sometimes there are more than one name in one spelled name
    annotation

    Parameters:
        spelled_name (str): The spelled name

    Returns:
        str: the name after removing the dashes
    """
    parts = []  # sometimes a spelled name may actually contain more than 1 name in the same annotation
    part = ""
    expect_next_char = True  # flag to alternate between checking for characters and dashes -

    for char in spelled_name:
        if char.isalpha() and expect_next_char:
            part += char
            expect_next_char = False
        elif char == '-':
            expect_next_char = True
            continue
        elif char.isalpha():
            parts.append(part)
            part = char

    parts.append(part)
    return ' '.join(parts)
