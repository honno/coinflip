import re

from slugify import slugify as slugify_

r_underscore = re.compile("_")


def slugify(text: str) -> str:
    if r_underscore.search(text):
        return slugify_(text, separator="_")
    else:
        return slugify_(text)
