import re

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

from _SourceCode.AnnotationHelpers import AnnotationCleaner
import _SourceCode.FileDataExtraction.FirstPageNamesExtraction as FirstPageNamesExtraction
from _SourceCode.AnnotationHelpers.AnnotationCleaner import remove_symbols_from_date
import _SourceCode.Constants as Constants
import _SourceCode.ToolsUtils.PresidioRecognizers as PresidioRecognizers
from _SourceCode.HelperFunctions import contains_keywords
from _SourceCode.ModelClasses.Annotation import Annotation
from _SourceCode.AnnotationHelpers.AnnotationChecker import is_invalid_annotation


def get_presidio_analysis_results(text, skip_1st_page_info_presidio):
    """
    Instantiate Presidio recognizers and call presidio to analyze the text
    """
    recognizer_registry = RecognizerRegistry()
    recognizer_registry.load_predefined_recognizers()

    # Add the other recognizers
    recognizer_registry.add_recognizer(PresidioRecognizers.IDRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.AgeRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.SpelledOutNamesRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.SimpleDateRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.SimpleTimeRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.SimpleHeightRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.SpelledOutItemRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.FacilityRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.SimpleURLRecognizer())
    recognizer_registry.add_recognizer(PresidioRecognizers.SimplePhoneNumberRecognizer())

    # Add the first name recognizer patterns from the first page
    if not skip_1st_page_info_presidio:
        name_recognizers, location_recognizer, organization_recognizer = get_first_page_recognizers(text)
        if name_recognizers is not None:
            recognizer_registry.add_recognizer(name_recognizers)
        if organization_recognizer is not None:
            recognizer_registry.add_recognizer(organization_recognizer)
        if location_recognizer is not None:
            recognizer_registry.add_recognizer(location_recognizer)

    analyzer = AnalyzerEngine(registry=recognizer_registry)

    results = analyzer.analyze(
        text=text,
        entities=Constants.presidio_labels,
        score_threshold=0.85,
        language='en'
    )
    total_unfiltered_annotations = len(results)
    converted = convert_presidio_results_to_annotations(text, results)
    presidio_results = clean_presidio_results(converted, text)
    return converted, presidio_results, total_unfiltered_annotations


def get_presidio_annotations(text, skip_1st_page_info_presidio):
    """
    get presidio annotations and merge adjacent annotations
    if they are next to each other and have the same label
    """
    original_results, presidio_results, total_unfiltered_annotations = get_presidio_analysis_results(text, skip_1st_page_info_presidio)
    merged_annotations = AnnotationCleaner.merge_adjacent_annotations(presidio_results, text)
    false_annotations = list(set(original_results) - set(merged_annotations))
    return merged_annotations, false_annotations, total_unfiltered_annotations


def convert_presidio_results_to_annotations(text, presidio_results):
    """
    convert Presidio result to Annotation
    """
    return [
        Annotation(
            start=item.start,
            end=item.end,
            label=item.entity_type,
            preview=text[item.start:item.end].strip(),
            source=Constants.SOURCE_PRESIDIO) for item in presidio_results]


def get_first_page_recognizers(text):
    """
    The entire text is a string. The first page text and the main pdf text are separated by 3 new lines \n
    Return list of names present in the first page and organization name (facility where inmate is held).
    Additionally, the location where the hearing is held
    """
    if not text:
        return None

    first_page_text = ''
    split_text = text.split('\n')
    for index, item in enumerate(split_text):
        if item.strip() == '' and split_text[index + 1].strip() == item.strip():
            first_page_text = '\n'.join(split_text[:index])
            break

    # Add recognizer for the names in the first page
    first_page_names, location_line, organization = FirstPageNamesExtraction.get_names_from_first_page(first_page_text)
    name_recognizers = PresidioRecognizers.get_names_recognizer(names=first_page_names)

    if organization is not None and organization:
        organization_recognizer = PresidioRecognizers.get_organization_recognizer(name=organization)
    else:
        organization_recognizer = None

    if location_line is not None and location_line:
        location_recognizer = PresidioRecognizers.get_location_recognizer(location_line=location_line)
    else:
        location_recognizer = None

    return name_recognizers, location_recognizer, organization_recognizer


