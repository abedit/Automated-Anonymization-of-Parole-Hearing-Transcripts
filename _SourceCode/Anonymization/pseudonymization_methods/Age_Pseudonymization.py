import re

from _SourceCode import HelperFunctions, Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity

"""
This is a class that holds the functions for the pseudonymization anonymization technique, namely for the AGE label.
"""
split_string_pattern = r'(\w+|[^\w\s]|\s)'
approximate_age_pattern = r'\b\d{1,2}ish\b'


def pseudonymize_age_labels(annotations):
    """
    Filters the annotations to only hold the AGE label.
    The numerical values in the annotations are replaced with "[AGE]
    The pseudonymized values are then filled inside NameEntity's replacement variable.

    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for AGE values with the 'replacement' variable filled.
    """

    name_entity_ages = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in annotations if
                        item.label == Constants.LABEL_AGE]

    # Next generate replacements for the age values
    for age in name_entity_ages:

        # Special case for 'one day'. If that's present in the original string, keep it.
        # Because most of the time it's not used as duration but rather like "one day you'll be able to..."
        # so it wouldn't make sense to anonymize it and end up with "[AGE] day you'll be able to..."
        if 'one day' in age.name.lower() or age.name.lower().endswith('or two'):
            age.name_replacement = age.name
            continue

        # if there are numbers written in words in the age value, convert them to digits
        age_value_worded_numbers = HelperFunctions.word_to_number(age.name)

        # Generate replacement value(s)
        pseudo_age = _get_pseudonymized_age(age_value_worded_numbers=age_value_worded_numbers)
        age.name_replacement = pseudo_age

    return name_entity_ages


def _get_pseudonymized_age(age_value_worded_numbers):
    """
    Takes the age value from the annotation with the numbers converted to digit form and
    outputs the same age annotation value but with the numbers replaced with "[AGE]",
    keeping the same sentence structure.

    Parameters:
        age_value_worded_numbers (str): age annotation string with the numbers in it in digit form
    Returns:
        Returns the age annotation string but with the numbers replaced with "[AGE]"
    """
    string_parts = [HelperFunctions.word_to_number(item) for item in
                    re.findall(split_string_pattern, age_value_worded_numbers)]

    for part, item in enumerate(string_parts):

        # if the current item in the string is a digit, replace it with the label type
        if item.isdigit() or re.search(approximate_age_pattern, item, re.IGNORECASE):
            string_parts[part] = "[AGE]"

        # for ordinal numbers, they're neither digits or alphabetic but rather both.
        # in such cases, they must be pseudonymized
        elif not item.isdigit() and not item.isalpha() and item.isalnum():
            has_ordinal_conditions = ['st' in item, 'nd' in item, 'rd' in item, 'th' in item]
            if any(has_ordinal_conditions):
                string_parts[part] = "[AGE]"

    return ''.join(string_parts).strip()
