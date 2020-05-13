"""Module to contain a standard slugify method"""
import re

from slugify import slugify as _slugify

__all_ = ["slugify"]

r_underscore = re.compile("_")


def slugify(text: str) -> str:
    """Slugify the string with underscore seperators if present"""
    if r_underscore.search(text):
        return _slugify(text, separator="_")
    else:
        return _slugify(text)
