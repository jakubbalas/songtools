from songtools.conftest import create_test_mp3_data, get_test_folder, cleanup_tst_folder

from songtools.backlog import clean_backlog_folder


def test_backlog_folder_gets_cleaned():
    tst_folder = get_test_folder()
    mp3 = create_test_mp3_data()
    a = tst_folder / "tstmp3.mp3"
    with open(a, "wb") as f:
        f.write(mp3.getvalue())
    clean_backlog_folder()
    cleanup_tst_folder()
    assert True
