import pytest

from songtools.naming import (
    has_cyrillic,
    remove_special_characters,
    multi_space_removal,
    remove_original_mix,
    basic_music_file_style,
    capitalize,
    extract_featuring_artists,
    build_correct_song_file_name,
)


def test_has_cyrillic():
    text = "Hello, world!"
    assert not has_cyrillic(text)
    text = "Привет, мир!"
    assert has_cyrillic(text)


def test_remove_special_characters():
    text = "Hi?my:name.is\x19a\x01big|j( * )dp>and<this/is\\my_crib.."
    assert (
        "Hi my name is a big j(x)dp and this is my crib  "
        == remove_special_characters(text)
    )


def test_multi_space_removal():
    text = "What do  you    think about too many    spaces?"
    assert "What do you think about too many spaces?" == multi_space_removal(text)


@pytest.mark.parametrize(
    "test_in,test_out",
    [
        ("test me (some mix)", "test me (some mix)"),
        ("original mix", "original mix"),
        ("test (original mix)", "test"),
        ("original mix (OriginAl MiX)", "original mix"),
        ("original mix (OriginAl MiXalot)", "original mix (OriginAl MiXalot)"),
        ("some song (original)", "some song"),
    ],
)
def test_remove_original_mix_from_title(test_in, test_out):
    assert remove_original_mix(test_in) == test_out


@pytest.mark.parametrize(
    "test_in,test_out",
    [
        ("Γεια σας κόσμε", "Geia Sas Kosme"),
        ("Ahoj * světe", "Ahoj X Svete"),
    ],
)
def test_basic_styling(test_in, test_out):
    assert basic_music_file_style(test_in) == test_out


@pytest.mark.parametrize(
    "test_in,test_out",
    [
        ("world's LAZIEST crowd", "World's Laziest Crowd"),
        ("JJ AND Lulu", "Jj and Lulu"),
        ("AND what IS this ?", "And What is This ?"),
        ("Sentence Of The Day At home", "Sentence of the Day at Home"),
    ],
)
def test_capitalizing(test_in, test_out):
    assert capitalize(test_in) == test_out


@pytest.mark.parametrize(
    "test_in,test_out",
    [
        ("smalls (ft. madonna)", ("smalls", ["madonna"])),
        ("rivers (feat JDP)", ("rivers", ["JDP"])),
        ("rivers feat. JDP", ("rivers", ["JDP"])),
    ],
)
def test_featuring_extraction(test_in, test_out):
    assert extract_featuring_artists(test_in) == test_out


@pytest.mark.parametrize(
    "test_artists,test_title,test_out",
    [
        (["JDP", "JakeDaPhunk"], "frequencies", "Jakedaphunk, Jdp - Frequencies"),
        (["JDP feat. JakeDaPhunk"], "frequencies", "Jakedaphunk, Jdp - Frequencies"),
        (["JDP "], "frequencies feat. JakeDaphunk", "Jakedaphunk, Jdp - Frequencies"),
        (["JDP", "Jake"], "frequencies feat. Jake", "Jake, Jdp - Frequencies"),
        (["JDP"], "frequencies (jake remix)", "Jdp - Frequencies (Jake Remix)"),
        (["JDP"], 'frequencies ("jake" remix)', 'Jdp - Frequencies ("Jake" Remix)'),
    ],
)
def test_build_correct_song_file_name(test_artists, test_title, test_out):
    assert build_correct_song_file_name(test_artists, test_title) == test_out
