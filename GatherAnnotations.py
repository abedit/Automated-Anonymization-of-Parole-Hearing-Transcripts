import argparse
import warnings
from datetime import datetime

from _SourceCode import HelperFunctions
from _SourceCode.AnnotationUtils import hearing_text_into_annotations


def main():
    parser = argparse.ArgumentParser(description="Process some files in batches.")
    parser.add_argument('--file_count', type=int, default=1, help='Number of files to process at a time')
    file_count = parser.parse_args().file_count

    if file_count > 5:
        warnings.warn(
            "Warning: Processing more than 5 files at a time will cause your pc to start lagging and/or become slow. The default value of 1 will be used.\nPlease note that processing a lot of files at the same time can actually result in the program to take longer.")
        file_count = 1
    if file_count < 1:
        file_count = 1

    """     
        Read the transcripts from the hearings_txt directory.
        Compute Presidio, StanfordNER and SpaCy annotations, combine them and output them into txt files
        for each transcript file
        Parameters:
        create_annotation_output_file - creates a file with only the output of the annotations
        insert_labels_in_text - Insert labels in the original text, for example: [John Doe | PERSON] is on his way.
        write_statistics - write # of correct annotations and # of filtered out annotations in a separate file. 
                            Also output the false annotations in the file.
    """

    start_time = datetime.now()  # record start time and later, the end time

    hearing_text_into_annotations(create_annotation_output_file=True,
                                  insert_labels_in_text=True,
                                  write_statistics=True,
                                  batch_size=file_count)

    # output start time and end time
    print(f"\nStarted at: {start_time.strftime('%d.%m.%Y %H:%M:%S')}")
    end_time = datetime.now()
    print(f"Ended at: {end_time.strftime('%d.%m.%Y %H:%M:%S')}")
    print(HelperFunctions.time_difference(start_time, end_time))


if __name__ == "__main__":
    main()
