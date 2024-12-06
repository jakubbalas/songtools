from unittest.mock import patch

import pytest

from songtools.conftest import create_test_mp3_data, MetadataFields
from pathlib import Path
from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker
from songtools.backlog import (
    clean_preimport_folder,
    IRRELEVANT_SUFFIXES,
    load_backlog_folder_files,
    load_backlog_folder_metadata, delete_song_folder, InsecureDeleteException, dedup_song_folder,
)
from songtools.db.models import BacklogSong, HeardSong
from songtools.db.session import get_in_memory_engine
from songtools.naming import get_song_name_hash
from songtools.song_file_types import SongFile


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

    screaming_suffix = mixed_folder / "onetwo - threefour.MP3"
    data = create_test_mp3_data(metadata=False)
    screaming_suffix.write_bytes(data)

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
    assert len(items) == 4


def test_dj_mixes_are_removed(test_folder, test_long_mp3_data):
    dj_mix = test_folder / "dj - mix.mp3"
    dj_mix.write_bytes(test_long_mp3_data)
    with patch('songtools.backlog.MUSIC_MIX_MIN_SECONDS', 800):
        clean_preimport_folder(test_folder)
    assert not dj_mix.exists()


def test_uppercase_suffixes_get_lowered(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    assert (tst_folder / "mixed_folder/Onetwo - Threefour.mp3").exists()


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
    load_backlog_folder_metadata(engine)

    session = sessionmaker(bind=engine)
    session = session()
    songs = session.query(BacklogSong).all()

    assert len(songs) == 1
    assert songs[0].title == mf.title


def test_delete_removes_files_and_subfolders(test_folder):
    engine = get_in_memory_engine()
    HeardSong.metadata.create_all(engine)

    song_1 = test_folder / "song_1.mp3"
    mf = MetadataFields(title="Song uno", artist="JdPouch")
    data = create_test_mp3_data(metadata=mf)
    song_1.write_bytes(data)
    song_1_name_hash = get_song_name_hash(SongFile(song_1))

    song_2 = test_folder / "song_2.mp3"
    mf = MetadataFields(title="Song  Duo", artist="JdPouch")
    data = create_test_mp3_data(metadata=mf)
    song_2.write_bytes(data)

    one_level_dir = test_folder / "one_dir"
    one_level_dir.mkdir()
    (one_level_dir / "stuff.txt").touch()

    two_level_dir = one_level_dir / "two_dir"
    two_level_dir.mkdir()
    song_3 = two_level_dir / "song_3.mp3"
    mf = MetadataFields(title="Song  Three", artist="JdVouch")
    data = create_test_mp3_data(metadata=mf)
    song_3.write_bytes(data)

    delete_song_folder(test_folder, engine)
    assert not test_folder.exists()

    session = sessionmaker(bind=engine)
    session = session()
    songs = session.query(HeardSong).order_by(asc(HeardSong.file_name)).all()
    assert len(songs) == 3
    assert songs[0].name_hash == song_1_name_hash


def test_existing_item_is_not_duplicated(test_folder):
    song_1 = test_folder / "song_1.mp3"
    mf = MetadataFields(title="Song uno", artist="JdPouch")
    data = create_test_mp3_data(metadata=mf)
    song_1.write_bytes(data)

    song_2 = test_folder / "song_2.mp3"
    mf = MetadataFields(title="Song uno", artist="JdPouch")
    data = create_test_mp3_data(metadata=mf)
    song_2.write_bytes(data)

    engine = get_in_memory_engine()
    HeardSong.metadata.create_all(engine)

    delete_song_folder(test_folder, engine)

    session = sessionmaker(bind=engine)
    session = session()
    songs = session.query(HeardSong).order_by(asc(HeardSong.file_name)).all()
    assert len(songs) == 1


def test_unknown_file_raises_exception(test_folder):
    unknown_file = test_folder / "unknown_file.ggwp"
    unknown_file.touch()
    with pytest.raises(InsecureDeleteException):
        delete_song_folder(test_folder, get_in_memory_engine())


def make_simple_song(folder: Path, title: str, artist: str = "JdP") -> Path:
    song = folder / f"{title} - {artist}.mp3"
    mf = MetadataFields(title=title, artist=artist)
    data = create_test_mp3_data(metadata=mf)
    song.write_bytes(data)
    return song


def test_dedup_removes_duplicates_also_in_subfolders(test_folder):
    engine = get_in_memory_engine()
    HeardSong.metadata.create_all(engine)

    song_1 = make_simple_song(test_folder, "Song uno")
    song_2 = make_simple_song(test_folder, "Song due")
    song_3 = make_simple_song(test_folder, "Song tre")
    folder_lvl_2 = test_folder / "lvl2"
    folder_lvl_2.mkdir()
    song_4 = make_simple_song(folder_lvl_2, "Song Four")
    song_5 = make_simple_song(folder_lvl_2, "Song five")
    folder_lvl_3 = folder_lvl_2 / "lvl3"
    folder_lvl_3.mkdir()
    song_6 = make_simple_song(folder_lvl_3, "Song Six")

    session = sessionmaker(bind=engine)
    session = session()
    with session as s:
        s.add_all([
            HeardSong(file_name=song_1.name, name_hash=get_song_name_hash(SongFile(song_1))),
            HeardSong(file_name=song_4.name, name_hash=get_song_name_hash(SongFile(song_4))),
            HeardSong(file_name=song_6.name, name_hash=get_song_name_hash(SongFile(song_6))),
        ])
        s.commit()



    dedup_song_folder(test_folder, engine)

    assert not song_1.exists()
    assert song_2.exists()
    assert song_3.exists()
    assert not song_4.exists()
    assert song_5.exists()
    assert not song_6.exists()
