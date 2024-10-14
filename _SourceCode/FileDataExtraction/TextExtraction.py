import itertools

import pdfplumber
import re
import _SourceCode.Constants as Constants
import os


def write_pdfs_into_txt_files(input_directory, output_directory):
    """
    Write pdf data into txt files
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    corrupted_files = []

    for filename in os.listdir(input_directory):
        file_path = os.path.join(input_directory, filename)
        if filename.lower().endswith('.pdf'):

            is_file_corrupted = is_pdf_corrupted(file_path)
            if is_file_corrupted:  # add to a list to output later
                corrupted_files.append(file_path)
                continue

            extracted_text = pdf_to_text(file_path)
            output_file_path = os.path.join(output_directory, os.path.splitext(filename)[0] + '.txt')
            with open(output_file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(extracted_text)
            print("Processed ", filename, " -> ", os.path.basename(output_file_path))

    if corrupted_files: # output the list of files that are corrupted
        print("\n\nThe following files were detected as corrupted: ")
        for item in corrupted_files:
            print(item)

import threading

file_access_lock = threading.Lock()
def extract_text_from_txt_file(file_name):
    """
    Extract text from PDF files in the hearing_txt directory
    """
    file_path = os.path.join(Constants.hearings_txt_directory, file_name)
    try:
        with file_access_lock:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        return text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\n ').replace('—', '-')
    except FileNotFoundError:
        print(f"ERROR: {file_path} does not exist.")
        return None


def extract_text_from_txt_file_directory(directory, file_name):
    """
    Extract text from text files given a directory
    """
    file_path = os.path.join(directory, file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            return text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\n ').replace('—', '-')
    except FileNotFoundError:
        print(f"ERROR: {file_path} does not exist.")
        return None


def pdf_to_text(pdf_path):
    """
    This function is customized towards the hearing files
    Get text from the PDF file with some added logic for the 2nd page and the last 2 pages.
    The main text will be cleaned so that each utterance is on 1 line.
    2nd page is the index which isn't important so it's skipped
    The last 2 pages contain the adjournment message which just needs to be appended at the end
    """
    extracted_text = []
    first_page_text = ""
    last_pages_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):

            # first page - take the data as is
            if page.page_number == 1:
                first_page_text = page.extract_text()

            # 2nd page - skip
            elif page.page_number == 2:
                continue

            # Main text data
            elif i < (total_pages - 2):
                temp_text = clean_text(text=page.extract_text())
                # sometimes "THIS TRANSCRIPT CONTAINS THE PROPOSED DECISION..." is present in the page
                # we don't need that part
                if Constants.adjournment_message in temp_text:
                    adjournment_index = temp_text.find(Constants.adjournment_message)
                    text_before_adjournment = temp_text[:adjournment_index]
                    extracted_text.append(text_before_adjournment)
                    last_pages_text = last_pages_text + "\n" + temp_text[adjournment_index:]
                elif Constants.hearing_decision_message in temp_text:
                    # same for "DECISION..."
                    extracted_text.append(temp_text[len(Constants.hearing_decision_message):])
                else:
                    extracted_text.append(temp_text)

            else:  # logic for last 2 pages which are the adjournment and transcriptor statement
                temp_text = page.extract_text()
                temp_text = temp_text[temp_text.find('\n') + 1:]
                cleaned_text = clean_text(text=temp_text)
                last_pages_text = last_pages_text + ("\n" if i < total_pages - 1 else "\n\n") + cleaned_text
            extracted_text.append('\n\n')

    joined_text = "\n".join(extracted_text)

    # in some cases where there is text written on the adjournment page, we need those as well.
    if 'ADJOURNMENT' in last_pages_text.split('\n'):
        for index, item in enumerate(last_pages_text.split('\n')):
            if item == 'ADJOURNMENT':
                last_pages_text = "\n".join(last_pages_text.split('\n')[index:])
                break
            if item:
                joined_text += f'\n{item}'
    formatted_text = utterances_one_line(joined_text)
    return first_page_text + "\n\n\n" + formatted_text + "\n\n\n" + last_pages_text


def clean_text(text):
    """
    Remove page numbers and "conduit transcriptions" which are present in every page
    """
    cleaned_lines = []
    for line in text.split('\n'):
        """
        Skip line if it's:
        1- just "Conduit Transcriptions"
        2- just a number
        3- in the form of "PAGE " followed by a number
        """
        if line.strip() == "Conduit Transcriptions" or line.strip().isdigit() \
                or re.search(r"PAGE \d+$", line):
            continue

        # Remove line numbers from every line
        line = re.sub(r'^\d+\s+', '', line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).replace('—', '-')


def generate_name_combinations(names):
    """
    If for example someone's name is "Lorenz San Juan"
    We must account for name combinations in case "San Juan" appears in the text
    So combinations can look like: Lorenz San, San Juan, Lorenz San Juan
    """
    combinations = []
    for name in names:
        parts = name.split()

        for i in range(len(parts)):
            for j in range(i + 1, len(parts) + 1):
                combination = ' '.join(parts[i:j])
                if '.' in combination and len(combination.replace('.', '')):
                    continue
                combinations.append(combination)

    return combinations


def utterances_one_line(text):
    """
    Now that we got the main text from the PDF, we have to make each utterance to be on 1 line
    We can distinguish a speaker change by checking for ':'
    """
    current_speaker = None
    current_speaker_text = []
    formatted_text = []
    lines = text.split('\n')
    for line in lines:
        # Check for speaker change by checking if there's a ':'
        if ':' in line and line.split(':')[0].isupper() and len(line.split(':')[0].split()) <= 5:

            if current_speaker_text and current_speaker:
                formatted_text.append(f"{current_speaker}: {' '.join(current_speaker_text)}")

            current_speaker = line.split(':')[0].strip()
            current_speaker_text = [line.split(':')[1].strip()] if len(line.split(':')) > 1 else []
        else:
            current_speaker_text.append(line.strip())

    if current_speaker_text and current_speaker:
        formatted_text.append(f"{current_speaker}: {' '.join(current_speaker_text)}")
    return '\n\n'.join(formatted_text).replace("    ", " ").replace("   ", " ").replace("  ", " ")


def is_pdf_corrupted(file_path):
    """
    Checks if the current PDF file is corrupted or not.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                _ = page.extract_text()
        return False
    except IOError:
        print(file_path + " is most likely corrupted.")
        return True