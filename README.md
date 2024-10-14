# Automated Anonymization of Parole Hearing Transcripts

---

## Table of Contents

- [This project in a nutshell (A brief summary)](#this-project-in-a-nutshell-a-brief-summary)
- [Packages to install first](#packages-to-install-first)
- [How to run the programs](#how-to-run-the-programs)
  - [Converting the transcript files into text files](#converting-the-transcript-files-into-text-files)
  - [Running the NER tools](#running-the-ner-tools)
  - [Applying the Pseudonymization method](#applying-the-pseudonymization-method)
- [NER tools used](#ner-tools-used)
- [Annotation filtering](#annotation-filtering)
- [Annotation Post-processing](#annotation-post-processing)
- [Libraries used in anonymization](#libraries-used-in-anonymization)
- [Anonymization Method - Pseudonymization](#anonymization-method---pseudonymization)

--- 

## This project in a nutshell (A brief summary)
3 main files:
* [HearingsPDFs2Text.py](HearingsPDFs2Text.py) - convert transcripts from PDF to txt files
* [GatherAnnotations.py](GatherAnnotations.py) - Run the automatic annotation on every transcript text file
* [Anonymization.py](Anonymization.py) - Apply given anonymization methods on the transcript texts

3 NER tools (Presidio, spaCy and StanfordNER) + Regular expressions are used on transcripts coming from the California Department of Corrections and Rehabilitation (CDCR) to detect personally identifiable information as annotations. The transcripts have a consistent format that allows the extraction of information from the first page.

Unlikely and false annotations are filtered out, merged into 1 list of annotations then cleaned to be used in the Pseudonymization method. 

Pseudonymization method implemented, with the focus of keeping the text around the annotations untouched for the data to be usable. It replaces detected annotations with their label type and an identifier for unique values, e.g. `[PERSON_1]`, `[PERSON_2]`... DATE, TIME and AGE entities are assigned an identifier but without the sequential number at the end, e.g. `[DAY_OF_WEEK]`, `[NUMBER]`...

---

# Packages to install first:
The project was done on Windows 11 with Python version `3.10.11`. `pip` version used is `23.1.2`.
The libraries used are the following:

* spacy==3.7.5
* transformers==4.45.2
* presidio_analyzer==2.2.354
* tokenizers==0.20.1
* en_core_web_trf==3.7.3 (Model for spaCy, downloaded from the original repository [here](https://github.com/explosion/spacy-models/releases/en_core_web_trf-3.7.3/), see [requirements.txt](requirements.txt))
* en_core_web_lg==3.7.1 (Model for Presidio, downloaded from the original repository [here](https://github.com/explosion/spacy-models/releases/en_core_web_lg-3.7.1/), see [requirements.txt](requirements.txt))
* torch==1.13.1
* inflect==7.3.1
* nltk==3.6.7
* pdfplumber==0.11.0
* python_dateutil==2.8.2
* word2number==1.1

You can use the [requirements.txt](requirements.txt) file to install them by running this command:
    
    pip install -r requirements.txt



# How to run the programs:

This section explains how to run the thesis program.
There are 3 main classes that can be run with each having a pre-condition that needs to be satisfied.

## Converting the transcript files into text files
The purpose of [HearingsPDFs2Text.py](HearingsPDFs2Text.py) is to convert hearing PDF files into text files (txt file format) with each utterance being on a single line and ignoring the second page as it's only the index and does not have important information.

### Command to run [HearingsPDFs2Text.py](HearingsPDFs2Text.py):

    python HearingsPDFs2Text.py

### Pre-condition
Must have a folder named `Hearing transcripts (PDF)` in the project directory with the parole hearing transcripts inside as PDF files.

### Output
A folder named `Hearing transcripts (Text)` is created containing the parole hearing transcripts converted to text files. 



---

## Running the NER tools
Running [GatherAnnotations.py](GatherAnnotations.py) file will initialize and apply the automatic annotation on every file inside the `Hearing transcripts (Text)` folder.

### Command to run [GatherAnnotations.py](GatherAnnotations.py):

    python GatherAnnotations.py

**❗NOTE ❗:** It is possible to pass an argument to have the automatic annotation process more than 1 file at a time. It can be done by passing the flag `--file_count` and the number of files to process at a time.

    python GatherAnnotations.py --file_count 3

`file_count` has a maximum value of 5 files, as processing 5 or more files at the same time will cause the device to lag and become slow. 

I recommend to process 3 files at a time as it does not slow the PC a lot and it results in a **very slightly** faster processing time vs processing 1 file at a time.

If you're unsure how much to pass in the argument, a value of 1 doesn't hurt.


### Pre-condition

Must have the `Hearing transcripts (Text)` folder in the project directory with the parole hearing transcripts as text files inside.

### Output
2 folders, `Annotations Output` and `Annotations JSON`, are created. The `Annotations JSON` folder contains a json file that has data about each transcript file name and its detected annotations. 

This json file is named `processed_annotations.json`. Whenever new annotation data comes in, it is appended in the json file as to not lose previous data. If new annotations come in for a file that already has annotations, the new annotations will override the old ones.

For instance, if the automatic annotation process is run on 3 hearing files, then the json will contain the annotations for the 3 hearing files. If the process is run on an extra file, the json will contain data about the 4 hearing files. Finally, if the process is run on a file that has already been processed, the new annotation data replaces the old data based on the name of the file.

Here is what the json structure looks like:

    [
      {
        "file": "[FILENAME HERE]"
        "annotations":
        [
          {
                "start": 37,
                "end": 47,
                "label": "LOCATION",
                "preview": "CALIFORNIA",
                "source": "StanfordNER"
          },
          ...
        ],
        ...
      }
    }




The `Annotations Output` folder contains the detected annotation for each file. Running the NER tools on a single transcript will create the following text files:
* A file with the same name as the original transcript with the detected annotations inserted into the original text. For example, if "Mr Michael Jordan" is present in the original transcript file, this file will have "Mr [Michael Jordan | PERSON]" with the label type present next to the detected annotations. This file is done to review the detected annotations from the original file.
* A file having the same name as the original transcript file but with `_ANNOTATIONS` appended at the end. The `GatherAnnotations.py` returns a list of [Annotation](_SourceCode/ModelClasses/Annotation.py) objects for each transcript. This file lists the content of each Annotation object such as the start position in the hearing text file, the end position, label type, text and NER tool source for each annotation detected.
* A file having the same name as the original but with `_STATS` appended at the end. This file contains the number of correct annotations detected in the original transcript text file, the number of filtered out annotations and they are then listed in the same `_STATS` file.

For example, the following is an illustration of what the project's directory tree looks like after running the [GatherAnnotations.py](GatherAnnotations.py) file:


    root/
    ├── GatherAnnotations.py
    ├── Annotations JSON/
    │   └── processed_annotations.json
    ├── Annotations Output/
    │   ├── *original transcript file name*.txt
    │   ├── *original transcript file name*_ANNOTATION.txt
    │   ├── *original transcript file name*_STATS.txt
    │   └── ...



---

## Applying the Pseudonymization method
The [Anonymization.py](Anonymization.py) file serves as an entry point for the anonymization methods. This file requires an argument to specify which anonymization method to use on the hearing transcript files.

### Command to run `Anonymization.py`
    python Anonymization.py 

## Pre-condition
Must have the json file inside `Annotations JSON` folder that is created from running the [GatheringAnnotations.py](GatherAnnotations.py) file.

## Output
A folder named `Anonymization Output` is created. Running an anonymization method creates a folder inside the `Anonymization Output` folder named `anonymization_output_PSEUDONYMIZATION`. 


The Pseudonymization method generates an extra folder named `anonymization_output_PSEUDONYMIZATION_INDEX` when run. The `_INDEX` folder contains files with the original file names but the transcripts but with `PSEUDONYMIZATION_INDEX` at the end and serves as index files with each containing the label type and the annotation values as well as their anonymized values.

For example, the following is an illustration of what the directory tree looks like after running the Pseudonymization method:

    Anonymization Output/
    ├── anonymization_output_PSEUDONYMIZATION/
    │   ├── *pseudonymized file name*.txt
    │   └── ...
    ├── anonymization_output_PSEUDONYMIZATION_INDEX/
    │   ├── *original transcript file name*_PSEUDONYMIZATION_INDEX.txt
    │   └── ...

---

# NER tools used

## Presidio: https://microsoft.github.io/presidio/

Presidio is a Data Protection and De-identification SDK by Microsoft. It's main task is identifying and anonymization sensitive information in texts and images like names, locations, phone numbers...

Integration was simple and it's easy to use. It takes a list of entities that you want to be detected.
See https://microsoft.github.io/presidio/supported_entities/

You can also give it custom recognizers with regular expressions for certain items. 

See file [PresidioRecognizers.py](PresidioRecognizers.py)

## Spacy: https://spacy.io/
SpaCy is a library for Natural Language Processing tasks such as tokenization, Parts of speech tagging, Named Entity Recognition, lemmatization and many more

SpaCy's 'en_core_web_trf' is used in this project. It can detect PERSON, GPE (Renamed to LOCATION), DATE, TIME and CARDINAL.


## StanfordNER: https://nlp.stanford.edu/software/CRF-NER.html
Stanford NER is a java implementation of a named entity recognizer. It has models trained on annotated data.
The 3 class one is used which detects PERSON, LOCATION, ORGANIZATION

We used the Stanford NER model, which is available under the GNU General Public License v2 or later. The model files can be downloaded from the official website at https://nlp.stanford.edu/software/CRF-NER.html.


# Annotation filtering

For each tool, A check is run on each label and filter out any annotation that is false. This is done by conditions on each entity type/label. 

See [AnnotationChecker.py](AnnotationHelpers/AnnotationChecker.py).


# Annotation Post-processing
The annotations retrieved from all 3 tools are then placed together. In Presidio's case and StandfordNER's case, the adjacent annotations are merged. For example: John (PERSON) Doe (PERSON) is a person.

If the annotations are separated by a space and they are the same label (PERSON), it's best to put them together: John Doe (PERSON).

The combined annotations are then cleaned: 
- Duplicates are removed
- In case there are overlaps, they are separated.
- If there are cases where there are multiple annotations with same start or same ends, take the longest one

See [AnnotationCleaner.py](AnnotationHelpers/AnnotationCleaner.py)

--- 

# Libraries used in anonymization:
- bart_large_mnli - zero shot model by Facebook - https://huggingface.co/facebook/bart-large-mnli
- inflect - https://github.com/jaraco/inflect
- word2number - https://github.com/akshaynagpal/w2n


---

# Anonymization Method - Pseudonymization:

The Pseudonymization method requires all entities to have their own logic. The aim is to produce labels with a sequential number like [PERSON_1] and [PERSON_2] which are assigned to unique names in the transcript.

A dictionary is used in every entity to make sure the proper sequential number is assigned to the pseudonymized value.

### PERSON
The logic consists of replacing each part of the full name with PERSON_X with X being a counter.

Then the other names follow the same logic.

We have a John Doe and the victim is Jane Smith. ➡️ We have a [PERSON 1] [PERSON 2] and the victim is [PERSON 3] [PERSON 4].

### SPELLED_NAME

The spelled name is normalized and then checked into the name map. Then take whatever replacement is for that name and replace the PERSON_ part with SPELLED_NAME_PERSON_. So if Nathan Fillion has pseudonymized value of PERSON_5, then the spelled name becomes SPELLED_NAME_PERSON_5.

### Organization

ORGANIZATION labels are pseudonymized based on their values. Values are saved in a map as well as their pseudonymized value. So that if the same value occurs, it would have the same pseudonymized value.

If the organization contains certain values like Prison, Jail... the pseudonymization is set as PRISON_X, JAIL_X... With each type of organization having its own counter.

### Email
The pseudonymization of each unique EMAIL_ADDRESS is assigned an [EMAIL_ADDRESS_1], [EMAIL_ADDRESS_2]... tag.

### URL Labels

Same logic as EMAIL_ADDRESS labels.

### ID 

Same logic. The letter part is removed and the number part is pseudonymized and saved in a map. The pseudonymized value is a tag [ID_1], [ID_2]...

### Location labels

Same logic as the previous labels but depending on the zero shot model's answer, the location is pseudonymized like this:
* if it's a state ➡️ STATE_X
* Country ➡️ COUNTRY_X


### NRP

Same logic as the LOCATION labels, depending on the zero shot classification model's answer, it could be RELIGION_X, NATIONALITY_X...

### Phone Numbers
Each unique value is pseudonymized as PHONE_NUMBER_X...

### Spelled out items
Each unique value is pseudonymized as SPELLED_OUT_ITEM...

### Date labels

The DATE labels are pseudonymized based the following cases.

* A full date like 12/23/2016 ➡️ [DATE]
* A year like 2013 ➡️ [YEAR]
* A number like 23 -> [NUMBER]
* A month February ➡️ [MONTH]. 
* A day of the week. Wednesday ➡️ [DAY_OF_WEEK]
* Ordinal number like 12th ➡️ [DAY]
* Decade like 20s, 30s ➡️ [DECADE]

### Time labels

Time annotations are replaced with [TIME] placeholders.

### Age

Numerical values in AGE annotations are replaced with [AGE] placeholders.


### Height

Numbers in the height string are pseudonymized by replacing the number part in the annotation value by [HEIGHT_X]...

--- 
