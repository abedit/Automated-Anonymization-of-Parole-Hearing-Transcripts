import re

from presidio_analyzer import Pattern, PatternRecognizer

from _SourceCode.FileDataExtraction.TextExtraction import generate_name_combinations


def get_names_recognizer(names):
    """
    Returns recognizers for names, name combinations and cut off names
    """

    if not names:
        return None

    extracted_names = []
    name_combinations = generate_name_combinations(names)
    extracted_names.extend(name_combinations)
    cut_off_names = (get_cutoff_names(name_combinations))

    # filter out 2 lettered names or occurrence where if the parts of name separated by space have the same length
    extracted_names = [item for item in extracted_names if len(item) > 2]

    name_patterns = [Pattern(f'exact_{name.replace(" ", "_")}', rf'\b{name}\b', 1.0) for name in extracted_names]
    name_patterns.extend(
        [Pattern(f'exact_{name.title().replace(" ", "_")}', rf'\b{name.title()}\b', 1.0) for name in extracted_names])
    name_patterns.extend(
        [Pattern(f'exact_{name.replace(" ", "_")}', rf'\b{name}[\b]?', 0.85) for name in cut_off_names])

    if not name_patterns:
        return None

    return PatternRecognizer("PERSON", patterns=name_patterns, context=['person', 'people', 'name', 'inmate'])


def get_organization_recognizer(name):
    """
    Returns simple recognizer for specific organization names with the name parameter being from the
    first page
    """
    other_organizations = [
        'Crip', 'Crips', 'Fresno Bulldog', 'Fresno',
    ]
    pattern = Pattern(f'exact_{name.replace(" ", "_")}', rf'\b{name}\b', 0.85)
    patterns = [pattern]
    patterns.extend([Pattern(f'exact_{item.replace(" ", "_")}', rf'\b{item}\b', 0.85) for item in other_organizations])
    return PatternRecognizer("ORGANIZATION", patterns=patterns,
                             context=['facility', 'prison', 'jail', 'detention', 'correctional', 'rehabilitation'])

def get_location_recognizer(location_line):
    """
    Returns simple recognizer for specific location values from the first page
    """
    if ',' in location_line:
        location = location_line.split(',')
    else:
        location = [location_line]

    patterns = []
    for index, item in enumerate(location):
        patterns.append(Pattern(f'exact_{item.strip().title().replace(" ","_")}_{index}', rf'\b{item.strip().title()}\b', 0.85))

    return PatternRecognizer("LOCATION", patterns=patterns)


def get_cutoff_names(names):
    """
    This function servers to get a list of names with the names being cut off at a certain index
    This is in case the name of someone was uttered but was cut off in the middle.
    """
    cut_off_index = 3
    cut_off_names = []
    for name in names:
        if len(name) > cut_off_index:
            for i in range(cut_off_index + 1, len(name) + 1):
                cut_off_names.append(f'{name[:i]}-')
        else:
            cut_off_names.append(name)
    return cut_off_names


class IDRecognizer(PatternRecognizer):
    """
    Simple ID patterns like 12345 or AB1234
    """
    patterns = [
        r'\b[A-Z]{0,4}\d{5,10}\b',
        r'\b[A-Z]{1,4}\d{4,10}\b',
        r'\b[A-Z]{1,4}\d{2,5}-(?!\d)' # For cut-off IDs
    ]

    def __init__(self):
        id_patterns = []

        for index, pattern in enumerate(IDRecognizer.patterns):
            id_patterns.append(Pattern(name=f'ID_{index}', regex=pattern, score=0.85))

        super().__init__(supported_entity="ID", patterns=id_patterns)


class AgeRecognizer(PatternRecognizer):
    """
    Age after a space and ends with a period or new line.
    Or Age after some specific words and ends with symbols
    """
    pattern_w_words = r'\b(?:being|were|Were|are|is|now|turned|be|was|Was|been|presently|at|I\'m|i\'m|You\'re|you\'re)\s+(\d{1,2})(?:[.,?](?!\d)|$)'

    def __init__(self):
        patterns = [
            Pattern('age_in_sentence', AgeRecognizer.pattern_w_words, 0.9),
            Pattern('age_xx.', r'[:]\s\d{1,2}\.(?!\d)', 0.9),
            Pattern('age_xx_years_old', r'\b\d{1,2}\s+years\s+old\b', 0.9),  # matches 'XX years old'
            Pattern('age_xx_year_old', r'\b\d{1,2}\s*-*\s*year\s*-*\s*old\b', 0.9),  # matches 'XX-year-old'
        ]
        super().__init__(supported_entity="AGE", patterns=patterns, context=['age', 'old', 'years old', 'age of'])


