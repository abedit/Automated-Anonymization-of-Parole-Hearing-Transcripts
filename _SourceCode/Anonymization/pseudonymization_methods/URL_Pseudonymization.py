
from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity



def pseudonymize_url_labels(annotations):
    """
    Filters the annotations to only hold the URL label.
    Urls are then saved in a map so that if the same url value is occurred more than once,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.
    Parameters:
        annotations (list): The list of Annotation items
    Returns:
        List of NameEntity for url values with the 'replacement' variable filled.
    """

    url_count = 1
    urls = list(
        set([item for item in annotations if item.label == Constants.LABEL_URL and item.preview]))
    urls = [NameEntity(name=item.preview, annotation_id=item.annotation_id) for item in urls]
    url_map = {}

    for url in urls:
        if url.name.lower() not in url_map:
            pseudo_url = "URL_" + str(url_count)
            url_count += 1
            url_map[url.name.lower()] = pseudo_url
        else:
            pseudo_url = url_map[url.name.lower()]

        url.name_replacement = '[' + pseudo_url + ']'

    return urls
