from datetime import datetime

from _SourceCode import Constants, HelperFunctions
from _SourceCode.Anonymization import AnonymizationMain

start_time = datetime.now()  # record start time and later, the end time

AnonymizationMain.anonymization_entry_point()

# output start time and end time
print(f"\nStarted at: {start_time.strftime('%d.%m.%Y %H:%M:%S')}")
end_time = datetime.now()
print(f"Ended at: {end_time.strftime('%d.%m.%Y %H:%M:%S')}")
print(HelperFunctions.time_difference(start_time, end_time))
