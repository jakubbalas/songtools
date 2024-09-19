from pathlib import Path
from abc import ABC, abstractmethod


class UnsupportedSongType(Exception):
    pass


class SongFile(ABC):
    def __init__(self, path: Path):
        self.path = path

    def get_path(self) -> Path:
        return self.path

    @abstractmethod
    def get_artists(self) -> list[str]:
        """
        :rtype: list[str]
        :return: List of artists collaborating on a song.
        """
        pass

    @abstractmethod
    def get_title(self) -> str:
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

    def get_artists(self) -> str:
        # TODO: implement
        pass

    def get_title(self) -> str:
        # TODO: implement
        pass
