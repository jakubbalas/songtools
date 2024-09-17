from pathlib import Path

from songtools.backlog import clean_backlog_folder, IRRELEVANT_SUFFIXES


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

    return root_folder


def test_remove_empty_dirs_from_backlog(test_folder: Path):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_backlog_folder(tst_folder)
    assert not (tst_folder / "empty_folder_a").exists()


def test_remove_irrelevant_files_from_backlog(test_folder):
    tst_folder = _prepare_dirty_backlog_folder(test_folder)
    clean_backlog_folder(tst_folder)
    # specifically not automating this to better see what's going on
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.txt").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.jpg").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.png").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.m3u").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.nfo").exists()
    assert not (tst_folder / "folder_with_rubbish/irrelevant_file.cue").exists()
