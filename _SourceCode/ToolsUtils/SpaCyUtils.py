import calendar
import re

from word2number import w2n
import en_core_web_trf
import _SourceCode.Constants as Constants
from _SourceCode import HelperFunctions
from _SourceCode.AnnotationHelpers import AnnotationCleaner
from _SourceCode.AnnotationHelpers.AnnotationChecker import person_titles, is_invalid_annotation
from _SourceCode.AnnotationHelpers.AnnotationCleaner import remove_symbols_from_date
from _SourceCode.HelperFunctions import contains_keywords
from _SourceCode.ModelClasses.Annotation import Annotation
from _SourceCode.ToolsUtils.PresidioRecognizers import SpelledOutNamesRecognizer


def get_spacy_annotations(text):
    """
    Give a text and filtered-out annotations that are false
    """
    # Load the model from a local path
    # https://spacy.io/models/en#en_core_web_trf
    spacy_obj = en_core_web_trf.load(disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])
    doc = spacy_obj(text)
    annotations = convert_spacy_results_to_annotations(
        [ent for ent in doc.ents if ent.label_ in Constants.spacy_labels])
    return filter_spacy_results(annotations, text)


def filter_spacy_results(annotations, text):
    """
    Filter out annotations based on the label.
    Some labels have additional logic
    """
    filtered_results = []
    total_unfiltered_annotations = len(annotations)

    for ann in annotations:
        if is_invalid_annotation(ann):
            continue
        if ann.label == 'PERSON':
            if re.search(SpelledOutNamesRecognizer.pattern, ann.preview):
                continue
            AnnotationCleaner.remove_person_title(ann)
            if ann.preview.lower().endswith(' through interpreter'):
                size = len(' through interpreter')
                ann.preview = ann.preview[:len(ann.preview) - size]
                ann.end = ann.end - size
            ann.handle_suffixes()
            ann.handle_prefixes()

            if is_invalid_annotation(ann):
                continue

        if ann.label == 'DATE':
            if is_actually_time(ann.preview):
                ann.label = 'TIME'
            if is_actually_age(ann.preview) or check_if_age_begin_utterance(ann, text):
                ann.label = 'AGE'

        if ann.label == 'DATE':
            remove_symbols_from_date(ann)

        # only in the case of CARDINAL, check if it starts with ':' and ends with '.'
        # in case it doesn't satisfy this requirement then skip it
        if ann.label == 'CARDINAL':
            if check_if_age_begin_utterance(ann, text):
                ann.label = 'AGE'
            else:
                continue

        if ann.label == 'GPE':
            ann.label = 'LOCATION'

        if '\n' in ann.preview:
            split_text = ann.preview.split('\n')
            if len(split_text) == 2:
                text_before_new_line = split_text[0]
                text_after_new_line = split_text[1]
                ann.end = ann.end - len(text_after_new_line) - 1
                ann.preview = text_before_new_line
            else:
                continue

        if not ann.preview.strip() or ann.preview.strip() in person_titles or ann.start == ann.end:
            continue

        filtered_results.append(ann)

    false_annotations = list(set(annotations) - set(filtered_results))

    return filtered_results, false_annotations, total_unfiltered_annotations


def check_if_age_begin_utterance(ann, entire_text):
    """
    In some cases where the age comes from a text that looks like this
    Commissioner John: 18
    We have to make sure the number after ':' is a number that's not decimal.
    """
    if contains_keywords(ann.preview, ['.', ',']):
        return False
    # Get the index of the first \n before the annotation text and the first \n after.
    # Basically get the entire utterance
    last_newline_index = entire_text.rfind('\n', 0, ann.end)
    next_newline_index = entire_text.find('\n', last_newline_index + 1)
    if last_newline_index == -1 or next_newline_index == -1:
        return False
    line = entire_text[last_newline_index:next_newline_index]

    words_to_number = is_number_in_words(ann.preview)
    # since it's an utterance, it should look like this 'Inmate John: .....'
    if ':' in line:
        split_line = line.split(':')[1]
        distance = abs(line.find(ann.preview) - line.find(':')) - 1  # make sure the : is nearby
        valid_conditions = [
            ann.preview in split_line,
            split_line.strip().endswith('.') or split_line.strip().endswith('?'),
            distance <= 4,
            (ann.preview.isdigit() and len(ann.preview) < 4 and int(ann.preview) < 200) or
            (words_to_number != -1 and words_to_number < 200)
        ]
        return all(valid_conditions)

    return False