class SpelledOutNamesRecognizer(PatternRecognizer):
    """
    Check for symbols between letters and allow a space between them
    """

    pattern = r'\b([A-Z]([-—])\s?[A-Z](\s?\2\s?[A-Z])*)\b'

    def __init__(self):
        super().__init__(supported_entity="SPELLED_NAME",
                         patterns=[Pattern('spelled_name', SpelledOutNamesRecognizer.pattern, 0.85)])


class SimpleDateRecognizer(PatternRecognizer):
    """
    Check for simple date like 30/05/2024
    or for years that start from 1971 and up
    """
    year_pattern = r'\b(197[1-9]|19[89]\d|20\d{2})(?:[.,?]{0,1})\b'
    year_in_sentence_pattern = r'\b(?:from|From|since|Since|in|In|\s)(197[1-9]|19[89]\d|20\d{2})\b'

    def __init__(self):
        patterns = [
            Pattern('Date_xx/xx/xxxx', r'\d{1,2}\/\d{1,2}\/(?:\d{4}|\d{2})\b', 0.85),
            Pattern('Date_year_xxxx.', SimpleDateRecognizer.year_pattern, 0.85),
            Pattern('Date_year_in_sentence', SimpleDateRecognizer.year_in_sentence_pattern, 0.85),
        ]
        super().__init__(supported_entity="DATE", patterns=patterns)


class SimpleTimeRecognizer(PatternRecognizer):
    """
    Check for simple time like 09:35 AM
    """

    def __init__(self):
        patterns = [
            Pattern('simple_time', r'(\d{1,2}:\d{2})\s{0,2}(AM|am|PM|pm)', 0.85),
        ]
        super().__init__(supported_entity="TIME", patterns=patterns)


class FacilityRecognizer(PatternRecognizer):
    """
    Check for series of words that end with FACILITY/Facility
    """

    def __init__(self):
        regex_patterns = [
            r'\b([A-Z][A-Z]+[-\s])+(FACILITY)\b',
            r'\b([A-Z][A-Z]+[-\s])+(FACILITIES)\b',
            r'\b([A-Z][a-z]+[-\s]?)+(Facility)\b',
            r'\b([A-Z][a-z]+[-\s]?)+(Facilities)\b',
        ]
        patterns = []
        for index, pattern in enumerate(regex_patterns):
            patterns.append(Pattern(f'facility{index + 1}', pattern, 0.85))
        super().__init__(supported_entity="ORGANIZATION", patterns=patterns, global_regex_flags=re.ASCII)


class SimpleHeightRecognizer(PatternRecognizer):
    """
    Check for simple height patterns
    """

    def __init__(self):
        regex_patterns = [
            r"(\d{1,2})['’](\d{1,2})[”\"]?",
            r"(\d{2,3})\s?(cm)",
            r"(\d{1,3})\s?(foot|Foot|feet|Feet)\s*(\d{0,2})?\s*(inches|inch|in)?",
            r"\b((?:one|two|three|four|five|six|seven|eight|nine))\s*(feet|foot|inches|inch|Feet|Foot|Inches|Inch)\b",
            r"\b((?:One|Two|Three|Four|Five|Six|Seven|Eight|Nine))\s*(feet|foot|inches|inch|Feet|Foot|Inches|Inch)\b",
        ]

        patterns = []
        for index, item in enumerate(regex_patterns):
            patterns.append(Pattern(f'height{index + 1}', item, 0.85))
        super().__init__(supported_entity="HEIGHT", patterns=patterns, context=["tall", "height"])


class SpelledOutItemRecognizer(PatternRecognizer):
    """
    Check for simple height patterns
    """

    pattern = r'\b[A-Z](,)?(-)?\s+as\s+in\s+\w+\b'

    def __init__(self):
        patterns = [Pattern('spelled_out_item', SpelledOutItemRecognizer.pattern, 0.85)]
        super().__init__(supported_entity="SPELLED_OUT_ITEM", patterns=patterns)

class SimpleURLRecognizer(PatternRecognizer):
    """
    Check for simple URL patterns
    """
    pattern = r'\b(www\.){0,1}\w+\.\w{3}(\.\w{2,3}){0,1}\b'

    def __init__(self):
        patterns = [Pattern('url', SimpleURLRecognizer.pattern, 0.85)]
        super().__init__(supported_entity="URL", patterns=patterns, )


class SimplePhoneNumberRecognizer(PatternRecognizer):
    """
    Check for simple phone patterns
    """

    def __init__(self):
        regex_patterns = [
            r"\(?\d{3}\)?-? *\d{3}-? *-?\d{4}",
        ]

        patterns = []
        for index, item in enumerate(regex_patterns):
            patterns.append(Pattern(f'phone{index + 1}', item, 0.85))
        super().__init__(supported_entity="PHONE_NUMBER", patterns=patterns,)
