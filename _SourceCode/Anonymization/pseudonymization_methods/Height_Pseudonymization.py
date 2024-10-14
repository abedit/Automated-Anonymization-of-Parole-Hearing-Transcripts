import re

from _SourceCode import HelperFunctions, Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity


def pseudonymize_height_labels(annotations):
    """
    Filters the annotations to only hold the HEIGHT label.
    Numerical values in HEIGHTs are replaced with the placeholder [HEIGHT]
    The full string is rebuild and filled inside the NameEntity's replacement variable.

    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for HEIGHT values with the 'replacement' variable filled.
    """

    heights = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in annotations if item.label == Constants.LABEL_HEIGHT]

    for height in heights:

        split_height = [str(HelperFunctions.word_to_number(item)) for item in
                        re.findall(Constants.split_string_pattern, height.name)]

        for index, part in enumerate(split_height):
            if part.isdigit():
                split_height[index] = "[HEIGHT]"

        height.name_replacement = ''.join(split_height)
    return heights
