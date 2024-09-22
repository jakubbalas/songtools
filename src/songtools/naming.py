import re
from functools import reduce
from unidecode import unidecode


def build_correct_song_name(artists: list[str], title: str) -> str:
    """Get the filename from the metadata of the file.
    If the file has no metadata, return the styled filename.

    :param list[str] artists: List of artists as mentioned in metadata.
    :param str title: Title of the song from metadata.

    :rtype: str
    :return: Valid filename that can be used.
    """

    return basic_music_file_style(", ".join(artists) + " - " + title)


def multi_space_removal(name: str) -> str:
    return " ".join(filter(None, name.split(" ")))


def remove_special_characters(name: str) -> str:
    translations = str.maketrans(
        {
            "?": " ",
            ":": " ",
            "*": "x",
            "\x19": " ",
            "\x01": " ",
            "|": " ",
            ">": " ",
            "<": " ",
            "/": " ",
            "\\": " ",
            "_": " ",
            ".": " ",
        }
    )
    return name.translate(translations).replace("( ", "(").replace(" )", ")")


def remove_original_mix(name: str) -> str:
    name = re.sub(r"\(\s*original\s*\)", "", name, flags=re.IGNORECASE)
    return re.sub(r"\(\s*original mix\s*\)", "", name, flags=re.IGNORECASE)


def basic_music_file_style(name: str) -> str:
    styles = [
        unidecode,
        remove_special_characters,
        multi_space_removal,
        remove_original_mix,
    ]
    return reduce(lambda acc, func: func(acc), styles, name)


def has_cyrillic(text: str):
    """Find out if text has cyrillic characters.

    :param text:
    :return:
    """
    return bool(re.search("[\u0400-\u04ff]", text))
