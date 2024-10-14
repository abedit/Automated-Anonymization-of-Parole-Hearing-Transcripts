
from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity



def pseudonymize_phone_number_labels(annotations):
    """
    Filters the annotations to only hold the PHONE_NUMBER label.
    Phone numbers are then pseudonymized and saved in a map so that if the same PHONE_NUMBER value is occurred again,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.

    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for PHONE_NUMBER values with the 'replacement' variable filled.
    """
    phone_numbers = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in annotations if
                     item.label == Constants.LABEL_PHONE_NUMBER]
    phone_numbers_map = {}
    phone_number_count = 1

    for phone_number in phone_numbers:
        if phone_number.name.lower() not in phone_numbers_map:
            pseudo_phone = "PHONE_NUMBER_" + str(phone_number_count)
            phone_number_count += 1
            phone_numbers_map[phone_number.name.lower()] = pseudo_phone
        else:
            pseudo_phone = phone_numbers_map[phone_number.name.lower()]

        phone_number.name_replacement = '[' + pseudo_phone + ']'

    return phone_numbers
