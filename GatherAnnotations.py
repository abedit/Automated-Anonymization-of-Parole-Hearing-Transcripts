import argparse
import os
import warnings
from datetime import datetime

from _SourceCode import HelperFunctions, Constants
from _SourceCode.AnnotationUtils import hearing_text_into_annotations


def main():
    parser = argparse.ArgumentParser(description="Process some files in batches.")
    parser.add_argument('--ignore_1stPage', action='store_true', help='Prevent the information of the first page to be fed into Presidio')

    args = parser.parse_args()
    ignore_1st_page = args.ignore_1stPage
    if ignore_1st_page:
        print("\n== Preventing the information of the first page to be fed into Presidio ==")

    """     
        Read the transcripts from the hearings_txt directory.
        Compute Presidio, StanfordNER and SpaCy annotations, combine them and output them into txt files
        for each transcript file
        Parameters:
        create_annotation_output_file - creates a file with only the output of the annotations
        insert_labels_in_text - Insert labels in the original text, for example: [John Doe | PERSON] is on his way.
        write_statistics - write # of correct annotations and # of filtered out annotations in a separate file. 
                            Also output the false annotations in the file.
        ignore_1stPage - If true, stop extracting information from the transcripts' first
                            pages and they won't be fed into Presidio. 
    """

    directory = Constants.hearings_txt_directory

    if not os.path.exists(directory):
        print(f"\nThe folder '{Constants.hearings_txt_directory}' does not exist. Please make sure to run HearingsPDFs2Text.py first.\n")
        return

    files = [file for file in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, file)) and file.endswith('.txt')]
    if not files:
        print(f"\nThe folder '{Constants.hearings_txt_directory}' does not contain .txt files. Please make sure to run HearingsPDFs2Text.py first.\n")
        return

    start_time = datetime.now()  # record start time and later, the end time

    hearing_text_into_annotations(create_annotation_output_file=True,
                                  insert_labels_in_text=True,
                                  write_statistics=True,
                                  ignore_1st_page_info=ignore_1st_page)

    # output start time and end time
    print(f"\nStarted at: {start_time.strftime('%d.%m.%Y %H:%M:%S')}")
    end_time = datetime.now()
    print(f"Ended at: {end_time.strftime('%d.%m.%Y %H:%M:%S')}")
    print(HelperFunctions.time_difference(start_time, end_time))


if __name__ == "__main__":
    main()