def clean_presidio_results(annotations, text):
    """
    filter out presidio results as needed depending on each label
    """
    filtered_results = []
    annotations.sort(key=lambda x: x.start)

    person_names = set()
    for ann in annotations:
        if contains_keywords(ann.preview, ['victim']) or ann.preview in ['DVI', 'DECS']:
            continue  # Skip this result

        if ann.label == Constants.LABEL_SPELLED_NAME:
            if is_invalid_annotation(ann):
                continue
            letters = [letter for letter in ann.preview if letter.isalpha()]
            if len(set(letters)) == 1:  # Example someone stuttering: I-I-I (repeating the same letter)
                continue

        if ann.label == Constants.LABEL_PERSON:
            if is_invalid_annotation(ann) or text[ann.end].isalpha() or text[ann.start - 1].isalpha():
                # 2nd and 3rd checks are for in case the annotation is in the middle of a word
                continue
            ann.handle_prefixes()
            ann.handle_suffixes()
            if '\n' in ann.preview:
                text_after_new_line = ann.preview.split('\n')[1]
                ann.end = ann.end - len(text_after_new_line) - 1
                ann.preview = ann.preview.split('\n')[0]

            ann.handle_spelled_name_in_person_name()

            # Very specific case. Sometimes the person's name is written like so I.CARDOZA.
            # Presidio already detects CARDOZA but not the 'I.' part.
            # We check if there's a space before it to make sure it's not words stuck with a period in between
            if text[ann.start - 1] == '.' and text[ann.start - 2].isalpha() and text[ann.start - 3] == ' ':
                ann.start = ann.start - 2
                ann.preview = text[ann.start:ann.end]
            clean_person_annotation(ann, person_names)

        if ann.label != Constants.LABEL_SPELLED_OUT_ITEM:
            # Remove certain prefixes and suffixes (unless it's a spelled_out_item then don't do that)
            ann.handle_prefixes()
            ann.handle_suffixes()

        if ann.label == Constants.LABEL_DATE:
            fix_date_annotation(ann, ann.preview)
            if ann.preview.lower().startswith('from'):
                ann.preview = ann.preview.replace('from', '').replace('From', '')
                ann.start = ann.start + 4
            remove_symbols_from_date(ann)
            # Sometimes Presidio detects years (2001, 2002..) but the different start and end index is not 4 characters long
            if len(ann.preview) == 4 and ann.end - ann.start == 5:
                ann.start = ann.start + 1

        if ann.label == Constants.LABEL_LOCATION:
            if is_invalid_annotation(ann):
                continue
            if ann.preview.lower() in person_names:
                ann.label = Constants.LABEL_PERSON

        if ann.label == Constants.LABEL_AGE:
            fix_age_annotation(ann, ann.preview)

        conditions = [
            ann.start == ann.end,
            ann.label == Constants.LABEL_NRP and is_invalid_annotation(ann)
        ]

        if ann.label == Constants.LABEL_URL:
            if is_invalid_annotation(ann):
                continue
            if ann.preview.endswith('.') or ann.preview.endswith('?'):
                ann.preview = ann.preview[:-1]
                ann.end = ann.end - 1

        if any(conditions):
            continue

        if not ann.preview.strip() or ann.start == ann.end:
            continue

        filtered_results.append(ann)

    return filtered_results


def clean_person_annotation(ann, person_names):
    """
    Logic for some PERSON annotations
    if the annotation is equal to 'California' then it's a location
    if it ends with ':' then remove it and adjust the annotation object
    if it has 'through interpreter', remove it and adjust the annotation
    """
    if ann.preview.lower() == 'california':
        ann.label = Constants.LABEL_LOCATION
    if ':' in ann.preview:
        name = ann.preview.split(':')[0]
        ann.end -= len(ann.preview) - len(name)
        ann.preview = name
    if ann.preview.lower().endswith(' through interpreter'):
        size = len(' through interpreter')
        ann.preview = ann.preview[:-size]
        ann.end -= size

    AnnotationCleaner.remove_person_title(ann)

    person_names.add(ann.preview.lower())
    person_names.update(ann.preview.lower().split())


def fix_age_annotation(result, text):
    """
    AgeRecognizer has a pattern that detects ages based on specific words before the number.
    It detects those words as well so we have to remove them from the final result
    """
    matches = re.search(PresidioRecognizers.AgeRecognizer.pattern_w_words, text)
    if matches and len(text.split()) >= 2:
        space_count = len(result.preview[len(text.split()[0]):]) - len(result.preview[len(text.split()[0]):].lstrip())
        result.start = result.start + len(text.split()[0]) + space_count
        result.preview = result.preview[len(text.split()[0]) + space_count:]

        if text.endswith(('.', '?', ',')):
            result.end = result.end - 1
            result.preview = result.preview[:-1]
        return
    elif text.startswith(': '):
        result.start = result.start + 2
        result.preview = result.preview[2:]
    if text.endswith(('.', '?', ',')):
        result.end = result.end - 1
        result.preview = result.preview[:-1]


def fix_date_annotation(result, text):
    """
    Fixes date annotation caught from the SimpleDateRecognizer
    """
    matches_2 = re.search(PresidioRecognizers.SimpleDateRecognizer.year_in_sentence_pattern, text)
    if matches_2:
        result.start = result.start + len(matches_2[1]) + 1  # remove the prepositions in the beginning
