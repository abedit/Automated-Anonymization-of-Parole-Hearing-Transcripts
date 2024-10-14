import re
from _SourceCode import Constants, HelperFunctions


def get_names_from_first_page(text):
    """
    Get the names that are present in the first page of the text.
    Additionally, get the organization where the inmate is held.
    This is also present in the first page.
     The 'text' is a string of the first page data
    """
    names = []
    organization = None
    location_line = None
    text_lines = text.split('\n')

    check_next_line = False
    header_line = ''

    if not HelperFunctions.contains_keywords(text, [item.lower() for item in Constants.first_page_names_headers]):
        return None, None, None

    for index, line in enumerate(text_lines):
        # if a header such as "PANEL PRESENT" or "OTHERS PRESENT" is present in the line,
        # the lines after contain names that needed to be extracted
        # set a flag to check them in the next loop iteration
        if any(header in line for header in Constants.first_page_names_headers):
            header_line = line
            check_next_line = True
            continue

        # should the code check the next line, extract the names, organization name and location
        if check_next_line and not re.search(r'\d', line):
            if ',' not in line and not header_line.isupper():
                names.append(line)
                if not organization and index + 1 < len(text_lines):
                    organization = text_lines[index + 1].strip()

                    # location is usually after the organization
                    if not location_line and index + 2 < len(text_lines):
                        location_line = text_lines[index + 2].strip()
                header_line = ''
            else:  # sometimes "unidentified" is present instead of an actual name, in that case
                # it is not needed
                if 'unidentified' not in line.lower():
                    comma_index = line.find(',')
                    if comma_index != -1:
                        names.append(line[:comma_index])
                    else:
                        upper_names = [item for item in line.split() if item.isupper()]
                        if upper_names:
                            names.append(' '.join(upper_names))

            if index + 1 < len(text_lines):
                # check if the next line is not one of the headers and as long as the current header is not uppercase
                check_next_line = (
                        not any(header in text_lines[index + 1] for header in Constants.first_page_names_headers)
                        and (check_next_line and header_line and header_line.isupper())
                )

        else:
            continue

    return list(set(names)), location_line, organization
