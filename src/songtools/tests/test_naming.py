import pytest

from songtools.naming import (
    has_cyrillic,
    remove_special_characters,
    multi_space_removal,
    remove_original_mix,
    basic_music_file_style,
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
        ("Γεια σας κόσμε", "Geia sas kosme"),
        ("Ahoj * světe", "Ahoj x svete"),
    ],
)
def test_basic_styling(test_in, test_out):
    assert basic_music_file_style(test_in) == test_out
