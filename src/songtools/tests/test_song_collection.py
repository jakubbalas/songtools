from unittest.mock import patch
from sqlalchemy.orm import Session
from sqlalchemy import select

from songtools.conftest import make_simple_song_file
from songtools.db.models import CollectionSong, HeardSong
from songtools.db.session import get_in_memory_engine
from songtools.song_collection import get_incorrectly_formatted_collection_names, sync_collection_items
from songtools.song_file_types import SongFile


def test_get_list_of_incorrectly_formatted_songs_in_collection(test_folder):
    make_simple_song_file(test_folder, "test", "artist", "Artist - Test.mp3")
    make_simple_song_file(test_folder, "test", "artist", "Artist - Test (original mix).mp3")
    make_simple_song_file(test_folder, "Song 1", "Other, Artist", "Other, Artist - Test.mp3")
    sub_folder = test_folder / "subfolder"
    sub_folder.mkdir()

    make_simple_song_file(sub_folder, "Song 2", "JTB", "whatev.mp3")
    with patch("songtools.song_collection.config.collection_path", test_folder.absolute()):
        res = get_incorrectly_formatted_collection_names()

    assert 3 == len(res)


def test_syncing_collection_makes_db_consistent_with_folder(test_folder):
    dance_folder = test_folder / "Dance"
    dance_folder.mkdir()
    make_simple_song_file(dance_folder, "song 1", "dance artist", "Dance Artist - Test.mp3")
    song_dance_2 = make_simple_song_file(dance_folder, "song 2", "dance artist")
    song_dance_2_file = SongFile(song_dance_2)

    rock_folder = test_folder / "Rock"
    rock_folder.mkdir()
    make_simple_song_file(rock_folder, "song 1", "rock artist")
    song_rock_2 = make_simple_song_file(rock_folder, "song 2", "rock 2 artist")
    song_rock_2_hash = SongFile(song_rock_2)


    indie_folder = rock_folder / "Indie"
    indie_folder.mkdir()
    make_simple_song_file(indie_folder, "song 2", "indie artist")

    db_engine = get_in_memory_engine()
    HeardSong.metadata.create_all(db_engine)
    CollectionSong.metadata.create_all(db_engine)

    with Session(db_engine) as session:
        session.add_all([
            CollectionSong(name_hash="tobedeleted", file_path="Dance/JDP - NotInteresting.mp3", file_size=1234),
            HeardSong(name_hash="toberemoved", file_name="Dance/JDP - Kicked Out.mp3", in_collection=True),
            HeardSong(name_hash=song_dance_2_file.name_hash, file_name="Dance/Dance Artist - Test.mp3", in_collection=False),
            HeardSong(name_hash=song_rock_2_hash.name_hash, file_name="Rock/Rock Artist - Test.mp3", in_collection=False),
        ])
        session.commit()

    with patch("songtools.song_collection.config.collection_path", test_folder.absolute()):
        sync_collection_items(db_engine)

    with Session(db_engine) as session:
        collection_songs = session.scalars(select(CollectionSong)).all()
        assert 5 == len(collection_songs)
        heard_songs = session.scalars(select(HeardSong).where(HeardSong.in_collection==True)).all()
        assert 5 == len(heard_songs)
        heard_songs = session.scalars(select(HeardSong)).all()
        assert 6 == len(heard_songs)
