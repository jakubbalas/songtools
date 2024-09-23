import re
from functools import reduce
from unidecode import unidecode


def build_correct_song_name(artists: list[str], title: str) -> str:
    """Get the filename from the metadata of the file.
    If the file has no metadata, return the styled filename.

    :param list[str] artists: List of artists as mentioned in metadata.
    :param str title: Title of the song from metadata.

    :return: Valid filename that can be used.
    """
    artists = [basic_music_file_style(artist) for artist in artists]
    title = basic_music_file_style(title)
    title = remove_original_mix(title)
    return ", ".join(artists) + " - " + title


def multi_space_removal(name: str) -> str:
    return " ".join(filter(None, name.split(" ")))


def remove_special_characters(name: str) -> str:
    """Replacing special characters that may cause issues with filesystems.

    :param name:
    :return: string with removed special characters.
    """
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
    """
    :return: string with removed original mix suffix.
    """

    return re.sub(r"\(\s*original( mix)?\s*\)", "", name, flags=re.IGNORECASE).strip()


def basic_music_file_style(name: str) -> str:
    """
    :param name: artist or song name (works also for whole filename)
    :return: prettified name useful for file naming
    """
    styles = [
        unidecode,
        remove_special_characters,
        multi_space_removal,
    ]
    return reduce(lambda acc, func: func(acc), styles, name)


def has_cyrillic(text: str):
    """Find out if text has cyrillic characters.

    :param text:
    :return:
    """
    return bool(re.search("[\u0400-\u04ff]", text))
