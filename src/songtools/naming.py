import re
from pathlib import Path


def get_filename_from_metadata(file: Path) -> str:
    """Get the filename from the metadata of the file.
    If the file has no metadata, return the styled filename.

    :param Path file: Path to the file.

    :rtype: str
    :return: Filename from the metadata.
    """
    pass


def has_cyrillic(text: str):
    """Find out if text has cyrillic characters.

    :param text:
    :return:
    """
    return bool(re.search("[\u0400-\u04ff]", text))
