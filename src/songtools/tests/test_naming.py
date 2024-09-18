from songtools.naming import has_cyrillic


def test_has_cyrillic():
    text = "Hello, world!"
    assert not has_cyrillic(text)
    text = "Привет, мир!"
    assert has_cyrillic(text)
