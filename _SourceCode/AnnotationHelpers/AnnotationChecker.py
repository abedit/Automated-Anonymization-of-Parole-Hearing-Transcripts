import calendar
import re
from datetime import datetime

from _SourceCode import HelperFunctions, Constants
from _SourceCode.HelperFunctions import contains_keywords
from _SourceCode.ToolsUtils import PresidioRecognizers

"""
Person titles to remove them from annotations. 
lowercase and title versions of these titles are appended to the list
"""
person_titles = [
    'INMATE', 'ATTORNEY', 'COMMISSIONER',
    'VICTIM', '<inaudible>', 'VNOK',
    'INTERPRETER', 'OBSERVER', 'OFFICER', 'DA', 'NS', 'Ms.', 'Ms',
    'Mr.', 'Mr', 'Dear', 'ADVOCATE', "SERGEANT", 'Dr.',
]
person_titles.extend([item.lower() for item in person_titles])
person_titles.extend([item.title() for item in person_titles])

"""
Values that make the person annotation invalid
"""
person_invalid_words = [
    'state', 'i\'', 'fentanyl', 'hearings', 'correctioanl',
    'lightswitch', 'prison', 'oh close', 'who\'s-', 'anger management',
    'priest', 'aspd', 'CHCF', 'gogi workbook', 'on top of',
    'crimie', 'an elder parole hearing', 'didn’t', 'w-what',
    'sexaholics anonymous', 'sexaholic anonymous', 'sexaholics',
    'wonder woman', 'schizo', 'it\'s', 'state', 'healthright',
    'grim reaper', 'jesus christ', 'greed dot', 'spider-man',
    'gold star gas', 'untitled'
] # 32

person_invalid_values_case_sensitive = [
    'cook', 'officer', 'long', 'long-', 'That\'s-',
    'God', 'Christ', 'Programmer', 'VNOK', 'GEO',
    'ho', 'crimee', 'CMF', 'ali', 'che', 'GTA',
    'Don’', 'mm', 'Once-', 'ISO', 'OGs', 'Ms', 'NAs',
    'UA', 'Uhm',
] # 25

person_invalid_values_case_insensitive = [
    'unidentified', 'covid', 'madam da', '',
    'sergeant', 'master', 'others', 'observer',
    'commissioner', 'presiding commissioner', 'i -',
    'pillars', 'remorse', 'inmate', 'gogi', 'a',
    'mother', 'cousin', 'daughter-in-law', '-',
    'chronos', 'chrono', 'you-you', 'pruno', 'doctor',
    'cga', 'don’t-', 'yo', 'you\'ve-', '--you',
    're', 'if', 'is', 'i', 'didn’t', 'gogi', 'panel',
    'for', 'eme', 'de -', 'i’d-', 'de', 'no', 'vsp',
    '-we\'ll', 'we\'re', 't- i', 'sci-fi', 'it\'s',
    'do-', 'chcf', 'avp', 'others present', 'level iii',
    'da', 'ctf', 'yts', 'uas', 'dnn', 'victim', 'am - am',
    'ns', 'god-', 'bs', 'unknown', 'niece', 'pelican bay',
    'ma\'am', 'district attorn,', 'lieutenant', 'dad', 'officer-',
    'criminon',
] # 72


def is_invalid_person(text):
    """
    Checks if the string (coming from an annotation with label 'PERSON') is a valid person name or not.
    The check is done by checking if the string contains certain words, equals to certain words or
    satisfies certain conditions.
    if any of the conditions are satisfied, returns true
    """
    conditions = [
        len(text) == 1,
        text in person_invalid_values_case_sensitive,
        text.lower() in person_invalid_values_case_insensitive,
        text.lower().endswith('anonymous'),
        text.lower().endswith(' award'),
        '/' in text,
        '.' in text and len(text.split('.')[0]) == 1,
        re.search(r'\d', text),
        contains_keywords(text, person_invalid_words),
        text.islower() and '.' not in text,
        re.fullmatch(PresidioRecognizers.SpelledOutNamesRecognizer.pattern, HelperFunctions.clean_name(text))
    ]
    return any(conditions)


def is_invalid_org(text):
    """
    Checks if the string represents an invalid organization name by checking if certain conditions are satisfied.
    Returns true if it's an invalid organization
    """
    invalid_words = [
        'initial parole consideration hearing',
        'board of parole', 'anger management', 'victim\'s', '\'s house', 'no.',
        'parole panel', 'parole cdc', 'attorney\'s office', 'domestic violence',
        'da ', 'district attorney', 'islam', 'muslim', 'vnok', 'israel', 'hearing for ',
    ] # 16
    conditions = [
        contains_keywords(text, invalid_words),
        text.lower().startswith('inmate'),
        text.lower() in [
            'dvi', 'memorial', 'pruno',
            'time', 'interpreter', 'sheriff\'s Department',
            'panel\'s', 'panel’s', 'prep', 'christian',
            'the', 'you\'ve', 'attorneys\'',
            'mac', 'eop', 'pms', 'house', 'central file',
            'gogi', 'office', 'conrep',
            'board', 'company', 'plane', 'insurance company',
            'sny', 'unidentified', 'observer',
            'parole board', 'request for assistance',
            'panel', 'parole', 'parole department', 'unintelligible',
            'state', 'gpl', 'psa', 'bpa', 'cra', 'sap', 'crn',
            'cdc', 'cdcr', 'cba',
        ], # 42
        re.search(PresidioRecognizers.SpelledOutNamesRecognizer.pattern, text) is not None,
        text in ['long'],
    ]

    return any(conditions)


