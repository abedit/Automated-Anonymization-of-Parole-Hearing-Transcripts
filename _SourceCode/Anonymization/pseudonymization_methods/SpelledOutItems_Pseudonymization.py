from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity


def pseudonymize_spelled_out_items_labels(annotations):
    """
    Filters the annotations to only hold the SPELLED_OUT_ITEM label.
    The original values are saved in a map as key with the pseudonymized values as values.
    If the same spelled item occurs again, they would have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.

    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for SPELLED_OUT_ITEM values with the 'replacement' variable filled.
    """


    spelled_out_items = [NameEntity(name=item.preview, annotation_id=item.annotation_id)
                         for item in sorted(annotations, key=lambda x: x.start)
                         if item.label == Constants.LABEL_SPELLED_OUT_ITEM]

    spelled_items_map = {}
    spelled_items_count = 1

    for spelled_out_item in spelled_out_items:
        if spelled_out_item.name.lower() not in spelled_items_map:
            pseudo_spelled_item = "SPELLED_OUT_ITEM_" + str(spelled_items_count)
            spelled_items_count += 1
            spelled_items_map[spelled_out_item.name.lower()] = pseudo_spelled_item
        else:
            pseudo_spelled_item = spelled_items_map[spelled_out_item.name.lower()]

        spelled_out_item.name_replacement = '[' + pseudo_spelled_item + ']'

    return spelled_out_items
