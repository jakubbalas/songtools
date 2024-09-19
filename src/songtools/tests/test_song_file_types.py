import pytest
from pathlib import Path

from songtools.song_file_types import get_song_file, MP3File, UnsupportedSongType


def test_missing_song_file_raises_error():
    with pytest.raises(FileNotFoundError):
        get_song_file(Path("test"))


def test_unsupported_song_file_raises_error(test_folder):
    unsupported_file = test_folder / "test.txt"
    unsupported_file.touch()
    with pytest.raises(UnsupportedSongType):
        get_song_file(unsupported_file)


def test_mp3_is_created(test_folder):
    mp3_file = test_folder / "test.mp3"
    mp3_file.touch()
    mp3_file = get_song_file(mp3_file)
    assert type(mp3_file) is MP3File
