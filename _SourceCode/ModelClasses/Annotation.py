import re

from _SourceCode.ToolsUtils import PresidioRecognizers


class Annotation:
    """
    Class that contains important data needed for each annotation.
    start and end are the indexes inside the text file
    label is the type of annotation (PERSON, LOCATION, ORGANIZATION...)
    preview is the string inside the text that was detected
        (for example: if the label is a person then preview is 'John Doe')
    source refers to which tool detected the annotation
    replacement is the replacement value filled by the anonymization methods
    annotation_id is the start and end together to make it easy to look for the proper annotation object (used in AnnotationReplace.py)
    """

    def __init__(self, start, end, label, preview, source):
        self.start = start
        self.end = end
        self.label = label
        self.preview = preview.strip()
        self.source = source
        self.replacement = ""
        self.annotation_id = f'{start}|{end}'

    def __repr__(self):
        return (f"Annotation(start={self.start}, end={self.end}, "
                f"label='{self.label}', text='{self.preview.strip()}', "
                f"source='{self.source}')")

    def __str__(self):
        return f"{self.preview} | {self.label} // start:{self.start}, end:{self.end} // source:'{self.source}'"

    def output_file_str(self):
        return "start: {0:>5}\t end: {1:>5}\t text: {3:<30}\t label: {2:<15}\t source: {4:<10}\n".format(
            self.start,
            self.end,
            self.label,
            self.preview,
            self.source)

    def to_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'label': self.label,
            'preview': self.preview.strip(),
            'source': self.source
        }

    def handle_prefixes(self):
        """
        sometimes predictions of PERSON show one of these in the beginning or end of person's name
        so they're being removed here
        """
        possible_prefixes = [
            '<unintelligible>', '<unintelligible', 'unintelligible>', 'unintelligible',
            '<UNINTELLIGIBLE>', '<UNINTELLIGIBLE', 'UNINTELLIGIBLE>', 'UNINTELLIGIBLE',
            '<', '> ', 'a ', 'an ', 'A ', 'An ', 'AN ', 'the ', '.', 'Niece\n ', 'Niece ',


        ]
        for prefix in possible_prefixes:
            if self.preview.startswith(prefix):
                split_text = self.preview.split(prefix, 1)
                if split_text[1]:
                    self.start = self.start + len(prefix)
                    self.preview = split_text[1]
                    if self.preview.startswith(' '):
                        self.start += 1
                        self.preview = self.preview[1:]


        if self.preview.lower().startswith('inmate '):
            split_text = self.preview.split()
            self.start = self.start + len('inmate ')
            self.preview = ' '.join(split_text[1:])

    def handle_suffixes(self):
        "Remove these suffixes if they are at the end of the annotation"
        possible_suffixes = [
            'unintelligible', '<unintelligible', '<unintelligible>', 'unintelligible>',
            'UNINTELLIGIBLE', '<UNINTELLIGIBLE', '<UNINTELLIGIBLE>', 'UNINTELLIGIBLE>',
            '>', '<', '’s', '\'s', ', uh', '?', '.', '’', '\'', "THROUGH", "through",
            '- and', '”', ',-', ',',
        ]
        for suffix in possible_suffixes:
            if self.preview.endswith(suffix):
                split_text = self.preview.split(suffix, 1)
                if split_text[0]:
                    self.end = self.end - len(suffix)
                    self.preview = split_text[0]



    def handle_spelled_name_in_person_name(self):
        """
        Some cases Spelled names are included in a PERSON annotation. Example:
        Annotation: PERSON | John J-O-H-N
        So we must separate the name from the spelled name
        """
        if re.search(PresidioRecognizers.SpelledOutNamesRecognizer.pattern, self.preview):
            spelled_out_name_part = re.search(PresidioRecognizers.SpelledOutNamesRecognizer.pattern,
                                              self.preview).group()
            split_ann_preview = self.preview.split(
                re.search(PresidioRecognizers.SpelledOutNamesRecognizer.pattern, self.preview).group())
            if split_ann_preview:
                self.preview = split_ann_preview[0]
                self.end = self.end - len(spelled_out_name_part) - 1