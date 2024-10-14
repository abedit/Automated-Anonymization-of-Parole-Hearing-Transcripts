import calendar
import re

from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity

time_regex = r'\d{1,2}[:;.]\d{2}'
ordinal_day_pattern = r'\b\d{1,2}(th|st|nd|rd)\b'
time_split_string_pattern = r'\d{1,2}[:;.]\d{2}|\b\d{1,2}/\d{1,2}/\d{4}\b|\w+|[^\w\s]|\s'
month_names = list(calendar.month_name)[1:]
months_pattern = r'\b(' + '|'.join(month_names) + r')'


def pseudonymize_time_labels(annotations):
    """
    Filters the annotations to only hold the TIME label.
    The process is to split each time value and go through the items one by one and pseudonymize them
    to keep the sentence structure
    TIME annotations are then pseudonymized by having the numerical values in the TIME annotation replaced
     with the placeholder [TIME]
    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for TIME values with the 'replacement' variable filled.
    """

    times = list(
        set([item for item in annotations if item.label == Constants.LABEL_TIME and item.preview]))
    times = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in times]

    for time_entity in times:
        split_string = [str(item) for item in re.findall(time_split_string_pattern, time_entity.name)]
        new_parts = []
        for part in split_string:
            is_part_time_conditions = [
                re.fullmatch(time_regex, part),  # if the part looks like a time XX:XX
                part.isdigit() and int(part) != 1,  # if it's a number
                re.fullmatch(ordinal_day_pattern, part),  # if it's an ordinal number like 1st, 2nd...
                re.fullmatch(months_pattern, part, re.IGNORECASE)  # if the current item is a month
            ]

            if any(is_part_time_conditions):
                pseudo_part = "[TIME]"
            else:
                pseudo_part = part

            new_parts.append(pseudo_part)

        # put the parts back together
        time_entity.name_replacement = ''.join(new_parts)

    return times
