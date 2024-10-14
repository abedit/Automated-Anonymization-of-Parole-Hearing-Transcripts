import re

from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity

uni_count = 1
school_count = 1
prison_count = 1
hospital_count = 1
jail_count = 1
asylum_count = 1
police_count = 1
facility_count = 1
senate_count = 1
training_count = 1
group_count = 1
bank_count = 1
program_count = 1
board_count = 1
office_count = 1
factory_count = 1
organization_count = 1


def pseudonymize_organization_labels(annotations, org_map):
    """
    Filters the annotations to only hold the ORGANIZATION label.
    Organizations are then pseudonymized and saved in a map so that if the same Organization value is occurred more than once,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.
    The process is to use a zero shot model to figure out what kind of Organization we have and then return a value with the sequential number
    based on the value returned from the model

    Parameters:
        annotations (list): The list of Annotation items
        org_map (dict): The organization map to be filled
    Returns:
        List of NameEntity for Organization values with the 'replacement' variable filled.
    """
    global uni_count, school_count, prison_count, hospital_count, jail_count, asylum_count, police_count, facility_count, senate_count, training_count, group_count, bank_count, program_count, board_count, office_count, factory_count
    global organization_count

    uni_count = 1
    school_count = 1
    prison_count = 1
    hospital_count = 1
    jail_count = 1
    asylum_count = 1
    police_count = 1
    facility_count = 1
    senate_count = 1
    training_count = 1
    group_count = 1
    bank_count = 1
    program_count = 1
    board_count = 1
    office_count = 1
    factory_count = 1
    organization_count = 1

    organizations = list(
        set([item for item in annotations if item.label == Constants.LABEL_ORGANIZATION]))
    organizations = [NameEntity(name=item.preview, all_caps=item.preview.isupper(), annotation_id=item.annotation_id)
                     for item in organizations]
    organizations.sort(key=lambda x: len(x.name))

    for organization in organizations:
        pseudo_org = _get_pseudonymized_org(organization.name, org_map)

        if organization.all_caps:
            pseudo_org = pseudo_org.upper()

        organization.name_replacement = '[' + pseudo_org + ']'

    return organizations


def _get_pseudonymized_org(original_org, org_map):
    """
    Get a pseudonymized Organization. If it's already present in the Organization_map, then return it.
    Otherwise, generate a new one and add it to the map.

    Parameters:
        original_org (str): The original Organization
        org_map (dict): The map of Organization and it's already generated pseudonymized values

    Returns:
        str: a pseudonymized Organization value
    """

    if original_org.title() in org_map:
        pseudo_name = org_map[original_org.title()]
        return pseudo_name.upper() if original_org.isupper() else pseudo_name

    pseudo_name = ""
    # check each part if it was already pseudonymized
    for key in org_map.keys():
        pattern = r'\b' + key + r'\b'
        if re.search(pattern, original_org, flags=re.IGNORECASE) is not None:
            pseudo_name = org_map[key]

    if pseudo_name:
        return pseudo_name.upper() if original_org.isupper() else pseudo_name

    pseudo_org = _pseudonymize_organization(original_org).title()
    org_map[original_org.title()] = pseudo_org

    return pseudo_org.upper() if original_org.isupper() else pseudo_org


def _pseudonymize_organization(original_org):
    """
    Generates a pseudonymized organization name based on if the original org contains some keywords,
    otherwise, generate pseudonymized company names

    Parameters:
        original_org (str): The original Organization
    Returns:
        str: a pseudonymized Organization value
    """
    global uni_count, school_count, prison_count, hospital_count, jail_count, asylum_count, police_count, facility_count, senate_count, training_count, group_count, bank_count, program_count, board_count, office_count, factory_count
    global organization_count

    keywords_suffixes = {
        "university": ("University", 'uni_count'),
        "school": ("School", 'school_count'),
        "prison": ("Prison", 'prison_count'),
        "hospital": ("Hospital", 'hospital_count'),
        "jail": ("Jail", 'jail_count'),
        "asylum": ("Asylum", 'asylum_count'),
        "police|pd$": ("Police_Department", 'police_count'),
        "facility|facilities": ("Facility", 'facility_count'),
        "senate": ("Senate", 'senate_count'),
        "training": ("Training", 'training_count'),
        "group": ("Group", 'group_count'),
        "bank": ("Bank", 'bank_count'),
        "program": ("Program", 'program_count'),
        "board": ("Board", 'board_count'),
        "office": ("Office", 'office_count'),
        "factories|factory": ("Factory", 'factory_count'),
        "industries|industry": ("Factory", 'factory_count'),
    }

    pseudonymized_value = ""
    # Check each keyword and assign the corresponding value
    for keyword, (suffix, counter_name) in keywords_suffixes.items():
        if re.search(keyword, original_org, flags=re.IGNORECASE):
            pseudonymized_value += (suffix.upper() if original_org.isupper() else suffix) + '_' + str(
                globals()[counter_name])
            globals()[counter_name] += 1
            break

    if pseudonymized_value:
        return pseudonymized_value
    else:
        pseudonymized_org = "ORGANIZATION_" + str(organization_count)
        organization_count += 1

        return pseudonymized_org
