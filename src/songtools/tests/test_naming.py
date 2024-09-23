from songtools.naming import (
    has_cyrillic,
    remove_special_characters,
    multi_space_removal,
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
