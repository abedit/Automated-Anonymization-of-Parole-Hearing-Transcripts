from _SourceCode import Constants
from _SourceCode.AnnotationHelpers.AnnotationChecker import person_titles


def merge_adjacent_annotations(annotation_data, text):
    """
    if 2 or more annotations are right next to each other and have the same label, merge them under one annotation
    """
    if not annotation_data:
        return []

    result = []

    current_ann = annotation_data[0]

    for ann in annotation_data[1:]:
        next_preview = ann.preview
        next_label = ann.label
        next_start = ann.start
        next_end = ann.end

        conditions = [
            next_start == current_ann.end + 1,
            next_start == current_ann.end + 2,
        ]
        symbols = [
            '\n', ':', ' ,', ', ', '. ', ' - ',
        ]
        # Check if the next entity is adjacent and of the same type and not separated by certain symbols
        if next_label == current_ann.label and any(conditions) and not any(
                char in text[current_ann.end:next_end] for char in symbols):
            current_ann.preview += ' ' + next_preview
            current_ann.end = next_end
        # if the annotations are right next to each other not separated by anything
        elif next_label == current_ann.label and next_start == current_ann.end:
            current_ann.preview += next_preview
            current_ann.end = next_end
        else:
            result.append(current_ann)
            current_ann = ann

    if current_ann not in result:
        result.append(current_ann)

    return [item for item in result if item.preview != '’']


def handle_duplicates_overlaps(annotations):
    """
    Some annotations can have the following cases:
    1- annotations that have the same start and same end with the same label (duplicates)
    2- annotations that have the same start and same end but different labels
    3- annotations that have the same start but different end
    4- annotations that have different start but same end
    5- annotations that have start before the last one ended (overlaps). Example:
    start:  2933	 end:  2964	 label: PERSON         	 text: Jones Smith S-M-I-T-H
    start:  2948	 end:  2963	 label: SPELLED_NAME   	 text: S-M-I-T-H

    Approach:
    For case 1, the duplicates are removed.

    For case 2, change label if the labels compared are between:
    PERSON and SPELLED_NAME -> SPELLED_NAME if it has hyphens otherwise PERSON
    LOCATION and ID -> ID if it has letters and no space, otherwise LOCATION
    DATE_TIME and ID -> ID
    etc...

    For cases 3 and 4, take whichever the 'text' is longest

    For case 5, if they have the same label, take the longest one.
        Otherwise separate by making one end and the other start right after.
    """

    annotations.sort(key=lambda x: x.start)

    # remove duplicates
    unique_ann = fix_labels_remove_duplicates(annotations)

    # now to look at annotations having the same start but different end
    same_start_diff_end = handle_same_start_diff_end(unique_ann)

    # now to look at annotations having the same end but different start
    diff_start_same_end = handle_diff_start_same_end(same_start_diff_end)

    diff_start_same_end.sort(key=lambda x: x.start)

    no_overlaps = handle_overlaps(diff_start_same_end)

    # remove empty preview annotations in case there are any
    output = [item for item in no_overlaps if item.preview and item.start != item.end]
    filtered_out_annotations = list(set(annotations) - set(output))
    return output, list(filtered_out_annotations)


def handle_overlaps(annotations):
    output = []
    """
    Overlap example:
    start:   860	 end:   894	 label: PERSON         	 text: John J-O-H-N CDCR 
    start:   870	 end:   888	 label: SPELLED_NAME   	 text: J-O-H-N  
    
    If they have the same label, take the longest one. 
    Otherwise separate by making one end and the other start right after.
    """
    if annotations:
        output.append(annotations[0])

    # starting from the second one
    for current_ann in annotations[1:]:

        last_ann = output[-1]
        if current_ann.start <= last_ann.end:
            if last_ann.source == Constants.SOURCE_PRESIDIO and last_ann.label == Constants.LABEL_ORGANIZATION:
                continue  # There's only one case of this happening but here presidio takes priority
            if last_ann.label == current_ann.label:
                continue  # Since they're the same labels just detected by different sources, it's fine here
            last_ann.end = current_ann.start - 1
            last_ann.preview = last_ann.preview[:last_ann.end - last_ann.start]
            del output[-1]
            output.append(last_ann)

        output.append(current_ann)

    return output


