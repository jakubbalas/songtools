import click
import mutagen
import math

from abc import ABC, abstractmethod
from pathlib import Path


class UnsupportedSongType(Exception):
    pass


class UnableToExtractData(Exception):
    pass


class SongFile(ABC):
    def __init__(self, path: Path):
        self.path = path
        try:
            self.metadata = mutagen.File(path)
        except mutagen.MutagenError:
            self.metadata = None
            self._check()
            click.secho(f"Could not read metadata from file {path}.", fg="yellow")
            self.metadata = None
        self._check()

    def _check(self):
        if self.path.stem.count("-") != 1 and not (
            self._get_metadata_title() and self._get_metadata_artists()
        ):
            raise UnableToExtractData(
                f"Unable to extract data from metadata or filename: {self.path}."
            )

    def get_artists(self) -> list[str]:
        """Retrieve artists from metadata, or filename if metadata is not present.

        :return: List of all artists collaborating on a song.
        """
        artists = self._get_metadata_artists()
        if not artists:
            click.secho(
                f"No artist metadata for song {self.path}, using file name.",
                fg="yellow",
            )
            artists = self._get_artists_from_filename()

        return [a.strip() for a in artists.split(", ")]

    def get_duration_seconds(self) -> int:
        """
        :return: Duration of the song in seconds
        """
        return math.ceil(self.metadata.info.length)

    def get_title(self) -> str:
        """
        :rtype: str
        :return: Song title
        """
        title = self._get_metadata_title()
        if not title:
            click.secho(
                f"No title metadata for song {self.path}, using file name.", fg="yellow"
            )
            title = self._get_title_from_filename()

        return title.strip()

    def _get_artists_from_filename(self) -> str:
        """Fallback method to extract artists from filename.

        :rtype: list[str]
        :return: List of artists collaborating on a song.
        """
        return self.path.stem.split("-")[0]

    @abstractmethod
    def _get_metadata_artists(self) -> list[str]:
        """
        :rtype: list[str]
        :return: List of artists collaborating on a song.
        """
        pass

    def _get_title_from_filename(self) -> str:
        """Fallback method to extract title from filename.

        :rtype: str
        :return: Title of a song.
        """
        return self.path.stem.split("-")[1]

    @abstractmethod
    def _get_metadata_title(self) -> str:
        """
        :rtype: str
        :return: Extracted title of a song.
        """
        pass


def get_song_file(file: Path) -> SongFile:
    """
    :param file:

    :return: Concrete SongFile object based on the file type.
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

    def _get_metadata_artists(self) -> str:
        """
        :rtype: str
        :return: Song artists
        """
        return self._get_tag("TPE1")

    def _get_metadata_title(self) -> str:
        """
        :rtype: str
        :return:
        """
        return self._get_tag("TIT2")

    def _get_tag(self, tag: str) -> str:
        if not self.metadata or not self.metadata.tags:
            return ""
        return str(self.metadata.tags.get(tag, ""))
