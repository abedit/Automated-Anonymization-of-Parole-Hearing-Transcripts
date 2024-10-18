import nltk.tag.stanford

from _SourceCode import Constants
from _SourceCode.AnnotationHelpers import AnnotationCleaner
from _SourceCode.AnnotationHelpers.AnnotationChecker import is_invalid_annotation
from _SourceCode.HelperFunctions import contains_keywords
from _SourceCode.ModelClasses.Annotation import Annotation


"""
StanfordNER tool is a class object due to the reason that to process files in batches would require a new instance
to access the StanfordNER model.
Originally it was 1 instance for all files but processing them in batches would give an error saying the file is in use.
Therefore, every file has its own instance of StanfordNER.
"""
class StanfordNER:

    stanford_ner = None
    def __init__(self):
        """
        Load the stanford NER jar file and model file
        """
        self.stanford_ner = nltk.tag.stanford.StanfordNERTagger('.\\_Resources\\stanford-ner\\english.all.3class.distsim.crf.ser.gz',
                                                           '.\\_Resources\\stanford-ner\\stanford-ner-4.2.0.jar',
                                                           encoding='utf-8')

    def get_stanford_ner_annotations(self, text):
        """
        Give a text and get the cleaned annotation data
        """

        if isinstance(self.stanford_ner, nltk.tag.stanford.StanfordNERTagger):
            tokenized_text = nltk.tokenize.word_tokenize(text)
            classified_text = self.stanford_ner.tag(tokenized_text)
            annotation_data = self.find_token_positions(text, classified_text)
            merged_data = AnnotationCleaner.merge_adjacent_annotations(annotation_data, text)
            return self.filter_annotation_result(merged_data)
        else:
            return []

    def find_token_positions(self, text, annotations):
        """
        Stanford NER doesn't provide a start and end index for each of its annotations
        so had to do it manually
        """
        end = 0
        results = []

        for word, label in annotations:
            start = text.find(word, end)
            end = text.find(word, end) + len(word)
            if label != 'O' and start != -1:
                ann = Annotation(
                    start=start,
                    end=end,
                    label=label,
                    preview=word,
                    source=Constants.SOURCE_STANFORD_NER
                )
                results.append(ann)

        return results

    def filter_annotation_result(self, annotations):
        """
        Filter out false positives based on the annotation label
        """
        result = []
        total_unfiltered_annotations = len(annotations)

        for ann in annotations:
            if is_invalid_annotation(ann):
                continue
            if ann.label == Constants.LABEL_PERSON:
                AnnotationCleaner.remove_person_title(ann)

                # Stanford NER sometimes detects 'unintelligible' in the PERSON labels
                ann.handle_prefixes()
                ann.handle_suffixes()

                if '\n' in ann.preview:
                    text_after_new_line = ann.preview.split('\n')[1]
                    new_end = ann.end - len(text_after_new_line) - 1
                    ann.end = max(new_end, 0)  # so that ann.end doesn't go negative
                    ann.preview = ann.preview.split('\n')[0]

                ann.handle_spelled_name_in_person_name()
            else:
                ann.handle_prefixes()
                ann.handle_suffixes()

            if ann.label == Constants.LABEL_LOCATION and contains_keywords(ann.preview, ["prison", "jail"]):
                ann.label = Constants.LABEL_ORGANIZATION
            if not ann.preview.strip() or ann.start == ann.end:
                continue
            result.append(ann)

        false_annotations = list(set(annotations) - set(result))

        return result, false_annotations, total_unfiltered_annotations