def fix_labels_remove_duplicates(annotations):
    """
    For annotations having the same start and same end (duplicates).
    These annotations must be filtered out.
    In some cases, the labels are incorrect between certain types of labels and must be fixed.
    """
    grouped = {}
    # Group annotations by start and end
    for item in annotations:
        key = item.start, item.end
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)

    unique_ann = []
    for key, group in grouped.items():
        seen = []

        # remove duplicates
        for item in group:
            if item not in seen:
                seen.append(item)

        final_annotation = None

        # look at annotations that have the same start and same end but different labels
        # in case of 2 annotations having the same start and end indexes but different label types,
        # certain label types take priority
        for item in seen:
            if final_annotation is None:
                final_annotation = item
                continue

            if item.label != final_annotation.label:
                if ((item.label == Constants.LABEL_PERSON and final_annotation.label == Constants.LABEL_SPELLED_NAME) or
                        (item.label == Constants.LABEL_SPELLED_NAME and final_annotation.label == Constants.LABEL_PERSON)):

                    final_annotation.label = Constants.LABEL_SPELLED_NAME if '-' in item.preview else Constants.LABEL_PERSON

                elif ((item.label == Constants.LABEL_LOCATION and final_annotation.label == Constants.LABEL_ID) or
                      (item.label == Constants.LABEL_ID and final_annotation.label == Constants.LABEL_LOCATION)):

                    final_annotation.label = Constants.LABEL_ID if any(
                        c.isalpha() for c in item.preview) and ' ' not in item.preview else Constants.LABEL_LOCATION

                elif ((item.label == Constants.LABEL_SPELLED_NAME and final_annotation.label == Constants.LABEL_LOCATION) or
                      (item.label == Constants.LABEL_LOCATION and final_annotation.label == Constants.LABEL_SPELLED_NAME)):

                   final_annotation.label = Constants.LABEL_LOCATION

                elif ((item.label == Constants.LABEL_NRP and final_annotation.label == Constants.LABEL_PERSON) or
                      (item.label == Constants.LABEL_PERSON and final_annotation.label == Constants.LABEL_NRP)):

                    final_annotation.label = Constants.LABEL_PERSON

                elif ((item.label == Constants.LABEL_PHONE_NUMBER and final_annotation.label == Constants.LABEL_ID) or
                      (item.label == Constants.LABEL_ID and final_annotation.label == Constants.LABEL_PHONE_NUMBER)):

                    final_annotation.label = Constants.LABEL_ID

            if len(item.preview) > len(final_annotation.preview):
                final_annotation = item

        unique_ann.append(final_annotation)
    return unique_ann


def handle_diff_start_same_end(annotations):
    """
    If annotations have the same end but different start indexes. Take the longer one
    """
    grouped = group_values(annotations, start=False)

    no_same_end_ann = []
    for key, value in grouped.items():
        if len(value) == 1:
            no_same_end_ann.append(value)
        else:
            max_ann = []
            max_len = value[0].end - value[0].start
            for i, item in enumerate(value):
                current_len = item.end - item.start
                # take the bigger annotation
                if current_len > max_len:
                    max_ann.append(item)
            if max_ann:
                no_same_end_ann.extend(max_ann)
            else:
                no_same_end_ann.append([value[0]])

    temp_annotations = []
    for item in no_same_end_ann:
        if isinstance(item, list) and item:
            temp_annotations.append(item[0])
        elif isinstance(item, dict):
            temp_annotations.append(item)
    return temp_annotations


def handle_same_start_diff_end(annotations):
    """
    If annotations have the same start but different end indexes. Take the longer one
    """
    grouped = group_values(annotations, start=True)

    no_same_start_ann = []
    for key, value in grouped.items():
        if len(value) == 1:
            no_same_start_ann.append(value)
        else:
            max_ann = []
            max_len = value[0].end - value[0].start
            for i, item in enumerate(value):
                current_len = item.end - item.start
                # take the bigger annotation
                if current_len > max_len:
                    max_ann.append(item)
            if max_ann:
                no_same_start_ann.extend([max_ann])
            else:
                no_same_start_ann.append([value[0]])

    temp_annotations = [item[0] if (isinstance(item, list) and item) else item for item in no_same_start_ann]
    return temp_annotations


def group_values(annotations, start=False):
    """
    Take list of annotations and returns them grouped by start and end indexes
    """
    grouped = {}
    for item in annotations:
        key = item.start if start else item.end
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    return grouped


def remove_person_title(ann):
    """
    In the case of 'INMATE JOHN' for example, the title 'INMATE' is not needed and will be removed
    """
    for title in person_titles:
        if ann.preview and ann.preview.split() and ann.preview.split()[0] == title:
            ann.start = ann.start + len(title)
            ann.preview = ann.preview.replace(title, '')
            if ann.preview.startswith(' '):
                ann.start = ann.start + 1
                ann.preview = ann.preview[1:]

        if ann.preview.endswith(':'):
            ann.end = ann.end - 1
            ann.preview = ann.preview.replace(':', '')


def remove_symbols_from_date(ann):
    """
    In case a date annotation ends with certain symbols, they need to be removed
    """
    symbols = ('?', '.', '!', ',', ':', ';')
    if ann.preview.endswith(symbols):
        ann.preview = ann.preview[:-1]
        ann.end = ann.end - 1
    if ann.preview.startswith(' '):
        ann.preview = ann.preview[1:]
        ann.start = ann.start + 1
