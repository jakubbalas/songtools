from songtools.conftest import create_test_mp3_data, MetadataFields
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from songtools.backlog import (
    clean_preimport_folder,
    IRRELEVANT_SUFFIXES,
    load_backlog_folder_files,
    load_backlog_folder_metadata,
)
from songtools.db.models import BacklogSong
from songtools.db.session import get_in_memory_engine


def _prepare_dirty_backlog_folder(root_folder: Path) -> Path:
    """Simulates a backlog folder that is in a proper disarray and needs cleaning.

    :rtype: Path
    :return: Test folder root path.
    """
    empty_folder_a = root_folder / "empty_folder_a"
    empty_folder_a.mkdir(exist_ok=True)
    empty_folder_a2 = empty_folder_a / "empty_folder_a2"
    empty_folder_a2.mkdir(exist_ok=True)

    metadata_only_folder = root_folder / "metadata_only_folder"
    metadata_only_folder.mkdir(exist_ok=True)
    metadata_file = metadata_only_folder / ".DS_Store"
    metadata_file.touch()

    folder_with_rubbish = empty_folder_a / "folder_with_rubbish"
    folder_with_rubbish.mkdir(exist_ok=True)

    for suffix in IRRELEVANT_SUFFIXES:
        irrelevant_suffix = folder_with_rubbish / f"irrelevant_file{suffix}"
        irrelevant_suffix.touch()

    mixed_folder = root_folder / "mixed_folder"
    mixed_folder.mkdir(exist_ok=True)
    cyrillic_file = mixed_folder / "cyrillic-file_тест.mp3"
    cyrillic_file.touch()

    cyrillic_in_meta_file = mixed_folder / "jdpouch - shouldwork.mp3"
    mf = MetadataFields(title="Song тест", artist="JdPouch")
    data = create_test_mp3_data(mf)
    cyrillic_in_meta_file.write_bytes(data)

    case_rename = mixed_folder / "JoUch - Freeze.mp3"
    data = create_test_mp3_data(metadata=False)
    case_rename.write_bytes(data)

    return root_folder


def test_remove_empty_dirs(test_folder: Path):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    assert not (tst_folder / "empty_folder_a").exists()
    assert not (tst_folder / "folder_with_rubbish").exists()


def test_remove_folders_with_metadata_only(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    assert not (tst_folder / "metadata_only_folder").exists()


def test_remove_irrelevant_files(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    # specifically not automating this to better see what's going on
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.txt").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.jpg").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.png").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.m3u").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.nfo").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.cue").exists()


def test_remove_files_with_cyrillic(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    assert not (tst_folder / "mixed_folder/cyrillic_file_тест.mp3").exists()


def test_renaming_casing_only_works(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    items = [f for f in test_folder.rglob("*")]
    print(items)
    assert (tst_folder / "mixed_folder/Jouch - Freeze.mp3").exists()


def test_expected_folder_structure_after_cleanup(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    items = [f for f in test_folder.rglob("*")]
    assert len(items) == 3


def test_dj_mixes_are_removed(test_folder, test_long_mp3_data):
    dj_mix = test_folder / "dj - mix.mp3"
    dj_mix.write_bytes(test_long_mp3_data)
    clean_preimport_folder(test_folder)
    assert not dj_mix.exists()


def test_songs_in_backlog_are_loaded_into_db(test_folder):
    engine = get_in_memory_engine()
    BacklogSong.metadata.create_all(engine)
    num_entries = 44
    for i in range(num_entries):
        f = test_folder / f"song_{i}.mp3"
        f.touch()
    load_backlog_folder_files(test_folder, engine, store_after=9)

    session = sessionmaker(bind=engine)
    session = session()
    songs = session.query(BacklogSong).count()
    assert songs == num_entries


def test_songs_from_the_db_get_metadata_loaded(test_folder):
    engine = get_in_memory_engine()
    BacklogSong.metadata.create_all(engine)

    song_1 = test_folder / "song_1.mp3"
    mf = MetadataFields(title="Song uno", artist="JdPouch")
    data = create_test_mp3_data(metadata=mf)
    song_1.write_bytes(data)

    load_backlog_folder_files(test_folder, engine, store_after=9)
    load_backlog_folder_metadata()

    session = sessionmaker(bind=engine)
    session = session()
    songs = session.query(BacklogSong).all()
    assert len(songs) == 1
    assert songs[0].title == mf.title
