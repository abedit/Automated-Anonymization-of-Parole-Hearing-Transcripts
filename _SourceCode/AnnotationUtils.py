import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import _SourceCode.Constants as Constants
from _SourceCode import WriteToFiles, JsonFunctions
from _SourceCode.AnnotationHelpers import AnnotationCleaner
from _SourceCode.AnnotationHelpers.AnnotationReplace import annotate_text
from _SourceCode.FileDataExtraction.TextExtraction import extract_text_from_txt_file
from _SourceCode.ToolsUtils.PresidioUtils import get_presidio_annotations
from _SourceCode.ToolsUtils.SpaCyUtils import get_spacy_annotations
from _SourceCode.ToolsUtils.StanfordNER import StanfordNER
from _SourceCode.WriteToFiles import prepare_write_statistics_into_file

"""
This class is the one that calls the NER tools and annotation cleaning before writing them into files.
"""

annotation_statistics = {
    "files_count": 0,  # counter for console output
    "total_filtered_out_annotations_from_final_cleaning": [],
    "total_annotation_count": [],  # store the # of correct annotations for each file
    "total_false_annotation_count": [],  # store the # of false annotations for each file
    "total_false_annotations": [],  # store the false annotations for each file
    "total_unfiltered_annotations_count": [],  # store the # of unfiltered annotations
    "correct_annotations": []  # total correct annotations
}

skip_1st_page_info_presidio = False


def hearing_text_into_annotations(
        create_annotation_output_file=False,
        insert_labels_in_text=True,
        write_statistics=False,
        ignore_1st_page_info=False):
    """
    Takes the txt files in the hearings_txt folder, gets the annotations,
    cleans them and writes them into files. Process files in batches.

    @param create_annotation_output_file    Create a file containing the correct annotations for a hearing file
    @param insert_labels_in_text    Get a copy of the original hearing text, insert the annotations
                                    to have something like [John Doe | PERSON] works in [New York | LOCATION].

    @param write_statistics     Write the filtered out annotations in a file
    @param ignore_1st_page_info  If true, stop extracting information from the transcripts' first
                            pages and they won't be fed into Presidio.
    """

    global annotation_statistics, skip_1st_page_info_presidio

    skip_1st_page_info_presidio = ignore_1st_page_info

    import nltk
    print("Downloading pacakge for StanfordNER.\n")
    nltk.download('punkt')  # This is for StanfordNER

    annotation_statistics = {
        "files_count": 0,  # counter for console output
        "total_filtered_out_annotations_from_final_cleaning": [],
        "total_annotation_count": [],  # store the # of correct annotations for each file
        "total_false_annotation_count": [],  # store the # of false annotations for each file
        "total_false_annotations": [],  # store the false annotations for each file
        "total_unfiltered_annotations_count": [],  # store the # of unfiltered annotations
        "correct_annotations": []
    }

    annotations_json = []
    directory = Constants.hearings_txt_directory
    files = [file for file in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, file)) and file.endswith('.txt')]

    if not os.path.exists(Constants.annotations_dir):
        os.makedirs(Constants.annotations_dir)

    print('\n')
    print('---------GATHERING ANNOTATIONS---------')

    for file in files:
        annotations = _annotations_for_file(
            file=file,
            directory=directory,
            create_annotation_output_file=create_annotation_output_file,
            insert_labels_in_text=insert_labels_in_text,
            write_statistics=write_statistics)
        annotation_statistics['files_count'] += 1
        # place the annotation data into a json file
        JsonFunctions.write_data_to_json(annotations)

    # write a separate file containing the number of correct and incorrect annotations as well as the average of all files
    if write_statistics and annotation_statistics["total_annotation_count"] and annotation_statistics[
        "total_false_annotation_count"]:
        WriteToFiles.write_statistics_for_all_files(annotation_statistics=annotation_statistics)

    return annotations_json


