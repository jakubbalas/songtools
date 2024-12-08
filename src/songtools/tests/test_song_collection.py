from songtools.conftest import make_simple_song_file
from songtools.song_collection import get_incorrectly_formatted_collection_names


def test_get_list_of_incorrectly_formatted_songs_in_collection(test_folder):
    make_simple_song_file(test_folder, "test", "artist", "Artist - Test.mp3")
    make_simple_song_file(test_folder, "test", "artist", "Artist - Test (original mix).mp3")
    make_simple_song_file(test_folder, "Song 1", "Other, Artist", "Other, Artist - Test.mp3")
    sub_folder = test_folder / "subfolder"
    sub_folder.mkdir()

    make_simple_song_file(sub_folder, "Song 2", "JTB", "whatev.mp3")
    res = get_incorrectly_formatted_collection_names(test_folder)

    assert 3 == len(res)
