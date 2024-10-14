from _SourceCode import Constants
from _SourceCode.ModelClasses.NameEntity import NameEntity


def pseudonymize_email_labels(annotations):
    """
    Filters the annotations to only hold the EMAIL_ADDRESS label.
    Emails are then saved in a map so that if the same Email value is occurred more than once,
    it will have the same pseudonymized value.
    The pseudonymized values are then filled inside NameEntity's replacement variable.

    Parameters:
        annotations (list): The list of Annotation items

    Returns:
        List of NameEntity for Email values with the 'replacement' variable filled.
    """

    emails = list(
        set([item for item in annotations if item.label == Constants.LABEL_EMAIL_ADDRESS]))
    emails = [NameEntity(name=item.preview, all_caps=item.preview.isupper(), annotation_id=item.annotation_id)
              for item in emails]

    email_count = 1
    email_map = {}
    for email in emails:
        if email.name.lower() not in email_map:
            pseudo_email = "EMAIL_" + str(email_count)
            email_count += 1
            email_map[email.name.lower()] = pseudo_email
        else:
            pseudo_email = email_map[email.name.lower()]

        email.name_replacement = '[' + pseudo_email + ']'

    return emails
