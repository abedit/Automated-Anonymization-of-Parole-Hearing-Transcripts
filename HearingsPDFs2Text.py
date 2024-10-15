import os
from datetime import datetime

from _SourceCode import Constants, HelperFunctions
from _SourceCode.FileDataExtraction import TextExtraction


"""
Take pdf files from the "Hearing transcripts (PDF)" folder and convert them to txt files inside the "Hearing transcripts (Text)"
The conversion function will skip the second page in the PDFs since they're just the index for the transcript.
"""

directory = Constants.input_hearings_directory

if not os.path.exists(directory):
    print(f"\nThe folder '{Constants.input_hearings_directory}' does not exist.\n")
else:
    start_time = datetime.now()  # record start time and later, the end time

    TextExtraction.write_pdfs_into_txt_files(Constants.input_hearings_directory, Constants.hearings_txt_directory)

    # output start time and end time
    print(f"\nStarted at: {start_time.strftime('%d.%m.%Y %H:%M:%S')}")
    end_time = datetime.now()
    print(f"Ended at: {end_time.strftime('%d.%m.%Y %H:%M:%S')}")
    print(HelperFunctions.time_difference(start_time, end_time))
