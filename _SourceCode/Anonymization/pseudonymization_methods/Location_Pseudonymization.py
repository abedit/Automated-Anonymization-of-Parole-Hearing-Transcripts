import re


from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity
from _SourceCode.ToolsUtils import Classifier

location_labels = ["Zip Code", "zip", "zipcode", "Address", "Country", "State", "City", "Miscellaneous"]
location_suffixes = {
    "Zip Code": ("Zip Code", 'zip_code_count'),
    "zip": ("Zip Code", 'zip_code_count'),
    "zipcode": ("Zip Code", 'zip_code_count'),
    "Address": ("Address", 'address_count'),
    "Country": ("Country", 'country_count'),
    "State": ("State", 'state_count'),
    "City": ("City", 'city_count'),
    "Miscellaneous": ("Miscellaneous", 'location_count'),
}
county_count = 1
zip_code_count = 1
address_count = 1
country_count = 1
state_count = 1
city_count = 1
location_count = 1


def pseudonymize_location_labels(annotations):
    """
    Filters the annotations to only hold the location label.
    Locations are then pseudonymized and saved in a map so that if the same location value is occurred more than once,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.
    The process is to use a zero shot model to figure out what kind of location we have and then
     pseudonymize a new value based on what the zero shot model says

    Parameters:
        annotations (list): The list of Annotation items

    Returns:
        List of NameEntity for Location values with the 'replacement' variable filled.
    """
    global zip_code_count, address_count, country_count, state_count, city_count, location_count
    global county_count
    county_count = 1
    zip_code_count = 1
    address_count = 1
    country_count = 1
    state_count = 1
    city_count = 1
    location_count = 1

    locations = list(
        set([item for item in annotations if item.label == Constants.LABEL_LOCATION and item.preview]))
    locations = [NameEntity(name=item.preview, all_caps=item.preview.isupper(), annotation_id=item.annotation_id) for
                 item in locations]

    locations.sort(key=lambda x: len(x.name))
    location_map = {}

    for location in locations:
        # if the location has 'county' in it, take a pseudonymized county from the list of counties
        if 'county' in location.name.lower():
            if location.name.title() in location_map:
                pseudo_location = location_map[location.name.title()]
            else:
                pseudo_location = ("COUNTY_" if location.name.isupper() else "County_") + str(county_count)
                county_count += 1
                location_map[location.name.title()] = pseudo_location
            location.name_replacement = '[' + (pseudo_location.upper() if location.name.isupper() else pseudo_location) + ']'
            continue

        pseudo_location = _get_pseudonymized_location(location.name, location_map)
        if location.all_caps:
            pseudo_location = pseudo_location.upper()

        location.name_replacement = '[' + pseudo_location.replace("\n", ". ") + ']'
    return locations


def _get_pseudonymized_location(location, location_map):
    """
    Get a pseudonymized location. If it's already present in the location_map, then return it.
    Otherwise generate a new one and add it to the map.

    Parameters:
        location (str): The original location
        location_map (dict): The map of Location and it's already generated pseudonymized values

    Returns:
        str: a pseudonymized location value
    """

    if not location.strip():
        return ''

    if location.title() in location_map:
        return location_map[location.title()]
    else:
        location_parts = re.findall(Constants.split_string_pattern, location)
        # see if part of it is in the map, if it's the case the return that
        # part's pseudonymized value
        for part in location_parts:
            if part.title() in location_map:
                return location_map[part.title()]

        # else pseudonymize the current value and add it to the map
        pseudo_location = _pseudonymize_value(location).title()
        location_map[location.title()] = pseudo_location.title()
        return pseudo_location


def _pseudonymize_value(location):
    """
    Get the type of location from the zero shot model and generate a pseudonymized location value based on
    the location type

    Parameters:
        location (str): The original location

    Returns:
        str: a pseudonymized location value
    """

    global location_count
    global zip_code_count, address_count, country_count, state_count, city_count, location_count

    location_type = Classifier.classify_entity(location, location_labels)
    if location_type is None:
        pseudo_location = "Location_" + str(location_count)
        location_count += 1
        return pseudo_location

    # Check location labels to see if the current location value contains one of the location suffixes
    for key, (suffix, counter_name) in location_suffixes.items():
        if key.lower() in location_type.lower():
            pseudo_location = suffix.replace(' ', '_').upper() + '_' + str(globals()[counter_name])
            globals()[counter_name] += 1
            return pseudo_location

    # Else just return Location_X
    pseudo_location = "Location_" + str(location_count)
    location_count += 1
    return pseudo_location