def is_invalid_location(text):
    """
    Checks if a string is a valid location by checking if it satisfies certain conditions.
    Returns true if it's an invalid location
    """
    invalid_words = [
        'subdivision', 'district', 'VA', 'islam',
        'inmate', 'dis', 'hvac', 'uh,', 'wham', 'de la', 'the <',
    ] # 11
    conditions = [
        text in ['dormie', 'R-', ], # 2
        text.lower() in [
            'son', 'daughter-in-law', 'sister', 'interpreter',
            'i\'m', 'p.o', 'oc', 'covid', 'the <', 'hasn\'t-', 'the <',
            'burg', 'miss.', 'segway', 'vnok', 'county', 'counties',
            'uh', 'she-', 'fla', 'ge-', 'shhh', 'miss', 'criminon', 'county of',
        ], # 25
        re.search(r'\d', text),
        len(text) == 1,
        contains_keywords(text, invalid_words)
    ]
    return any(conditions)


def is_invalid_url(text):
    """
    Checks if a string is a valid url.
    Returns true if it's an invalid url
    """
    conditions = [
        text.startswith('...'),
        '..' in text,
    ]

    return any(conditions)


def is_invalid_nrp(text):
    """
    NRP stands for Nationality Religion Politics (political affiliations)
    Checks if a text is a valid NRP.
    Returns true if it's an invalid NRP
    """
    invalid_words = [
        'did-', 'nazi', 'dui', 'sop', 'tetnis', 'syspointe', 'causitive',
        'perpe', 'disciplinarians', 'inno', 'tet', 'isudt',
    ] # 12
    conditions = [
        contains_keywords(text, invalid_words),
        '.' in text,
        text.lower() in ['contra', 'adseg', 'marines', 'ak', 'objecti', 'focu', 'lin-', # 7
                         ],
        re.search(r'\d', text),
        len(text) < 2,
    ]
    return any(conditions)


month_names = list(calendar.month_name)[1:]
days_of_week = list(calendar.day_name)
days_of_week.extend([f'{item}s' for item in days_of_week])
months_pattern = r'\b(' + '|'.join(month_names) + r')\b'
days_of_week_pattern = r'\b(' + '|'.join(days_of_week) + r')\b'


def is_invalid_date(text):
    """
    Checks if a text is a valid date by checking if it satisfies certain conditions.
    Returns true if it's an invalid date
    """
    invalid_words = [
        'motel',
        'that day', 'whole day',
        'section', 'today',
        '\n', 'calendar', 'first few',
        'confused myself',
        'a lot', 'great', 'good',
        'the year', 'rare',
        '1073', '’ years',
        'those', 'gram', 'credential',
        'weekend', 'uh, good', 'grade',
        'bad', 'last', 'small season',
        'tomorrow', 'yesterday',
        'every day', 'the day', 'this day', 'a day',
        'the worst', 'nice day', 'important', 'cra',
    ] # 34
    conditions = [
        contains_keywords(text, invalid_words),
        text.lower() in [
            '\'',
            'day', 'now',
            'years',
            'year',
            'season',
            'the first half',
            'the second half', 'daily', 'weekly', 'monthly', 'yearly',
        ], # 12
        text.endswith('%'),
        re.search(r"(\d['’]\d)", text) is not None,
        re.search(r'\b\d+[A-Za-z]\b', text) is not None,
        text.isdigit() and len(text) == 3,
        text.isdigit() and len(text) == 4 and int(text) > (datetime.now().year + 100),
        not text.isdigit() and len(text) == 1,
    ]

    if not any(conditions):
        # valid date according to the above checks but let's check for one more thing
        # Check if there are numbers written as words or there are decades (twenties, thirties...)
        # or days of the week or month name
        split_text = HelperFunctions.split_string(text)
        split_text = [str(HelperFunctions.word_to_number(item)) for item in split_text]
        split_text = [HelperFunctions.replace_decade_words(item) for item in split_text]

        numerical_values = [item for item in split_text if item.isdigit() or bool(re.search(r'\d', item))]

        valid_date_conditions = [
            len(numerical_values) > 0,
            re.search(months_pattern, text, re.IGNORECASE) is not None,
            re.search(days_of_week_pattern, text, re.IGNORECASE) is not None,
        ]
        if any(valid_date_conditions):
            return False  # is valid date
        else:
            return True  # is invalid date

    return any(conditions)


def is_invalid_time(text):
    """
    Checks if a text is a valid time by checking if it satisfies certain conditions.
    Returns true if it's an invalid time
    """
    invalid_words = [
        'robbery',
    ]
    conditions = [
        not re.search(r'\d', text),
        contains_keywords(text, invalid_words),
    ]

    return any(conditions)


def is_invalid_spelled_name(text):
    """
    Checks if a text is a valid spelled name by checking if all characters separated by '-' are uppercase.
    Returns true if it's an invalid spelled name
    """
    if '-' in text:
        split_text = text.split('-')
        split_text = [item for item in split_text if item]
        upper_chars = [item for item in split_text if item.isupper()]
        return len(split_text) != len(upper_chars)
    return True


def is_invalid_annotation(ann):
    """
    Main entry point for checking if an annotation is invalid
    """
    text = ann.preview
    match ann.label:
        case Constants.LABEL_PERSON:
            return is_invalid_person(text)

        case Constants.LABEL_LOCATION:
            return is_invalid_location(text)

        case Constants.LABEL_NRP:
            return is_invalid_nrp(text)

        case Constants.LABEL_URL:
            return is_invalid_url(text)

        case Constants.LABEL_SPELLED_NAME:
            return is_invalid_spelled_name(text)

        case Constants.LABEL_DATE:
            return is_invalid_date(text)

        case Constants.LABEL_TIME:
            return is_invalid_time(text)

        case Constants.LABEL_ORGANIZATION:
            return is_invalid_org(text)

    return False
