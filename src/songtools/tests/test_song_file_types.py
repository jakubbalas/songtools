import pytest
from pathlib import Path
from songtools.conftest import create_test_mp3_data, MetadataFields
from songtools.song_file_types import (
    SongFile,
    UnsupportedSongType,
    UnableToExtractData,
)


def test_missing_song_file_raises_error():
    with pytest.raises(FileNotFoundError):
        SongFile(Path("test"))


def test_unsupported_song_file_raises_error(test_folder: Path):
    unsupported_file = test_folder / "test.txt"
    unsupported_file.touch()
    with pytest.raises(UnsupportedSongType):
        SongFile(unsupported_file)


def test_mp3_without_data_raises_exception(test_folder: Path):
    mp3_file = test_folder / "test_no_dash.mp3"
    mp3_file.touch()

    with pytest.raises(UnableToExtractData):
        SongFile(mp3_file)

    mp3_file = test_folder / "test-too-many_dashes.mp3"
    mp3_file.touch()

    with pytest.raises(UnableToExtractData):
        SongFile(mp3_file)


def test_mp3_gets_data_from_metadata(test_folder: Path):
    test_mp3_file = test_folder / "test_art - test.mp3"

    mt = MetadataFields(artist="Chi:mera, Jake DaPhunk", title="My awesome song")
    test_mp3_file.write_bytes(create_test_mp3_data(mt))

    song = SongFile(test_mp3_file)
    assert song.artists == ["Chi:mera", "Jake DaPhunk"]
    assert song.title == "My awesome song"


def test_mp3_gets_artist_and_title_from_filename_if_metadata_doesnt_contain_it(
    test_folder: Path,
):
    test_mp3_file = test_folder / "jdp - glowing skies.mp3"
    test_mp3_file.write_bytes(create_test_mp3_data(metadata=True))

    song = SongFile(test_mp3_file)
    assert song.artists == [
        "jdp",
    ]
    assert song.title == "glowing skies"


def test_mp3_gets_artists_and_title_from_filename_if_metadata_not_present(
    test_folder: Path,
):
    test_mp3_file = test_folder / "chimera, jdp - get it.mp3"
    test_mp3_file.touch()

    song = SongFile(test_mp3_file)
    assert song.artists == ["chimera", "jdp"]
    assert song.title == "get it"


def test_duration_is_present_for_files_with_no_metadata(test_folder, test_mp3_data):
    test_mp3_file = test_folder / "chimera, jdp - get it.mp3"
    test_mp3_file.write_bytes(test_mp3_data)

    song = SongFile(test_mp3_file)
    assert song.duration_seconds == 17


def test_flac_file_gets_metadata(test_folder: Path, flac_data):
    test_flac_file = test_folder / "JdPouch - shouldwork.flac"
    test_flac_file.write_bytes(flac_data)

    song = SongFile(test_flac_file)
    assert type(song) is SongFile
    assert song.artists == ["JdPouch"]
