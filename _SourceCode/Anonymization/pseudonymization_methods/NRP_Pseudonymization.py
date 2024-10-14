
from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity
import inflect

from _SourceCode.ToolsUtils import Classifier

nrp_types = ["Person's religion", "Religion name", "Politics", "Political Stance", "Nationality", "Language",
             "Ethnicity"]
inflect_engine = inflect.engine()
religion_count = 1
politics_count = 1
nationality_count = 1
language_count = 1
ethnicity_count = 1
nrp_count = 1


def pseudonymize_nrp_labels(annotations):
    """
    Filters the annotations to only hold the NRP label.
    NRPs are then pseudonymized and saved in a map so that if the same NRP value is occurred more than once,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.
    The process is to replace the type returned from the zero shot classification method and use it as
    label replacement with the sequential number appended at the end

    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for NRP values with the 'replacement' variable filled.
    """
    global religion_count, politics_count, nationality_count, language_count, ethnicity_count, nrp_count

    religion_count = 1
    politics_count = 1
    nationality_count = 1
    language_count = 1
    ethnicity_count = 1
    nrp_count = 1

    nrps = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in annotations if
            item.label == Constants.LABEL_NRP]
    nrp_map = {}

    for nrp in nrps:

        has_a = nrp.name.lower().startswith('a ')
        has_the = nrp.name.lower().startswith('the ')
        has_aa = nrp.name.lower().startswith('aa ')
        has_ex = nrp.name.lower().startswith('ex-')

        current_nrp = nrp.name.title()
        if 'islamic' == nrp.name.lower():  # in this specific case, remove the 'ic' for the nrp_map
            current_nrp = current_nrp[:-2]

        if has_a or has_the or has_aa:
            split_nrp = current_nrp.lower().split()
            if len(split_nrp) > 1:
                current_nrp = ' '.join(split_nrp[1:len(split_nrp)])
        elif has_ex:
            current_nrp = current_nrp.lower().replace('ex-', '')

        singular_word = inflect_engine.singular_noun(current_nrp.title())
        if not singular_word:  # if word is not plural, singular_noun() returns False
            singular_word = current_nrp.title()

        pseudo_nrp = _get_pseudo_NRP_w_map(nrp_map=nrp_map, singular_word=singular_word)
        nrp.name_replacement = '[' + (pseudo_nrp.upper() if nrp.name.isupper() else pseudo_nrp) + ']'

    return nrps


def _get_pseudo_NRP_w_map(nrp_map, singular_word):
    """
    Takes the nrp_map and the singular word form of the original NRP obtained from the inflect library
    Generates a pseudonymized NRP, compares it to existing values to make sure it's unique, add to map and return it

    Parameters:
        nrp_map (dict): the NRP map and its values
        singular_word (str): the single form of the word obtained thanks to the inflect library
    Returns:
        Returns a random element in the religion_names, religions, political_affiliations or nationalities list
    """

    # if NRP not in the map, use it
    if singular_word in nrp_map:
        pseudo_nrp = nrp_map[singular_word]
    else:
        # Use a zero shot model to figure out if this NRP is
        # a nationality, religion or political affiliation
        nrp_type = Classifier.classify_entity(singular_word, nrp_types)
        pseudo_nrp = _get_pseudo_value(nrp_type)

    nrp_map[singular_word] = pseudo_nrp  # add to map
    return pseudo_nrp


def _get_pseudo_value(nrp_type):
    """
    Take the nrp type from the zero shot model and append the count at the end
    If it's a specific value like "Religion", return "RELIGION_X" with X being a counter

    Parameters:
        nrp_type (str): the nrp type from the zero shot model
    Returns:
        (str) Returns a pseudonymized value under the form of RELIGION_X, NATIONALITY_X...
    """

    global religion_count, politics_count, nationality_count, ethnicity_count, language_count, nrp_count

    if nrp_type is None:
        pseudonymized_value = "NRP_" + str(nrp_count)
        nrp_count += 1
        return pseudonymized_value

    pseudonymized_value = ""
    match nrp_type:
        case "Person's religion":
            pseudonymized_value = "RELIGION_" + str(religion_count)
            religion_count += 1
        case "Religion name":
            pseudonymized_value = "RELIGION_" + str(religion_count)
            religion_count += 1
        case "Politics":
            pseudonymized_value = "POLITICAL_" + str(politics_count)
            politics_count += 1
        case "Political Stance":
            pseudonymized_value = "POLITICAL_" + str(politics_count)
            politics_count += 1
        case "Nationality":
            pseudonymized_value = "NATIONALITY_" + str(nationality_count)
            nationality_count += 1
        case "Ethnicity":
            pseudonymized_value = "ETHNICITY_" + str(ethnicity_count)
            ethnicity_count += 1
        case "Language":
            pseudonymized_value = "LANGUAGE_" + str(language_count)
            language_count += 1

    return pseudonymized_value
