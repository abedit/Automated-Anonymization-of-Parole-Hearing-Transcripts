class NameEntity:
    """
    Class that contains a named entities and sensitive information like a person's name, organization or location...
    'name' is the value in the annotation
    'name_replacement' is the replacement value filled by the anonymization methods
    'all_caps' is if the original annotation was fully capitalized
    'annotation_id' is if the original annotation's annotation_id

    """
    def __init__(self, name="", all_caps=False, annotation_id="", name_replacement=""):
        self.name = name
        self.name_replacement = name_replacement
        self.all_caps = all_caps
        self.annotation_id = annotation_id


    def __repr__(self):
        values = []
        if self.name:
            values.append("name=" + self.name)

        values.append(f'all_caps={self.all_caps}')

        if self.name_replacement:
            values.append(f'name_replacement={self.name_replacement}')

        if self.annotation_id:
            values.append(f'annotation_id={self.annotation_id}')

        return "NameEntity(" + ", ".join(values) + ")"

