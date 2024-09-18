import pytest
from pathlib import Path
from songtools.song_file_types import SongFile, MP3File


def test_song_file():
    with pytest.raises(FileNotFoundError):
        SongFile.construct(Path("test"))


def test_mp3_is_created(test_folder):
    mp3_file = test_folder / "test.mp3"
    mp3_file.touch()
    mp3_file = SongFile.construct(mp3_file)
    assert type(mp3_file) is MP3File