def _annotations_for_file(file, directory, create_annotation_output_file, insert_labels_in_text, write_statistics):
    """
    Process a single file. Extracts annotations, cleans them, and performs necessary post-processing.
    This is the function that gets called concurrently.
    """

    file_path = os.path.join(directory, file)
    file_name_no_format = file.replace(Constants.text_format, '')
    text = extract_text_from_txt_file(file)

    print(annotation_statistics['files_count'] + 1, "----", f"\rProcessing: {file_path}...\n")

    # Get combined annotations from all NER tools
    annotations, false_annotations, total_unfiltered_annotations = _get_combined_annotations(text)

    # Clean the annotations
    unique_annotations, filtered_out_annotations = AnnotationCleaner.handle_duplicates_overlaps(annotations)

    unique_annotations.sort(key=lambda x: int(x.start))

    annotation_statistics['total_unfiltered_annotations_count'].append(total_unfiltered_annotations)
    annotation_statistics['total_filtered_out_annotations_from_final_cleaning'].extend(filtered_out_annotations)

    _file_post_processing(
        create_annotation_output_file=create_annotation_output_file,
        insert_labels_in_text=insert_labels_in_text,
        write_statistics=write_statistics,
        file_path=file_path,
        file_name_no_format=file_name_no_format,
        unique_annotations=unique_annotations,
        false_annotations=false_annotations,
        text=text
    )

    print('\n')

    # Return file annotations for final collection
    return {
        'file': file_name_no_format.replace(Constants.text_format, ''),
        'annotations': [ann.to_dict() for ann in unique_annotations],
    }


def _get_combined_annotations(text):
    # return
    """
    Get annotations from the tools and combine them in one list
    """
    inner_total_unfiltered_annotations_count = 0
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(get_presidio_annotations, text, skip_1st_page_info_presidio): 'presidio',
            executor.submit(get_spacy_annotations, text): 'spacy',
            executor.submit(StanfordNER().get_stanford_ner_annotations, text): 'stanford'
        }

        combined_annotations = []
        false_annotations = []

        for future in as_completed(futures):
            annotations, false_anns, total_unfiltered_annotations = future.result()
            inner_total_unfiltered_annotations_count += total_unfiltered_annotations
            combined_annotations.extend(annotations)
            false_annotations.extend(false_anns)

    combined_annotations.sort(key=lambda x: x.start)
    false_annotations.extend([item for item in combined_annotations if not item.preview])
    combined_annotations = [item for item in combined_annotations if item.preview]  # remove empty annotations if any
    return combined_annotations, false_annotations, inner_total_unfiltered_annotations_count


def _file_post_processing(
        create_annotation_output_file,
        insert_labels_in_text,
        write_statistics,
        file_path,
        file_name_no_format,
        unique_annotations,
        false_annotations,
        text
):
    """
    This function prepares the data to write into annotation stat files, also inserts the annotations in the text.
    """
    if create_annotation_output_file:  # create a separate file with the correct annotations
        annotation_file_name = file_name_no_format + '_ANNOTATIONS.txt'
        output_file_path = os.path.join(Constants.annotations_dir, annotation_file_name)
        WriteToFiles.write_annotations_into_file(output_file_path, unique_annotations)
        print(annotation_statistics['files_count'] + 1, "----", len(unique_annotations), "annotations written in",
              output_file_path)

    print(annotation_statistics['files_count'] + 1, "----", f"\rProcessed: {file_path}...")

    if insert_labels_in_text:  # insert the labels into a copy of the transcript file for review
        annotated_text = annotate_text(text, unique_annotations)
        file = os.path.join(Constants.annotations_dir, file_name_no_format + Constants.text_format)
        WriteToFiles.write_text_into_file(file, annotated_text)
        print("Labels inserted in ", file)

    unique_annotations.sort(key=lambda x: int(x.start))
    # write total # of correct and incorrect annotations + all of the false annotations for a single hearing file
    if write_statistics:
        stat_file = prepare_write_statistics_into_file(file_name_no_format, unique_annotations, false_annotations)
        print("Statistics written in ", stat_file)

        annotation_statistics['correct_annotations'].extend(unique_annotations)
        annotation_statistics['total_annotation_count'].append(len(unique_annotations))
        annotation_statistics['total_false_annotation_count'].append(len(false_annotations))
        annotation_statistics['total_false_annotations'].extend(false_annotations)
