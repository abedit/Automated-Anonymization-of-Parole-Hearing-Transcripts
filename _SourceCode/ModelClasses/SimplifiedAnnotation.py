class SimplifiedAnnotation:

    def __init__(self, start, end, label):
        self.start = start
        self.end = end
        self.label = label
    """
    Class that contains important data needed for each annotation.
    start and end are the indexes inside the text file
    label is the type of annotation (PERSON, LOCATION, ORGANIZATION...)
    """
