import io
from dataclasses import dataclass

import pytest
import mutagen.id3 as mt_id3
from mutagen.mp3 import MP3
from pathlib import Path

TEST_FOLDER = "/tmp/songtools_test"


def get_test_folder() -> Path:
    """Return the test folder. If it doesn't exist, create it.

    :rtype: Path
    :return: Test folder path.
    """
    tst_folder = Path(TEST_FOLDER)
    if not tst_folder.exists():
        tst_folder.mkdir()
    return tst_folder


def cleanup_tst_folder() -> None:
    """Remove all files from the test folder and the folder itself"""
    root_tst_folder = get_test_folder()
    nst = 0
    while True and nst < 100:
        test_folder_items = root_tst_folder.rglob("*")
        items = list(test_folder_items)
        if not items:
            break
        for item in items:
            if TEST_FOLDER not in str(item.resolve()):
                raise Exception("Trying to delete a folder outside the test folder")
            if item.is_file():
                item.unlink()
            else:
                try:
                    item.rmdir()
                except OSError:
                    # Run again after files were removed
                    pass
    root_tst_folder.rmdir()
    pass


def make_simple_song_file(
    folder: Path,
    title: str,
    artist: str = "JdP",
    filename: str | None = None,
    source: str = "memory",
) -> Path:
    if filename is None:
        filename = f"{title} - {artist}.mp3"
    song = folder / filename
    mf = MetadataFields(title=title, artist=artist)

    if source == "silence15min.mp3":
        mp3_path = Path(__file__).parent / "tests/fixtures/silence15min.mp3"
        data = mp3_path.read_bytes()
    else:
        data = create_test_mp3_data(metadata=mf)
    song.write_bytes(data)
    return song


@pytest.fixture
def test_folder() -> Path:
    """Fixture to create a test folder and clean it up after the test is done.

    :yields: Test folder path.
    """
    folder = get_test_folder()
    yield folder
    cleanup_tst_folder()


@pytest.fixture
def test_mp3_data(test_folder) -> bytes:
    """Load empty mp3 file.

    :param Path test_folder: Test folder path.

    :rtype: bytes
    :return: MP3 file data.
    """
    mp3_path = Path(__file__).parent / "tests/fixtures/silence20s.mp3"
    return mp3_path.read_bytes()


@pytest.fixture
def test_long_mp3_data(test_folder) -> bytes:
    mp3_path = Path(__file__).parent / "tests/fixtures/silence15min.mp3"
    return mp3_path.read_bytes()


@pytest.fixture
def flac_data(test_folder) -> bytes:
    """
    :param Path test_folder: Test folder path.
    :return: empty FLAC file data.
    """
    flac_path = Path(__file__).parent / "tests/fixtures/silence20s.flac"
    return flac_path.read_bytes()


@dataclass
class MetadataFields:
    title: str
    artist: str


def create_test_mp3_data(metadata: MetadataFields | bool | None = None) -> bytes:
    """Create an empty MP3 file with some basic ID3 tags.

    :rtype: io.BytesIO
    :return: mp3 data that can be stored in a file.

    """
    # Create an in-memory file-like object for MP3
    mp3_data = io.BytesIO()

    mp3_data.write(b"\xff\xfb\x90")
    mp3_data.write(b"\x00" * 32)
    mp3_data.write(
        b"dXing\x00\x00\x00\x0f\x00\x00\x00\x12\x00\x00\x0eY\x00AAAAAKKKKKKSSSSS\\\\\\\\\\\\dddddllllllttttt||||||"
        b"\x85\x85\x85\x85\x85\x8d\x8d\x8d\x8d\x8d\x8d\x95\x95\x95\x95\x95\x95\x9d\x9d\x9d\x9d\x9d"
        b"\xa5\xa5\xa5\xa5\xa5\xa5\xae\xae\xae\xae\xae\xb6\xb6\xb6\xb6\xb6\xb6\xbe\xbe\xbe\xbe\xbe"
        b"\xf7\xf7\xf7\xf7\xf7\xf7\xff\xff\xff\xff\xff\x00\x00\x00PLAME3.100\x04\xb9"
        b"\x00\x00\x00\x00\x00\x00\x00\x005 $\x06qM"
    )

    if metadata is True:
        # For testing non-existing fields
        mp3_data.seek(0)
        audio = MP3(mp3_data, ID3=mt_id3.ID3)
        audio.add_tags()
        audio.save(mp3_data)

    elif type(metadata) is MetadataFields:
        mp3_data.seek(0)
        audio = MP3(mp3_data, ID3=mt_id3.ID3)
        audio.add_tags()
        audio["TIT2"] = mt_id3.TIT2(encoding=3, text=metadata.title)
        audio["TPE1"] = mt_id3.TPE1(encoding=3, text=metadata.artist)
        audio.save(mp3_data)
    mp3_data.seek(0)
    return mp3_data.read()
