from songtools.conftest import create_test_mp3_data, MetadataFields
from pathlib import Path

from songtools.backlog import clean_preimport_folder, IRRELEVANT_SUFFIXES


def _prepare_dirty_backlog_folder(root_folder: Path) -> Path:
    """Simulates a backlog folder that is in a proper disarray and needs cleaning.

    :rtype: Path
    :return: Test folder root path.
    """
    empty_folder_a = root_folder / "empty_folder_a"
    empty_folder_a.mkdir(exist_ok=True)
    empty_folder_a2 = empty_folder_a / "empty_folder_a2"
    empty_folder_a2.mkdir(exist_ok=True)
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

    return root_folder


def test_remove_empty_dirs(test_folder: Path):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    assert not (tst_folder / "empty_folder_a").exists()
    assert not (tst_folder / "folder_with_rubbish").exists()


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
    assert tst_folder / "mixed_folder/cyrillic_file_тест.mp3"


def test_expected_folder_structure_after_cleanup(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_preimport_folder(tst_folder)
    items = [f for f in test_folder.glob("*")]
    assert len(items) == 0
