import mutagen
from pathlib import Path
from abc import ABC, abstractmethod


class UnsupportedSongType(Exception):
    pass


class SongFile(ABC):
    def __init__(self, path: Path):
        self.path = path
        try:
            self.metadata = mutagen.File(path)
        except mutagen.MutagenError:
            self.metadata = None

    def get_artists(self) -> list[str]:
        artists = self.get_metadata_artists()
        if not artists:
            artists = self.get_artists_from_filename()

        return artists.split(", ")

    def get_artists_from_filename(self) -> str:
        """Fallback method to extract artists from filename.

        :rtype: list[str]
        :return: List of artists collaborating on a song.
        """
        return self.path.stem.split("-")[0]

    @abstractmethod
    def get_metadata_artists(self) -> list[str]:
        """
        :rtype: list[str]
        :return: List of artists collaborating on a song.
        """
        pass

    def get_title(self) -> str:
        title = self.get_metadata_title()
        if not title:
            title = self.get_title_from_filename()

        return title

    def get_title_from_filename(self) -> str:
        """Fallback method to extract title from filename.

        :rtype: str
        :return: Title of a song.
        """
        return self.path.stem.split("-")[1]

    @abstractmethod
    def get_metadata_title(self) -> str:
        """
        :rtype: str
        :return: Extracted title of a song.
        """
        pass


def get_song_file(file: Path) -> SongFile:
    """

    :param file:
    :return:
    """
    if not file.exists():
        raise FileNotFoundError(f"Song File {file} does not exist.")
    if file.suffix == ".mp3":
        return MP3File(file)
    else:
        raise UnsupportedSongType(f"Song File {file} is not supported.")


class MP3File(SongFile):
    def __init__(self, file: Path):
        super().__init__(file)

    def get_metadata_artists(self) -> str:
        return str(self.metadata.tags.get("TPE1"))

    def get_metadata_title(self) -> str:
        # TODO: implement
        return ""
