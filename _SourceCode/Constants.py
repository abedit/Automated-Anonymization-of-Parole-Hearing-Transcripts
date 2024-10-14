input_hearings_directory = '.\\Hearing transcripts (PDF)'
hearings_txt_directory = '.\\Hearing transcripts (Text)'
output_json_directory = '.\\Annotations JSON'
output_json_file = 'processed_annotations.json'
annotations_dir = '.\\Annotations Output'
resources_folder = '.\\_Resources'
text_format = '.txt'
presidio_threshold = 0.85
output_anonymization = '.\\Anonymization Output\\anonymization_output_'
first_page_names_headers = [
    "PANEL PRESENT",
    "OTHERS PRESENT",
    "Transcribed by",
    "Hearing of"
]
adjournment_message = 'ADJOURNMENT\nTHIS TRANSCRIPT CONTAINS THE PROPOSED DECISION'
hearing_decision_message = 'CALIFORNIA BOARD OF PAROLE HEARINGS\nDECISION'

presidio_labels = [
    "PERSON",
    "LOCATION",
    "ORGANIZATION",
    "SPELLED_NAME",
    "ID",
    "DATE",
    "TIME",
    "HEIGHT",
    "AGE",
    "EMAIL_ADDRESS",
    "URL",
    "NRP",
    "SPELLED_OUT_ITEM",
    "PHONE_NUMBER",
]

spacy_labels = [
    "PERSON",
    "DATE",
    "TIME",
    "CARDINAL", "GPE",
]

person_titles = [
    'INMATE', 'ATTORNEY', 'COMMISSIONER',
    'VICTIM', '<inaudible>', 'VNOK',
    'INTERPRETER', 'OBSERVER', 'OFFICER'
]
person_titles.extend([item.lower() for item in person_titles])
person_titles.extend([item.title() for item in person_titles])

worded_numbers_pattern = r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|' \
                         r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|' \
                         r'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)' \
                         r'(?:[-\s](?:one|two|three|four|five|six|seven|eight|nine|ten|' \
                         r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|' \
                         r'thirty|forty|fifty|sixty|seventy|eighty|ninety))?\b'

split_string_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b|\w+|[^\w\s]|\s'
split_string_pattern_for_file = r'\d{4}-\d{1,2}-\d{1,2}|\b\d{1,2}/\d{1,2}/\d{4}\b|\w+|[^\w\s]|\s'

LABEL_SPELLED_NAME = 'SPELLED_NAME'
LABEL_ID = 'ID'
LABEL_DATE = 'DATE'
LABEL_TIME = 'TIME'
LABEL_ORGANIZATION = 'ORGANIZATION'
LABEL_HEIGHT = 'HEIGHT'
LABEL_AGE = 'AGE'
LABEL_PERSON = 'PERSON'
LABEL_PHONE_NUMBER = 'PHONE_NUMBER'
LABEL_EMAIL_ADDRESS = 'EMAIL_ADDRESS'
LABEL_LOCATION = 'LOCATION'
LABEL_URL = 'URL'
LABEL_NRP = 'NRP'
LABEL_SPELLED_OUT_ITEM = 'SPELLED_OUT_ITEM'

SOURCE_PRESIDIO = "Presidio"
SOURCE_SPACY = "SpaCy"
SOURCE_STANFORD_NER = "StanfordNER"

PSEUDONYMIZATION = 'PSEUDONYMIZATION'




