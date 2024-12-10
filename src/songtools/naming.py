import re
import string
from pathlib import Path
from random import randint

from functools import reduce
from unidecode import unidecode

from songtools.utils import echo


def  build_correct_song_file_name(artists: list[str], orig_title: str) -> str:
    """Get the filename from the metadata of the file.
    If the file has no metadata, return the styled filename.

    :param artists: List of artists as mentioned in metadata.
    :param orig_title: Title of the song from metadata.

    :return: Valid filename that can be used.
    """
    orig_title = basic_music_file_style(orig_title)
    title = handle_title(orig_title)
    artists = [basic_music_file_style(a) for a in artists]

    artists = handle_artists(artists, remove_original_mix(orig_title))

    return ", ".join(artists) + " - " + title


def handle_title(title: str) -> str:
    """
    :param title: Title of the song.
    :return: Correctly formatted title.
    """
    title = basic_music_file_style(title)
    title = remove_original_mix(title)
    title, _ = extract_featuring_artists(title)
    return title


def handle_artists(artists: list[str], title: str) -> list[str]:
    """Handle artists that are in the metadata.

    :param artists: List of artists from metadata.
    :param title: original title that can contain feat artists.
    :return: Correctly formatted artist names.
    """
    all_artists = []
    for a in artists:
        artist, featuring = extract_featuring_artists(a)
        all_artists.append(artist)
        all_artists += featuring
    _, title_artists = extract_featuring_artists(title)
    title_artists = [basic_music_file_style(a) for a in title_artists]
    all_artists += title_artists
    all_artists = [basic_music_file_style(a) for a in all_artists]
    return sorted(set(all_artists))


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
    :return: string with removed "original mix" suffix.
    """

    return re.sub(r"\(\s*original( mix)?\s*\)", "", name, flags=re.I).strip()


def basic_music_file_style(name: str) -> str:
    """
    :param name: artist or song name (works also for whole filename)
    :return: prettified name useful for file naming
    """
    styles = [unidecode, remove_special_characters, multi_space_removal, capitalize]
    return reduce(lambda acc, func: func(acc), styles, name)


def has_cyrillic(text: str):
    """Find out if text has cyrillic characters.

    :param text:
    :return:
    """
    return bool(re.search("[\u0400-\u04ff]", text))


def capitalize(name: str) -> str:
    """
    :param name: name to capitalize
    :return: correctly capitalized name
    """
    name = string.capwords(name)

    replacements = {
        " And ": " and ",
        " At ": " at ",
        " Of ": " of ",
        " The ": " the ",
        " Is ": " is ",
    }
    for k, v in replacements.items():
        name = name.replace(k, v)

    # Capitalize first character after characters: (,"
    name = re.sub(
        r'[\(,"\[]\s*([a-z])',
        lambda match: f"{match.group(0)[0]}{match.group(1).upper()}",
        name,
    )

    return name


def extract_featuring_artists(title) -> (str, list[str]):
    """Takes title and extracts featuring artists from it.

    :param title: original title
    :return: title without featuring artists and list of featuring artists
    """
    artists = []
    patterns = [
        (r"(Feat(\.?)|ft\.|featuring) (.*?) -", " -"),
        (r"\((Feat(\.?)|ft\.) (.*?)\) ", ""),
        (r" \(?\[?(Feat(\.?)|ft\.) (.*?)\)?\]?$", ""),
    ]
    for regex in patterns:
        feats = re.search(regex[0], title, re.I)
        if feats:
            artists.append(re.search(regex[0], title, re.I).group(3))
            title = title.replace(re.search(regex[0], title, re.I).group(0), regex[1])

    return title, artists
