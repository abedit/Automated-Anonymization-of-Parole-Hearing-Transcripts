class Stats:
    """
    General class to have statistics of each file.
    filtered_annotations refers to the correct number of annotations (after filtering out the wrong ones)
    false_annotations contains the list of the (false) annotations that were filtered out
    """
    def __init__(self, filtered_annotations, false_annotations):
        self.filtered_annotations = filtered_annotations
        self.false_annotations = false_annotations

    def __repr__(self):
        return (f"Annotation(filtered_annotations={self.filtered_annotations}, "
                f"false_annotations='{self.false_annotations}')")

    def __str__(self):
        return (f"filtered_annotations {len(self.filtered_annotations)}\n"
                f"false_annotations {len(self.false_annotations)}\n")

    def toString(self):
        return (f"filtered_annotations (correct): {len(self.filtered_annotations)}\n"
                f"false_annotations: {len(self.false_annotations)}\n")