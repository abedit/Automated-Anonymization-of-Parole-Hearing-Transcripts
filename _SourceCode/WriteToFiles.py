import os

import _SourceCode.Constants as Constants
from _SourceCode.ModelClasses.Stats import Stats


def write_text_into_file(file, text):
    """
    Write text into the file
    """
    directory = os.path.dirname(file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(file):
        os.remove(file)


    with open(file, 'w', encoding='utf-8') as text_file:
        text_file.write(text)


def write_statistics_for_all_files(annotation_statistics):
    """
    Write a file that has the # of correct annotations, the # of annotations in each entity, the # of filtered out annotations from the white list
    and each tool's logic to filter out unlikeley annotations, the # of annotations filtered out in each entity, the # of annotations
     filtered out from the duplicates/overlap phase, the # of annotations removed in each entity, and finally the total unfiltered annotations detected
    """
    out_file = os.path.join(Constants.annotations_dir, 'Final' + Constants.text_format)
    with open(out_file, 'w', encoding='utf-8') as text_file:
        text_file.write(f'total (correct) annotations: {sum(annotation_statistics["total_annotation_count"])}\n\n')

        text_file.write(f"total PERSON correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_PERSON])}\n")
        text_file.write(f"total LOCATION correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_LOCATION])}\n")
        text_file.write(f"total ORGANIZATION correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_ORGANIZATION])}\n")
        text_file.write(f"total SPELLED_NAME correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_SPELLED_NAME])}\n")
        text_file.write(f"total ID correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_ID])}\n")
        text_file.write(f"total DATE correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_DATE])}\n")
        text_file.write(f"total TIME correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_TIME])}\n")
        text_file.write(f"total AGE correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_AGE])}\n")
        text_file.write(f"total HEIGHT correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_HEIGHT])}\n")
        text_file.write(f"total EMAIL_ADDRESS correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_EMAIL_ADDRESS])}\n")
        text_file.write(f"total URL correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_URL])}\n")
        text_file.write(f"total NRP correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_NRP])}\n")
        text_file.write(f"total SPELLED_OUT_ITEM correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_SPELLED_OUT_ITEM])}\n")
        text_file.write(f"total PHONE_NUMBER correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == Constants.LABEL_PHONE_NUMBER])}\n")
        text_file.write(f"total CARDINAL correct annotations: {len([item for item in annotation_statistics['correct_annotations'] if item.label == 'CARDINAL'])}\n")
        text_file.write(f"==================================================================================\n\n")

        text_file.write(f"total false annotations: {sum(annotation_statistics['total_false_annotation_count'])} filtered out from the whitelists and checks\n\n")
        text_file.write(f"total PERSON annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_PERSON])}\n")
        text_file.write(f"total LOCATION annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_LOCATION])}\n")
        text_file.write(f"total ORGANIZATION annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_ORGANIZATION])}\n")
        text_file.write(f"total SPELLED_NAME annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_SPELLED_NAME])}\n")
        text_file.write(f"total ID annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_ID])}\n")
        text_file.write(f"total DATE annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_DATE])}\n")
        text_file.write(f"total TIME annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_TIME])}\n")
        text_file.write(f"total AGE annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_AGE])}\n")
        text_file.write(f"total HEIGHT annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_HEIGHT])}\n")
        text_file.write(f"total EMAIL_ADDRESS annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_EMAIL_ADDRESS])}\n")
        text_file.write(f"total URL annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_URL])}\n")
        text_file.write(f"total NRP annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_NRP])}\n")
        text_file.write(f"total SPELLED_OUT_ITEM annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_SPELLED_OUT_ITEM])}\n")
        text_file.write(f"total PHONE_NUMBER annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == Constants.LABEL_PHONE_NUMBER])}\n")
        text_file.write(f"total CARDINAL annotations filtered out: {len([item for item in annotation_statistics['total_false_annotations'] if item.label == 'CARDINAL'])}\n")
        text_file.write(f"==================================================================================\n\n")

        text_file.write(f"Total filtered out annotations from the post-processing phase (duplicates, overlaps...): {len(annotation_statistics['total_filtered_out_annotations_from_final_cleaning'])}\n")
        text_file.write(f"total PERSON annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_PERSON])}\n")
        text_file.write(f"total LOCATION annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_LOCATION])}\n")
        text_file.write(f"total ORGANIZATION annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_ORGANIZATION])}\n")
        text_file.write(f"total SPELLED_NAME annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_SPELLED_NAME])}\n")
        text_file.write(f"total ID annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_ID])}\n")
        text_file.write(f"total DATE annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_DATE])}\n")
        text_file.write(f"total TIME annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_TIME])}\n")
        text_file.write(f"total AGE annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_AGE])}\n")
        text_file.write(f"total HEIGHT annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_HEIGHT])}\n")
        text_file.write(f"total EMAIL_ADDRESS annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_EMAIL_ADDRESS])}\n")
        text_file.write(f"total URL annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_URL])}\n")
        text_file.write(f"total NRP annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_NRP])}\n")
        text_file.write(f"total SPELLED_OUT_ITEM annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_SPELLED_OUT_ITEM])}\n")
        text_file.write(f"total PHONE_NUMBER annotations filtered out {len([item for item in annotation_statistics['total_filtered_out_annotations_from_final_cleaning'] if item.label == Constants.LABEL_PHONE_NUMBER])}\n\n")
        text_file.write(f"==================================================================================\n\n")

        text_file.write(f"total unfiltered annotations detected: {sum(annotation_statistics['total_unfiltered_annotations_count'])}")

def write_annotations_into_file(file, annotations):
    """
    Write in a file with the suffix _ANNOTATIONS.txt and contain the correct annotations of a specific file
    """
    if not annotations:
        return

    if os.path.exists(file):
        os.remove(file)
    with open(file, 'w', encoding='utf-8') as text_file:
        for annotation in annotations:
            text_file.write(annotation.output_file_str())


def write_stats_into_file(file, stats):
    """
    Write list of Stats into file
    """
    if not stats:
        return

    if os.path.exists(file):
        os.remove(file)
    with open(file, 'w', encoding='utf-8') as text_file:
        # for stat in stats:
        text_file.write(stats.toString())
        text_file.write('\n\n')
        stats.false_annotations.sort(key=lambda x: int(x.start))
        for ann in stats.false_annotations:
            text_file.write(ann.output_file_str())


def prepare_write_statistics_into_file(file_name_no_format, unique_annotations, false_annotations):

    out_file = os.path.join(Constants.annotations_dir, file_name_no_format + '_STATS' + Constants.text_format)
    stat = Stats(
        filtered_annotations=unique_annotations,
        false_annotations=false_annotations,
    )
    write_stats_into_file(out_file, stat)
    return out_file
