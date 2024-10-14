import os
import re
import shutil
from datetime import datetime, timedelta

from word2number import w2n

from _SourceCode import Constants

split_string_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b|\w+|[^\w\s]'


def split_string(text):
    """
    Split a string thanks to regular expression
    """
    return [str(word_to_number(item)) for item in
            re.findall(split_string_pattern, text.replace('-', ' '))]


def replace_decade_words(text):
    # Mapping of decade words to their numeric representations
    decade_map = {
        'twenties': '20s',
        'thirties': '30s',
        'forties': '40s',
        'fifties': '50s',
        'sixties': '60s',
        'seventies': '70s',
        'eighties': '80s',
        'nineties': '90s'
    }

    # Create a regex pattern from the keys of the map
    # The pattern will look for whole words only to avoid partial matches
    pattern = r'\b(' + '|'.join(key for key in decade_map.keys()) + r')\b'

    if re.match(pattern, text.lower()) is None:
        return text
    else:
        match = re.match(pattern, text.lower()).group()
        return decade_map[match]


def word_to_number(text):
    """
    For numbers written in letter form, convert them to digits.

    Parameters:
        text (str): a string that has a number written like this: three, fourteen...

    Returns:
        str: return the string with the worded numbers converted to digits.
         In case the text doesn't have numbers in it, returns the string as it is.
    """

    pattern = Constants.worded_numbers_pattern

    def replace_match(match):
        # get the matched text
        word = match.group(0)
        try:
            # convert the matched word to a number
            converted_number = w2n.word_to_num(word)
            return str(converted_number)
        except (ValueError, IndexError):
            # else return the original word
            return word

    converted_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    return converted_text


def build_string(string_list):
    """
    Build a string from a string list
    """
    if not isinstance(string_list, list):
        return string_list

    output = ""
    for index, item in enumerate(string_list):
        output += space(string_list, index) + str(item)
    if output:
        return output
    else:
        ' '.join(string_list)


def space(string_list, index):
    """
    Function to manage spacing in strings based on punctuation

    Parameters:
        string_list (list): words and elements of a string in the form of a list.
        index (int): index in the list

    Returns:
        str: A space or empty string based on if the item before the current index is a number/character or if it has symbols.
    """
    item = string_list[index]
    symbols = ['\'', ',', '’', '?', '‘']  # numbers before these symbols should not have a space after them

    # if these symbols are present, there shouldn't be a space around the current item
    no_space_symbols = ['\\', '/', '.']
    if item in symbols or item in no_space_symbols or (index > 0 and str(string_list[index - 1]) in ['‘', '\'']):
        return ""

    if index > 0 and (str(string_list[index - 1]).isalnum() or str(string_list[index - 1]) in symbols):
        return " "
    return ""


def contains_keywords(text, key_words):
    """
    Takes a string and a list of strings
    Checks if that string is in any of the strings in the list
    """
    return any(word in text.lower() for word in key_words)


def clean_name(name):
    """
    Remove symbols in the name if it has them
    """
    cleaned_name = re.sub(r"’s|'s|’|'|\.|\?|!|>|<", "", name)
    cleaned_name = re.sub(r'\d', '', cleaned_name)
    # cleaned_name = re.sub(r'\b\s-\s*', ' ', cleaned_name)

    return cleaned_name.strip()


def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')



def time_difference(date1, date2):
    """
    Calculate the difference between two dates and returns elapsed time between these dates as string
    """

    delta = date2 - date1

    # Calculate the difference in days, hours, minutes and seconds
    seconds = int(delta.total_seconds() % 60)
    minutes = (delta.seconds // 60) % 60
    hours = delta.seconds//3600
    days = delta.days

    elapsed_time = f"Time elapsed: "

    if days > 0:
        elapsed_time += str(days) + ' ' + ('day' if days == 1 else 'days') + ', '
    if hours > 0:
        elapsed_time += str(hours) + ' ' + ('hour' if hours == 1 else 'hours') + ', '

    elapsed_time += f'{minutes} minutes, {seconds} seconds'
    elapsed_time = elapsed_time.strip()

    if elapsed_time.endswith(','):
        elapsed_time = elapsed_time[:-1]

    return elapsed_time


def month_to_number(month_name):
    """
    Convert month to number for datetime object
    """

    month_names = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    if month_name not in month_names:
        return month_name

    return month_names.get(month_name)