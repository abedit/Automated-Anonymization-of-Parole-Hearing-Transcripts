import re

from _SourceCode import HelperFunctions, Constants
from _SourceCode.AnnotationHelpers.AnnotationReplace import clean_name
from _SourceCode.ModelClasses.NameEntity import NameEntity

person_count = 1  # the main count to add next to the PERSON_ part


def pseudonymize_person_labels(annotations, name_mapping):
    """
    Takes person labels from annotations, pseudonymize their names each part of the names, stores the pseudonymized values in a map
    and returns the person annotations as NameEntity list with their replacement value filled.

    Parameters:
        annotations (list): List of annotations
        name_mapping (dict): Map original names to their pseudonymized versions

    Returns:
        list: List of updated NameEntity items with pseudonymized names
    """
    global person_count
    person_count = 1
    person_annotations = [item for item in annotations if
                          item.label == Constants.LABEL_PERSON and len(item.preview) > 1]

    person_annotations.sort(key=lambda x: int(x.start))

    for annotation in person_annotations:
        parts = re.findall(Constants.split_string_pattern, clean_name(annotation.preview))

        new_parts = []
        # Check if it's a cut off name.
        # If it's the case, check if it already exists in the map and use the already pseudonymized name for
        # the normal name
        cut_off_name_found = _handle_cut_off_name(clean_name(annotation.preview), new_parts, name_mapping)

        if not cut_off_name_found:
            new_parts = [_get_unique_name(original_name=part,
                                          name_mapping=name_mapping,
                                          is_full_name=False) for part in parts]

        # set the replacement, keeping in mind the casing
        annotation.replacement = ''.join(new_parts)

    combined_entities = [NameEntity(
        name=clean_name(name.preview).title(),
        all_caps=name.preview.isupper(),
        name_replacement=name.replacement,
        annotation_id=f"{name.start}|{name.end}"
    ) for name in person_annotations]

    return combined_entities

def _get_unique_name(original_name, name_mapping, is_full_name=False):
    """
    Replace the name given with a pseudonymized version, either from the map or create a new one

    Parameters:
        original_name (str): original name to be pseudonymized
        name_mapping (dict): map of original names and their pseudonymized versions
        is_full_name (bool): flag to know if the name_entities is from the full_names list or the other_names list

    Returns:
        str: newly generated pseudonymized name for the original_name given
    """

    if not is_full_name and not original_name.isalpha():
        return original_name

    if is_full_name:
        parts = re.findall(Constants.split_string_pattern, original_name)  # original_name.split()
        new_parts = []

        for part in parts:
            if not part.isalpha():
                new_parts.append(part)
                continue

            # Some names are detected with -- or - in them (not surrounded by letters)
            # in that case no need to anonymize
            # Same applies for words like 'unintelligible' in the middle of the name
            should_append_without_change = [
                part == '-',
                re.search(r'-+(?!\w)', part) is not None,
                HelperFunctions.contains_keywords(part, ['unintelligible', 'inaudible'])
            ]
            if any(should_append_without_change):
                if 'unintelligible' == part.lower():
                    new_parts.append('<unintelligible>')
                elif 'inaudible' == part.lower():
                    new_parts.append('<inaudible>')
                else:
                    new_parts.append(part.lower())
                continue

            part = part.title()
            # if the part is already in the map, use it
            if part in name_mapping:
                new_parts.append(name_mapping[part])
            else:
                # Otherwise generate new
                new_name = _get_pseudo_value()

                new_parts.append(new_name)
                name_mapping[part] = new_name
                name_mapping[f'{part[0].upper()}'] = f'{new_name.upper()}'

        return ''.join(new_parts)

    else:
        # Check if the name has already been generated and return it if it's the case
        original_name = original_name.title()
        if original_name in name_mapping:
            return name_mapping[original_name]
        else:
            # Generate a new unique name and make sure it's actually unique
            new_name = _get_pseudo_value()
            name_mapping[original_name] = new_name
            name_mapping[f'{original_name[0].upper()}'] = f'{new_name.upper()}'
            return new_name


def _handle_cut_off_name(name, new_parts, name_mapping):
    """
    Handle cut off names like: Hernan- (when the full name is Hernandez for example)

    Parameters:
        name (str): The name from the name parts list
        new_parts (list): in case it is a cut-off name, add the pseudonymized value to this list
        name_mapping (dict): name map of original name and their pseudonymized values

    Returns:
        bool: Returns true if the cut-off name has already a pseudonymized name in the map and was assigned to the
                new_parts list. Else, returns false.
    """

    if name.endswith('-'):
        pseudo_name = ""
        for key in name_mapping.keys():
            if name[:-1].title() in key:
                # It's a cut off name
                pseudo_name = name_mapping[key]
                break

        if pseudo_name:
            new_parts.append(pseudo_name)
            return True

    return False


def _get_pseudo_value():
    """
    Return a value under the form of PERSON_X with X being a counter.
    Increment the counter
    """

    global person_count

    pseudonymized_name = '[PERSON_' + str(person_count) + ']'
    person_count += 1
    return pseudonymized_name
