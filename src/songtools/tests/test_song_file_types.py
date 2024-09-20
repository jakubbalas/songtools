import pytest
from pathlib import Path
from mutagen import id3
from mutagen.mp3 import MP3

from songtools.song_file_types import get_song_file, MP3File, UnsupportedSongType


def test_missing_song_file_raises_error():
    with pytest.raises(FileNotFoundError):
        get_song_file(Path("test"))


def test_unsupported_song_file_raises_error(test_folder: Path):
    unsupported_file = test_folder / "test.txt"
    unsupported_file.touch()
    with pytest.raises(UnsupportedSongType):
        get_song_file(unsupported_file)


def test_mp3_is_created(test_folder: Path):
    mp3_file = test_folder / "test.mp3"
    mp3_file.touch()
    mp3_file = get_song_file(mp3_file)
    assert type(mp3_file) is MP3File


def test_mp3_gets_data_from_metadata(test_folder: Path, test_mp3_data):
    test_mp3_file = test_folder / "test_art - test.mp3"
    test_mp3_file.write_bytes(test_mp3_data)

    audio = MP3(test_mp3_file, ID3=id3.ID3)
    audio.add_tags()
    audio["TPE1"] = id3.TPE1(encoding=3, text="Chi:mera, Jake DaPhunk")
    audio["TIT2"] = id3.TIT2(encoding=3, text="My awesome song")
    audio.save(test_mp3_file)

    song = get_song_file(test_mp3_file)
    assert song.get_artists() == ["Chi:mera", "Jake DaPhunk"]
    assert song.get_title() == "My awesome song"


def test_mp3_gets_artist_and_title_from_filename_if_metadata_doesnt_contain_it(
    test_folder: Path, test_mp3_data
):
    test_mp3_file = test_folder / "jdp - glowing skies.mp3"
    test_mp3_file.write_bytes(test_mp3_data)

    audio = MP3(test_mp3_file, ID3=id3.ID3)
    audio.add_tags()
    audio.save(test_mp3_file)

    song = get_song_file(test_mp3_file)
    assert song.get_artists() == [
        "jdp",
    ]
    assert song.get_title() == "glowing skies"


def test_mp3_gets_artists_and_title_from_filename_if_metadata_not_present(
    test_folder: Path,
):
    test_mp3_file = test_folder / "chimera, jdp - get it.mp3"
    test_mp3_file.touch()

    song = get_song_file(test_mp3_file)
    assert song.get_artists() == ["chimera", "jdp"]
    assert song.get_title() == "get it"
