from songtools.conftest import get_test_folder, cleanup_tst_folder

from songtools.backlog import clean_backlog_folder


def _prepare_dirty_backlog_folder():
    """Simulates a backlog folder that is in a proper disarray and needs cleaning.

    :rtype: Path
    :return: Test folder root path.
    """
    root_folder = get_test_folder()
    empty_folder_a = root_folder / "empty_folder_a"
    empty_folder_a.mkdir(exist_ok=True)
    empty_folder_a2 = empty_folder_a / "empty_folder_a2"
    empty_folder_a2.mkdir(exist_ok=True)

    return root_folder


def test_backlog_removes_empty_dirs():
    tst_folder = _prepare_dirty_backlog_folder()
    clean_backlog_folder(tst_folder)
    assert not (tst_folder / "empty_folder_a").exists()
    cleanup_tst_folder()
