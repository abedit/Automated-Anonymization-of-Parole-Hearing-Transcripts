import calendar
import re
from datetime import datetime

from _SourceCode import HelperFunctions, Constants
from _SourceCode.Constants import split_string_pattern
from _SourceCode.ModelClasses.NameEntity import NameEntity

simple_date_pattern = (r'\d{1,2}\/\d{1,2}\/(?:\d{4}|\d{2})\b|'
                       r'\d{1,2}-\d{1,2}-(?:\d{4}|\d{2})\b|'
                       r'\d{1,2}\\\d{1,2}\\(?:\d{4}|\d{2})\b|'
                       r'\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2})\b')

month_names = list(calendar.month_name)[1:]
months_pattern = r'\b(' + '|'.join(month_names) + r')'

days_of_week_pattern = r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)s{0,1}\b'

ordinal_day_pattern = r'\b\d{1,2}(th|st|nd|rd)\b'
decade_pattern = r'\b\d0s\b'

def pseudonymize_date_labels(annotations):
    """
    Filters the annotations to only hold the DATE label.
    The process is to split each date value and go through the items one by one and replace with the
    appropriate placeholder to keep the sentence structure
    Every numerical value in the entity's value is replaced with a placeholder depending on the case of the value.
    Placeholders can be [DATE], [DAY_OF_WEEK], [YEAR]...
    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for DATE values with the 'replacement' variable filled.
    """

    date_entities = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in annotations if
                     item.label == Constants.LABEL_DATE]

    for date in date_entities:

        # if the entire annotation value is a date that looks like XX/XX/XXXX
        if bool(re.fullmatch(simple_date_pattern, date.name)):
            date.name_replacement = "[DATE]"
            continue

        # check if the following strings are included in the text
        # to know if we must convert words in the strings to numbers or not
        cut_off_numbers_conditions = [
            HelperFunctions.contains_keywords(date.name.lower(),
                                              ['thousand- ',
                                               'ninety- ',
                                               'nineteen eighty- ', 'seventy- ',
                                               'sixty- ', 'fifty- ', 'forty- ', 'thirty- ', 'twenty- ']),
        ]
        if all(cut_off_numbers_conditions):
            split_string = [str(item) for item in
                            re.findall(split_string_pattern, date.name)]
        else:
            split_string = [str(HelperFunctions.word_to_number(item)) for item in
                            re.findall(split_string_pattern, date.name)]

        # in case the original string has 'thousand' or nineteen in it
        if HelperFunctions.contains_keywords(date.name.lower(), ['thousand', 'nineteen']):
            handling_case = _handle_nineteen_thousand_date_case(date_name=date.name, split_string=split_string)
            if handling_case[0]:
                # Nothing to handle so no need to proceed with this item
                date.name_replacement = date.name
                continue
            elif handling_case[1]:
                split_string = handling_case[1]

        split_string = [HelperFunctions.replace_decade_words(item) for item in split_string]
        # copy of the list so we can modify it as we please
        copy_split_string = list(split_string)

        for index, item_in_string in enumerate(split_string):

            if item_in_string == ' ':
                continue

            # if it's a day (from 1 to 31), age or a year
            if bool(re.fullmatch(simple_date_pattern, item_in_string)):
                copy_split_string[index] = "[DATE]"
                continue

            # if current item is a number. Could be 1, 2 or 4 digits.
            elif item_in_string.isdigit():
                if len(item_in_string) == 4:
                    copy_split_string[index] = "[YEAR]"
                else:
                    copy_split_string[index] = "[NUMBER]"

            # if the current item is a month
            elif re.fullmatch(months_pattern, item_in_string, re.IGNORECASE):
                copy_split_string[index] = "[MONTH]"

            # if the current item is a day of the week
            elif re.search(days_of_week_pattern, item_in_string, re.IGNORECASE) is not None:
                copy_split_string[index] = "[DAY_OF_WEEK]"

            # match cases like 1st, 2nd, 3rd... For dates like December 25th, January 2nd...
            elif re.fullmatch(ordinal_day_pattern, item_in_string):
                copy_split_string[index] = "[DAY]"

            # if it's a decade 20s, 30s, 40s...
            elif re.fullmatch(decade_pattern, item_in_string):
                copy_split_string[index] = "[DECADE]"

        # convert all items to string and rebuild the string. Then fill the replacement value
        copy_split_string = [str(item) for item in copy_split_string]
        rebuilt_string = ''.join(copy_split_string)
        if rebuilt_string != date.name:
            date.name_replacement = ''.join(copy_split_string)

    return date_entities


def _handle_nineteen_thousand_date_case(date_name, split_string):
    """
    Handle scenarios like "In two thousand- 2015" or in 2 1000- 2015 (output thanks to word2number)
    In this case, we look if there are numbers in the string such as 1000 or 19.

    Parameters:
        date_name (str): the current date item
        split_string (list): List containing the items in date_name
        but separated (and cleaned depending on the if statement before this function call)
    Returns:
        (bool, list) the bool part determines if we should proceed with the loop where this function is called
        and the list is the new split screen that should be used in the original function
    """

    # Look for numbers under or equal 1000 --> year that needs to be built
    # (like two thousand five -> 2 1000 5 -> 2000 5 -> 2005)

    digit_list = [item for item in split_string if item.isdigit() and int(item) <= 1000]

    if not digit_list and not [item for item in split_string if item.isdigit()]:
        return True, []  # True means to skip the loop where this function is called

    start_index = 0
    end_index = len(split_string) - 1
    if digit_list:
        # retain the start index and end index of the items that we need to focus on in split_string
        for index, item in enumerate(split_string):
            if item == digit_list[0]:
                start_index = index
            elif item == digit_list[-1]:
                end_index = index

    full_year = 0
    # Start building the year
    if len(digit_list) >= 2:
        if digit_list[1] == '1000':
            # for years with 1000, it goes like this: two thousand five -> 2 1000 5 -> 2000 5 -> 2005
            full_year = int(digit_list[0]) * int(digit_list[1])
            if len(digit_list) >= 3 and int(digit_list[2]) < 100:
                full_year = full_year + int(digit_list[2])
        elif digit_list[0] == '19':
            # for years with 19, it goes like this:
            # nineteen eighty five -> 19(*100) 80 5 -> 1980 5 -> 1985
            full_year = (int(digit_list[0]) * 100) + int(digit_list[1])
            if len(digit_list) >= 3 and full_year + int(digit_list[2]) < (datetime.now().year + 10):
                full_year = full_year + int(digit_list[2])

    # in case the final year output is 2000, it's a special value and so we don't generate new year for this
    if full_year == 2000 or ((full_year == 0 or len(str(full_year)) != 4) and any(
            item.isdigit() and len(item) == 4 for item in split_string)):
        # false means not to stop the loop and to override split_string's value
        return False, [item for item in re.findall(split_string_pattern, date_name)]
    elif full_year == 0 or len(str(full_year)) != 4:
        return True, []
    else:
        full_false_year = ""
        skip_until_end_index = False

        # put together the final string using the start_index and end_index.
        # In case there are more data around the year string, we need those as well.
        for index, item in enumerate(split_string):
            if skip_until_end_index:
                continue

            if index < start_index:
                full_false_year += str(item)
            else:
                full_false_year += str(full_year)
                skip_until_end_index = True  # stop the loop

        full_false_year += ''.join(split_string[end_index + 1:])
        return False, [item for item in re.findall(split_string_pattern, full_false_year)]