def is_actually_time(text):
    """
    We are only interested in time annotations that look like '12:00' or contains this
    """
    match = re.search(r'\d{1,2}:\d\d', text)
    if match:
        return True
    return False


def is_actually_age(text):
    """
    Checks if the date is actually an age value.
    For example a date that looks like "3 years ago" is actually a duration or age value which is something we need to keep
    but under the AGE label and not DATE
    """
    age_keywords = [
        'age', 'year', 'years', 'old', 'months', 'month', 'week', 'weeks',
        'over', 'about', 'day', 'days', 'next',
    ]
    invalid_age_keywords = [
        'for',
        'since',
        'the last', 'this',
        'summer', 'winter', 'autumn', 'fall', 'spring',
        'number',
    ]

    months = list(calendar.month_name)[1:]
    month_regex = r'\b(' + '|'.join(months) + r')\b'
    has_month = re.search(month_regex, text, re.IGNORECASE) is not None

    days = list(calendar.day_name)
    day_regex = r'\b(' + '|'.join(days) + r')\b'
    has_days_name = re.search(day_regex, text, re.IGNORECASE) is not None

    year_regex = r'\b\d{4}\b'
    has_age = re.search(r'\b\d{2}\b', text, re.IGNORECASE) is not None
    has_year = re.search(year_regex, text, re.IGNORECASE) is not None

    false_conditions = [
        has_month,  # check if it contains a month name
        has_days_name,
        has_year and not has_age,
    ]

    if any(false_conditions):
        return False

    has_number = re.search(r'\d', text) is not None
    number_in_words = [is_number_in_words(part) for part in text.split()]
    has_number_words = any(n != -1 for n in number_in_words)

    conditions = [
        contains_keywords(text, age_keywords) and not contains_keywords(text, invalid_age_keywords) and (
                has_number or has_number_words),
        text.isdigit() and len(text) == 2 and text[0] != '0',
        text.isdigit() and len(text) == 3 and text[0] != '0' and int(text) < 200,
        text.isdigit() and len(text) == 1,
        re.search(r'\d-\d/\d', text) is not None or re.search(r'\d \d/\d', text),
        '½' in text and text.replace('½', '').isdigit() and len(text.replace('½', '')) == 2,
        text.lower().endswith('ish') and text.lower().replace('ish', '').isdigit() and len(
            text.lower().replace('ish', '')) in [1, 2],
    ]

    if not any(conditions):
        split_string = [str(HelperFunctions.word_to_number(item)) for item in
                        re.findall(r'\w+|[^\w\s]', text)]
        written_age_conditions = [
            len(split_string) > 1,
            # for cases like 'three zero' --> '3 0'
            all(item.isdigit() for item in [str(temp) for temp in split_string if temp != ' ']),
            all(len(item) == 1 for item in [str(temp) for temp in split_string if temp != ' ']),
        ]
        if all(written_age_conditions):
            return True

    return any(conditions)


def convert_spacy_results_to_annotations(annotations):
    """
    Convert from SpaCy format to Annotation class
    """
    return [
        Annotation(
            start=item.start_char,
            end=item.end_char,
            label=item.label_,
            preview=item.text.strip(),
            source=Constants.SOURCE_SPACY) for item in annotations]


def is_number_in_words(text):
    try:
        # Attempt to convert the entire string to a number
        number = w2n.word_to_num(text)
        return number
    except (IndexError, ValueError):
        return -1
