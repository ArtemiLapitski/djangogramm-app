from re import match
from django.core.exceptions import ValidationError


def name_validator(name: str) -> str:
    name = name.strip()
    if '  ' in name:
        raise ValidationError("Double space is not allowed")
    if not name[0].isalpha():
        raise ValidationError("First character should be a letter")
    elif not match("^[a-zA-Z0-9 -]*$", name):
        raise ValidationError("Only letters, numbers and spaces are allowed")
    else:
        return name.title()
