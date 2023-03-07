from django.core.exceptions import ValidationError
import re

"""
Insert your validator codes here
"""

def is_valid_username():
    """Raises an exception if a string contains characters other than latin alphabet, number, and _ - ."""
    if re.search(r"[^\w\d.\-]"):
        raise ValidationError("Not a valid username!")

