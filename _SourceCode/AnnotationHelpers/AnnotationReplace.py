import re

from _SourceCode import Constants
from _SourceCode.HelperFunctions import clean_name


def insert_into_annotations(
        annotations,
        names=None,
        locations=None,
        organizations=None,
        nrps=None,
        dates=None,
        times=None,
        ids=None,
        spelled_names=None,
        ages=None,
        heights=None,
        phone_numbers=None,
        emails=None,
        urls=None,
        spelled_out_items=None,

):
    """
    Insert the replacements in the NameEntity entities into the Annotation object
    The way it's done is to look by annotationId for all labels except the PERSON labels
    """
    if organizations is None:
        organizations = list()
    for annotation in annotations:
        match annotation.label:
            case Constants.LABEL_PERSON:
                if names:
                    name = clean_name(annotation.preview).title()
                    name_entity = next((person for person in names if person.name == name), None)
                    if name_entity is not None and name_entity.name_replacement:
                        if name_entity.name == name:
                            annotation.replacement = name_entity.name_replacement.upper() if annotation.preview.isupper() else name_entity.name_replacement.title()

            case Constants.LABEL_LOCATION:
                if locations:
                    location_entity = next((item for item in locations if item.annotation_id == annotation.annotation_id), None)
                    if location_entity is not None:
                        annotation.replacement = location_entity.name_replacement.upper() if annotation.preview.isupper() else location_entity.name_replacement

            case Constants.LABEL_ORGANIZATION:
                if organizations:
                    organization_entity = next((item for item in organizations if item.annotation_id == annotation.annotation_id), None)
                    if organization_entity is not None:
                        annotation.replacement = organization_entity.name_replacement.upper() if annotation.preview.isupper() else organization_entity.name_replacement

            case Constants.LABEL_NRP:
                if nrps:
                    nrp_entity = next((item for item in nrps if item.annotation_id == annotation.annotation_id), None)
                    if nrp_entity is not None:
                        annotation.replacement = nrp_entity.name_replacement.upper() if annotation.preview.isupper() else nrp_entity.name_replacement

            case Constants.LABEL_DATE:
                if dates:
                    date_entity = next((item for item in dates if item.annotation_id == annotation.annotation_id), None)
                    if date_entity is not None:
                        annotation.replacement = date_entity.name_replacement

            case Constants.LABEL_TIME:
                if times:
                    time_entity = next((item for item in times if item.annotation_id == annotation.annotation_id), None)
                    if time_entity is not None:
                        annotation.replacement = time_entity.name_replacement

            case Constants.LABEL_ID:
                if ids:
                    id_entity = next((item for item in ids if item.annotation_id == annotation.annotation_id), None)
                    if id_entity is not None:
                        annotation.replacement = id_entity.name_replacement

            case Constants.LABEL_SPELLED_NAME:
                if spelled_names:
                    spelled_name_entity = next((item for item in spelled_names if item.annotation_id == annotation.annotation_id), None)
                    if spelled_name_entity is not None:
                        annotation.replacement = spelled_name_entity.name_replacement

            case Constants.LABEL_AGE:
                if ages:
                    age_entity = next((item for item in ages if item.annotation_id == annotation.annotation_id), None)
                    if age_entity is not None:
                        annotation.replacement = age_entity.name_replacement

            case Constants.LABEL_HEIGHT:
                if heights:
                    height_entity = next((item for item in heights if item.annotation_id == annotation.annotation_id), None)
                    if height_entity is not None:
                        annotation.replacement = height_entity.name_replacement

            case Constants.LABEL_PHONE_NUMBER:
                if phone_numbers:
                    phone_number_entity = next((item for item in phone_numbers if item.annotation_id == annotation.annotation_id), None)
                    if phone_number_entity is not None:
                        annotation.replacement = phone_number_entity.name_replacement

            case Constants.LABEL_EMAIL_ADDRESS:
                if emails:
                    email_entity = next((item for item in emails if item.annotation_id == annotation.annotation_id), None)
                    if email_entity is not None:
                        annotation.replacement = email_entity.name_replacement

            case Constants.LABEL_URL:
                if urls:
                    spelled_entity = next((item for item in urls if item.annotation_id == annotation.annotation_id), None)
                    if spelled_entity is not None:
                        annotation.replacement = spelled_entity.name_replacement

            case Constants.LABEL_SPELLED_OUT_ITEM:
                if spelled_out_items:
                    spelled_entity = next(
                        (item for item in spelled_out_items if item.annotation_id == annotation.annotation_id), None)
                    if spelled_entity is not None:
                        annotation.replacement = spelled_entity.name_replacement

    return annotations


def annotate_text(text, annotations):
    """
    Insert labels into the text in a way the text looks like this:
    [John Doe | PERSON] is a pharmacist in [New York | LOCATION].
    """
    annotations.sort(key=lambda x: int(x.start), reverse=True)
    for ann in annotations:
        label_insertion = f" | {ann.label}]"
        start = int(ann.start)
        end = int(ann.end)
        text = text[:start] + "[" + text[start:end] + label_insertion + text[end:]

    return text

